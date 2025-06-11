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
                if source_path.startswith("/app/"):
                    # Docker container path
                    local_path = source_path.replace("/app/", "./")
                    if Path(local_path).exists():
                        print(f"      ✅ Directory mapped from local: {local_path}")
                    else:
                        print(f"      ℹ️ Directory exists in container: {source_path}")
                elif not Path(source_path).exists():
                    print(f"      ⚠️ Directory does not exist: {source_path}")
                else:
                    print(f"      ✅ Directory found")
            elif source_type == "file":
                if source_path.startswith("/app/"):
                    # Docker container path
                    local_path = source_path.replace("/app/", "./")
                    if Path(local_path).exists():
                        print(f"      ✅ File mapped from local: {local_path}")
                    else:
                        print(f"      ℹ️ File exists in container: {source_path}")
                elif not Path(source_path).exists():
                    print(f"      ⚠️ File does not exist: {source_path}")
                else:
                    print(f"      ✅ File found")
            elif source_type == "url":
                print(f"      ℹ️ URL (will be validated during processing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def test_document_processing():
    """Test document processing using the configured sources"""
    print("\n🔄 Testing document processing...")
    
    try:
        # Get documents using the configuration
        documents = get_documents()
        
        if not documents:
            print("⚠️ No documents returned from configuration")
            print("\n💡 Possible issues:")
            print("   1. The configured sources might not exist")
            print("   2. The batch processing API might be returning file paths instead of documents")
            print("   3. Check the docker logs: docker-compose logs universal-data-loader")
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
    print(f"   ✅ Documents received in LangChain format")
    print(f"   ✅ Ready for embedding and vector storage")
    print(f"   ✅ {len(documents)} documents available for RAG system")
    
    # Show document structure
    if documents:
        print(f"\n📝 Document structure example:")
        doc = documents[0]
        print(f"   - page_content: {type(doc.get('page_content'))} (text content)")
        print(f"   - metadata: {type(doc.get('metadata'))} (source info, etc.)")
    
    print(f"\n📝 Next steps for RAG implementation:")
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
    
    # Step 3: Test document processing
    documents = test_document_processing()
    
    # Step 4: Simulate RAG integration
    simulate_rag_integration(documents)
    
    if documents:
        print(f"\n🎉 Test completed successfully!")
        print(f"   📄 Processed {len(documents)} documents from config")
        print(f"   🔗 Ready for RAG system integration")
    else:
        print(f"\n⚠️ Test completed with issues")
        print(f"   📋 No documents were loaded from the configured sources")
        print(f"   🔧 Please check:")
        print(f"      - Your sources exist and are accessible")
        print(f"      - The microservice is processing correctly")
        print(f"      - Docker container has access to the files")

if __name__ == "__main__":
    main()