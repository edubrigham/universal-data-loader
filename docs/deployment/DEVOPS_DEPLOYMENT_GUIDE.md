# Universal Data Loader - DevOps Deployment Guide

**Complete guide for DevOps engineers to build, deploy, and manage the Universal Data Loader microservice**

## 🎯 Overview

The Universal Data Loader is a containerized FastAPI microservice that processes documents into LangChain-compatible format. This guide provides step-by-step instructions for DevOps teams to build Docker images and deploy to Azure Container Registry.

### **What You're Deploying:**
- **FastAPI REST API** microservice (Python 3.11)
- **Document processing engine** with OCR capabilities
- **Async job processing** with automatic cleanup
- **Health monitoring** with built-in endpoints
- **Production-ready** with security hardening

---

## 🏗️ Build Requirements

### **System Requirements**
- Docker Engine 20.10+ 
- Docker Compose 2.0+ (for local testing)
- Azure CLI 2.37+ (for Azure deployment)
- 4GB RAM minimum for build process
- 10GB disk space for build artifacts

### **Repository Structure**
```
unstructured/
├── infrastructure/docker/
│   ├── Dockerfile              # Multi-stage production build
│   └── nginx.conf              # Optional reverse proxy config
├── app/                        # FastAPI application source
├── requirements/               # Python dependencies
│   ├── base.txt               # Core dependencies
│   ├── production.txt         # Production-only dependencies
│   └── development.txt        # Development dependencies
├── docker-compose.yml          # Local testing configuration
└── pyproject.toml             # Python project configuration
```

---

## 🐳 Docker Build Process

### **Step 1: Build the Docker Image**

```bash
# Navigate to repository root
cd /path/to/unstructured

# Build the production image
docker build \
  -f infrastructure/docker/Dockerfile \
  -t universal-data-loader:latest \
  --target production \
  .

# Optional: Build with specific version tag
docker build \
  -f infrastructure/docker/Dockerfile \
  -t universal-data-loader:1.0.0 \
  --target production \
  .
```

### **Step 2: Test the Built Image Locally**

```bash
# Run the container for testing
docker run -d \
  --name universal-data-loader-test \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  universal-data-loader:latest

# Wait for startup (30 seconds)
sleep 30

# Test health endpoint
curl -f http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2025-06-19T10:00:00.000000","active_jobs":0}

# Clean up test container
docker stop universal-data-loader-test
docker rm universal-data-loader-test
```

### **Build Arguments and Options**

| Build Argument | Default | Description |
|----------------|---------|-------------|
| `PYTHON_VERSION` | `3.11-slim` | Python base image version |
| `ENVIRONMENT` | `production` | Build environment (development/production) |
| `PORT` | `8000` | Application port |

**Example with build arguments:**
```bash
docker build \
  -f infrastructure/docker/Dockerfile \
  --build-arg PYTHON_VERSION=3.11-slim \
  --build-arg ENVIRONMENT=production \
  -t universal-data-loader:latest \
  .
```

---

## 🚀 Azure Container Registry Deployment

### **Prerequisites**
```bash
# Install Azure CLI (if not already installed)
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Set your subscription
az account set --subscription "your-subscription-id"

# Verify access to your container registry
az acr login --name your-registry-name
```

### **Step 1: Tag Image for Azure Registry**

```bash
# Tag for Azure Container Registry
docker tag universal-data-loader:latest \
  your-registry-name.azurecr.io/universal-data-loader:latest

# Optional: Tag with version
docker tag universal-data-loader:latest \
  your-registry-name.azurecr.io/universal-data-loader:1.0.0
```

### **Step 2: Push to Azure Container Registry**

```bash
# Push latest version
docker push your-registry-name.azurecr.io/universal-data-loader:latest

# Push specific version (if tagged)
docker push your-registry-name.azurecr.io/universal-data-loader:1.0.0

# Verify the push
az acr repository list --name your-registry-name --output table
az acr repository show-tags --name your-registry-name --repository universal-data-loader
```

### **Step 3: Create Service Principal (if needed)**

```bash
# Create service principal for container registry access
az ad sp create-for-rbac \
  --name universal-data-loader-sp \
  --role acrpull \
  --scope /subscriptions/your-subscription-id/resourceGroups/your-rg/providers/Microsoft.ContainerRegistry/registries/your-registry-name

# Note the output:
# {
#   "appId": "service-principal-id",
#   "password": "service-principal-secret",
#   "tenant": "tenant-id"
# }
```

---

## 🔧 Production Configuration

### **Environment Variables**

| Variable | Default | Description | Required |
|----------|---------|-------------|----------|
| `PORT` | `8000` | Service port | No |
| `HOST` | `0.0.0.0` | Service host | No |
| `ENVIRONMENT` | `production` | Runtime environment | No |
| `MAX_WORKERS` | `3` | Concurrent job workers | No |
| `JOB_TIMEOUT` | `300` | Job timeout in seconds | No |
| `MAX_FILE_SIZE` | `104857600` | Max upload size (100MB) | No |
| `LOG_LEVEL` | `INFO` | Logging level | No |
| `CORS_ORIGINS` | `*` | Allowed CORS origins | No |

### **Resource Requirements**

#### **Minimum (Development/Testing)**
- **CPU**: 0.5 cores
- **Memory**: 1GB RAM
- **Storage**: 5GB disk
- **Network**: Standard networking

#### **Recommended (Production)**
- **CPU**: 1-2 cores
- **Memory**: 2-4GB RAM
- **Storage**: 10GB disk
- **Network**: Load balancer compatible

#### **High Load (Enterprise)**
- **CPU**: 2-4 cores
- **Memory**: 4-8GB RAM
- **Storage**: 20GB disk
- **Network**: Multiple replicas behind load balancer

### **Health Check Configuration**

```bash
# Built-in health check (included in Dockerfile)
HEALTHCHECK --interval=30s --timeout=30s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### **Security Configuration**

The container includes these security features:
- ✅ **Non-root user**: Runs as `appuser`
- ✅ **Read-only filesystem**: Application files are immutable
- ✅ **Minimal attack surface**: Based on slim Python image
- ✅ **Input validation**: All inputs sanitized
- ✅ **Rate limiting**: Built-in API rate limiting
- ✅ **Temporary file cleanup**: Automatic cleanup of processed files

---

## 🚢 Container Deployment Options

### **Option 1: Azure Container Instances (Simplest)**

```bash
# Create container instance
az container create \
  --resource-group your-resource-group \
  --name universal-data-loader \
  --image your-registry-name.azurecr.io/universal-data-loader:latest \
  --cpu 1 \
  --memory 2 \
  --ports 8000 \
  --environment-variables \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO \
  --registry-login-server your-registry-name.azurecr.io \
  --registry-username service-principal-id \
  --registry-password service-principal-secret

# Get public IP
az container show \
  --resource-group your-resource-group \
  --name universal-data-loader \
  --query ipAddress.ip \
  --output tsv
```

### **Option 2: Azure App Service (Managed)**

```bash
# Create App Service Plan
az appservice plan create \
  --name universal-data-loader-plan \
  --resource-group your-resource-group \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group your-resource-group \
  --plan universal-data-loader-plan \
  --name universal-data-loader-app \
  --deployment-container-image-name your-registry-name.azurecr.io/universal-data-loader:latest

# Configure container registry
az webapp config container set \
  --name universal-data-loader-app \
  --resource-group your-resource-group \
  --docker-custom-image-name your-registry-name.azurecr.io/universal-data-loader:latest \
  --docker-registry-server-url https://your-registry-name.azurecr.io \
  --docker-registry-server-user service-principal-id \
  --docker-registry-server-password service-principal-secret

# Configure app settings
az webapp config appsettings set \
  --resource-group your-resource-group \
  --name universal-data-loader-app \
  --settings \
    ENVIRONMENT=production \
    PORT=8000 \
    LOG_LEVEL=INFO
```

### **Option 3: Azure Kubernetes Service (Scalable)**

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: universal-data-loader
  labels:
    app: universal-data-loader
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
        image: your-registry-name.azurecr.io/universal-data-loader:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: PORT
          value: "8000"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "1Gi"
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
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
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
  type: LoadBalancer
```

```bash
# Deploy to AKS
kubectl apply -f k8s-deployment.yaml

# Get service endpoint
kubectl get service universal-data-loader-service
```

---

## 📊 Monitoring and Logging

### **Health Monitoring**

```bash
# Health check endpoint
curl http://your-app-url/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-06-19T10:00:00.000000",
  "uptime": "running",
  "active_jobs": 0,
  "memory_usage": "512MB",
  "disk_usage": "2GB"
}
```

### **Application Metrics**

The service exposes these endpoints for monitoring:
- `GET /health` - Service health status
- `GET /api/v1/jobs/status` - Job queue status
- `GET /docs` - OpenAPI documentation

### **Log Configuration**

```bash
# View container logs
docker logs universal-data-loader

# For Azure Container Instances
az container logs \
  --resource-group your-resource-group \
  --name universal-data-loader

# For Azure App Service
az webapp log tail \
  --resource-group your-resource-group \
  --name universal-data-loader-app
```

### **Log Levels and Output**
- **ERROR**: Service failures, processing errors
- **WARNING**: Resource limits, slow processing
- **INFO**: Job status, service lifecycle
- **DEBUG**: Detailed processing information

---

## 🔒 Security Best Practices

### **Container Security**
- ✅ Container runs as non-root user (`appuser`)
- ✅ Minimal base image (Python slim)
- ✅ No sensitive data in environment variables
- ✅ Read-only application filesystem
- ✅ Automatic cleanup of temporary files

### **Network Security**
```bash
# Restrict access to specific IP ranges
az webapp config access-restriction add \
  --resource-group your-resource-group \
  --name universal-data-loader-app \
  --rule-name "office-access" \
  --action Allow \
  --ip-address 203.0.113.0/24 \
  --priority 300
```

### **Registry Security**
```bash
# Enable admin user (not recommended for production)
az acr update --name your-registry-name --admin-enabled false

# Use managed identity instead
az webapp identity assign \
  --resource-group your-resource-group \
  --name universal-data-loader-app

# Grant ACR pull permission to managed identity
az role assignment create \
  --assignee $(az webapp identity show --resource-group your-resource-group --name universal-data-loader-app --query principalId --output tsv) \
  --role acrpull \
  --scope /subscriptions/your-subscription-id/resourceGroups/your-resource-group/providers/Microsoft.ContainerRegistry/registries/your-registry-name
```

---

## 🔄 CI/CD Pipeline Integration

### **Azure DevOps Pipeline (YAML)**

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
    - main
    - develop
  paths:
    include:
    - app/*
    - infrastructure/*
    - requirements/*

variables:
  containerRegistry: 'your-registry-name.azurecr.io'
  imageName: 'universal-data-loader'
  dockerfilePath: 'infrastructure/docker/Dockerfile'

stages:
- stage: Build
  displayName: Build and Push
  jobs:
  - job: Build
    displayName: Build Docker Image
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: Docker@2
      displayName: Build Docker Image
      inputs:
        containerRegistry: '$(containerRegistry)'
        repository: '$(imageName)'
        command: 'build'
        Dockerfile: '$(dockerfilePath)'
        tags: |
          $(Build.BuildId)
          latest

    - task: Docker@2
      displayName: Push Docker Image
      inputs:
        containerRegistry: '$(containerRegistry)'
        repository: '$(imageName)'
        command: 'push'
        tags: |
          $(Build.BuildId)
          latest

- stage: Deploy
  displayName: Deploy to Production
  dependsOn: Build
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: Deploy
    displayName: Deploy to Azure
    environment: 'production'
    pool:
      vmImage: 'ubuntu-latest'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebAppContainer@1
            displayName: Deploy to Azure App Service
            inputs:
              azureSubscription: 'your-service-connection'
              appName: 'universal-data-loader-app'
              imageName: '$(containerRegistry)/$(imageName):$(Build.BuildId)'
```

### **GitHub Actions Workflow**

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  REGISTRY: your-registry-name.azurecr.io
  IMAGE_NAME: universal-data-loader

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Log in to Azure Container Registry
      uses: azure/docker-login@v1
      with:
        login-server: ${{ env.REGISTRY }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}

    - name: Build and push Docker image
      uses: docker/build-push-action@v3
      with:
        context: .
        file: infrastructure/docker/Dockerfile
        push: true
        tags: |
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to Azure App Service
      uses: azure/webapps-deploy@v2
      with:
        app-name: 'universal-data-loader-app'
        publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE }}
        images: '${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}'
```

---

## 🧪 Testing and Validation

### **Container Testing Script**

```bash
#!/bin/bash
# test-deployment.sh

set -e

CONTAINER_NAME="universal-data-loader-test"
IMAGE_NAME="universal-data-loader:latest"
PORT="8000"

echo "🧪 Testing Universal Data Loader deployment..."

# Clean up any existing test container
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

# Start container
echo "🚀 Starting container..."
docker run -d \
  --name $CONTAINER_NAME \
  -p $PORT:$PORT \
  -e ENVIRONMENT=production \
  $IMAGE_NAME

# Wait for startup
echo "⏳ Waiting for service to start..."
sleep 30

# Health check
echo "🩺 Testing health endpoint..."
if curl -f http://localhost:$PORT/health; then
  echo "✅ Health check passed"
else
  echo "❌ Health check failed"
  docker logs $CONTAINER_NAME
  exit 1
fi

# API documentation check
echo "📚 Testing API documentation..."
if curl -f http://localhost:$PORT/docs >/dev/null 2>&1; then
  echo "✅ API documentation accessible"
else
  echo "❌ API documentation not accessible"
fi

# Test basic functionality
echo "🔄 Testing basic functionality..."
RESPONSE=$(curl -s -X POST "http://localhost:$PORT/api/v1/jobs/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://httpbin.org/json"}')

if echo "$RESPONSE" | grep -q "job_id"; then
  echo "✅ Basic functionality test passed"
else
  echo "❌ Basic functionality test failed"
  echo "Response: $RESPONSE"
fi

# Clean up
echo "🔧 Cleaning up..."
docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME

echo "🎉 All tests passed! Container is ready for deployment."
```

### **Automated Testing Integration**

```bash
# Add to your CI/CD pipeline
chmod +x test-deployment.sh
./test-deployment.sh
```

---

## 📞 Support and Troubleshooting

### **Common Issues**

| Issue | Symptom | Solution |
|-------|---------|----------|
| Build fails | Docker build errors | Check Dockerfile syntax, network connectivity |
| Container won't start | Health check fails | Check logs: `docker logs container-name` |
| Out of memory | Container stops unexpectedly | Increase memory limits in deployment |
| Registry push fails | Authentication errors | Verify Azure CLI login and permissions |
| Slow response times | High latency | Scale horizontally or increase CPU/memory |

### **Debug Commands**

```bash
# Check container logs
docker logs universal-data-loader --tail 100 -f

# Exec into running container
docker exec -it universal-data-loader /bin/bash

# Check resource usage
docker stats universal-data-loader

# Test connectivity
curl -v http://localhost:8000/health

# Check registry connectivity
az acr check-health --name your-registry-name
```

### **Performance Tuning**

```bash
# For high-load scenarios, increase workers
docker run -d \
  --name universal-data-loader \
  -p 8000:8000 \
  -e MAX_WORKERS=5 \
  -e JOB_TIMEOUT=600 \
  --memory=4g \
  --cpus=2 \
  your-registry-name.azurecr.io/universal-data-loader:latest
```

---

## 📋 Deployment Checklist

### **Pre-Deployment**
- [ ] Docker Engine installed and configured
- [ ] Azure CLI installed and authenticated
- [ ] Access to Azure Container Registry verified
- [ ] Resource group and container registry created
- [ ] Service principal created (if needed)
- [ ] Network security rules configured

### **Build Process**
- [ ] Repository cloned locally
- [ ] Docker build completed successfully
- [ ] Container tested locally
- [ ] Image tagged for registry
- [ ] Image pushed to Azure Container Registry
- [ ] Registry access verified

### **Deployment**
- [ ] Deployment method chosen (ACI/App Service/AKS)
- [ ] Environment variables configured
- [ ] Resource limits set appropriately
- [ ] Health checks configured
- [ ] Security settings applied
- [ ] Monitoring configured

### **Post-Deployment**
- [ ] Health endpoint responds correctly
- [ ] API documentation accessible
- [ ] Basic functionality tested
- [ ] Performance monitoring active
- [ ] Log aggregation configured
- [ ] Backup and recovery plan documented

---

## 🎯 Quick Reference

### **Essential Commands**
```bash
# Build
docker build -f infrastructure/docker/Dockerfile -t universal-data-loader:latest .

# Test locally
docker run -d --name test -p 8000:8000 universal-data-loader:latest

# Tag for Azure
docker tag universal-data-loader:latest your-registry.azurecr.io/universal-data-loader:latest

# Push to Azure
docker push your-registry.azurecr.io/universal-data-loader:latest

# Health check
curl http://localhost:8000/health
```

### **Important URLs**
- **Health Check**: `http://your-app-url/health`
- **API Documentation**: `http://your-app-url/docs`
- **OpenAPI Spec**: `http://your-app-url/openapi.json`

### **Support Contacts**
- **Repository Issues**: [GitHub Issues](https://github.com/your-org/universal-data-loader/issues)
- **Documentation**: [Integration Guide](../integration/INTEGRATION_GUIDE.md)
- **Container Guide**: [Container README](CONTAINER_README.md)

---

**🚀 Ready to deploy! This microservice will provide plug-and-play document processing for all your RAG applications.**