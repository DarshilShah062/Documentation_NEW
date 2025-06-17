import os
import streamlit as st
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
try:
    # Older versions of langchain_pinecone exposed `PineconeVectorStore` directly
    from langchain_pinecone import PineconeVectorStore
except ImportError:  # pragma: no cover - handle new package versions
    # Newer releases renamed the class to `Pinecone`
    from langchain_pinecone import Pinecone as PineconeVectorStore
from pinecone import Pinecone
import hashlib
from datetime import datetime
from google_drive_manager import GoogleDriveManager

class DocumentProcessor:
    def __init__(self):
        load_dotenv()
        
        # Initialize Google Drive manager
        self.drive_manager = GoogleDriveManager()
        
        # Initialize Pinecone and OpenAI
        self.setup_clients()
        
        # Text splitter configuration
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
    
    def get_env_variable(self, key, default=None):
        """Get environment variable with Streamlit secrets fallback"""
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
        return os.getenv(key, default)
    
    def setup_clients(self):
        """Initialize Pinecone and OpenAI clients"""
        try:
            # Get API keys
            openai_key = self.get_env_variable('OPENAI_API_KEY')
            pinecone_key = self.get_env_variable('PINECONE_API_KEY')
            
            if not openai_key or not pinecone_key:
                if hasattr(st, 'error'):
                    st.error("❌ Missing API keys. Please check your configuration.")
                else:
                    print("❌ Missing API keys. Please check your configuration.")
                return False
            
            # Initialize embeddings with explicit API key
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=openai_key,
                model="text-embedding-3-small"  # Ensure compatibility
            )
            
            # Initialize Pinecone
            pc = Pinecone(api_key=pinecone_key)
            index_name = self.get_env_variable('PINECONE_INDEX_NAME', 'chatbot')
            
            # Check if index exists
            try:
                if index_name not in pc.list_indexes().names():
                    error_msg = f"❌ Pinecone index '{index_name}' not found. Please create it first."
                    if hasattr(st, 'error'):
                        st.error(error_msg)
                    else:
                        print(error_msg)
                    return False
            except Exception as e:
                print(f"Warning: Could not verify Pinecone index: {e}")
            
            self.vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=self.embeddings
            )
            
            return True
            
        except Exception as e:
            error_msg = f"❌ Error setting up clients: {e}"
            if hasattr(st, 'error'):
                st.error(error_msg)
            else:
                print(error_msg)
            return False
    
    def generate_file_hash(self, content):
        """Generate hash for content to detect changes"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def process_single_file_from_drive(self, file_id, file_name):
        """Process a single file from Google Drive"""
        try:
            # Get file content from Drive
            content = self.drive_manager.get_file_content(file_id)
            if not content:
                return {'success': False, 'error': 'Could not read file content', 'chunks': 0}
            
            # Check if already processed
            if self.drive_manager.is_file_processed(file_name):
                return {'success': False, 'error': 'File already processed', 'chunks': 0}
            
            # Split content into chunks
            chunks = self.text_splitter.split_text(content)
            
            if not chunks:
                return {'success': False, 'error': 'No content to process', 'chunks': 0}
            
            # Create metadata for each chunk
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadata = {
                    'source': file_name,
                    'file_id': file_id,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'processed_date': datetime.now().isoformat(),
                    'content_hash': self.generate_file_hash(chunk)
                }
                metadatas.append(metadata)
            
            # Add to vector store
            self.vectorstore.add_texts(chunks, metadatas=metadatas)
            
            # Update processed files record in Drive
            self.drive_manager.add_processed_file(file_name, file_id, len(chunks))
            
            return {
                'success': True, 
                'chunks': len(chunks),
                'file_name': file_name
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'chunks': 0}
    
    def process_multiple_files_from_drive(self, file_list):
        """Process multiple files from Google Drive"""
        results = {
            'processed': [],
            'errors': [],
            'total_chunks': 0
        }
        
        for file_info in file_list:
            file_id = file_info['id']
            file_name = file_info['name']
            
            result = self.process_single_file_from_drive(file_id, file_name)
            
            if result['success']:
                results['processed'].append({
                    'name': file_name,
                    'chunks': result['chunks']
                })
                results['total_chunks'] += result['chunks']
            else:
                results['errors'].append({
                    'name': file_name,
                    'error': result['error']
                })
        
        return results
    
    def get_processing_stats(self):
        """Get processing statistics from Google Drive"""
        try:
            processed_data = self.drive_manager.get_processed_files_data()
            total_files = len(self.drive_manager.list_files('.md'))
            processed_files = len(processed_data.get('processed_files', {}))
            unprocessed_files = total_files - processed_files
            
            if 'total_chunks' in processed_data:
                total_chunks = processed_data['total_chunks']
            else:
                total_chunks = sum(
                    file_info.get('chunks_count', 0)
                    for file_info in processed_data.get('processed_files', {}).values()
                )
            
            return {
                'total_files': total_files,
                'processed_files': processed_files,
                'unprocessed_files': unprocessed_files,
                'total_chunks': total_chunks,
                'last_updated': processed_data.get('last_updated')
            }
            
        except Exception as e:
            st.error(f"Error getting processing stats: {e}")
            return {
                'total_files': 0,
                'processed_files': 0,
                'unprocessed_files': 0,
                'total_chunks': 0,
                'last_updated': None
            }
    
    def reprocess_file(self, file_name):
        """Reprocess a file (remove old data and process again)"""
        try:
            # Find the file in Drive
            all_files = self.drive_manager.list_files('.md')
            target_file = None
            
            for file in all_files:
                if file['name'] == file_name:
                    target_file = file
                    break
            
            if not target_file:
                return {'success': False, 'error': 'File not found in Drive'}
            
            # Remove from processed files record
            self.drive_manager.remove_processed_file(file_name)
            
            # Delete existing vectors from Pinecone (if possible)
            # Note: This requires implementing vector deletion by metadata
            try:
                # This is a simplified approach - in production you might want
                # more sophisticated vector management
                pass
            except Exception as e:
                print(f"Warning: Could not clean up old vectors: {e}")
            
            # Process the file again
            result = self.process_single_file_from_drive(target_file['id'], file_name)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def remove_file_from_processing(self, file_name):
        """Remove file from processed files list (for cleanup)"""
        try:
            return self.drive_manager.remove_processed_file(file_name)
        except Exception as e:
            st.error(f"Error removing file from processing: {e}")
            return False
    
    def get_file_processing_details(self, file_name):
        """Get detailed processing information for a specific file"""
        try:
            processed_data = self.drive_manager.get_processed_files_data()
            processed_files = processed_data.get('processed_files', {})
            
            if file_name in processed_files:
                return processed_files[file_name]
            else:
                return None
                
        except Exception as e:
            st.error(f"Error getting file processing details: {e}")
            return None
    
    def search_similar_content(self, query, k=5):
        """Search for similar content in the vector store"""
        try:
            if not hasattr(self, 'vectorstore') or not self.vectorstore:
                return []
            
            results = self.vectorstore.similarity_search(query, k=k)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'content': result.page_content,
                    'source': result.metadata.get('source', 'Unknown'),
                    'chunk_index': result.metadata.get('chunk_index', 0),
                    'processed_date': result.metadata.get('processed_date', 'Unknown')
                })
            
            return formatted_results
            
        except Exception as e:
            st.error(f"Error searching content: {e}")
            return []
    
    def validate_drive_connection(self):
        """Validate Google Drive connection and setup"""
        if not self.drive_manager.service:
            return False, "Google Drive service not initialized"
        
        try:
            # Test basic Drive access
            self.drive_manager.service.files().list(pageSize=1).execute()
            
            # Check if processed_files.json exists
            if not self.drive_manager.processed_files_id:
                return False, "processed_files.json not found or created"
            
            return True, "Google Drive connection validated"
            
        except Exception as e:
            return False, f"Drive validation failed: {e}"
    
    def get_pinecone_stats(self):
        """Get statistics about Pinecone index"""
        try:
            if not hasattr(self, 'vectorstore') or not self.vectorstore:
                return {'error': 'Pinecone not initialized'}
            
            # This is a simplified version - actual implementation depends on Pinecone client
            return {
                'status': 'connected',
                'index_name': self.get_env_variable('PINECONE_INDEX_NAME', 'chatbot')
            }
            
        except Exception as e:
            return {'error': str(e)}
