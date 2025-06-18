import os
import json
import streamlit as st
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from datetime import datetime
import io

class GoogleDriveManager:
    def __init__(self):
        load_dotenv()
        self.service = None
        self.folder_id = None
        self.processed_files_id = None
        self.setup_drive_connection()
    
    def get_env_variable(self, key, default=None):
        """Get environment variable with Streamlit secrets fallback"""
        # Try Streamlit secrets first
        if hasattr(st, 'secrets'):
            try:
                # Handle nested secrets for google_drive_credentials
                if key == 'GOOGLE_DRIVE_CREDENTIALS':
                    if 'google_drive_credentials' in st.secrets:
                        return dict(st.secrets['google_drive_credentials'])
                elif key in st.secrets:
                    return st.secrets[key]
            except Exception as e:
                print(f"Error accessing Streamlit secrets: {e}")
        
        # Fallback to environment variables
        return os.getenv(key, default)
    
    def setup_drive_connection(self):
        """Setup Google Drive API connection"""
        try:
            # Get credentials
            credentials_data = self.get_credentials()
            if not credentials_data:
                print("Google Drive credentials not found")
                return False
            
            # Create credentials object
            credentials = service_account.Credentials.from_service_account_info(
                credentials_data,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            # Build service
            self.service = build('drive', 'v3', credentials=credentials)
            
            # Set folder ID
            self.folder_id = self.get_env_variable('GOOGLE_DRIVE_FOLDER_ID')
            if not self.folder_id:
                print("Google Drive folder ID not found")
                return False
            
            # Initialize processed files tracking
            self.setup_processed_files_tracking()
            
            return True
            
        except Exception as e:
            print(f"Error setting up Google Drive connection: {e}")
            return False
    
    def get_credentials(self):
        """Get Google Drive credentials from various sources"""
        try:
            # Method 1: Try Streamlit secrets (nested format)
            if hasattr(st, 'secrets') and 'google_drive_credentials' in st.secrets:
                print("Using Google Drive credentials from Streamlit secrets")
                return dict(st.secrets['google_drive_credentials'])
            
            # Method 2: Try environment variable (JSON string)
            creds_json = self.get_env_variable('GOOGLE_DRIVE_CREDENTIALS')
            if creds_json:
                if isinstance(creds_json, str):
                    print("Using Google Drive credentials from environment variable")
                    return json.loads(creds_json)
                elif isinstance(creds_json, dict):
                    return creds_json
            
            # Method 3: Try individual Streamlit secrets
            if hasattr(st, 'secrets'):
                required_keys = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id']
                if all(key in st.secrets for key in required_keys):
                    print("Using individual Google Drive credentials from Streamlit secrets")
                    return {key: st.secrets[key] for key in required_keys}
            
            # Method 4: Try service account file
            service_account_file = self.get_env_variable('GOOGLE_SERVICE_ACCOUNT_FILE', 'service_account.json')
            if os.path.exists(service_account_file):
                print(f"Using service account file: {service_account_file}")
                with open(service_account_file, 'r') as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"Error getting credentials: {e}")
            return None
    
    def setup_processed_files_tracking(self):
        """Setup processed files tracking in Google Drive"""
        try:
            if not self.service:
                return False
            
            # Look for existing processed_files.json
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and name='processed_files.json'",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            
            if files:
                self.processed_files_id = files[0]['id']
                print(f"Found existing processed_files.json: {self.processed_files_id}")
            else:
                # Create new processed_files.json
                self.processed_files_id = self.create_processed_files_json()
                print(f"Created new processed_files.json: {self.processed_files_id}")
            
            return True
            
        except Exception as e:
            print(f"Error setting up processed files tracking: {e}")
            return False
    
    def create_processed_files_json(self):
        """Create initial processed_files.json in Google Drive"""
        try:
            initial_data = {
                "processed_files": {},
                "total_chunks": 0,
                "last_updated": datetime.now().isoformat(),
                "created": datetime.now().isoformat(),
                "version": "2.0"
            }
            
            file_content = json.dumps(initial_data, indent=2)
            
            # Upload to Google Drive
            media = MediaIoBaseUpload(
                io.BytesIO(file_content.encode()),
                mimetype='application/json'
            )
            
            file_metadata = {
                'name': 'processed_files.json',
                'parents': [self.folder_id]
            }
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            print(f"Error creating processed_files.json: {e}")
            return None
    
    def get_file_content(self, file_id):
        """Get content of a file from Google Drive"""
        try:
            if not self.service:
                return None
            
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return file_content.getvalue().decode('utf-8')
            
        except Exception as e:
            print(f"Error getting file content: {e}")
            return None
    
    def get_processed_files_data(self):
        """Get processed files data from Google Drive"""
        try:
            if not self.processed_files_id:
                return {"processed_files": {}, "total_chunks": 0}
            
            content = self.get_file_content(self.processed_files_id)
            if content:
                return json.loads(content)
            else:
                return {"processed_files": {}, "total_chunks": 0}
                
        except Exception as e:
            print(f"Error getting processed files data: {e}")
            return {"processed_files": {}, "total_chunks": 0}
    
    def is_file_processed(self, filename):
        """Check if file is already processed"""
        processed_data = self.get_processed_files_data()
        return filename in processed_data.get('processed_files', {})
    
    def add_processed_file(self, filename, file_id, chunks_count, vector_ids=None):
        """Add file to processed files record"""
        try:
            processed_data = self.get_processed_files_data()

            file_record = {
                'file_id': file_id,
                'chunks_count': chunks_count,
                'processed_date': datetime.now().isoformat()
            }
            if vector_ids is not None:
                file_record['vector_ids'] = vector_ids

            processed_data['processed_files'][filename] = file_record
            
            # Update total chunks
            processed_data['total_chunks'] = sum(
                file_info.get('chunks_count', 0) 
                for file_info in processed_data['processed_files'].values()
            )
            
            processed_data['last_updated'] = datetime.now().isoformat()
            
            return self.update_processed_files_json(processed_data)
            
        except Exception as e:
            print(f"Error adding processed file: {e}")
            return False
    
    def update_processed_files_json(self, data):
        """Update processed_files.json in Google Drive"""
        try:
            if not self.processed_files_id:
                return False
            
            file_content = json.dumps(data, indent=2)
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_content.encode()),
                mimetype='application/json'
            )
            
            self.service.files().update(
                fileId=self.processed_files_id,
                media_body=media
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating processed files JSON: {e}")
            return False
    
    def list_files(self, extension='.md'):
        """List files in Google Drive folder"""
        try:
            if not self.service:
                return []
            
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and name contains '{extension}'",
                fields="files(id, name, modifiedTime, size, webViewLink)"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def list_unprocessed_files(self):
        """Get list of unprocessed files"""
        all_files = self.list_files('.md')
        processed_data = self.get_processed_files_data()
        processed_files = processed_data.get('processed_files', {})
        
        return [f for f in all_files if f['name'] not in processed_files]
    
    def list_processed_files(self):
        """Get list of processed files with their info"""
        all_files = self.list_files('.md')
        processed_data = self.get_processed_files_data()
        processed_files = processed_data.get('processed_files', {})
        
        processed_list = []
        for file in all_files:
            if file['name'] in processed_files:
                file['processed_info'] = processed_files[file['name']]
                processed_list.append(file)
        
        return processed_list
    
    def get_folder_info(self):
        """Get information about the Google Drive folder"""
        try:
            if not self.service or not self.folder_id:
                return None
            
            folder = self.service.files().get(
                fileId=self.folder_id,
                fields="name, id, modifiedTime"
            ).execute()
            
            return folder
            
        except Exception as e:
            print(f"Error getting folder info: {e}")
            return None

    def file_exists(self, filename):
        """Check if a file with the given name exists in Drive"""
        try:
            if not self.service:
                return False

            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and name='{filename}' and trashed=false",
                fields="files(id)"
            ).execute()
            return len(results.get('files', [])) > 0

        except Exception as e:
            print(f"Error checking file existence: {e}")
            return False
    
    def upload_content_as_file(self, content, filename):
        """Upload content as a file to Google Drive"""
        try:
            if not self.service:
                return None

            # Prevent uploading if a file with the same name already exists
            if self.file_exists(filename):
                print(f"File '{filename}' already exists in Drive")
                return None
            
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode()),
                mimetype='text/markdown'
            )
            
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            return None
    
    def delete_file(self, file_id):
        """Delete a file from Google Drive"""
        try:
            if not self.service:
                return False
            
            self.service.files().delete(fileId=file_id).execute()
            return True
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def remove_processed_file(self, filename):
        """Remove file from processed files record"""
        try:
            processed_data = self.get_processed_files_data()
            
            if filename in processed_data.get('processed_files', {}):
                del processed_data['processed_files'][filename]
                
                # Recalculate total chunks
                processed_data['total_chunks'] = sum(
                    file_info.get('chunks_count', 0) 
                    for file_info in processed_data['processed_files'].values()
                )
                
                processed_data['last_updated'] = datetime.now().isoformat()
                
                return self.update_processed_files_json(processed_data)
            
            return True
            
        except Exception as e:
            print(f"Error removing processed file: {e}")
            return False
