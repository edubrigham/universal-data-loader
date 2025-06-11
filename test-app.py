#!/usr/bin/env python3
"""
Test Application for Universal Data Loader
Demonstrates proper usage of the connector and configuration
"""

import os
import json
from pathlib import Path
from client.python.universal_loader_connector import get_documents, process_url, health_check

def test_microservice_health():
    """Test if the microservice is running"""
    print("🔍 Testing microservice health...")
    try:
        health = health_check()
        print(f"✅ Service Status: {health['status']}")
        return True
    except Exception as e:
        print(f"❌ Service not available: {e}")
        print("💡 Start the service with: docker-compose up -d")
        return False

def check_configuration():
    """Check and display current configuration"""
    print("\n📄 Checking configuration...")
    
    config_file = Path("config/documents.json")
    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        
        print(f"✅ Configuration loaded from: {config_file}")
        print(f"   Microservice URL: {config.get('microservice_url', 'Not set')}")
        print(f"   Sources configured: {len(config.get('sources', []))}")
        
        # Check each source
        for i, source in enumerate(config.get('sources', [])):
            source_type = source.get('type')
            source_path = source.get('path')
            print(f"   [{i+1}] {source_type}: {source_path}")
            
            # Validate source
            if source_type == "directory":
                if not Path(source_path).exists():
                    print(f"      ⚠️ Directory does not exist: {source_path}")
                else:
                    print(f"      ✅ Directory found")
            elif source_type == "file":
                if not Path(source_path).exists():
                    print(f"      ⚠️ File does not exist: {source_path}")
                else:
                    print(f"      ✅ File found")
            elif source_type == "url":
                print(f"      ℹ️ URL (will be validated during processing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def create_sample_data():
    """Create sample data if the configured directory doesn't exist"""
    print("\n📁 Creating sample data...")
    
    # Create data directory
    data_dir = Path("./data/documents")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample documents
    sample_docs = [
        {
            "filename": "company_overview.md",
            "content": """# Company Overview

Our company specializes in AI-powered document processing solutions.

## Mission
Transform how organizations handle document data for AI applications.

## Products
- Universal Data Loader: Microservice for document processing
- AI Integration Tools: Seamless LLM integration capabilities
- Enterprise Solutions: Scalable document processing platforms
"""
        },
        {
            "filename": "technical_docs.md", 
            "content": """# Technical Documentation

## Architecture
The Universal Data Loader uses a microservices architecture with:
- REST API endpoints
- Containerized deployment
- Horizontal scaling capabilities

## Supported Formats
- PDF documents
- Microsoft Word files
- PowerPoint presentations
- Web pages and HTML content
- Plain text files

## Integration
Easy integration with LangChain and other LLM frameworks.
"""
        }
    ]
    
    for doc in sample_docs:
        doc_path = data_dir / doc["filename"]
        doc_path.write_text(doc["content"])
        print(f"   ✅ Created: {doc_path}")
    
    print(f"✅ Sample data created in: {data_dir}")

def test_document_processing():
    """Test document processing using the configured sources"""
    print("\n🔄 Testing document processing...")
    
    try:
        # Try to get documents using the configuration
        documents = get_documents()
        
        if not documents:
            print("⚠️ No documents returned from configuration")
            print("\n💡 Trying alternative: processing a test URL...")
            
            # Try processing a simple URL as fallback
            test_documents = process_url("https://httpbin.org/html")
            
            if test_documents:
                print(f"✅ Successfully processed URL: {len(test_documents)} documents")
                return test_documents
            else:
                print("❌ URL processing also failed")
                return []
        
        print(f"✅ Successfully processed configured sources: {len(documents)} documents")
        
        # Show document details
        print(f"\n📊 Document Analysis:")
        total_content_length = 0
        sources = set()
        
        for i, doc in enumerate(documents[:3]):  # Show first 3
            content = doc.get('page_content', '')
            metadata = doc.get('metadata', {})
            
            total_content_length += len(content)
            if metadata.get('source_path'):
                sources.add(metadata['source_path'])
            
            print(f"\n📖 Document {i+1}:")
            print(f"   📍 Source: {metadata.get('source_path', 'Unknown')}")
            print(f"   📏 Length: {len(content)} characters")
            print(f"   🏷️  Type: {metadata.get('source_type', 'Unknown')}")
            print(f"   📄 Content Preview: {content[:150]}...")
        
        if len(documents) > 3:
            print(f"\n   ... and {len(documents) - 3} more documents")
        
        print(f"\n📊 Summary:")
        print(f"   📁 Sources Processed: {len(sources)}")
        print(f"   📄 Total Documents: {len(documents)}")
        print(f"   📏 Total Content: {total_content_length:,} characters")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error processing documents: {e}")
        return []

def simulate_rag_integration(documents):
    """Simulate how documents would be used in a RAG system"""
    if not documents:
        print("\n⚠️ No documents available for RAG simulation")
        return
    
    print(f"\n🧠 RAG Integration Simulation:")
    print(f"   ✅ Documents received as 'documents' variable")
    print(f"   ✅ LangChain format - ready for embedding")
    print(f"   ✅ Can now create vector store and retriever")
    
    # Simulate what would happen next in a real RAG system
    print(f"\n📝 Next steps would be:")
    print(f"   1. embeddings = OpenAIEmbeddings()")
    print(f"   2. vectorstore = Chroma.from_documents(documents, embeddings)")
    print(f"   3. retriever = vectorstore.as_retriever()")
    print(f"   4. qa_chain = RetrievalQA.from_chain_type(llm, retriever=retriever)")

def main():
    """Main test function"""
    print("🚀 Universal Data Loader - Test Application")
    print("=" * 60)
    
    # Step 1: Check microservice health
    if not test_microservice_health():
        return
    
    # Step 2: Check configuration
    if not check_configuration():
        return
    
    # Step 3: Create sample data if needed
    create_sample_data()
    
    # Step 4: Test document processing
    documents = test_document_processing()
    
    # Step 5: Simulate RAG integration
    simulate_rag_integration(documents)
    
    if documents:
        print(f"\n🎉 Test completed successfully!")
        print(f"   📄 Processed {len(documents)} documents")
        print(f"   🔗 Ready for RAG system integration")
    else:
        print(f"\n⚠️ Test completed with issues")
        print(f"   📋 Check configuration and data sources")
        print(f"   🔧 Verify microservice is processing requests correctly")

if __name__ == "__main__":
    main()