# 🏏 CricBattle Document Management System

A comprehensive system for managing markdown documents with automatic processing pipeline: **Markdown Loader → Text Splitter → OpenAI Embeddings → Pinecone Vector Store**.

## ✨ Features

- 📝 **Beautiful Web Interface** - Streamlit-based dashboard for document management
- 🔍 **Auto-Watch Functionality** - Automatically processes new/modified files
- 📤 **Easy Document Upload** - Drag-and-drop or manual text input
- 🔄 **Batch Processing** - Process all documents with one click
- 📊 **Real-time Dashboard** - Monitor processing status and metrics
- 🛠️ **File Management** - Browse, preview, and manage documents
- ⚡ **High Performance** - Efficient chunking and embedding generation

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Markdown      │───▶│   Text          │───▶│   OpenAI        │───▶│   Pinecone      │
│   Loader        │    │   Splitter      │    │   Embeddings    │    │   Vector Store  │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Ensure your `.env` file contains:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=chatbot
REGION=us-east-1
```

### 3. Run the Application

```bash
python main.py
```

Or directly with Streamlit:
```bash
streamlit run streamlit_app.py
```

### 4. Access the Dashboard

Open your browser and go to: `http://localhost:8501`

## 📁 Project Structure

```
Production Chatbot 2/
└── Pinecone_adder/
    ├── .env                    # Environment variables
    ├── main.py                 # Application entry point
    ├── streamlit_app.py        # Web interface
    ├── document_processor.py   # Core processing logic
    ├── file_watcher.py         # Auto-watch functionality
    ├── requirements.txt        # Python dependencies
    ├── processed_files.json    # Processing history (auto-created)
    ├── README.md              # This file
    └── Documentation/         # Markdown files folder
        ├── SalaryCap.md
        ├── Registration and login.md
        └── ... (other .md files)
```

## 🎯 Usage Guide

### Adding Documents

**Method 1: File Upload**
1. Go to the "📝 Add Document" tab
2. Upload a `.md` file using the file uploader
3. Preview and save to Documentation folder

**Method 2: Direct Text Input**
1. Go to the "📝 Add Document" tab
2. Enter filename and markdown content
3. Click "Create Document"

**Method 3: Direct File Addition**
1. Add `.md` files directly to the `Documentation/` folder
2. Enable auto-watch or manually scan for processing

### Processing Documents

**Automatic Processing:**
- Enable "🔍 Auto-watch Documentation folder" in the sidebar
- New/modified files are processed automatically

**Manual Processing:**
- Click "🔄 Scan for New Documents" in the sidebar
- Or use "🚀 Scan and Process All Documents" in the Process tab

### Monitoring

**Dashboard Tab:**
- View system metrics and status
- See recently processed files
- Monitor Pinecone connection

**File Manager Tab:**
- Browse all documentation files
- View file details and content
- Reprocess or delete files

## ⚙️ Configuration

### Text Splitting Settings

The system uses `RecursiveCharacterTextSplitter` with:
- **Chunk Size:** 1000 characters
- **Chunk Overlap:** 200 characters
- **Separators:** `["\n\n", "\n", ".", "!", "?", ",", " ", ""]`

### Embedding Model

- **Model:** `text-embedding-3-small`
- **Dimension:** 1536
- **Provider:** OpenAI

### Vector Store

- **Provider:** Pinecone
- **Metric:** Cosine similarity
- **Cloud:** AWS Serverless

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install -r requirements.txt
```

**2. Pinecone connection issues**
- Verify your API key in `.env`
- Check if index exists in Pinecone dashboard
- Ensure correct region setting

**3. OpenAI API errors**
- Verify API key and billing status
- Check rate limits

**4. Files not processing**
- Ensure files are in `.md` format
- Check file permissions
- Look for error messages in the interface

### Debug Mode

Add debug logging by setting environment variable:
```bash
export STREAMLIT_LOGGER_LEVEL=debug
```

## 🛡️ Security Notes

- Store API keys securely in `.env` file
- Don't commit `.env` file to version control
- Use environment-specific API keys
- Monitor API usage and costs

## 📚 API References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs in the Streamlit interface
3. Open an issue with detailed error information

---

**Happy Document Managing! 🏏📚**
#   d o c u m e n t a t i o n  
 #   d o c u m e n t a t i o n  
 