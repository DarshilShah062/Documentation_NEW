import os
import json
from google_drive_manager import GoogleDriveManager

def cleanup_duplicate_processed_files():
    """Clean up duplicate processed_files.json files and ensure single source of truth"""
    
    drive_manager = GoogleDriveManager()
    
    if not drive_manager.service:
        print("❌ Google Drive not connected")
        return
    
    try:
        # Search for ALL processed_files.json files
        query = f"'{drive_manager.folder_id}' in parents and name='processed_files.json' and trashed=false"
        results = drive_manager.service.files().list(
            q=query, 
            fields="files(id, name, modifiedTime, size)"
        ).execute()
        files = results.get('files', [])
        
        print(f"Found {len(files)} processed_files.json files")
        
        if len(files) > 1:
            # Sort by modification time, keep the most recent
            files.sort(key=lambda x: x.get('modifiedTime', ''), reverse=True)
            
            print(f"Keeping most recent file: {files[0]['id']} (Modified: {files[0].get('modifiedTime')})")
            
            # Delete duplicates
            for duplicate_file in files[1:]:
                print(f"Deleting duplicate: {duplicate_file['id']} (Modified: {duplicate_file.get('modifiedTime')})")
                drive_manager.service.files().delete(fileId=duplicate_file['id']).execute()
            
            print("✅ Cleanup complete!")
        
        elif len(files) == 1:
            print("✅ Only one processed_files.json found - no cleanup needed")
        
        else:
            print("❌ No processed_files.json found")
        
        # Verify the final state
        final_data = drive_manager.get_processed_files_data()
        print(f"\nFinal state:")
        print(f"- Total processed files: {final_data.get('total_processed', 0)}")
        print(f"- Total chunks: {final_data.get('total_chunks', 0)}")
        print(f"- Last updated: {final_data.get('last_updated', 'Unknown')}")
        
        if final_data.get('migration_info', {}).get('migrated_from_local'):
            print("- Migration info: Data migrated from local storage ✅")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    cleanup_duplicate_processed_files()