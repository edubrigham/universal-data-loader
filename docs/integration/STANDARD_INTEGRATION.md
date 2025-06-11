# Universal Data Loader - Standard Integration Guide

## 🎯 Quick Integration (2 files, 3 steps)

Any LLM application can integrate with the Universal Data Loader using this **standard pattern**:

### **Step 1: Copy the Connector**
Copy `universal_loader_connector.py` to your project root.

### **Step 2: Create Configuration**
Create a `config/` folder and add your document sources:

```bash
mkdir config
cp config/documents.json.template config/documents.json
# Edit config/documents.json with your sources
```

### **Step 3: Use Simple API**
```python
from universal_loader_connector import get_documents

# This processes everything in config/documents.json
documents = get_documents()

# Use documents with any LLM framework
for doc in documents:
    print(f"Content: {doc['page_content']}")
    print(f"Source: {doc['metadata']['source']}")
```

**That's it!** 🎉

---

## 📁 Standard Project Structure

```
your_llm_app/
├── config/
│   ├── documents.json          # Your main document sources
│   ├── training_data.json      # Optional: for model training
│   └── rag_knowledge.json      # Optional: for RAG systems
├── universal_loader_connector.py    # The connector (copy from repo)
└── your_app.py                 # Your LLM application
```

---

## ⚙️ Configuration Examples

### Basic Configuration (`config/documents.json`)

```json
{
  "microservice_url": "http://localhost:8000",
  "sources": [
    {
      "type": "url",
      "path": "https://docs.your-company.com",
      "output_prefix": "company_docs"
    },
    {
      "type": "directory",
      "path": "./data/documents/",
      "recursive": true,
      "include_patterns": ["*.pdf", "*.docx"],
      "output_prefix": "local_docs"
    }
  ],
  "processing": {
    "output_format": "documents",
    "include_metadata": true,
    "enable_chunking": false
  },
  "batch_options": {
    "max_workers": 3,
    "merge_all": true
  }
}
```

### RAG System Configuration (`config/rag_knowledge.json`)

```json
{
  "microservice_url": "http://localhost:8000",
  "sources": [
    {
      "type": "url",
      "path": "https://docs.company.com",
      "output_prefix": "docs"
    },
    {
      "type": "file",
      "path": "./knowledge/handbook.pdf",
      "output_prefix": "handbook"
    }
  ],
  "processing": {
    "output_format": "documents",
    "include_metadata": true,
    "enable_chunking": false,
    "_chunking_example": {
      "_comment": "To enable chunking for vector databases:",
      "_enable_chunking": true,
      "_chunking_strategy": "by_title",
      "_max_chunk_size": 600,
      "_chunk_overlap": 100
    }
  }
}
```

### Training Data Configuration (`config/training_data.json`)

```json
{
  "microservice_url": "http://localhost:8000",
  "sources": [
    {
      "type": "directory",
      "path": "./training_corpus/",
      "recursive": true,
      "include_patterns": ["*.txt", "*.md"],
      "output_prefix": "training"
    }
  ],
  "processing": {
    "output_format": "text",
    "include_metadata": false,
    "enable_chunking": false
  }
}
```

---

## 🔌 Standard API Functions

### Main Functions

```python
from universal_loader_connector import get_documents, process_url, process_file

# Process all sources from config/documents.json
documents = get_documents()

# Process all sources from config/rag_knowledge.json  
rag_docs = get_documents("rag_knowledge")

# Process single URL
url_docs = process_url("https://example.com/article")

# Process single file
file_docs = process_file("./data/report.pdf")
```

### Integration Examples

#### RAG System
```python
from universal_loader_connector import get_documents
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Load documents
documents = get_documents("rag_knowledge")

# Create vector store
embeddings = OpenAIEmbeddings()
vectorstore = Chroma.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever()

# Ready for RAG!
```

#### Document Analysis
```python
from universal_loader_connector import process_file

# Analyze uploaded document
documents = process_file("uploaded_report.pdf")

for doc in documents:
    # Your analysis logic
    content = doc['page_content']
    source = doc['metadata']['filename']
    page = doc['metadata'].get('page_number', 1)
    
    print(f"Page {page} from {source}: {len(content)} chars")
```

#### Training Data Preparation
```python
from universal_loader_connector import get_documents

# Get clean text for training
documents = get_documents("training_data")

# Save as training file
with open("model_training.txt", "w") as f:
    for doc in documents:
        f.write(doc['page_content'] + '\n\n')
```

---

## 🚀 Deployment

### Prerequisites
```bash
# 1. Start Universal Data Loader microservice
docker-compose up -d

# 2. Verify it's running
curl http://localhost:8000/health
```

### Application Setup
```bash
# 1. Copy connector to your project
cp universal_loader_connector.py your_project/

# 2. Create config directory
mkdir your_project/config

# 3. Copy and edit configuration
cp config/documents.json.template your_project/config/documents.json
# Edit with your sources...

# 4. Install requirements
pip install requests

# 5. Test integration
cd your_project
python -c "from universal_loader_connector import get_documents; print(len(get_documents()))"
```

---

## 🔧 Configuration Reference

### Source Types

| Type | Description | Required Fields | Optional Fields |
|------|-------------|----------------|----------------|
| `url` | Web content | `path` | `output_prefix` |
| `file` | Single file | `path` | `output_prefix` |
| `directory` | Folder of files | `path` | `recursive`, `include_patterns`, `exclude_patterns`, `output_prefix` |

### Processing Options

| Option | Default | Description |
|--------|---------|-------------|
| `output_format` | `"documents"` | Output format: `documents`, `text`, `json`, `elements` |
| `enable_chunking` | `false` | Enable document chunking |
| `chunking_strategy` | `null` | Required if chunking enabled: `basic`, `by_title`, `by_page` |
| `max_chunk_size` | `null` | Required if chunking enabled: Maximum characters per chunk |
| `chunk_overlap` | `null` | Optional when chunking: Overlap between chunks |
| `include_metadata` | `true` | Include document metadata |
| `min_text_length` | `50` | Filter out short content |
| `remove_headers_footers` | `true` | Clean headers/footers |

### Batch Options

| Option | Default | Description |
|--------|---------|-------------|
| `max_workers` | `3` | Parallel processing workers |
| `continue_on_error` | `true` | Continue if individual sources fail |
| `merge_all` | `true` | Combine all sources into one result |

---

## ❓ Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `ConnectionError` | Start microservice: `docker-compose up -d` |
| `FileNotFoundError` | Create `config/documents.json` from template |
| Empty results | Check source paths in configuration |
| Timeout errors | Reduce `max_workers` or increase timeout |

### Health Check
```python
from universal_loader_connector import health_check

status = health_check()
print(f"Service status: {status['status']}")
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.INFO)

# Now get_documents() will show detailed logs
documents = get_documents()
```

---

## 🎯 Best Practices

### 1. **Use Appropriate Configs**
- **Modern RAG systems**: Use `enable_chunking: false` to leverage large context windows
- **Legacy vector databases**: Use `enable_chunking: true` with `chunking_strategy: "by_title"` and 600-800 char chunks
- **Training data**: Use `output_format: "text"` with no metadata
- **Document analysis**: Use `enable_chunking: false` to preserve complete context

### 2. **Organize Sources**
- Group related sources in separate config files
- Use descriptive `output_prefix` names
- Filter files with `include_patterns`/`exclude_patterns`

### 3. **Error Handling**
```python
try:
    documents = get_documents()
except ConnectionError:
    print("Universal Data Loader not running")
except FileNotFoundError:
    print("Configuration file missing")
```

### 4. **Performance**
- Use `max_workers: 3-5` for parallel processing
- Set `continue_on_error: true` for batch reliability
- Cache results for repeated processing

---

## 📞 Support

- **API Documentation**: http://localhost:8000/docs (when microservice is running)
- **Test Integration**: `python universal_loader_connector.py`
- **Example App**: `python example_llm_app.py`

---

**🎉 Ready to integrate? Copy the connector and create your config!**