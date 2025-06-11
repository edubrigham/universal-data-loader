# Universal Data Loader Microservice 🚀📄➡️🤖

**Containerized document processing microservice for LLM applications**

Transform any document into AI-ready data through a scalable REST API. Perfect for RAG systems, chatbots, and knowledge bases.

## 🎯 What This Does

This microservice provides a REST API that:
- ✅ Processes documents (PDFs, Word, PowerPoint, websites, etc.) via HTTP requests
- ✅ Returns AI-ready structured data for immediate use in LLM applications  
- ✅ Scales horizontally as a containerized microservice
- ✅ Integrates seamlessly with RAG pipelines and vector databases

---

## 🚀 Quick Start - Deploy the Microservice

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start the microservice
git clone <repository-url>
cd unstructured

# Start the microservice (takes 30 seconds)
docker-compose up -d

# Verify it's running
curl http://localhost:8000/health
```

**That's it!** Your microservice is now running at `http://localhost:8000`

### Option 2: Manual Docker Build

```bash
# Build the container
docker build -f infrastructure/docker/Dockerfile -t universal-data-loader .

# Run the microservice
docker run -d -p 8000:8000 --name universal-data-loader universal-data-loader

# Check status
curl http://localhost:8000/health
```

---

## 🧠 LLM Application Integration

### Python Connector (Easiest Integration)

The microservice includes a Python connector that makes integration with LLM applications simple:

```python
# Import the connector
from client.python.universal_loader_connector import get_documents, process_url

# Example 1: Process documents from configuration
documents = get_documents()  # Reads config/documents.json
print(f"Loaded {len(documents)} documents for RAG system")

# Example 2: Process a single URL dynamically
documents = process_url("https://company.com/docs")

# Documents are returned in LangChain format - ready for RAG!
# Use directly with any vector database:
# vectorstore = Chroma.from_documents(documents)
# retriever = vectorstore.as_retriever()
```

### Configuration-Based Processing (Recommended)

Create `config/documents.json` to define your document sources:

```json
{
  "microservice_url": "http://localhost:8000",
  "sources": [
    {
      "type": "url",
      "path": "https://your-company.com/docs",
      "output_prefix": "company_docs"
    }
  ],
  "processing": {
    "output_format": "documents",
    "include_metadata": true,
    "min_text_length": 10
  }
}
```

Then load all sources at once:

```python
documents = get_documents()  # Processes all sources in config
```

### RAG System Integration Example

```python
#!/usr/bin/env python3
"""Complete RAG system using Universal Data Loader"""

from client.python.universal_loader_connector import get_documents
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

def build_rag_system():
    """Build a complete RAG system from configured document sources"""
    
    # Step 1: Load documents from microservice
    print("🔄 Loading documents from Universal Data Loader...")
    documents = get_documents()
    print(f"✅ Loaded {len(documents)} documents")
    
    # Step 2: Create vector store
    print("🔄 Creating vector store...")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    
    # Step 3: Create retriever and QA chain
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    llm = ChatOpenAI(temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    
    print("✅ RAG system ready!")
    return qa_chain

# Use the RAG system
qa_system = build_rag_system()
response = qa_system("What are the main policies in our documentation?")
print(f"Answer: {response['result']}")
```

---

## 📡 REST API Documentation

### Health Check
```bash
GET /health
```
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "uptime": "running",
  "active_jobs": 0
}
```

### Process Single File/URL
```bash
POST /process/documents
Content-Type: application/json

{
  "source": "https://example.com/document.pdf",
  "source_type": "url",
  "output_format": "documents",
  "chunking_strategy": "auto",
  "max_chunk_size": 1000
}
```

### Batch Processing
```bash
POST /process/batch
Content-Type: application/json

{
  "sources": [
    {"type": "url", "path": "https://site1.com"},
    {"type": "url", "path": "https://site2.com"}
  ],
  "processing": {
    "output_format": "documents",
    "include_metadata": true
  }
}
```

Response:
```json
{
  "job_id": "job_abc123",
  "status": "completed", 
  "documents_count": 25,
  "created_at": "2024-01-01T12:00:00"
}
```

### Get Job Results
```bash
GET /jobs/{job_id}/results
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# .env file
PORT=8000
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production

# Optional: Configure document processing
MAX_CHUNK_SIZE=1000
DEFAULT_OUTPUT_FORMAT=documents
```

### Docker Compose Configuration

```yaml
# docker-compose.yml
services:
  universal-data-loader:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

---

## 🛠️ Development & Testing

### Run Tests
```bash
# Start the service
docker-compose up -d

# Run tests
python -m pytest tests/ -v

# Test with example integration
python examples/rag_integration/example_llm_app.py
```

### Monitor Service
```bash
# Check health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Check logs
docker-compose logs -f universal-data-loader
```

---

## 📁 Supported Formats

| Document Type | Support | API Processing |
|---------------|---------|----------------|
| PDF Documents | ✅ Full | `/process/documents` |
| Word Documents | ✅ Full | `/process/documents` |
| PowerPoint | ✅ Full | `/process/documents` |
| Web Pages | ✅ Full | `/process/documents` |
| Text Files | ✅ Full | `/process/documents` |
| Email Files | ✅ Full | `/process/documents` |
| CSV Data | ✅ Full | `/process/documents` |

---

## 🔧 Advanced Integration

### Custom Processing Pipeline

```python
import requests

def custom_document_pipeline(sources):
    """Custom processing pipeline using REST API directly"""
    
    # Process documents via API
    response = requests.post("http://localhost:8000/process/batch", json={
        "sources": sources,
        "processing": {
            "output_format": "documents",
            "max_chunk_size": 500,
            "include_metadata": True
        }
    })
    
    job_data = response.json()
    job_id = job_data["job_id"]
    
    # Get results
    results = requests.get(f"http://localhost:8000/jobs/{job_id}/results")
    return results.json()["documents"]
```

### Multiple Environment Deployment

```bash
# Development
docker-compose -f docker-compose.yml up

# Production with scaling
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --scale universal-data-loader=3

# With reverse proxy
docker-compose --profile production up
```

---

## 🚀 Production Deployment

### Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: universal-data-loader
spec:
  replicas: 3
  selector:
    matchLabels:
      app: universal-data-loader
  template:
    metadata:
      labels:
        app: universal-data-loader
    spec:
      containers:
      - name: universal-data-loader
        image: universal-data-loader:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
```

### Health Monitoring

```bash
# Configure health checks
curl -f http://localhost:8000/health || exit 1

# Monitor with external tools
# - Prometheus metrics: http://localhost:8000/metrics  
# - Structured logging: Check container logs
```

---

## 💡 Real-World Use Cases

### 1. Enterprise RAG Chatbot
```python
# Load company documents and build searchable knowledge base
documents = get_documents()  # Processes all company docs
vectorstore = Chroma.from_documents(documents)
chatbot = ConversationalRetrievalChain.from_llm(llm, vectorstore.as_retriever())
```

### 2. Document Analysis Service  
```python
# Process incoming documents via API
@app.post("/analyze-document")
def analyze_document(url: str):
    documents = process_url(url)
    # Run analysis on processed documents
    return analyze_content(documents)
```

### 3. Knowledge Base Sync
```python
# Regularly sync external documentation
def sync_knowledge_base():
    documents = get_documents()  # Auto-processes configured sources
    update_vector_database(documents)
    
# Run as scheduled job
schedule.every().day.at("02:00").do(sync_knowledge_base)
```

---

## 🆘 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs universal-data-loader

# Verify port availability
lsof -i :8000

# Test with minimal config
curl http://localhost:8000/health
```

### Document Processing Issues
```bash
# Check specific job status
curl http://localhost:8000/jobs/{job_id}/status

# Test with simple URL
curl -X POST http://localhost:8000/process/documents \
  -H "Content-Type: application/json" \
  -d '{"source": "https://httpbin.org/html", "source_type": "url"}'
```

### Integration Issues
```python
# Test connector directly
from client.python.universal_loader_connector import health_check
print(health_check())  # Should return {"status": "healthy"}
```

---

## 📚 Next Steps

1. **Deploy**: `docker-compose up -d`
2. **Configure**: Edit `config/documents.json` with your sources  
3. **Integrate**: Use Python connector in your LLM application
4. **Scale**: Add replicas and monitoring for production

**Need help?** Check `/docs` endpoint for interactive API documentation or examine the integration examples in `examples/rag_integration/`.