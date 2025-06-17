import json
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2.service_account import Credentials

def test_drive_setup():
    # Load your downloaded JSON file
    with open('streamlit-drive-credentials.json', 'r') as f:
        creds_dict = json.load(f)
    
    # Set up credentials
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/drive']
    )
    
    # Build Drive service
    service = build('drive', 'v3', credentials=credentials)
    
    # Test by listing files in your folder
    folder_id = '1Z9LciPkDfBQO6pc_L-viYxeAJXhN5CQV'  # Replace with your actual folder ID
    
    try:
        # Test 1: List files in folder
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        print(f"✅ Success! Found {len(files)} files in the Drive folder")
        
        if files:
            print("Files in folder:")
            for file in files:
                print(f"  - {file['name']} (ID: {file['id']})")
        
        # Test 2: Create a text file
        print("\n🔄 Testing file creation...")
        
        file_metadata = {
            'name': 'test_file.txt',
            'parents': [folder_id]
        }
        
        # Create proper media upload object
        media_content = 'Hello from Python! This is a test file.'
        media_body = MediaIoBaseUpload(
            io.BytesIO(media_content.encode('utf-8')),
            mimetype='text/plain',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id,name'
        ).execute()
        
        print(f"✅ Test file created successfully!")
        print(f"   File Name: {file.get('name')}")
        print(f"   File ID: {file.get('id')}")
        
        # Test 3: Verify file was created
        print("\n🔄 Verifying file creation...")
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        print(f"✅ Now found {len(files)} files in the Drive folder")
        
        # Test 4: Clean up test file
        print("\n🔄 Cleaning up test file...")
        service.files().delete(fileId=file.get('id')).execute()
        print("✅ Test file deleted successfully")
        
        # Test 5: Final verification
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            fields="files(id, name)"
        ).execute()
        
        files = results.get('files', [])
        print(f"✅ Final count: {len(files)} files in the Drive folder")
        
        print("\n🎉 All tests passed! Google Drive setup is working correctly.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Additional debugging info
        if "HttpError" in str(type(e)):
            print(f"HTTP Error details: {e}")
        
        # Check if folder ID is valid
        try:
            folder_info = service.files().get(fileId=folder_id).execute()
            print(f"✅ Folder exists: {folder_info.get('name')}")
        except Exception as folder_error:
            print(f"❌ Folder ID might be invalid: {folder_error}")

def test_permissions():
    """Additional test to check service account permissions"""
    print("\n🔍 Testing service account permissions...")
    
    try:
        with open('streamlit-drive-credentials.json', 'r') as f:
            creds_dict = json.load(f)
        
        credentials = Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        
        # Get info about the service account
        about = service.about().get(fields="user").execute()
        print(f"✅ Service account email: {about.get('user', {}).get('emailAddress', 'Unknown')}")
        
        # Test basic Drive access
        results = service.files().list(pageSize=1).execute()
        print("✅ Basic Drive API access confirmed")
        
    except Exception as e:
        print(f"❌ Permission test failed: {e}")

if __name__ == "__main__":
    test_drive_setup()
    test_permissions()