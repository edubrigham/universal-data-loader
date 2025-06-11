"""
Batch Processing Examples for Universal Data Loader

This script demonstrates various batch processing capabilities including:
- Processing multiple URLs
- Processing multiple directories 
- Using configuration files
- Custom batch configurations
"""

import sys
import json
from pathlib import Path

# Add the parent directory to the path to import our module
sys.path.append(str(Path(__file__).parent.parent))

from universal_loader import (
    BatchProcessor, 
    BatchConfig, 
    InputSource, 
    InputType, 
    OutputConfig,
    LoaderConfig,
    OutputFormat
)
from universal_loader.batch_processor import (
    process_urls_batch,
    process_directories_batch
)
from universal_loader.batch_config import (
    create_simple_batch_config,
    create_url_batch_config,
    create_directory_batch_config
)


def example_simple_batch_urls():
    """Example: Quick batch processing of multiple URLs"""
    print("=== Simple URL Batch Processing ===")
    
    urls = [
        "https://en.wikipedia.org/wiki/Artificial_intelligence",
        "https://en.wikipedia.org/wiki/Machine_learning",
        "https://en.wikipedia.org/wiki/Deep_learning"
    ]
    
    try:
        print(f"🌐 Processing {len(urls)} URLs...")
        
        # Quick batch processing
        summary = process_urls_batch(
            urls=urls,
            output_dir="url_batch_demo",
            max_workers=2,
            verbose=True
        )
        
        print(f"✅ Batch completed!")
        print(f"📊 Processed {summary['successful_sources']}/{summary['total_sources']} URLs")
        print(f"📋 Created {summary['total_documents']} documents")
        print(f"📁 Output files: {len(summary['output_files'])}")
        
        # Clean up
        output_dir = Path("url_batch_demo")
        if output_dir.exists():
            for file in output_dir.glob("*"):
                file.unlink()
            output_dir.rmdir()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_custom_batch_config():
    """Example: Custom batch configuration with mixed sources"""
    print("\n=== Custom Batch Configuration ===")
    
    # Create test files
    test_dir = Path("batch_test_docs")
    test_dir.mkdir(exist_ok=True)
    
    test_files = []
    try:
        # Create sample files
        file1 = test_dir / "doc1.txt"
        file1.write_text("This is the first test document for batch processing.")
        test_files.append(file1)
        
        file2 = test_dir / "doc2.md"
        file2.write_text("# Second Document\n\nThis is a markdown document for testing.")
        test_files.append(file2)
        
        # Create custom batch configuration
        config = BatchConfig(
            loader_config=LoaderConfig(
                output_format=OutputFormat.DOCUMENTS,
                chunking_strategy="basic",
                max_chunk_size=500,
                chunk_overlap=50,
                include_metadata=True
            ),
            sources=[
                InputSource(
                    type=InputType.FILE,
                    path=str(file1),
                    output_prefix="test_doc1"
                ),
                InputSource(
                    type=InputType.FILE, 
                    path=str(file2),
                    output_prefix="test_doc2"
                ),
                InputSource(
                    type=InputType.DIRECTORY,
                    path=str(test_dir),
                    recursive=False,
                    include_patterns=["*.txt", "*.md"],
                    output_prefix="test_dir"
                )
            ],
            output=OutputConfig(
                base_path="custom_batch_output",
                separate_by_source=True,
                merge_all=True,
                filename_template="{source_name}_processed"
            ),
            max_workers=1,
            verbose=True,
            add_batch_metadata=True
        )
        
        print(f"📋 Processing custom batch with {len(config.sources)} sources...")
        
        # Process batch
        processor = BatchProcessor(config)
        summary = processor.process_all()
        
        print(f"✅ Custom batch completed!")
        print(f"📊 Results: {summary['successful_sources']}/{summary['total_sources']} sources")
        print(f"📋 Documents: {summary['total_documents']}")
        print(f"🔤 Words: {summary['total_words']}")
        
        # Show output files
        print(f"\n📁 Generated files:")
        for source, output_file in summary['output_files'].items():
            file_size = Path(output_file).stat().st_size if Path(output_file).exists() else 0
            print(f"  {source}: {output_file} ({file_size} bytes)")
        
    finally:
        # Clean up
        for file in test_files:
            if file.exists():
                file.unlink()
        if test_dir.exists():
            test_dir.rmdir()
        
        # Clean up output
        output_dir = Path("custom_batch_output")
        if output_dir.exists():
            for file in output_dir.glob("*"):
                file.unlink()
            output_dir.rmdir()


def example_config_file_batch():
    """Example: Using configuration files for batch processing"""
    print("\n=== Configuration File Batch Processing ===")
    
    # Create a configuration file
    config_data = {
        "loader_config": {
            "output_format": "documents",
            "chunking_strategy": "basic",
            "max_chunk_size": 200,
            "include_metadata": True
        },
        "sources": [
            {
                "type": "file",
                "path": "examples/test_data/20250412000218756416-00163124-Fiscaal_attest-2024.pdf",
                "output_prefix": "test_pdf"
            }
        ],
        "output": {
            "base_path": "config_batch_output",
            "separate_by_source": True,
            "merge_all": False,
            "filename_template": "{source_name}_from_config"
        },
        "max_workers": 1,
        "verbose": True
    }
    
    config_file = Path("batch_config_demo.json")
    
    try:
        # Save configuration
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"📄 Created config file: {config_file}")
        
        # Load and process from config file
        from universal_loader.batch_processor import process_batch_from_config_file
        
        print(f"📋 Processing from configuration file...")
        summary = process_batch_from_config_file(config_file)
        
        print(f"✅ Config file batch completed!")
        print(f"📊 Batch ID: {summary['batch_id']}")
        print(f"📋 Documents: {summary['total_documents']}")
        print(f"📁 Output: {list(summary['output_files'].values())[0]}")
        
    finally:
        # Clean up
        if config_file.exists():
            config_file.unlink()
        
        output_dir = Path("config_batch_output")
        if output_dir.exists():
            for file in output_dir.glob("*"):
                file.unlink()
            output_dir.rmdir()


def example_advanced_filtering():
    """Example: Advanced filtering with patterns"""
    print("\n=== Advanced Filtering Example ===")
    
    # Create test directory with various files
    test_dir = Path("filter_test_docs")
    test_dir.mkdir(exist_ok=True)
    
    test_files = []
    try:
        # Create files with different extensions
        files_to_create = [
            ("important_doc.txt", "This is an important document."),
            ("draft_notes.txt", "These are draft notes."),
            ("final_report.md", "# Final Report\n\nThis is the final report."),
            ("temp_file.tmp", "Temporary file content."),
            ("backup_data.bak", "Backup file content.")
        ]
        
        for filename, content in files_to_create:
            file_path = test_dir / filename
            file_path.write_text(content)
            test_files.append(file_path)
        
        # Create batch config with filtering
        config = BatchConfig(
            loader_config=LoaderConfig(
                output_format=OutputFormat.DOCUMENTS,
                include_metadata=True
            ),
            sources=[
                InputSource(
                    type=InputType.DIRECTORY,
                    path=str(test_dir),
                    recursive=True,
                    include_patterns=["*.txt", "*.md"],  # Only text and markdown
                    exclude_patterns=["*draft*", "*temp*"],  # Exclude drafts and temp files
                    output_prefix="filtered_docs"
                )
            ],
            output=OutputConfig(
                base_path="filtered_output",
                separate_by_source=True,
                merge_all=False
            ),
            verbose=True
        )
        
        print(f"📁 Created {len(test_files)} test files")
        print(f"🔍 Applying filters: include=[*.txt, *.md], exclude=[*draft*, *temp*]")
        
        # Process with filtering
        processor = BatchProcessor(config)
        summary = processor.process_all()
        
        print(f"✅ Filtering batch completed!")
        print(f"📊 Expected: 2 files (important_doc.txt, final_report.md)")
        print(f"📋 Actually processed: {summary['total_documents']} documents")
        
        if summary['total_documents'] == 2:
            print(f"✅ Filtering worked correctly!")
        else:
            print(f"⚠️ Unexpected number of documents processed")
        
    finally:
        # Clean up
        for file in test_files:
            if file.exists():
                file.unlink()
        if test_dir.exists():
            test_dir.rmdir()
        
        output_dir = Path("filtered_output")
        if output_dir.exists():
            for file in output_dir.glob("*"):
                file.unlink()
            output_dir.rmdir()


def example_parallel_processing():
    """Example: Parallel processing with multiple workers"""
    print("\n=== Parallel Processing Example ===")
    
    # Create multiple test files
    test_dir = Path("parallel_test_docs")
    test_dir.mkdir(exist_ok=True)
    
    test_files = []
    try:
        # Create several files to process in parallel
        for i in range(5):
            file_path = test_dir / f"doc_{i+1}.txt"
            content = f"Document {i+1}\n" + "Content line. " * 20  # Make it substantial
            file_path.write_text(content)
            test_files.append(file_path)
        
        # Create sources for each file
        sources = []
        for i, file_path in enumerate(test_files):
            sources.append(InputSource(
                type=InputType.FILE,
                path=str(file_path),
                output_prefix=f"parallel_doc_{i+1}"
            ))
        
        config = BatchConfig(
            loader_config=LoaderConfig(
                output_format=OutputFormat.DOCUMENTS,
                chunking_strategy="basic",
                max_chunk_size=500,
                chunk_overlap=50  # Small chunks for demonstration
            ),
            sources=sources,
            output=OutputConfig(
                base_path="parallel_output",
                separate_by_source=True,
                merge_all=True
            ),
            max_workers=3,  # Parallel processing
            verbose=True
        )
        
        print(f"⚡ Processing {len(test_files)} files with 3 parallel workers...")
        
        import time
        start_time = time.time()
        
        processor = BatchProcessor(config)
        summary = processor.process_all()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"✅ Parallel processing completed in {processing_time:.2f} seconds!")
        print(f"📊 Results: {summary['successful_sources']}/{summary['total_sources']} files")
        print(f"📋 Total documents: {summary['total_documents']}")
        print(f"📁 Output files: {len(summary['output_files'])}")
        
    finally:
        # Clean up
        for file in test_files:
            if file.exists():
                file.unlink()
        if test_dir.exists():
            test_dir.rmdir()
        
        output_dir = Path("parallel_output")
        if output_dir.exists():
            for file in output_dir.glob("*"):
                file.unlink()
            output_dir.rmdir()


if __name__ == "__main__":
    print("Universal Data Loader - Batch Processing Examples")
    print("=" * 70)
    
    example_simple_batch_urls()
    example_custom_batch_config()
    example_config_file_batch()
    example_advanced_filtering()
    example_parallel_processing()
    
    print("\n" + "=" * 70)
    print("🎉 Batch processing examples completed!")
    print("\n🚀 Key capabilities demonstrated:")
    print("  📱 Simple URL batch processing")
    print("  ⚙️ Custom batch configurations") 
    print("  📄 Configuration file-based processing")
    print("  🔍 Advanced file filtering with patterns")
    print("  ⚡ Parallel processing with multiple workers")
    print("  📊 Comprehensive batch statistics and reporting")
    print("\n💡 Perfect for large-scale document processing pipelines!")