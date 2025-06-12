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
# Clone the repository
git clone <repository-url>
cd unstructured

# Set up your environment configuration
# This creates a .env file with a secure, random API key.
cp .env.example .env

# Start the microservice (takes 30-60 seconds on first run)
docker-compose up --build -d

# Verify it's running
curl http://localhost:8000/health
```

**That's it!** Your microservice is now running at `http://localhost:8000` and is secured with an API key. Your key is stored in the `.env` file.

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

# Initialize the connector with your API key
# The connector will automatically read the ULOADER_API_KEY environment variable
from universal_loader_client import UnstructuredClient
client = UnstructuredClient(api_key="YOUR_API_KEY_HERE")

# Example 1: Process documents from configuration
documents = client.get_documents_from_config("config/documents.json")
print(f"Loaded {len(documents)} documents for RAG system")

# Example 2: Process a single URL dynamically
documents = client.process_url("https://company.com/docs")

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
  "api_key": "your-secret-api-key-here",
  "sources": [
    {
      "type": "url",
      "path": "https://your-company.com/docs",
      "output_prefix": "company_docs"
    },
    {
      "type": "url_list",
      "path": "./data/urls.txt",
      "output_prefix": "web_content"
    }
  ],
  "processing": {
    "output_format": "documents",
    "include_metadata": true,
    "min_text_length": 10
  }
}
```

**URL List Format (`./data/urls.txt`):**
```
https://company.com/page1
https://company.com/page2
# Comments are ignored
https://company.com/page3
```

Then load all sources at once:

```python
# The connector can be configured to read the key from the config or an env var.
documents = get_documents_from_config("config/documents.json")
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

The Universal Data Loader exposes a clean, job-based REST API. All core endpoints are consolidated under the `/api/v1/jobs/` prefix. **Access to endpoints that create or delete jobs requires API key authentication.**

The API key must be sent as a header: `x-api-key: YOUR_SECRET_KEY`

### The Asynchronous Workflow

1.  **Submit a Job**: `POST` a request to an endpoint (`/file`, `/url`, or `/batch`) to start a processing job.
2.  **Get a Job ID**: The API immediately returns a `job_id`.
3.  **Check Status**: `GET /{job_id}` to check if the job is `pending`, `processing`, or `completed`.
4.  **Get Result**: `GET /{job_id}/result` to download the final LangChain documents.

### Key Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `GET /health` | `GET` | Checks the health and status of the microservice. |
| `/api/v1/jobs/file` | `POST` | Process a single file by uploading it in the request body. |
| `/api/v1/jobs/url` | `POST` | Process a single document from a given URL. |
| `/api/v1/jobs/batch` | `POST` | Process multiple sources (files, URLs, etc.) in one job. |
| `/api/v1/jobs/{job_id}` | `GET` | Retrieve the current status of a specific job. |
| `/api/v1/jobs/{job_id}/result`| `GET` | Retrieve the processed documents for a completed job. |
| `/api/v1/jobs/{job_id}` | `DELETE`| Clean up all data and files associated with a job. (Auth Required) |


### Example: Processing a URL with `curl`

```bash
# 1. Set your API Key from your .env file
API_KEY=$(grep API_SECRET_KEY .env | cut -d '=' -f2)

# 2. Submit the URL with the key in the header and get a Job ID
JOB_ID=$(curl -s -X POST "http://localhost:8000/api/v1/jobs/url" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $API_KEY" \
  -d '{"url": "https://en.wikipedia.org/wiki/Artificial_intelligence"}' | jq -r .job_id)

echo "Processing with Job ID: $JOB_ID"

# 3. Poll for completion (publicly accessible)
sleep 5 
curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID" | jq .status

# 4. Download the final result (publicly accessible)
curl -s "http://localhost:8000/api/v1/jobs/$JOB_ID/result" | jq .
```

### Document Processing Issues
```bash
# Check specific job status
curl http://localhost:8000/api/v1/jobs/{job_id}

# Test with simple URL (replace YOUR_API_KEY with your actual key)
curl -X POST http://localhost:8000/api/v1/jobs/url \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"url": "https://httpbin.org/html"}'
```

---

## ⚙️ Configuration

### Environment Variables

The primary method of configuration is via a `.env` file in the project root. You can create one by copying the provided example:

```bash
cp .env.example .env
```

The server will automatically load the following variables from this file:

- `API_SECRET_KEY`: **(Required)** A secure, unique key that clients must provide in the `x-api-key` header to access protected endpoints.
- `PORT`: The port on which the microservice will run. Defaults to `8000`.
- `ENVIRONMENT`: Set to `development` to enable features like auto-reloading. Defaults to `production`.

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