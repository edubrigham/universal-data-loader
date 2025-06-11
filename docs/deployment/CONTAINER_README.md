# Universal Data Loader - Containerized Microservice 🐳

**Plug-and-play document processing service for any LLM application**

## 🎯 What This Container Does

This container provides a **REST API microservice** that converts any document into LangChain-compatible format. Perfect for AI applications that need to process documents without dealing with the complexity of document parsing.

**Input:** PDFs, Word docs, URLs, directories of files  
**Output:** LangChain Documents ready for RAG, training, or analysis  
**Interface:** REST API with async job processing  

## 🚀 Quick Start (2 minutes)

### Option 1: Docker Compose (Recommended)

```bash
# Download and start
curl -O https://raw.githubusercontent.com/your-repo/universal-data-loader/main/docker-compose.yml
docker-compose up -d

# Test it works
curl http://localhost:8000/health
```

### Option 2: Direct Docker Run

```bash
docker run -d \
  --name universal-data-loader \
  -p 8000:8000 \
  your-registry/universal-data-loader:latest

# Test it works  
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-11T09:36:00.000000",
  "active_jobs": 0
}
```

### Quick Test

```bash
# Process a URL
curl -X POST "http://localhost:8000/process/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://en.wikipedia.org/wiki/Machine_learning"}'

# Returns: {"job_id": "job_abc123_1699123456", "status": "pending"}

# Check status
curl "http://localhost:8000/jobs/job_abc123_1699123456"

# Download result when completed
curl "http://localhost:8000/download/job_abc123_1699123456"
```

---

## 🏗️ Container Architecture

```
┌─────────────────────────────────────────┐
│  Universal Data Loader Container        │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   FastAPI   │  │   Document      │   │
│  │   REST API  │──│   Processing    │   │
│  │             │  │   Engine        │   │
│  └─────────────┘  └─────────────────┘   │
│                                         │
│  ┌─────────────┐  ┌─────────────────┐   │
│  │   Async     │  │   File Storage  │   │
│  │   Job Queue │  │   & Cleanup     │   │
│  │             │  │                 │   │
│  └─────────────┘  └─────────────────┘   │
└─────────────────────────────────────────┘
           │
           ▼
    Your LLM Application
```

## 📡 API Endpoints

### Core Processing Endpoints

| Endpoint | Method | Purpose | Input | Response |
|----------|--------|---------|-------|----------|
| `POST /process/file` | Upload & process file | Form data + config | Job ID |
| `POST /process/url` | Process web content | URL + config | Job ID |
| `POST /process/batch` | Process multiple sources | Sources array | Job ID |
| `GET /jobs/{job_id}` | Check processing status | Job ID | Status info |
| `GET /download/{job_id}` | Download results | Job ID | LangChain Documents |

### Management Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `GET /health` | Service health check |
| `GET /docs` | Interactive API documentation |
| `DELETE /jobs/{job_id}` | Clean up job data |

---

## 💻 Integration Examples

### Python Integration

```python
import requests
import time

class DataLoaderClient:
    def __init__(self, url="http://localhost:8000"):
        self.url = url
    
    def process_documents(self, sources):
        # Submit batch job
        response = requests.post(f"{self.url}/process/batch", json={
            "sources": sources,
            "loader_config": {"output_format": "documents"}
        })
        job_id = response.json()["job_id"]
        
        # Wait for completion
        while True:
            status = requests.get(f"{self.url}/jobs/{job_id}").json()
            if status["status"] == "completed":
                return requests.get(f"{self.url}/download/{job_id}").json()
            time.sleep(2)

# Usage
client = DataLoaderClient()
documents = client.process_documents([
    {"type": "url", "path": "https://company.com/docs"},
    {"type": "file", "path": "/data/manual.pdf"}
])

# Documents are now LangChain-compatible
for doc in documents:
    print(f"Content: {doc['page_content']}")
    print(f"Source: {doc['metadata']['source']}")
```

### JavaScript/Node.js Integration

```javascript
const axios = require('axios');

class DataLoaderClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async processUrl(url, config = {}) {
        // Submit job
        const response = await axios.post(`${this.baseUrl}/process/url`, {
            url: url,
            output_format: 'documents',
            ...config
        });
        
        const jobId = response.data.job_id;
        
        // Wait for completion
        while (true) {
            const statusResponse = await axios.get(`${this.baseUrl}/jobs/${jobId}`);
            const status = statusResponse.data.status;
            
            if (status === 'completed') {
                const result = await axios.get(`${this.baseUrl}/download/${jobId}`);
                return result.data;
            } else if (status === 'failed') {
                throw new Error(`Processing failed: ${statusResponse.data.error_message}`);
            }
            
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }
}

// Usage
const client = new DataLoaderClient();
const documents = await client.processUrl('https://example.com/article');
console.log(`Processed ${documents.length} documents`);
```

### curl Examples

```bash
# Process a single URL
curl -X POST "http://localhost:8000/process/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "output_format": "documents",
    "enable_chunking": false
  }'

# Upload and process a file
curl -X POST "http://localhost:8000/process/file" \
  -F "file=@document.pdf" \
  -F 'config={"output_format": "documents", "include_metadata": true}'

# Batch process multiple sources
curl -X POST "http://localhost:8000/process/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"type": "url", "path": "https://docs.company.com"},
      {"type": "url", "path": "https://company.com/policies"}
    ],
    "loader_config": {"output_format": "documents"},
    "max_workers": 2
  }'
```

---

## 🔧 Configuration Options

### Document Processing Config

```json
{
  "output_format": "documents",        // "documents" | "json" | "text"
  "enable_chunking": false,            // Enable document chunking
  "chunking_strategy": "by_title",     // Required if chunking: "basic" | "by_title" | "by_page"
  "max_chunk_size": 800,               // Required if chunking: Characters per chunk
  "chunk_overlap": 100,                // Optional when chunking: Overlap between chunks
  "include_metadata": true,            // Include document metadata
  "min_text_length": 50,               // Filter short content
  "remove_headers_footers": true,      // Clean up headers/footers
  "ocr_languages": ["eng", "fra"]      // OCR language support
}
```

### Batch Processing Config

```json
{
  "sources": [
    {
      "type": "file",                   // "file" | "directory" | "url"
      "path": "/data/document.pdf",
      "output_prefix": "company_docs",
      "custom_config": {                // Override global config
        "enable_chunking": true,
        "chunking_strategy": "basic", 
        "max_chunk_size": 1000
      }
    }
  ],
  "max_workers": 3,                     // Parallel processing
  "continue_on_error": true             // Don't stop on failures
}
```

---

## 🐳 Deployment Options

### Development Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  universal-data-loader:
    image: universal-data-loader:latest
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Production Deployment with Nginx

```yaml
# docker-compose.yml
version: '3.8'
services:
  universal-data-loader:
    image: universal-data-loader:latest
    restart: always
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - universal-data-loader
```

### Kubernetes Deployment

```yaml
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
    spec:
      containers:
      - name: universal-data-loader
        image: universal-data-loader:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: universal-data-loader-service
spec:
  selector:
    app: universal-data-loader
  ports:
  - port: 8000
    targetPort: 8000
```

---

## 🛠️ Build and Deployment

### Building the Container

```bash
# Clone repository
git clone <repository-url>
cd unstructured

# Build container
docker build -t universal-data-loader:latest .

# Or use the deployment script
./deploy.sh development
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Service port |
| `HOST` | `0.0.0.0` | Service host |
| `MAX_WORKERS` | `3` | Default max workers |
| `TIMEOUT` | `300` | Job timeout (seconds) |

### Health Monitoring

```bash
# Check container health
docker exec universal-data-loader curl -f http://localhost:8000/health

# Monitor logs
docker logs universal-data-loader -f

# Check resource usage
docker stats universal-data-loader
```

---

## 🔍 Monitoring and Troubleshooting

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

**Healthy Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-11T09:36:00.000000",
  "uptime": "running",
  "active_jobs": 2
}
```

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Container won't start | Health check fails | Check logs: `docker logs universal-data-loader` |
| Out of memory | Processing stops | Increase memory: `deploy.resources.limits.memory: 4G` |
| Slow processing | High response times | Scale replicas or increase CPU limits |
| File upload fails | 413 error | Increase nginx `client_max_body_size` |

### Debug Commands

```bash
# View container logs
docker logs universal-data-loader --tail 100 -f

# Exec into container
docker exec -it universal-data-loader /bin/bash

# Test API directly
curl -v http://localhost:8000/health

# Check job queue
curl http://localhost:8000/admin/jobs
```

---

## 🔒 Security Considerations

### Production Security

- **Rate Limiting:** Built-in rate limiting (configurable)
- **File Size Limits:** Max upload size: 100MB (configurable)
- **Timeout Protection:** Jobs timeout after 5 minutes (configurable)
- **Input Validation:** All inputs validated and sanitized
- **No Persistent Storage:** Temporary files cleaned up automatically

### Network Security

```nginx
# nginx.conf - Rate limiting example
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
server {
    limit_req zone=api burst=20 nodelay;
    client_max_body_size 100M;
}
```

---

## 📊 Performance Characteristics

### Throughput

- **Single Document:** ~2-5 seconds (depending on size)
- **Batch Processing:** ~1-3 documents/second/worker
- **Concurrent Jobs:** Up to 10 parallel jobs (configurable)
- **Memory Usage:** ~512MB base + ~100MB per active job

### Scaling

```yaml
# Horizontal scaling example
services:
  universal-data-loader:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
  
  nginx:
    # Load balance across replicas
    upstream universal-data-loader {
      server universal-data-loader_1:8000;
      server universal-data-loader_2:8000;
      server universal-data-loader_3:8000;
    }
```

---

## 🎯 Use Cases

### RAG System Setup

```python
# Build knowledge base for RAG
sources = [
    {"type": "directory", "path": "/company_docs/"},
    {"type": "url", "path": "https://docs.company.com"},
    {"type": "file", "path": "/policies/handbook.pdf"}
]

documents = client.process_batch(sources)

# Use with LangChain
from langchain_chroma import Chroma
vectorstore = Chroma.from_documents(documents)
retriever = vectorstore.as_retriever()
```

### Training Data Preparation

```python
# Prepare clean training data
documents = client.process_batch(
    sources=[{"type": "directory", "path": "/training_data/"}],
    config={
        "output_format": "text",
        "min_text_length": 100,
        "include_metadata": False
    }
)
```

### Real-time Document Analysis

```python
# Process documents as they arrive
def handle_uploaded_file(file_path):
    documents = client.process_file(file_path)
    return analyze_documents(documents)
```

---

## 📞 Support

### Getting Help

- **API Documentation:** http://localhost:8000/docs (when running)
- **Integration Guide:** [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Issues:** Create issue in repository

### Testing

```bash
# Run container tests
python test_container.py

# Run integration examples
python client_example.py
```

---

## 📝 License

MIT License - see LICENSE file for details.

---

**🎉 Ready to integrate? Check the [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed setup instructions!**