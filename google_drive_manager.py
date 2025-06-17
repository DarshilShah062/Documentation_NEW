import os
import io
import json
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.service_account import Credentials
from datetime import datetime
from dotenv import load_dotenv

class GoogleDriveManager:
    def __init__(self):
        load_dotenv()
        self.service = None
        self.folder_id = None
        self.processed_files_id = None
        self.setup_drive_service()
    
    def get_credentials(self):
        """Get Google Drive credentials from Streamlit secrets or environment"""
        try:
            # Try Streamlit secrets first (for deployment)
            if hasattr(st, 'secrets') and 'google_drive_credentials' in st.secrets:
                creds_dict = dict(st.secrets['google_drive_credentials'])
                folder_id = st.secrets.get('GOOGLE_DRIVE_FOLDER_ID')
                return creds_dict, folder_id
            
            # Fallback to environment variables (for local development)
            creds_json = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
            folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
            
            if creds_json and folder_id:
                creds_dict = json.loads(creds_json)
                return creds_dict, folder_id
            
            return None, None
            
        except Exception as e:
            print(f"Error getting credentials: {e}")
            return None, None
    
    def setup_drive_service(self):
        """Initialize Google Drive service and find/create processed_files.json"""
        try:
            creds_dict, folder_id = self.get_credentials()
            
            if not creds_dict or not folder_id:
                print("Google Drive credentials not found")
                return False
            
            credentials = Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            
            self.service = build('drive', 'v3', credentials=credentials)
            self.folder_id = folder_id
            
            # Test the connection and find/create processed_files.json
            self.service.files().list(pageSize=1).execute()
            self._cleanup_and_setup_processed_files()
            
            print("✅ Google Drive service initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error setting up Google Drive: {e}")
            self.service = None
            return False
    
    def _cleanup_and_setup_processed_files(self):
        """Clean up duplicate processed_files.json and create/update the single one"""
        try:
            # Search for ALL processed_files.json files in the folder
            query = f"'{self.folder_id}' in parents and name='processed_files.json' and trashed=false"
            results = self.service.files().list(
                q=query, 
                fields="files(id, name, modifiedTime)"
            ).execute()
            files = results.get('files', [])
            
            if len(files) > 1:
                # Sort by modification time, keep the most recent
                files.sort(key=lambda x: x.get('modifiedTime', ''), reverse=True)
                self.processed_files_id = files[0]['id']
                
                print(f"Found {len(files)} processed_files.json files. Keeping the most recent.")
                
                # Delete duplicate files
                for duplicate_file in files[1:]:
                    try:
                        self.service.files().delete(fileId=duplicate_file['id']).execute()
                        print(f"✅ Deleted duplicate processed_files.json: {duplicate_file['id']}")
                    except Exception as e:
                        print(f"❌ Error deleting duplicate: {e}")
                
            elif len(files) == 1:
                self.processed_files_id = files[0]['id']
                print(f"✅ Found existing processed_files.json: {self.processed_files_id}")
            else:
                # Create new processed_files.json with existing data
                self.processed_files_id = self._create_processed_files_with_existing_data()
                print(f"✅ Created new processed_files.json: {self.processed_files_id}")
                
        except Exception as e:
            print(f"❌ Error cleaning up processed_files.json: {e}")
            self.processed_files_id = None
    
    def _create_processed_files_with_existing_data(self):
        """Create processed_files.json with existing processed files data"""
        try:
            # Your existing processed files from the vector database
            existing_processed_files = {
                "Prediction.md": {
                    "file_id": "unknown",  # Will be updated when we find the actual file
                    "processed_date": "2024-01-01T00:00:00",  # Placeholder date
                    "chunks_count": 0,  # Will be updated
                    "status": "processed",
                    "content_hash": "c99b265f148aabe9dd1a8b1854091334",
                    "migrated_from_local": True
                },
                "Registration and login.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "9b4afa3623b7de23771c18126720ebc6",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for Boosters Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "655e6384087a951a5579eeb19f9df8d8",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for Extra Scoring Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "c88d05ccd21dd02e18517db10887728e",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for Leaderboards Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "723f1a0681a778ff77efb2c77aac7cac",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for League Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "3a6d56a17575f42fa574a1f311162415",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for LM Tools Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "b58419cc99178aa984175b078fd509b8",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for Scoring Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "bba452031b7a8694962ba21a93fa9ab4",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for Team Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "1e6f7396a2a1f32e7d80ac7e5eb9ee3d",
                    "migrated_from_local": True
                },
                "Salary Cap Rules for Trades Set Up.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "050ffdae9959f220006f7f97c2ca3f4a",
                    "migrated_from_local": True
                },
                "SalaryCap.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "ea40bf898f23b2f17b00b0fede39362d",
                    "migrated_from_local": True
                },
                "Full Public Tournament Guide - Salary Cap.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "3f87283c0fb1eeae03145ba1895dda08",
                    "migrated_from_local": True
                },
                "Booster in Salary cap season long formate.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "202cf0a0c3422c091f03a6d445eb46ad",
                    "migrated_from_local": True
                },
                "How Budget works.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "fb6c3215f9c917ae76d4195fcacf9fdd",
                    "migrated_from_local": True
                },
                "How Trades work.md": {
                    "file_id": "unknown",
                    "processed_date": "2024-01-01T00:00:00",
                    "chunks_count": 0,
                    "status": "processed",
                    "content_hash": "e032309fcdb5e9af15bbfe05d2ab5a43",
                    "migrated_from_local": True
                }
            }
            
            # Update file IDs for files that exist in Drive
            self._update_existing_file_ids(existing_processed_files)
            
            initial_data = {
                "processed_files": existing_processed_files,
                "last_updated": datetime.now().isoformat(),
                "total_processed": len(existing_processed_files),
                "total_chunks": 134,  # Your existing chunks count
                "migration_info": {
                    "migrated_from_local": True,
                    "migration_date": datetime.now().isoformat(),
                    "original_chunks_count": 134
                }
            }
            
            file_metadata = {
                'name': 'processed_files.json',
                'parents': [self.folder_id]
            }
            
            media = MediaIoBaseUpload(
                io.BytesIO(json.dumps(initial_data, indent=2).encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
            
        except Exception as e:
            print(f"❌ Error creating processed_files.json with existing data: {e}")
            return None
    
    def _update_existing_file_ids(self, processed_files_dict):
        """Update file IDs for files that already exist in Google Drive"""
        try:
            # Get all files in the Drive folder
            all_files = self.list_files(exclude_processed_json=False)
            
            for file in all_files:
                file_name = file['name']
                if file_name in processed_files_dict:
                    processed_files_dict[file_name]['file_id'] = file['id']
                    print(f"✅ Updated file ID for {file_name}: {file['id']}")
            
        except Exception as e:
            print(f"❌ Error updating existing file IDs: {e}")
    
    def get_processed_files_data(self):
        """Get processed files data from Google Drive"""
        if not self.service or not self.processed_files_id:
            return {
                "processed_files": {}, 
                "last_updated": None, 
                "total_processed": 0,
                "total_chunks": 0
            }
        
        try:
            content = self.get_file_content(self.processed_files_id)
            if content:
                data = json.loads(content)
                # Ensure all required fields exist
                if 'total_chunks' not in data:
                    data['total_chunks'] = len(data.get('processed_files', {})) * 5  # Estimate
                return data
            else:
                return {
                    "processed_files": {}, 
                    "last_updated": None, 
                    "total_processed": 0,
                    "total_chunks": 0
                }
                
        except Exception as e:
            print(f"❌ Error getting processed files data: {e}")
            return {
                "processed_files": {}, 
                "last_updated": None, 
                "total_processed": 0,
                "total_chunks": 0
            }
    
    def update_processed_files_data(self, data):
        """Update processed files data in Google Drive"""
        if not self.service or not self.processed_files_id:
            return False
        
        try:
            data["last_updated"] = datetime.now().isoformat()
            data["total_processed"] = len(data.get("processed_files", {}))
            
            # Calculate total chunks
            total_chunks = 0
            for file_info in data.get("processed_files", {}).values():
                total_chunks += file_info.get("chunks_count", 0)
            
            # If we have migrated data with existing chunks, preserve that count
            if "migration_info" in data and data["migration_info"].get("migrated_from_local"):
                data["total_chunks"] = max(total_chunks, data.get("total_chunks", 134))
            else:
                data["total_chunks"] = total_chunks
            
            content = json.dumps(data, indent=2)
            
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype='application/json',
                resumable=True
            )
            
            self.service.files().update(
                fileId=self.processed_files_id,
                media_body=media
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating processed files data: {e}")
            return False
    
    def add_processed_file(self, filename, file_id, chunks_count=0):
        """Add a file to processed files list"""
        data = self.get_processed_files_data()
        data["processed_files"][filename] = {
            "file_id": file_id,
            "processed_date": datetime.now().isoformat(),
            "chunks_count": chunks_count,
            "status": "processed"
        }
        return self.update_processed_files_data(data)
    
    def remove_processed_file(self, filename):
        """Remove a file from processed files list"""
        data = self.get_processed_files_data()
        if filename in data["processed_files"]:
            del data["processed_files"][filename]
            return self.update_processed_files_data(data)
        return True
    
    def is_file_processed(self, filename):
        """Check if a file has been processed"""
        data = self.get_processed_files_data()
        return filename in data.get("processed_files", {})
    
    def upload_file(self, file_path, file_name=None):
        """Upload file to Google Drive"""
        if not self.service:
            return None
            
        try:
            if not file_name:
                file_name = os.path.basename(file_path)
            
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Determine MIME type based on file extension
            mime_type = 'text/plain'
            if file_name.endswith('.md'):
                mime_type = 'text/markdown'
            elif file_name.endswith('.txt'):
                mime_type = 'text/plain'
            elif file_name.endswith('.json'):
                mime_type = 'application/json'
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            print(f"✅ File uploaded: {file_name} (ID: {file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            print(f"❌ Error uploading file {file_name}: {e}")
            return None
    
    def upload_content_as_file(self, content, file_name):
        """Upload content directly as file to Google Drive"""
        if not self.service:
            return None
            
        try:
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Determine MIME type
            mime_type = 'text/markdown' if file_name.endswith('.md') else 'text/plain'
            
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype=mime_type,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            print(f"✅ Content uploaded as file: {file_name} (ID: {file.get('id')})")
            return file.get('id')
            
        except Exception as e:
            print(f"❌ Error uploading content as file {file_name}: {e}")
            return None
    
    def download_file(self, file_id, local_path):
        """Download file from Google Drive"""
        if not self.service:
            return False
            
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(local_path, 'wb') as f:
                f.write(fh.getvalue())
            
            return True
            
        except Exception as e:
            print(f"❌ Error downloading file: {e}")
            return False
    
    def list_files(self, file_extension=None, exclude_processed_json=True):
        """List all files in the Drive folder"""
        if not self.service:
            return []
            
        try:
            query = f"'{self.folder_id}' in parents and trashed=false" if self.folder_id else "trashed=false"
            
            if exclude_processed_json:
                query += " and name!='processed_files.json'"
            
            if file_extension:
                query += f" and name contains '{file_extension}'"
            
            results = self.service.files().list(
                q=query,
                fields="files(id, name, modifiedTime, size, mimeType, webViewLink)",
                orderBy="modifiedTime desc"
            ).execute()
            
            return results.get('files', [])
            
        except Exception as e:
            print(f"❌ Error listing files: {e}")
            return []
    
    def list_unprocessed_files(self):
        """List files that haven't been processed yet"""
        all_files = self.list_files('.md')
        processed_data = self.get_processed_files_data()
        processed_files = processed_data.get("processed_files", {})
        
        unprocessed = []
        for file in all_files:
            if file['name'] not in processed_files:
                unprocessed.append(file)
        
        return unprocessed
    
    def list_processed_files(self):
        """List files that have been processed"""
        all_files = self.list_files('.md')
        processed_data = self.get_processed_files_data()
        processed_files = processed_data.get("processed_files", {})
        
        processed = []
        for file in all_files:
            if file['name'] in processed_files:
                file['processed_info'] = processed_files[file['name']]
                processed.append(file)
        
        return processed
    
    def delete_file(self, file_id):
        """Delete file from Google Drive"""
        if not self.service:
            return False
            
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"✅ File deleted: {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting file: {e}")
            return False
    
    def get_file_content(self, file_id):
        """Get file content as string"""
        if not self.service:
            return None
            
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            return fh.getvalue().decode('utf-8')
            
        except Exception as e:
            print(f"❌ Error getting file content: {e}")
            return None
    
    def update_file_content(self, file_id, content):
        """Update file content in Google Drive"""
        if not self.service:
            return False
            
        try:
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype='text/markdown',
                resumable=True
            )
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            print(f"✅ File updated: {file_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating file: {e}")
            return False
    
    def get_folder_info(self):
        """Get information about the configured Drive folder"""
        if not self.service or not self.folder_id:
            return None
            
        try:
            folder_info = self.service.files().get(
                fileId=self.folder_id,
                fields="id, name, webViewLink, createdTime, modifiedTime"
            ).execute()
            
            return folder_info
            
        except Exception as e:
            print(f"❌ Error getting folder info: {e}")
            return None