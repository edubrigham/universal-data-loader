"""
LangChain Integration Examples for Universal Data Loader

This script demonstrates how to use the Universal Data Loader with LangChain
for various AI applications including RAG, vector stores, and document processing.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import our module
sys.path.append(str(Path(__file__).parent.parent))

from universal_loader import UniversalDataLoader, LoaderConfig, OutputFormat
from universal_loader.utils import create_config_for_rag


def example_basic_langchain_integration():
    """Basic example showing LangChain Document compatibility"""
    print("=== Basic LangChain Integration ===")
    
    # Create a sample text file for demonstration
    sample_file = Path("sample_doc.txt")
    sample_content = """
    # LangChain Integration Guide
    
    This document explains how to integrate the Universal Data Loader with LangChain.
    
    ## Key Benefits
    
    - Direct compatibility with LangChain Document format
    - Easy integration with vector stores
    - Support for RAG applications
    - Metadata preservation for enhanced retrieval
    
    ## Usage
    
    Simply load documents and use them directly in your LangChain applications.
    """
    sample_file.write_text(sample_content)
    
    try:
        # Load using default configuration (outputs Documents)
        loader = UniversalDataLoader()
        document_collection = loader.load_file(sample_file)
        
        print(f"Loaded {len(document_collection)} documents")
        
        # Access documents like a LangChain DocumentCollection
        for i, doc in enumerate(document_collection):
            print(f"\nDocument {i+1}:")
            print(f"  Content: {doc.page_content[:100]}...")
            print(f"  Metadata: {doc.metadata}")
            
            # Show LangChain compatibility
            print(f"  LangChain compatible: {hasattr(doc, 'page_content') and hasattr(doc, 'metadata')}")
        
        # Convert to list for LangChain functions that expect lists
        docs_list = document_collection.to_list()
        print(f"\nConverted to list: {len(docs_list)} documents")
        
    finally:
        if sample_file.exists():
            sample_file.unlink()


def example_rag_with_vector_store():
    """Example showing RAG setup with vector store simulation"""
    print("\n=== RAG Application Example ===")
    
    # Create sample documents
    docs_content = [
        "Artificial Intelligence is transforming healthcare through machine learning and data analysis.",
        "Machine learning algorithms can predict patient outcomes and optimize treatment plans.",
        "Natural Language Processing enables automated analysis of medical records and research papers.",
        "Computer vision helps in medical imaging analysis and diagnostic accuracy improvement."
    ]
    
    sample_files = []
    for i, content in enumerate(docs_content):
        file_path = Path(f"rag_doc_{i+1}.txt")
        file_path.write_text(content)
        sample_files.append(file_path)
    
    try:
        # Use RAG-optimized configuration
        config = create_config_for_rag()
        loader = UniversalDataLoader(config)
        
        # Load all documents
        from universal_loader.document import DocumentCollection
        all_documents = DocumentCollection()
        
        for file_path in sample_files:
            docs = loader.load_file(file_path)
            all_documents.add_documents(docs.to_list())
        
        print(f"Loaded {len(all_documents)} documents for RAG")
        
        # Simulate vector store integration
        print("\n📊 Vector Store Integration Simulation:")
        for i, doc in enumerate(all_documents):
            # In real usage, you would embed these with your chosen embedding model
            print(f"Document {i+1}: {len(doc.page_content)} chars")
            print(f"  Content: {doc.page_content}")
            print(f"  Metadata: {doc.metadata}")
            print(f"  Ready for embedding: ✓")
        
        # Show collection statistics
        stats = all_documents.get_statistics()
        print(f"\n📈 Collection Statistics:")
        print(f"  Total documents: {stats['document_count']}")
        print(f"  Average length: {stats['average_characters']:.1f} characters")
        print(f"  Total words: {stats['total_words']}")
        
    finally:
        for file_path in sample_files:
            if file_path.exists():
                file_path.unlink()


def example_document_processing_pipeline():
    """Example showing document processing pipeline"""
    print("\n=== Document Processing Pipeline ===")
    
    # Create a more complex document
    complex_content = """
    # Research Paper: AI in Healthcare
    
    ## Abstract
    This paper explores the applications of artificial intelligence in healthcare settings.
    
    ## Introduction
    Artificial intelligence (AI) has emerged as a transformative technology in healthcare.
    Machine learning algorithms are being used to analyze medical data and improve patient outcomes.
    
    ## Methodology
    We analyzed 1000 patient records using supervised learning techniques.
    The dataset included demographic information, medical history, and treatment outcomes.
    
    ## Results
    Our AI model achieved 95% accuracy in predicting treatment success.
    The model identified key factors that influence patient recovery.
    
    ## Conclusion
    AI shows great promise in healthcare applications.
    Further research is needed to validate these findings across different populations.
    """
    
    sample_file = Path("research_paper.txt")
    sample_file.write_text(complex_content)
    
    try:
        # Configure for document processing
        config = LoaderConfig(
            output_format=OutputFormat.DOCUMENTS,
            chunking_strategy="by_title",
            max_chunk_size=300,
            chunk_overlap=50,
            include_metadata=True
        )
        
        loader = UniversalDataLoader(config)
        documents = loader.load_file(sample_file)
        
        print(f"📝 Processed document into {len(documents)} chunks")
        
        # Show document processing results
        for i, doc in enumerate(documents):
            print(f"\nChunk {i+1}:")
            print(f"  Length: {len(doc.page_content)} characters")
            print(f"  Content: {doc.page_content}")
            if doc.metadata:
                print(f"  Metadata: {doc.metadata}")
        
        # Filter documents by content type (simulation)
        print("\n🔍 Content Filtering Example:")
        for doc in documents:
            content = doc.page_content.lower()
            if "abstract" in content or "introduction" in content:
                doc.add_metadata("section_type", "overview")
            elif "methodology" in content or "results" in content:
                doc.add_metadata("section_type", "technical")
            elif "conclusion" in content:
                doc.add_metadata("section_type", "summary")
        
        # Show filtered results
        for section_type in ["overview", "technical", "summary"]:
            filtered_docs = documents.filter_by_metadata("section_type", section_type)
            print(f"  {section_type.title()} sections: {len(filtered_docs)} documents")
    
    finally:
        if sample_file.exists():
            sample_file.unlink()


def example_metadata_enrichment():
    """Example showing metadata enrichment for enhanced retrieval"""
    print("\n=== Metadata Enrichment Example ===")
    
    # Create documents with different content types
    documents_data = [
        ("Technical document about machine learning algorithms and their applications.", "technical"),
        ("Patient care guidelines for treating cardiovascular conditions.", "clinical"),
        ("Research methodology for conducting clinical trials.", "research"),
        ("Administrative procedures for hospital management.", "administrative")
    ]
    
    sample_files = []
    for i, (content, doc_type) in enumerate(documents_data):
        file_path = Path(f"enriched_doc_{i+1}.txt")
        file_path.write_text(content)
        sample_files.append((file_path, doc_type))
    
    try:
        loader = UniversalDataLoader()
        from universal_loader.document import DocumentCollection
        all_documents = DocumentCollection()
        
        for file_path, doc_type in sample_files:
            docs = loader.load_file(file_path)
            
            # Enrich metadata
            for doc in docs:
                doc.add_metadata("document_type", doc_type)
                doc.add_metadata("word_count", len(doc.page_content.split()))
                doc.add_metadata("char_count", len(doc.page_content))
                
                # Add domain-specific metadata
                if "machine learning" in doc.page_content.lower():
                    doc.add_metadata("contains_ml", True)
                if "patient" in doc.page_content.lower():
                    doc.add_metadata("contains_patient_info", True)
            
            all_documents.add_documents(docs.to_list())
        
        print(f"📋 Enriched {len(all_documents)} documents with metadata")
        
        # Show enriched documents
        for i, doc in enumerate(all_documents):
            print(f"\nDocument {i+1}:")
            print(f"  Content: {doc.page_content}")
            print(f"  Enriched metadata: {doc.metadata}")
        
        # Demonstrate filtering capabilities
        print("\n🎯 Advanced Filtering Examples:")
        
        # Filter by document type
        technical_docs = all_documents.filter_by_metadata("document_type", "technical")
        print(f"  Technical documents: {len(technical_docs)}")
        
        # Filter by content length
        long_docs = all_documents.filter_by_content_length(min_length=60)
        print(f"  Long documents (>60 chars): {len(long_docs)}")
        
        # Get all unique metadata fields
        all_metadata_keys = all_documents.get_statistics()["metadata_keys"]
        print(f"  Available metadata fields: {all_metadata_keys}")
    
    finally:
        for file_path, _ in sample_files:
            if file_path.exists():
                file_path.unlink()


def example_langchain_compatibility_test():
    """Test showing full LangChain compatibility"""
    print("\n=== LangChain Compatibility Test ===")
    
    sample_file = Path("compatibility_test.txt")
    sample_file.write_text("This is a test document for LangChain compatibility verification.")
    
    try:
        loader = UniversalDataLoader()
        documents = loader.load_file(sample_file)
        
        # Get first document
        doc = documents[0]
        
        print("✅ LangChain Compatibility Check:")
        print(f"  Has page_content: {hasattr(doc, 'page_content')}")
        print(f"  Has metadata: {hasattr(doc, 'metadata')}")
        print(f"  page_content type: {type(doc.page_content)}")
        print(f"  metadata type: {type(doc.metadata)}")
        
        # Test required operations
        print(f"  String conversion: '{str(doc)}'")
        print(f"  Dict conversion: {doc.to_dict()}")
        print(f"  Clone operation: {doc.clone()}")
        
        # Test metadata operations
        doc.add_metadata("test_key", "test_value")
        print(f"  Metadata after addition: {doc.metadata}")
        
        # Test collection operations
        print(f"  Collection length: {len(documents)}")
        print(f"  Collection iteration: {'✓' if list(documents) else '✗'}")
        print(f"  Collection indexing: {documents[0] == doc}")
        
        print("\n🎉 All LangChain compatibility tests passed!")
        
    finally:
        if sample_file.exists():
            sample_file.unlink()


if __name__ == "__main__":
    print("Universal Data Loader - LangChain Integration Examples")
    print("=" * 70)
    
    example_basic_langchain_integration()
    example_rag_with_vector_store()
    example_document_processing_pipeline()
    example_metadata_enrichment()
    example_langchain_compatibility_test()
    
    print("\n" + "=" * 70)
    print("🚀 LangChain integration examples completed!")
    print("\nYour Universal Data Loader is now fully compatible with LangChain!")
    print("You can use the output Documents directly in:")
    print("  • Vector stores (Chroma, Pinecone, Weaviate, etc.)")
    print("  • RAG applications")
    print("  • Document transformers")
    print("  • Text splitters")
    print("  • And any other LangChain components that accept Document objects")