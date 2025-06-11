# Universal Data Loader - LLM Integration Guide

**For Software Engineer LLMs setting up AI applications**

## 🎯 Overview

The Universal Data Loader is a containerized microservice that converts documents (PDFs, Word, URLs, etc.) into LangChain-compatible format for immediate use in LLM applications. This guide provides step-by-step integration instructions.

## 🚀 Quick Integration (5 minutes)

### Step 1: Deploy the Container

```bash
# Option A: Docker Compose (Recommended)
curl -O https://raw.githubusercontent.com/your-repo/universal-data-loader/main/docker-compose.yml
docker-compose up -d

# Option B: Direct Docker Run
docker run -d \
  --name universal-data-loader \
  -p 8000:8000 \
  -e PORT=8000 \
  your-registry/universal-data-loader:latest

# Verify deployment
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-11T09:36:00.000000",
  "uptime": "running",
  "active_jobs": 0
}
```

### Step 2: Test Document Processing

```bash
# Test URL processing
curl -X POST "http://localhost:8000/process/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "output_format": "documents"
  }'

# Returns job_id for async processing
```

### Step 3: Integrate with Your LLM Application

```python
import requests
import time
import json

class UniversalDataLoaderClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def process_documents(self, sources, wait_for_completion=True):
        """Process documents and return LangChain-compatible format"""
        # Submit batch job
        response = requests.post(f"{self.base_url}/process/batch", json={
            "sources": sources,
            "loader_config": {"output_format": "documents"}
        })
        job_id = response.json()["job_id"]
        
        if wait_for_completion:
            return self._wait_and_download(job_id)
        return job_id
    
    def _wait_and_download(self, job_id):
        """Wait for job completion and download results"""
        while True:
            status = requests.get(f"{self.base_url}/jobs/{job_id}").json()
            if status["status"] == "completed":
                result = requests.get(f"{self.base_url}/download/{job_id}")
                return result.json()
            elif status["status"] == "failed":
                raise Exception(f"Job failed: {status.get('error_message')}")
            time.sleep(2)

# Usage in your LLM app
loader = UniversalDataLoaderClient()
documents = loader.process_documents([
    {"type": "url", "path": "https://company.com/docs"},
    {"type": "file", "path": "/data/manual.pdf"}
])

# Documents are now in LangChain format
for doc in documents:
    print(f"Content: {doc['page_content']}")
    print(f"Metadata: {doc['metadata']}")
```

---

## 🏗️ Architecture Integration Patterns

### Pattern 1: Microservice Integration (Recommended)

```yaml
# docker-compose.yml for your LLM application
version: '3.8'
services:
  your-llm-app:
    build: .
    depends_on:
      - universal-data-loader
    environment:
      - DATA_LOADER_URL=http://universal-data-loader:8000
  
  universal-data-loader:
    image: your-registry/universal-data-loader:latest
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
```

### Pattern 2: Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: universal-data-loader
spec:
  replicas: 2
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
        image: your-registry/universal-data-loader:latest
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
          initialDelaySeconds: 30
          periodSeconds: 10
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
  type: ClusterIP
```

### Pattern 3: Serverless Integration (AWS Lambda/Cloud Functions)

```python
# serverless_client.py
import boto3
import requests
import os

class ServerlessDataLoader:
    def __init__(self):
        # Use container URL from environment
        self.loader_url = os.getenv('DATA_LOADER_URL', 'http://universal-data-loader:8000')
    
    def lambda_handler(self, event, context):
        """AWS Lambda handler that processes documents"""
        sources = event.get('sources', [])
        
        # Process documents
        response = requests.post(f"{self.loader_url}/process/batch", json={
            "sources": sources,
            "loader_config": {"output_format": "documents"}
        })
        
        # Return job ID for async processing
        return {
            'statusCode': 200,
            'body': response.json()
        }
```

---

## 📡 API Reference

### Core Endpoints

| Endpoint | Method | Purpose | Input | Output |
|----------|--------|---------|-------|--------|
| `/process/file` | POST | Process uploaded file | File + config | Job ID |
| `/process/url` | POST | Process URL content | URL + config | Job ID |
| `/process/batch` | POST | Process multiple sources | Sources array | Job ID |
| `/jobs/{job_id}` | GET | Check job status | Job ID | Status info |
| `/download/{job_id}` | GET | Download results | Job ID | LangChain Documents |
| `/health` | GET | Health check | None | Service status |

### Request Examples

#### Single File Processing
```bash
curl -X POST "http://localhost:8000/process/file" \
  -F "file=@document.pdf" \
  -F 'config={"output_format":"documents","chunking_strategy":"by_title"}'
```

#### URL Processing
```bash
curl -X POST "http://localhost:8000/process/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "output_format": "documents",
    "max_chunk_size": 800,
    "include_metadata": true
  }'
```

#### Batch Processing
```bash
curl -X POST "http://localhost:8000/process/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {"type": "url", "path": "https://docs.company.com"},
      {"type": "file", "path": "/data/manual.pdf"},
      {"type": "directory", "path": "/data/policies/"}
    ],
    "loader_config": {
      "output_format": "documents",
      "chunking_strategy": "by_title",
      "max_chunk_size": 600
    },
    "max_workers": 3
  }'
```

### Response Format

All endpoints return LangChain-compatible documents:

```json
[
  {
    "page_content": "Document text content here...",
    "metadata": {
      "source": "document.pdf",
      "page_number": 1,
      "element_type": "text",
      "languages": ["eng"],
      "batch_id": "batch_123",
      "processed_at": "2025-06-11T09:36:00"
    }
  }
]
```

---

## 🔧 Configuration Options

### Document Processing Configuration

```json
{
  "output_format": "documents",        // "documents" | "json" | "text" | "elements"
  "chunking_strategy": "by_title",     // null | "basic" | "by_title" | "by_page"
  "max_chunk_size": 800,               // Characters per chunk
  "chunk_overlap": 100,                // Overlap between chunks
  "include_metadata": true,            // Include document metadata
  "min_text_length": 50,               // Filter short content
  "remove_headers_footers": true,      // Clean up headers/footers
  "ocr_languages": ["eng", "fra"]      // OCR language support
}
```

### Batch Processing Configuration

```json
{
  "sources": [
    {
      "type": "file",                   // "file" | "directory" | "url"
      "path": "/data/document.pdf",
      "output_prefix": "company_docs",
      "custom_config": {                // Override global config per source
        "max_chunk_size": 1000
      }
    }
  ],
  "output_config": {
    "separate_by_source": true,         // Individual files per source
    "merge_all": false,                 // Combined file with all sources
    "filename_template": "{source_name}_processed"
  },
  "max_workers": 3,                     // Parallel processing
  "continue_on_error": true             // Don't stop on individual failures
}
```

---

## 🔄 Integration Workflows

### Workflow 1: RAG System Integration

```python
# rag_integration.py
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
import requests

class RAGDataLoader:
    def __init__(self, loader_url="http://universal-data-loader:8000"):
        self.loader_url = loader_url
        self.embeddings = OpenAIEmbeddings()
    
    def setup_knowledge_base(self, document_sources):
        """Setup RAG knowledge base from various sources"""
        
        # Process documents through Universal Data Loader
        response = requests.post(f"{self.loader_url}/process/batch", json={
            "sources": document_sources,
            "loader_config": {
                "output_format": "documents",
                "chunking_strategy": "by_title",
                "max_chunk_size": 600,
                "chunk_overlap": 100
            }
        })
        
        job_id = response.json()["job_id"]
        
        # Wait for completion and get documents
        documents = self._wait_for_documents(job_id)
        
        # Create vector store
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            collection_name="company_knowledge"
        )
        
        return vectorstore.as_retriever()

# Usage
rag_loader = RAGDataLoader()
retriever = rag_loader.setup_knowledge_base([
    {"type": "url", "path": "https://docs.company.com"},
    {"type": "directory", "path": "/data/policies/"},
    {"type": "file", "path": "/data/handbook.pdf"}
])
```

### Workflow 2: Training Data Preparation

```python
# training_data_prep.py
import requests
import json

class TrainingDataPreparator:
    def __init__(self, loader_url="http://universal-data-loader:8000"):
        self.loader_url = loader_url
    
    def prepare_training_data(self, sources, output_file):
        """Prepare clean training data from documents"""
        
        response = requests.post(f"{self.loader_url}/process/batch", json={
            "sources": sources,
            "loader_config": {
                "output_format": "text",
                "chunking_strategy": "basic",
                "max_chunk_size": 2000,
                "chunk_overlap": 50,
                "include_metadata": False,
                "min_text_length": 100
            }
        })
        
        # Process and save training data
        documents = self._get_results(response.json()["job_id"])
        
        with open(output_file, 'w') as f:
            for doc in documents:
                f.write(doc['page_content'] + '\n\n')

# Usage
prep = TrainingDataPreparator()
prep.prepare_training_data(
    sources=[{"type": "directory", "path": "/data/training_docs/"}],
    output_file="training_data.txt"
)
```

### Workflow 3: Real-time Document Processing

```python
# realtime_processing.py
import asyncio
import aiohttp

class RealtimeDocumentProcessor:
    def __init__(self, loader_url="http://universal-data-loader:8000"):
        self.loader_url = loader_url
    
    async def process_document_stream(self, document_queue):
        """Process documents as they arrive"""
        async with aiohttp.ClientSession() as session:
            while True:
                document_path = await document_queue.get()
                
                # Submit for processing
                async with session.post(
                    f"{self.loader_url}/process/file",
                    data={'file': open(document_path, 'rb')}
                ) as response:
                    job_data = await response.json()
                
                # Handle result asynchronously
                asyncio.create_task(
                    self._handle_result(session, job_data["job_id"])
                )
```

---

## 🔒 Security & Production Considerations

### Security Configuration

```bash
# Environment variables for production
export DATA_LOADER_API_KEY="your-secure-api-key"
export ALLOWED_ORIGINS="https://your-app.com,https://api.your-app.com"
export MAX_FILE_SIZE="100MB"
export RATE_LIMIT="100/minute"
```

### Production Docker Compose

```yaml
# production-docker-compose.yml
version: '3.8'
services:
  universal-data-loader:
    image: your-registry/universal-data-loader:latest
    restart: always
    environment:
      - NODE_ENV=production
      - RATE_LIMIT=100/minute
    volumes:
      - ./logs:/app/logs
      - ./ssl:/app/ssl:ro
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Monitoring Integration

```python
# monitoring.py
import logging
import prometheus_client

class DataLoaderMonitoring:
    def __init__(self):
        self.processing_time = prometheus_client.Histogram(
            'document_processing_seconds',
            'Time spent processing documents'
        )
        self.document_count = prometheus_client.Counter(
            'documents_processed_total',
            'Total documents processed'
        )
    
    def monitor_processing(self, job_id):
        """Monitor document processing metrics"""
        start_time = time.time()
        
        # Your processing logic here
        
        processing_time = time.time() - start_time
        self.processing_time.observe(processing_time)
        self.document_count.inc()
```

---

## 🧪 Testing & Validation

### Integration Tests

```python
# test_integration.py
import pytest
import requests
import time

class TestDataLoaderIntegration:
    
    @pytest.fixture
    def loader_url(self):
        return "http://localhost:8000"
    
    def test_health_check(self, loader_url):
        """Test service health"""
        response = requests.get(f"{loader_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_url_processing(self, loader_url):
        """Test URL document processing"""
        response = requests.post(f"{loader_url}/process/url", json={
            "url": "https://en.wikipedia.org/wiki/Machine_learning",
            "output_format": "documents"
        })
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Wait for completion
        documents = self._wait_for_completion(loader_url, job_id)
        assert len(documents) > 0
        assert "page_content" in documents[0]
        assert "metadata" in documents[0]
    
    def test_batch_processing(self, loader_url):
        """Test batch processing"""
        response = requests.post(f"{loader_url}/process/batch", json={
            "sources": [
                {"type": "url", "path": "https://example.com"}
            ],
            "loader_config": {"output_format": "documents"}
        })
        
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        documents = self._wait_for_completion(loader_url, job_id)
        assert isinstance(documents, list)

# Run tests
# pytest test_integration.py -v
```

### Load Testing

```bash
# load_test.sh
#!/bin/bash

# Test concurrent processing
for i in {1..10}; do
  curl -X POST "http://localhost:8000/process/url" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://httpbin.org/json"}' &
done

wait
echo "Load test completed"
```

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Container builds successfully
- [ ] Health check responds correctly
- [ ] All environment variables configured
- [ ] Security settings reviewed
- [ ] Resource limits set appropriately

### Production Deployment
- [ ] SSL/TLS certificates configured
- [ ] Load balancer configured
- [ ] Monitoring and logging setup
- [ ] Backup and recovery plan
- [ ] Rate limiting configured

### Post-deployment
- [ ] Integration tests pass
- [ ] Performance metrics within expected range
- [ ] Error rates acceptable
- [ ] Monitoring alerts configured

---

## 🔧 Troubleshooting

### Common Issues

| Issue | Symptom | Solution |
|-------|---------|----------|
| Container won't start | Health check fails | Check logs: `docker logs universal-data-loader` |
| Out of memory | Processing stops | Increase memory limits in docker-compose.yml |
| Slow processing | High response times | Scale horizontally or increase CPU limits |
| File upload fails | 413 error | Increase `client_max_body_size` in nginx.conf |

### Debug Commands

```bash
# Check container logs
docker logs universal-data-loader --tail 100 -f

# Monitor resource usage
docker stats universal-data-loader

# Test API connectivity
curl -v http://localhost:8000/health

# Check processing queue
curl http://localhost:8000/jobs/status
```

---

## 📞 Support & Maintenance

### Health Monitoring Endpoint

```bash
# Automated health check
curl http://localhost:8000/health | jq .
{
  "status": "healthy",
  "timestamp": "2025-06-11T09:36:00.000000",
  "uptime": "running",
  "active_jobs": 2,
  "memory_usage": "512MB",
  "disk_usage": "2GB"
}
```

### Maintenance Operations

```bash
# Clean up old jobs (automated cleanup available)
curl -X DELETE http://localhost:8000/admin/cleanup?older_than=24h

# Restart service
docker-compose restart universal-data-loader

# Update to latest version
docker-compose pull
docker-compose up -d
```

---

This integration guide provides everything needed to successfully deploy and integrate the Universal Data Loader into any LLM application. The containerized service handles all document processing complexity while providing a clean, standardized API for AI applications.