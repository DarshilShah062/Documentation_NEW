import streamlit as st
import pandas as pd
from datetime import datetime
from document_processor import DocumentProcessor
from google_drive_manager import GoogleDriveManager

# Page config
st.set_page_config(
    page_title="AI Chatbot Document Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-bottom: 2rem;
        border-radius: 10px;
    }
    .section-header {
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin-bottom: 1rem;
        font-weight: bold;
        font-size: 1.2rem;
        color: #000;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #28a745;
        color: #000;
    }
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-processed {
        background-color: #d4edda;
        color: #155724;
    }
    .status-unprocessed {
        background-color: #fff3cd;
        color: #856404;
    }
    .file-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 3px solid #007bff;
        color: #000;
    }
    .stCheckbox > label {
        font-size: 0px !important;
    }
    .stCheckbox > label > div {
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'processor' not in st.session_state:
        st.session_state.processor = DocumentProcessor()
    
    if 'drive_manager' not in st.session_state:
        st.session_state.drive_manager = GoogleDriveManager()
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()

def main():
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Chatbot Document Manager</h1>
        <p>Google Drive Integration • Cloud-First • User-Controlled Processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔧 System Status")
        
        # Google Drive Status
        if st.session_state.drive_manager.service:
            st.success("✅ Google Drive Connected")
            folder_info = st.session_state.drive_manager.get_folder_info()
            if folder_info:
                st.info(f"📁 {folder_info.get('name', 'Unknown')}")
        else:
            st.error("❌ Google Drive Disconnected")
            st.info("Check your credentials configuration")
        
        # Pinecone Status
        pinecone_stats = st.session_state.processor.get_pinecone_stats()
        if 'error' not in pinecone_stats:
            st.success("✅ Pinecone Connected")
            st.info(f"📊 Index: {pinecone_stats.get('index_name', 'Unknown')}")
        else:
            st.error("❌ Pinecone Error")
            st.error(pinecone_stats['error'])
        
        st.markdown("---")
        
        # Quick Stats - FIXED to show correct vector chunks
        stats = st.session_state.processor.get_processing_stats()
        st.markdown("### 📊 Quick Stats")
        st.metric("📄 Total Files", stats['total_files'])
        st.metric("✅ Processed", stats['processed_files'])
        st.metric("⏳ Pending", stats['unprocessed_files'])
        # FIXED: Show actual total chunks including migrated data
        st.metric("🧩 Vector Chunks", stats['total_chunks'])
        
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "📝 Add Document", 
        "🔍 Process Documents", 
        "📋 File Manager", 
        "🔍 Search"
    ])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_add_document()
    
    with tab3:
        show_process_documents()
    
    with tab4:
        show_file_manager()
    
    with tab5:
        show_search_interface()

def show_dashboard():
    """Enhanced dashboard with processing overview - FIXED vector chunks display"""
    st.markdown('<div class="section-header">📊 Processing Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.drive_manager.service:
        st.error("❌ Google Drive not connected. Please check your configuration.")
        return
    
    # Get comprehensive stats
    stats = st.session_state.processor.get_processing_stats()
    
    # Metrics row - FIXED to show correct total chunks
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📄 Total Files", 
            stats['total_files'],
            help="Total markdown files in Google Drive"
        )
    
    with col2:
        st.metric(
            "✅ Processed Files", 
            stats['processed_files'],
            delta=f"{stats['processed_files'] - stats['unprocessed_files']}" if stats['unprocessed_files'] > 0 else None
        )
    
    with col3:
        st.metric(
            "⏳ Pending Processing", 
            stats['unprocessed_files'],
            delta=f"-{stats['unprocessed_files']}" if stats['unprocessed_files'] > 0 else "0"
        )
    
    with col4:
        # FIXED: Show actual vector chunks including migrated data
        st.metric(
            "🧩 Vector Chunks", 
            stats['total_chunks'],
            help="Total chunks stored in Pinecone (including migrated data)"
        )
    
    # Processing progress
    if stats['total_files'] > 0:
        progress = stats['processed_files'] / stats['total_files']
        st.progress(progress, text=f"Processing Progress: {progress:.1%}")
    
    # Show migration info if available
    processed_data = st.session_state.drive_manager.get_processed_files_data()
    if processed_data.get("migration_info", {}).get("migrated_from_local"):
        st.info("📂 Data migrated from local storage. Vector chunks include previously processed content.")
    
    st.markdown("---")
    
    # Recent activity
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Unprocessed Files")
        unprocessed = st.session_state.drive_manager.list_unprocessed_files()
        
        if unprocessed:
            for file in unprocessed[:5]:  # Show first 5
                st.markdown(f"""
                <div class="file-card">
                    <strong>{file['name']}</strong><br>
                    <small>Modified: {file.get('modifiedTime', 'Unknown')[:19].replace('T', ' ')}</small>
                    <span class="status-badge status-unprocessed">Pending</span>
                </div>
                """, unsafe_allow_html=True)
            
            if len(unprocessed) > 5:
                st.info(f"+ {len(unprocessed) - 5} more files pending processing")
        else:
            st.success("🎉 All files are processed!")
    
    with col2:
        st.markdown("### ✅ Recently Processed")
        processed = st.session_state.drive_manager.list_processed_files()
        
        if processed:
            # Sort by processed date
            processed.sort(key=lambda x: x.get('processed_info', {}).get('processed_date', ''), reverse=True)
            
            for file in processed[:5]:  # Show first 5
                processed_info = file.get('processed_info', {})
                chunks = processed_info.get('chunks_count', 0)
                
                # Show if migrated from local
                migrated_badge = " (Migrated)" if processed_info.get('migrated_from_local') else ""
                
                st.markdown(f"""
                <div class="file-card">
                    <strong>{file['name']}{migrated_badge}</strong><br>
                    <small>Processed: {processed_info.get('processed_date', 'Unknown')[:19].replace('T', ' ')}</small><br>
                    <small>Chunks: {chunks if chunks > 0 else 'Legacy'}</small>
                    <span class="status-badge status-processed">Processed</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No files processed yet")
    
    # Last update info
    if stats['last_updated']:
        st.markdown(f"*Last updated: {stats['last_updated'][:19].replace('T', ' ')}*")

def show_process_documents():
    """Document processing interface with user control - FIXED checkbox labels"""
    st.markdown('<div class="section-header">🔍 Process Documents to Pinecone Database</div>', unsafe_allow_html=True)
    
    if not st.session_state.drive_manager.service:
        st.error("❌ Google Drive not connected.")
        return
    
    # Get unprocessed files
    unprocessed_files = st.session_state.drive_manager.list_unprocessed_files()
    processed_files = st.session_state.drive_manager.list_processed_files()
    
    # Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⏳ Pending Processing", len(unprocessed_files))
    
    with col2:
        st.metric("✅ Already Processed", len(processed_files))
    
    with col3:
        st.metric("📁 Total Files", len(unprocessed_files) + len(processed_files))
    
    if not unprocessed_files:
        st.success("🎉 All files are already processed!")
        
        # Show option to reprocess files
        st.markdown("### 🔄 Reprocess Files")
        st.info("You can reprocess files if you've made changes to them.")
        
        if processed_files:
            selected_reprocess = st.selectbox(
                "Select file to reprocess:",
                options=[f['name'] for f in processed_files],
                key="reprocess_selector"
            )
            
            if st.button("🔄 Reprocess Selected File", type="secondary"):
                if not st.session_state.get("confirm_reprocess", False):
                    st.session_state.confirm_reprocess = True
                    st.warning("⚠️ Click the button again to confirm reprocessing")
                else:
                    with st.spinner("Reprocessing file..."):
                        result = st.session_state.processor.reprocess_file(selected_reprocess)

                    if result['success']:
                        st.success(f"✅ File reprocessed: {selected_reprocess} ({result['chunks']} chunks)")
                        st.rerun()
                    else:
                        st.error(f"❌ Reprocessing failed: {result['error']}")
                    st.session_state.confirm_reprocess = False
        
        return
    
    st.markdown("### 📄 Files Ready for Processing")
    
    # Display unprocessed files with selection
    if unprocessed_files:
        # Create selection interface
        st.markdown("Select files to process:")
        
        selected_files = []
        
        # Batch selection options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Select All"):
                st.session_state.selected_all = True
        
        with col2:
            if st.button("❌ Deselect All"):
                st.session_state.selected_all = False
        
        with col3:
            process_mode = st.selectbox(
                "Processing Mode:",
                options=["Individual", "Batch"],
                help="Individual: Process files one by one. Batch: Process all selected files at once."
            )
        
        # File selection checkboxes - FIXED labels
        for i, file in enumerate(unprocessed_files):
            default_selected = getattr(st.session_state, 'selected_all', False)
            
            col1, col2, col3 = st.columns([1, 3, 2])
            
            with col1:
                # FIXED: Added proper label for accessibility
                selected = st.checkbox(
                    f"Select {file['name']}", 
                    value=default_selected,
                    key=f"file_select_{i}",
                    label_visibility="hidden"  # Hide the label visually but keep it for accessibility
                )
                if selected:
                    selected_files.append(file)
            
            with col2:
                st.markdown(f"**{file['name']}**")
                st.caption(f"Modified: {file.get('modifiedTime', 'Unknown')[:19].replace('T', ' ')}")
                if file.get('size'):
                    st.caption(f"Size: {int(file['size']) / 1024:.1f} KB")
            
            with col3:
                if st.button(f"👁️ Preview {file['name']}", key=f"preview_{i}"):
                    with st.expander(f"Preview: {file['name']}", expanded=True):
                        content = st.session_state.drive_manager.get_file_content(file['id'])
                        if content:
                            st.text_area(
                                f"Content of {file['name']}:", 
                                content[:500] + "..." if len(content) > 500 else content, 
                                height=200, 
                                key=f"preview_content_{i}",
                                label_visibility="visible"
                            )
                        else:
                            st.error("Could not load file content")
        
        # Processing actions
        if selected_files:
            st.markdown(f"### 🚀 Process {len(selected_files)} Selected File(s)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if process_mode == "Individual":
                    if st.button("🔄 Process Files Individually", type="primary"):
                        process_files_individually(selected_files)
                else:
                    if st.button("🚀 Process All Selected Files", type="primary"):
                        process_files_batch(selected_files)
            
            with col2:
                st.markdown("**Selected Files:**")
                for file in selected_files:
                    st.write(f"• {file['name']}")
        
        else:
            st.info("👆 Please select files to process")

def show_file_manager():
    """Enhanced file manager for Google Drive files - FIXED labels"""
    st.markdown('<div class="section-header">📋 Google Drive File Manager</div>', unsafe_allow_html=True)
    
    if not st.session_state.drive_manager.service:
        st.error("❌ Google Drive not connected.")
        return
    
    # Get all files
    all_files = st.session_state.drive_manager.list_files('.md')
    processed_data = st.session_state.drive_manager.get_processed_files_data()
    processed_files_dict = processed_data.get('processed_files', {})
    
    if not all_files:
        st.info("📁 No markdown files found in Google Drive")
        st.markdown("Use the 'Add Document' tab to upload your first document.")
        return
    
    # File type filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        file_filter = st.selectbox(
            "Filter files by status:",
            options=["All Files", "Processed Only", "Unprocessed Only"],
            key="file_filter"
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort files by:",
            options=["Name", "Modified Date", "Processing Status"],
            key="sort_by"
        )
    
    with col3:
        if st.button("🔄 Refresh File List"):
            st.rerun()
    
    # Filter and sort files
    filtered_files = []
    
    for file in all_files:
        is_processed = file['name'] in processed_files_dict
        
        if file_filter == "Processed Only" and not is_processed:
            continue
        elif file_filter == "Unprocessed Only" and is_processed:
            continue
        
        # Add processing info
        file['is_processed'] = is_processed
        if is_processed:
            file['processing_info'] = processed_files_dict[file['name']]
        
        filtered_files.append(file)
    
    # Sort files
    if sort_by == "Name":
        filtered_files.sort(key=lambda x: x['name'])
    elif sort_by == "Modified Date":
        filtered_files.sort(key=lambda x: x.get('modifiedTime', ''), reverse=True)
    elif sort_by == "Processing Status":
        filtered_files.sort(key=lambda x: (x['is_processed'], x['name']))
    
    st.markdown(f"### 📄 Files ({len(filtered_files)} found)")
    
    # Display files
    for i, file in enumerate(filtered_files):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.markdown(f"**{file['name']}**")
                st.caption(f"Modified: {file.get('modifiedTime', 'Unknown')[:19].replace('T', ' ')}")
                if file.get('size'):
                    st.caption(f"Size: {int(file['size']) / 1024:.1f} KB")
            
            with col2:
                if file['is_processed']:
                    processing_info = file['processing_info']
                    migrated = processing_info.get('migrated_from_local', False)
                    
                    if migrated:
                        st.markdown('<span class="status-badge status-processed">✅ Migrated</span>', unsafe_allow_html=True)
                        st.caption("Legacy chunks")
                    else:
                        st.markdown('<span class="status-badge status-processed">✅ Processed</span>', unsafe_allow_html=True)
                        st.caption(f"Chunks: {processing_info.get('chunks_count', 0)}")
                    
                    st.caption(f"Date: {processing_info.get('processed_date', 'Unknown')[:10]}")
                else:
                    st.markdown('<span class="status-badge status-unprocessed">⏳ Pending</span>', unsafe_allow_html=True)
            
            with col3:
                # Action buttons
                if st.button(f"👁️ View {file['name']}", key=f"view_{i}"):
                    st.session_state[f"show_content_{i}"] = not st.session_state.get(f"show_content_{i}", False)
                
                if st.button(f"🔗 Open {file['name']} in Drive", key=f"drive_{i}"):
                    st.markdown(f'[Open in Google Drive]({file.get("webViewLink", "#")})', unsafe_allow_html=True)
            
            with col4:
                if not file['is_processed']:
                    if st.button(f"🔄 Process {file['name']}", key=f"process_{i}", type="primary"):
                        with st.spinner(f"Processing {file['name']}..."):
                            result = st.session_state.processor.process_single_file_from_drive(file['id'], file['name'])
                            
                            if result['success']:
                                st.success(f"✅ Processed! {result['chunks']} chunks created")
                                st.rerun()
                            else:
                                st.error(f"❌ Processing failed: {result['error']}")
                else:
                    if st.button(f"🔄 Reprocess {file['name']}", key=f"reprocess_{i}", type="secondary"):
                        if not st.session_state.get(f"confirm_reprocess_{i}", False):
                            st.session_state[f"confirm_reprocess_{i}"] = True
                            st.warning("⚠️ Click the button again to confirm reprocessing")
                        else:
                            with st.spinner(f"Reprocessing {file['name']}..."):
                                result = st.session_state.processor.reprocess_file(file['name'])

                            if result['success']:
                                st.success(f"✅ Reprocessed! {result['chunks']} chunks created")
                                st.rerun()
                            else:
                                st.error(f"❌ Reprocessing failed: {result['error']}")
                            st.session_state[f"confirm_reprocess_{i}"] = False
                
                if st.button(f"🗑️ Delete {file['name']}", key=f"delete_{i}", type="secondary"):
                    if st.session_state.get(f"confirm_delete_{i}", False):
                        # Perform deletion
                        with st.spinner("Deleting..."):
                            success = st.session_state.processor.delete_file(file['id'], file['name'])
                            if success:
                                st.success(f"✅ Deleted {file['name']}")
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete file")
                    else:
                        st.session_state[f"confirm_delete_{i}"] = True
                        st.error("⚠️ Click delete again to confirm")
            
            # Show content if requested
            if st.session_state.get(f"show_content_{i}", False):
                with st.expander(f"Content: {file['name']}", expanded=True):
                    content = st.session_state.drive_manager.get_file_content(file['id'])
                    if content:
                        st.text_area(
                            f"File Content - {file['name']}:", 
                            content, 
                            height=300, 
                            key=f"content_{i}",
                            label_visibility="visible"
                        )
                        
                        # Show processing details if processed
                        if file['is_processed']:
                            st.markdown("**Processing Details:**")
                            processing_info = file['processing_info']
                            st.json(processing_info)
                    else:
                        st.error("Could not load file content")
            
            st.markdown("---")

def show_add_document():
    """Add document interface - Google Drive only"""
    st.markdown('<div class="section-header">📝 Add New Document to Google Drive</div>', unsafe_allow_html=True)
    
    if not st.session_state.drive_manager.service:
        st.error("❌ Google Drive not connected. Please check your configuration.")
        return
    
    with st.form("add_document_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            filename = st.text_input(
                "📝 Filename (without .md extension)", 
                placeholder="e.g., new_feature_guide",
                help="Enter a descriptive filename for your document"
            )
        
        with col2:
            auto_process = st.checkbox(
                "🔄 Auto-process after upload", 
                value=False,
                help="If checked, document will be automatically processed to Pinecone after upload"
            )
        
        content = st.text_area(
            "📄 Markdown Content",
            height=400,
            placeholder="""# Document Title

## Overview
Enter your document content here...

## Features
- Feature 1
- Feature 2

## Code Examples
```python
def example():
    return "Hello World"
```

## Conclusion
Summary of the document...
""",
            help="Enter your document content in Markdown format"
        )
        
        submit_button = st.form_submit_button("☁️ Save to Google Drive", type="primary")

        if submit_button:
            if filename and content:
                full_filename = filename + '.md'

                if st.session_state.drive_manager.file_exists(full_filename):
                    st.error(f"❌ A file named '{full_filename}' already exists in Google Drive")
                    return

                with st.spinner("Uploading to Google Drive..."):
                    file_id = st.session_state.drive_manager.upload_content_as_file(content, full_filename)
                    
                    if file_id:
                        st.success(f"✅ Document uploaded to Google Drive: {full_filename}")
                        
                        if auto_process:
                            with st.spinner("Processing to Pinecone..."):
                                result = st.session_state.processor.process_single_file_from_drive(file_id, full_filename)
                                
                                if result['success']:
                                    st.success(f"✅ Document processed to Pinecone! ({result['chunks']} chunks created)")
                                else:
                                    st.error(f"❌ Processing failed: {result['error']}")
                        else:
                            st.info("📝 Document saved. Use the 'Process Documents' tab to add it to the chatbot's knowledge base.")
                    else:
                        st.error("❌ Failed to upload document to Google Drive")
            else:
                st.error("❌ Please provide both filename and content")

    st.markdown("---")
    st.markdown("### 📤 Upload Files from Your Device")

    uploaded_files = st.file_uploader(
        "Select Markdown files to upload",
        type=["md", "txt"],
        accept_multiple_files=True,
        key="local_file_uploader",
    )

    if uploaded_files:
        auto_process_files = st.checkbox(
            "🔄 Auto-process uploaded files",
            key="auto_process_upload",
            value=False,
        )

        if st.button("☁️ Upload Selected File(s)"):
            for up_file in uploaded_files:
                file_bytes = up_file.read()
                filename = up_file.name

                if st.session_state.drive_manager.file_exists(filename):
                    st.error(f"❌ A file named '{filename}' already exists in Google Drive")
                    continue

                with st.spinner(f"Uploading {filename}..."):
                    file_id = st.session_state.drive_manager.upload_file_object(file_bytes, filename, up_file.type)

                if file_id:
                    st.success(f"✅ Uploaded {filename}")

                    if auto_process_files:
                        with st.spinner(f"Processing {filename}..."):
                            result = st.session_state.processor.process_single_file_from_drive(file_id, filename)

                            if result['success']:
                                st.success(f"✅ Processed {filename} ({result['chunks']} chunks)")
                            else:
                                st.error(f"❌ Processing failed for {filename}: {result['error']}")
                else:
                    st.error(f"❌ Failed to upload {filename}")

def process_files_individually(selected_files):
    """Process files one by one with individual progress"""
    st.markdown("### 🔄 Processing Files Individually")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()
    
    processed_count = 0
    total_chunks = 0
    errors = []
    
    for i, file in enumerate(selected_files):
        status_text.text(f"Processing {file['name']}... ({i+1}/{len(selected_files)})")
        
        result = st.session_state.processor.process_single_file_from_drive(file['id'], file['name'])
        
        with results_container:
            if result['success']:
                st.success(f"✅ {file['name']} - {result['chunks']} chunks created")
                processed_count += 1
                total_chunks += result['chunks']
            else:
                st.error(f"❌ {file['name']} - {result['error']}")
                errors.append(f"{file['name']}: {result['error']}")
        
        progress_bar.progress((i + 1) / len(selected_files))
    
    status_text.text("Processing complete!")
    
    # Final summary
    st.markdown("### 📊 Processing Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Processed", processed_count)
    
    with col2:
        st.metric("❌ Errors", len(errors))
    
    with col3:
        st.metric("🧩 Total Chunks", total_chunks)
    
    if errors:
        with st.expander("❌ Error Details"):
            for error in errors:
                st.error(error)
    
    if processed_count > 0:
        st.success(f"🎉 Successfully processed {processed_count} files with {total_chunks} total chunks!")
        st.balloons()

def process_files_batch(selected_files):
    """Process all selected files in batch"""
    st.markdown("### 🚀 Batch Processing Files")
    
    with st.spinner("Processing all selected files..."):
        results = st.session_state.processor.process_multiple_files_from_drive(selected_files)
    
    # Display results
    st.markdown("### 📊 Batch Processing Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("✅ Processed", len(results['processed']))
    
    with col2:
        st.metric("❌ Errors", len(results['errors']))
    
    with col3:
        st.metric("🧩 Total Chunks", results['total_chunks'])
    
    # Detailed results
    if results['processed']:
        with st.expander("✅ Successfully Processed Files", expanded=True):
            for file_info in results['processed']:
                st.success(f"✅ {file_info['name']} - {file_info['chunks']} chunks")
    
    if results['errors']:
        with st.expander("❌ Processing Errors"):
            for error_info in results['errors']:
                st.error(f"❌ {error_info['name']}: {error_info['error']}")
    
    if results['processed']:
        st.success(f"🎉 Batch processing complete! {len(results['processed'])} files processed with {results['total_chunks']} total chunks.")
        st.balloons()

def show_search_interface():
    """Search interface for the knowledge base"""
    st.markdown('<div class="section-header">🔍 Search Knowledge Base</div>', unsafe_allow_html=True)
    
    # Check if there are processed files
    stats = st.session_state.processor.get_processing_stats()
    
    if stats['processed_files'] == 0:
        st.warning("⚠️ No files have been processed yet. Process some documents first to test the search functionality.")
        return
    
    st.info(f"📊 Knowledge base contains {stats['processed_files']} processed files with {stats['total_chunks']} chunks.")
    
    # Search interface
    with st.form("search_form"):
        query = st.text_input(
            "🔍 Enter your search query:",
            placeholder="e.g., How to implement authentication?",
            help="Enter a question or topic you want to search for in your processed documents"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_results = st.slider("Number of results:", 1, 10, 5)
        
        with col2:
            search_button = st.form_submit_button("🔍 Search", type="primary")
    
    if search_button and query:
        with st.spinner("Searching knowledge base..."):
            results = st.session_state.processor.search_similar_content(query, k=num_results)
        
        if not results:
            st.warning("No results found. Try a different query or check if your documents are properly processed.")
            return
        
        st.markdown(f"### 📊 Search Results ({len(results)} found)")
        
        for i, result in enumerate(results):
            with st.expander(f"Result {i+1}: {result['source']}", expanded=i < 3):
                st.markdown(f"**Source:** {result['source']}")
                st.markdown(f"**Chunk:** {result['chunk_index'] + 1}")
                st.markdown(f"**Processed:** {result['processed_date'][:19].replace('T', ' ')}")
                
                st.markdown("**Content:**")
                st.markdown(result['content'])
                
                # Relevance indicator (simplified)
                relevance = 100 - (i * 10)  # Simple decreasing relevance
                st.progress(relevance / 100, text=f"Relevance: {relevance}%")
    

if __name__ == "__main__":
    main()
