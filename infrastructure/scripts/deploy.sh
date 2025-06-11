#!/bin/bash
set -e

echo "🚀 Universal Data Loader - Deployment Script"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT=${1:-"development"}
PORT=${2:-"8000"}
REGISTRY=${3:-""}

echo -e "${BLUE}Environment:${NC} $ENVIRONMENT"
echo -e "${BLUE}Port:${NC} $PORT"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

if ! command_exists docker-compose; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data logs ssl

# Build the container
echo ""
echo "🏗️ Building Universal Data Loader container..."
docker build -t universal-data-loader:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Container built successfully${NC}"
else
    echo -e "${RED}❌ Container build failed${NC}"
    exit 1
fi

# Tag for registry if provided
if [ -n "$REGISTRY" ]; then
    echo ""
    echo "🏷️ Tagging for registry: $REGISTRY"
    docker tag universal-data-loader:latest $REGISTRY/universal-data-loader:latest
    
    echo "📤 Pushing to registry..."
    docker push $REGISTRY/universal-data-loader:latest
fi

# Deploy based on environment
echo ""
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🚀 Starting development deployment..."
    
    # Stop existing containers
    docker-compose down 2>/dev/null || true
    
    # Start the service
    docker-compose up -d universal-data-loader
    
elif [ "$ENVIRONMENT" = "production" ]; then
    echo "🚀 Starting production deployment with reverse proxy..."
    
    # Stop existing containers
    docker-compose --profile production down 2>/dev/null || true
    
    # Start with nginx reverse proxy
    docker-compose --profile production up -d
    
else
    echo -e "${RED}❌ Unknown environment: $ENVIRONMENT${NC}"
    echo "Available environments: development, production"
    exit 1
fi

# Wait for service to be ready
echo ""
echo "⏳ Waiting for service to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:$PORT/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Service is ready!${NC}"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Health check
echo ""
echo "🏥 Performing health check..."
HEALTH_RESPONSE=$(curl -s http://localhost:$PORT/health)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "Response: $HEALTH_RESPONSE"
else
    echo -e "${RED}❌ Health check failed${NC}"
    echo "Checking logs..."
    docker logs universal-data-loader --tail 20
    exit 1
fi

# Service information
echo ""
echo "🎉 Deployment completed successfully!"
echo "======================================"
echo -e "${GREEN}Service URL:${NC} http://localhost:$PORT"
echo -e "${GREEN}API Documentation:${NC} http://localhost:$PORT/docs"
echo -e "${GREEN}Health Check:${NC} http://localhost:$PORT/health"
echo ""
echo "📋 Quick test commands:"
echo "curl http://localhost:$PORT/health"
echo "curl -X POST 'http://localhost:$PORT/process/url' -H 'Content-Type: application/json' -d '{\"url\": \"https://httpbin.org/json\"}'"
echo ""
echo "📊 Monitor logs: docker logs universal-data-loader -f"
echo "🔄 Restart service: docker-compose restart universal-data-loader"
echo "🛑 Stop service: docker-compose down"

if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "🔒 Production notes:"
    echo "• Service is running behind nginx reverse proxy"
    echo "• Rate limiting is enabled (10 requests/second)"
    echo "• Max file upload size: 100MB"
    echo "• SSL certificates should be placed in ./ssl/ directory"
fi

echo ""
echo -e "${YELLOW}🔧 Integration guide: INTEGRATION_GUIDE.md${NC}"
echo -e "${YELLOW}📖 API documentation: http://localhost:$PORT/docs${NC}"