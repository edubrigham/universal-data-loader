"""
Directory Processing Examples for Universal Data Loader

This script demonstrates how to process entire directories containing
multiple file types and use the results in LangChain applications.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import our module
sys.path.append(str(Path(__file__).parent.parent))

from universal_loader import UniversalDataLoader, LoaderConfig, OutputFormat
from universal_loader.utils import create_config_for_rag


def setup_test_directory():
    """Create a test directory with multiple file types"""
    test_dir = Path("test_documents")
    test_dir.mkdir(exist_ok=True)
    
    # Create different file types
    files_created = []
    
    # Text file
    txt_file = test_dir / "research_notes.txt"
    txt_file.write_text("""
# Research Notes on AI in Healthcare

## Key Findings
- Machine learning improves diagnostic accuracy by 25%
- Natural language processing reduces documentation time
- Computer vision assists in medical imaging analysis

## Next Steps
- Implement pilot program in cardiology department
- Train staff on new AI tools
- Evaluate patient outcomes
""")
    files_created.append(txt_file)
    
    # Markdown file  
    md_file = test_dir / "project_summary.md"
    md_file.write_text("""
# AI Healthcare Project Summary

## Objectives
1. Improve patient care through AI assistance
2. Reduce physician workload and burnout
3. Enhance diagnostic accuracy

## Technology Stack
- **Machine Learning**: TensorFlow, PyTorch
- **NLP**: Transformers, spaCy
- **Computer Vision**: OpenCV, PIL

## Timeline
- Q1: Requirements gathering
- Q2: Prototype development  
- Q3: Pilot implementation
- Q4: Full deployment
""")
    files_created.append(md_file)
    
    # HTML file
    html_file = test_dir / "meeting_minutes.html"
    html_file.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>AI Project Meeting Minutes</title>
</head>
<body>
    <h1>Weekly AI Project Meeting</h1>
    
    <h2>Attendees</h2>
    <ul>
        <li>Dr. Smith - Chief Medical Officer</li>
        <li>Jane Doe - AI Research Lead</li>
        <li>Bob Johnson - IT Director</li>
    </ul>
    
    <h2>Discussion Points</h2>
    <p>The team discussed the progress on the AI healthcare initiative. 
    Key achievements include successful model training and initial testing results.</p>
    
    <h2>Action Items</h2>
    <ol>
        <li>Complete ethics review by next week</li>
        <li>Schedule user training sessions</li>
        <li>Prepare demonstration for board meeting</li>
    </ol>
</body>
</html>
""")
    files_created.append(html_file)
    
    # CSV file
    csv_file = test_dir / "patient_data.csv"
    csv_file.write_text("""
Patient_ID,Age,Diagnosis,Treatment,Outcome
P001,65,Diabetes,Medication,Improved
P002,72,Hypertension,Lifestyle,Stable
P003,58,Heart Disease,Surgery,Recovered
P004,45,Asthma,Inhaler,Controlled
P005,67,Arthritis,Physical Therapy,Improved
""")
    files_created.append(csv_file)
    
    return test_dir, files_created


def example_basic_directory_processing():
    """Basic example of processing an entire directory"""
    print("=== Basic Directory Processing ===")
    
    test_dir, files_created = setup_test_directory()
    
    try:
        # Process entire directory with default settings
        loader = UniversalDataLoader()
        documents = loader.load_directory(test_dir)
        
        print(f"📁 Processed directory: {test_dir}")
        print(f"📄 Files found: {len(files_created)} files")
        print(f"📋 Documents created: {len(documents)} documents")
        
        # Show documents by source file
        by_file = {}
        for doc in documents:
            source_file = doc.get_metadata('source_file', 'Unknown')
            file_name = Path(source_file).name
            if file_name not in by_file:
                by_file[file_name] = 0
            by_file[file_name] += 1
        
        print(f"\n📊 Documents by file:")
        for file_name, count in by_file.items():
            print(f"  {file_name}: {count} documents")
        
        # Show collection statistics
        stats = documents.get_statistics()
        print(f"\n📈 Collection Statistics:")
        print(f"  Total documents: {stats['document_count']}")
        print(f"  Total words: {stats['total_words']:,}")
        print(f"  Average length: {stats['average_characters']:.1f} chars")
        print(f"  Metadata fields: {len(stats['metadata_keys'])} fields")
        
    finally:
        # Cleanup
        for file_path in files_created:
            if file_path.exists():
                file_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def example_directory_with_filtering():
    """Example showing how to filter documents from directory processing"""
    print("\n=== Directory Processing with Filtering ===")
    
    test_dir, files_created = setup_test_directory()
    
    try:
        # Process directory with RAG configuration
        config = create_config_for_rag()
        loader = UniversalDataLoader(config)
        documents = loader.load_directory(test_dir)
        
        print(f"📁 Processed {len(documents)} documents with RAG optimization")
        
        # Filter by file type
        print(f"\n🔍 Filtering by file type:")
        
        # Handle both DocumentCollection and list formats
        if hasattr(documents, 'get_metadata_values'):
            file_types = documents.get_metadata_values('source_file')
        else:
            # Fallback for list format
            file_types = []
            for doc in documents:
                if hasattr(doc, 'get_metadata'):
                    source_file = doc.get_metadata('source_file')
                    if source_file:
                        file_types.append(source_file)
                        
        for source_file in set(file_types):
            if source_file and source_file != 'Unknown':
                file_ext = Path(source_file).suffix
                file_docs = []
                for doc in documents:
                    if doc.get_metadata('source_file') == source_file:
                        file_docs.append(doc)
                
                print(f"  {file_ext} files: {len(file_docs)} documents")
                
                # Show content preview for first document of each type
                if file_docs:
                    preview = file_docs[0].page_content[:100].replace('\n', ' ')
                    print(f"    Preview: {preview}...")
        
        # Filter by content length
        print(f"\n📏 Filtering by content length:")
        short_docs = documents.filter_by_content_length(max_length=100)
        medium_docs = documents.filter_by_content_length(min_length=100, max_length=300)
        long_docs = documents.filter_by_content_length(min_length=300)
        
        print(f"  Short documents (<100 chars): {len(short_docs)}")
        print(f"  Medium documents (100-300 chars): {len(medium_docs)}")
        print(f"  Long documents (>300 chars): {len(long_docs)}")
        
        # Filter by element type
        print(f"\n🏷️ Filtering by element type:")
        if hasattr(documents, 'get_metadata_values'):
            element_types = documents.get_metadata_values('element_type')
            for element_type in set(element_types):
                if element_type:
                    type_docs = documents.filter_by_metadata('element_type', element_type)
                    print(f"  {element_type}: {len(type_docs)} documents")
        else:
            # Fallback for list format
            element_types = {}
            for doc in documents:
                if hasattr(doc, 'get_metadata'):
                    element_type = doc.get_metadata('element_type')
                    if element_type:
                        element_types[element_type] = element_types.get(element_type, 0) + 1
            
            for element_type, count in element_types.items():
                print(f"  {element_type}: {count} documents")
        
    finally:
        # Cleanup
        for file_path in files_created:
            if file_path.exists():
                file_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def example_directory_rag_pipeline():
    """Complete RAG pipeline example using directory processing"""
    print("\n=== Directory RAG Pipeline Example ===")
    
    test_dir, files_created = setup_test_directory()
    
    try:
        # Step 1: Process directory with RAG-optimized settings
        config = LoaderConfig(
            output_format=OutputFormat.DOCUMENTS,
            chunking_strategy="by_title",
            max_chunk_size=200,  # Smaller chunks for better retrieval
            chunk_overlap=50,
            include_metadata=True,
            min_text_length=30  # Filter out very short content
        )
        
        loader = UniversalDataLoader(config)
        documents = loader.load_directory(test_dir, recursive=True)
        
        print(f"🔄 Step 1: Processed directory into {len(documents)} chunks")
        
        # Step 2: Enrich metadata for better retrieval
        print(f"🔄 Step 2: Enriching metadata...")
        
        for doc in documents:
            # Add document type classification
            content_lower = doc.page_content.lower()
            
            if any(word in content_lower for word in ['objective', 'goal', 'plan']):
                doc.add_metadata('content_type', 'planning')
            elif any(word in content_lower for word in ['finding', 'result', 'data']):
                doc.add_metadata('content_type', 'research')
            elif any(word in content_lower for word in ['meeting', 'attendee', 'action']):
                doc.add_metadata('content_type', 'meeting')
            elif any(word in content_lower for word in ['patient', 'diagnosis', 'treatment']):
                doc.add_metadata('content_type', 'clinical')
            else:
                doc.add_metadata('content_type', 'general')
            
            # Add readiness score (simulation)
            word_count = len(doc.page_content.split())
            if word_count > 20:
                doc.add_metadata('retrieval_score', 'high')
            elif word_count > 10:
                doc.add_metadata('retrieval_score', 'medium')
            else:
                doc.add_metadata('retrieval_score', 'low')
        
        # Step 3: Demonstrate retrieval simulation
        print(f"🔄 Step 3: Simulating retrieval scenarios...")
        
        # Simulate different query types
        queries = [
            ("AI healthcare objectives", "planning"),
            ("Patient treatment outcomes", "clinical"), 
            ("Meeting action items", "meeting"),
            ("Research findings", "research")
        ]
        
        for query, expected_type in queries:
            relevant_docs = documents.filter_by_metadata('content_type', expected_type)
            high_quality = len([d for d in relevant_docs if d.get_metadata('retrieval_score') == 'high'])
            
            print(f"  Query: '{query}'")
            print(f"    Found {len(relevant_docs)} relevant documents")
            print(f"    High-quality chunks: {high_quality}")
            
            # Show best match
            if relevant_docs:
                best_doc = None
                for doc in relevant_docs:
                    if doc.get_metadata('retrieval_score') == 'high':
                        best_doc = doc
                        break
                
                if not best_doc and relevant_docs:
                    best_doc = relevant_docs[0]
                
                if best_doc:
                    preview = best_doc.page_content[:80].replace('\n', ' ')
                    print(f"    Best match: {preview}...")
        
        # Step 4: Save processed documents for vector store
        output_file = "rag_processed_documents.json"
        loader.save_output(documents, output_file)
        print(f"🔄 Step 4: Saved {len(documents)} processed documents to {output_file}")
        
        # Show final statistics
        stats = documents.get_statistics()
        print(f"\n📊 Final RAG Pipeline Results:")
        print(f"  Total documents: {stats['document_count']}")
        print(f"  Ready for embedding: ✓")
        print(f"  Metadata enriched: ✓")
        print(f"  Optimized for retrieval: ✓")
        
        # Cleanup output file
        if Path(output_file).exists():
            Path(output_file).unlink()
        
    finally:
        # Cleanup
        for file_path in files_created:
            if file_path.exists():
                file_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


def example_cli_directory_processing():
    """Demonstrate CLI directory processing"""
    print("\n=== CLI Directory Processing Example ===")
    
    test_dir, files_created = setup_test_directory()
    
    try:
        print(f"📁 Created test directory: {test_dir}")
        print(f"📄 Files: {[f.name for f in files_created]}")
        
        print(f"\n💻 CLI Commands for directory processing:")
        print(f"# Basic directory processing")
        print(f"python uloader.py {test_dir}/ -o directory_output.json")
        
        print(f"\n# With RAG optimization and statistics") 
        print(f"python uloader.py {test_dir}/ -o rag_output.json --preset rag --stats")
        
        print(f"\n# Recursive processing with custom settings")
        print(f"python uloader.py {test_dir}/ -o custom_output.json \\")
        print(f"  --format documents \\")
        print(f"  --chunk-size 300 \\")
        print(f"  --chunk-overlap 50 \\")
        print(f"  --recursive \\")
        print(f"  --verbose")
        
        print(f"\n# Different output formats")
        print(f"python uloader.py {test_dir}/ -o text_output.txt --format text")
        print(f"python uloader.py {test_dir}/ -o json_output.json --format json")
        
        print(f"\n✨ All these commands will:")
        print(f"  • Process all supported files in the directory")
        print(f"  • Return LangChain-compatible Documents")
        print(f"  • Preserve metadata from each source file")
        print(f"  • Apply the specified processing settings")
        print(f"  • Work directly with vector stores and RAG systems")
        
    finally:
        # Cleanup
        for file_path in files_created:
            if file_path.exists():
                file_path.unlink()
        if test_dir.exists():
            test_dir.rmdir()


if __name__ == "__main__":
    print("Universal Data Loader - Directory Processing Examples")
    print("=" * 70)
    
    example_basic_directory_processing()
    example_directory_with_filtering()
    example_directory_rag_pipeline()
    example_cli_directory_processing()
    
    print("\n" + "=" * 70)
    print("🎉 Directory processing examples completed!")
    print("\n🚀 Your Universal Data Loader can process:")
    print("  📁 Entire directories with mixed file types")
    print("  🔄 Recursive subdirectory processing") 
    print("  🎯 Automatic file type detection")
    print("  📋 Batch document generation for LangChain")
    print("  🏷️ Rich metadata preservation per source file")
    print("  🔍 Advanced filtering and collection operations")
    print("\n💡 Perfect for building knowledge bases from document collections!")