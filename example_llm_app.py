#!/usr/bin/env python3
"""
Example LLM Application using Universal Data Loader
Demonstrates the standard integration pattern
"""

# STANDARD INTEGRATION - Just these 2 files needed:
# 1. Copy universal_loader_connector.py to your project root  
# 2. Create config/documents.json with your sources

from universal_loader_connector import get_documents, process_url, process_file


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
    """Example: Analyzing a single document"""
    print("\n📄 Analyzing single document...")
    
    # Process a single file or URL
    documents = process_file("./examples/test_data/20250412000218756416-00163124-Fiscaal_attest-2024.pdf")
    
    print(f"✅ Analyzed document: {len(documents)} sections")
    
    # Example analysis
    for i, doc in enumerate(documents[:3]):  # Show first 3 sections
        print(f"\n📋 Section {i+1}:")
        print(f"   Content: {doc['page_content'][:100]}...")
        print(f"   Source: {doc['metadata'].get('filename', 'Unknown')}")
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
    """Example: Real-time document processing"""
    print("\n⚡ Real-time processing example...")
    
    # Process new content as it arrives
    new_url = "https://httpbin.org/json"
    documents = process_url(new_url)
    
    print(f"✅ Processed new content: {len(documents)} documents")
    
    # Process and analyze immediately
    for doc in documents:
        content = doc['page_content']
        metadata = doc['metadata']
        
        # Your analysis logic here
        print(f"📊 Analyzed content from: {metadata.get('url', 'Unknown')}")
        print(f"   Length: {len(content)} characters")
    
    return documents


def main():
    """Main application demonstrating different use cases"""
    print("🚀 Example LLM Application with Universal Data Loader")
    print("=" * 70)
    
    try:
        # 1. Build RAG system from configured sources
        rag_documents = build_rag_system()
        
        # 2. Analyze individual documents
        analysis_documents = analyze_single_document()
        
        # 3. Process training data
        # training_documents = process_training_data()
        
        # 4. Real-time processing
        realtime_documents = real_time_processing()
        
        print("\n🎉 All examples completed successfully!")
        print(f"📊 Total documents processed: {len(rag_documents + analysis_documents + realtime_documents)}")
        
    except FileNotFoundError as e:
        print(f"⚠️ Configuration missing: {e}")
        print("\n💡 Quick setup:")
        print("1. Copy config/documents.json.template to config/documents.json")
        print("2. Edit config/documents.json with your sources")
        print("3. Run this script again")
        
    except ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Start the Universal Data Loader:")
        print("   docker-compose up -d")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()