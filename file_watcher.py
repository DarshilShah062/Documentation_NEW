import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from document_processor import DocumentProcessor

class MarkdownFileHandler(FileSystemEventHandler):
    def __init__(self, processor: DocumentProcessor):
        self.processor = processor
        self.processing_lock = threading.Lock()
    
    def process_file_safely(self, file_path: str):
        """Process file with thread safety"""
        with self.processing_lock:
            if file_path.endswith('.md'):
                print(f"Detected change in: {file_path}")
                self.processor.process_single_file(file_path)
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            # Add a small delay to ensure file is completely written
            threading.Timer(2.0, self.process_file_safely, [event.src_path]).start()
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            threading.Timer(2.0, self.process_file_safely, [event.src_path]).start()

class DocumentWatcher:
    def __init__(self, documentation_folder: str = "Documentation"):
        self.documentation_folder = documentation_folder
        self.processor = DocumentProcessor()
        self.observer = None
        self.is_watching = False
    
    def start_watching(self):
        """Start watching the documentation folder"""
        if self.is_watching:
            return
        
        event_handler = MarkdownFileHandler(self.processor)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.documentation_folder, recursive=True)
        self.observer.start()
        self.is_watching = True
        print(f"Started watching {self.documentation_folder}")
    
    def stop_watching(self):
        """Stop watching the documentation folder"""
        if self.observer and self.is_watching:
            self.observer.stop()
            self.observer.join()
            self.is_watching = False
            print("Stopped watching")
    
    def is_active(self):
        return self.is_watching

# Global watcher instance
watcher = DocumentWatcher()
