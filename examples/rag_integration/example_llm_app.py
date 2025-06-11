#!/usr/bin/env python3
"""
Example LLM Application using Universal Data Loader Connector
This simulates a RAG application that processes documents from a directory
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import the connector
sys.path.insert(0, str(Path(__file__).parent))

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "client" / "python"))

from universal_loader_connector import get_documents, health_check, process_url, process_file


def simulate_rag_application():
    """Simulate a RAG application processing documents from a directory"""
    print("🤖 RAG Application - Processing Documents from Directory")
    print("-" * 60)
    
    try:
        # Step 1: Check if microservice is running
        print("🔍 Checking Universal Data Loader service...")
        health = health_check()
        print(f"✅ Service Status: {health['status']}")
        
        # Step 2: Process documents from config/documents.json 
        print("\n📄 Processing documents using batch connector...")
        print("📁 Reading sources from config/documents.json...")
        
        # This calls the microservice to process all sources in the config
        documents = get_documents()
        
        # Step 3: Display results as a RAG application would use them
        print(f"\n✅ Successfully received {len(documents)} documents from microservice")
        
        if documents:
            print("\n📊 RAG Application Analysis:")
            total_content_length = 0
            sources = set()
            
            for i, doc in enumerate(documents[:3]):  # Show first 3 documents
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
            
            print(f"\n📊 Summary for RAG System:")
            print(f"   📁 Sources Processed: {len(sources)}")
            print(f"   📄 Total Documents: {len(documents)}")
            print(f"   📏 Total Content: {total_content_length:,} characters")
            
            # This is what a real RAG application would do next:
            print(f"\n🧠 Ready for RAG Integration!")
            print(f"   ✅ Documents received as 'documents' variable")
            print(f"   ✅ LangChain format - ready for embedding")
            print(f"   ✅ Can now create vector store and retriever")
            
            return documents
        
        else:
            print("⚠️ No documents were returned from microservice")
            return []
        
    except Exception as e:
        print(f"❌ Error in RAG application: {e}")
        import traceback
        traceback.print_exc()
        return []


def build_rag_system():
    """Example: Building a RAG system with the connector"""
    print("🧠 Building RAG Knowledge Base...")
    
    # This automatically reads config/documents.json and processes all sources
    documents = get_documents()
    
    print(f"✅ Loaded {len(documents)} documents for RAG")
    
    # Now use with any vector database (Chroma, Pinecone, etc.)
    # Example with Chroma:
    # from langchain_chroma import Chroma
    # vectorstore = Chroma.from_documents(documents)
    # retriever = vectorstore.as_retriever()
    
    return documents


def analyze_single_document():
    """Example: Analyzing documents from config"""
    print("\n📄 Analyzing documents from config...")
    
    # Load documents from config/documents.json
    documents = get_documents()
    
    print(f"✅ Loaded {len(documents)} documents from configuration")
    
    # Example analysis - show first few documents
    for i, doc in enumerate(documents[:3]):  # Show first 3 sections
        print(f"\n📋 Document {i+1}:")
        print(f"   Content: {doc['page_content'][:100]}...")
        print(f"   Source: {doc['metadata'].get('filename', doc['metadata'].get('url', 'Unknown'))}")
        print(f"   Page: {doc['metadata'].get('page_number', 'N/A')}")
    
    return documents


def process_training_data():
    """Example: Processing training data"""
    print("\n🏋️ Processing training data...")
    
    # Use specific config for training data (text format, no metadata)
    documents = get_documents("training_data")
    
    print(f"✅ Prepared training data: {len(documents)} text chunks")
    
    # Save as training file
    with open("model_training_data.txt", "w") as f:
        for doc in documents:
            f.write(doc['page_content'] + '\n\n')
    
    print("💾 Saved to model_training_data.txt")
    return documents


def real_time_processing():
    """Example: Real-time processing from configured sources"""
    print("\n⚡ Real-time processing example...")
    
    # Process documents from config - same as other functions
    documents = get_documents()
    
    print(f"✅ Processed content from config: {len(documents)} documents")
    
    # Process and analyze immediately
    for i, doc in enumerate(documents[:2]):  # Show first 2 sections
        content = doc['page_content']
        metadata = doc['metadata']
        
        # Your analysis logic here
        print(f"📊 Document section {i+1}:")
        print(f"   Source: {metadata.get('filename', 'Unknown')}")
        print(f"   Page: {metadata.get('page_number', 'N/A')}")
        print(f"   Length: {len(content)} characters")
        print(f"   Preview: {content[:100]}...")
    
    return documents


def main():
    """Main application demonstrating the critical fix"""
    print("🚀 Testing Universal Data Loader - RAG Application Integration")
    print("=" * 70)
    
    try:
        # This is the key test: RAG application gets documents directly as a variable
        print("🎯 CRITICAL TEST: RAG Application receiving documents as variable")
        documents = simulate_rag_application()
        
        if documents:
            print(f"\n✅ SUCCESS: RAG application received {len(documents)} documents as variable")
            print("✅ Documents are ready for immediate consumption by RAG system")
            print("✅ No file downloads needed - documents returned directly from microservice")
        else:
            print("❌ FAILED: No documents returned - need to check configuration")
            
        # Additional examples
        print(f"\n📚 Additional Integration Examples:")
        
        # 1. Build RAG system from configured sources  
        rag_documents = build_rag_system()
        
        # 2. Analyze individual documents
        analysis_documents = analyze_single_document()
        
        print("\n🎉 All integration tests completed!")
        
    except FileNotFoundError as e:
        print(f"⚠️ Configuration missing: {e}")
        print("\n💡 Quick setup:")
        print("1. Edit config/documents.json with your document sources")
        print("2. Make sure paths and URLs are valid")  
        print("3. Run this script again")
        
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Start the Universal Data Loader:")
        print("   docker-compose up -d")
        print("   Wait for health check: curl http://localhost:8000/health")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()