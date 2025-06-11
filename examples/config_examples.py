"""
Configuration examples for different use cases
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from universal_loader.config import LoaderConfig, OutputFormat, ChunkingStrategy
from universal_loader.utils import (
    create_default_config, 
    create_config_for_rag, 
    create_config_for_training,
    save_config_to_file,
    load_config_from_file
)


def example_create_configs():
    """Create and save different configuration examples"""
    print("=== Creating Configuration Examples ===")
    
    # 1. Default configuration
    default_config = create_default_config()
    save_config_to_file(default_config, "config_default.json")
    print("✓ Default configuration saved to config_default.json")
    
    # 2. RAG-optimized configuration
    rag_config = create_config_for_rag()
    save_config_to_file(rag_config, "config_rag.json")
    print("✓ RAG configuration saved to config_rag.json")
    
    # 3. Training-optimized configuration
    training_config = create_config_for_training()
    save_config_to_file(training_config, "config_training.json")
    print("✓ Training configuration saved to config_training.json")
    
    # 4. Custom OCR configuration
    ocr_config = LoaderConfig(
        output_format=OutputFormat.JSON,
        chunking_strategy=ChunkingStrategy.BY_TITLE,
        ocr_languages=["eng", "fra", "deu"],  # Multiple languages
        extract_images=True,
        max_chunk_size=1200,
        min_text_length=25,
        remove_headers_footers=True,
        custom_partition_kwargs={
            "strategy": "hi_res",  # High resolution for better OCR
            "infer_table_structure": True
        }
    )
    save_config_to_file(ocr_config, "config_ocr.json")
    print("✓ OCR configuration saved to config_ocr.json")
    
    # 5. Minimal processing configuration
    minimal_config = LoaderConfig(
        output_format=OutputFormat.TEXT,
        include_metadata=False,
        chunking_strategy=None,  # No chunking
        min_text_length=0,  # Keep all text
        remove_headers_footers=False,  # Keep everything
        custom_partition_kwargs={}
    )
    save_config_to_file(minimal_config, "config_minimal.json")
    print("✓ Minimal configuration saved to config_minimal.json")


def example_load_and_modify_config():
    """Load a configuration and modify it"""
    print("\n=== Loading and Modifying Configuration ===")
    
    try:
        # Load the RAG configuration
        config = load_config_from_file("config_rag.json")
        print(f"Loaded RAG config: chunk_size={config.max_chunk_size}")
        
        # Modify it for a specific use case
        config.max_chunk_size = 1500  # Larger chunks
        config.chunk_overlap = 200    # More overlap
        config.ocr_languages = ["eng", "spa"]  # Add Spanish
        
        # Save the modified version
        save_config_to_file(config, "config_rag_modified.json")
        print("✓ Modified RAG configuration saved to config_rag_modified.json")
        
    except FileNotFoundError:
        print("Error: RAG configuration file not found. Run example_create_configs() first.")


def example_configuration_comparison():
    """Compare different configurations"""
    print("\n=== Configuration Comparison ===")
    
    configs = {
        "Default": create_default_config(),
        "RAG": create_config_for_rag(),
        "Training": create_config_for_training()
    }
    
    print(f"{'Setting':<20} {'Default':<12} {'RAG':<12} {'Training':<12}")
    print("-" * 60)
    
    settings = [
        ("Output Format", "output_format"),
        ("Include Metadata", "include_metadata"),
        ("Chunking Strategy", "chunking_strategy"),
        ("Max Chunk Size", "max_chunk_size"),
        ("Chunk Overlap", "chunk_overlap"),
        ("Min Text Length", "min_text_length"),
        ("Remove Headers", "remove_headers_footers")
    ]
    
    for setting_name, setting_attr in settings:
        row = f"{setting_name:<20}"
        for config_name, config in configs.items():
            value = getattr(config, setting_attr)
            row += f"{str(value):<12}"
        print(row)


def example_custom_partition_kwargs():
    """Examples of custom partition keyword arguments"""
    print("\n=== Custom Partition Arguments ===")
    
    # Example 1: High-resolution PDF processing
    pdf_config = LoaderConfig(
        custom_partition_kwargs={
            "strategy": "hi_res",
            "infer_table_structure": True,
            "extract_images_in_pdf": True,
            "languages": ["eng"],
            "include_page_breaks": True
        }
    )
    save_config_to_file(pdf_config, "config_pdf_hiRes.json")
    print("✓ High-resolution PDF config saved")
    
    # Example 2: Fast processing configuration
    fast_config = LoaderConfig(
        custom_partition_kwargs={
            "strategy": "fast",
            "skip_infer_table_types": True
        }
    )
    save_config_to_file(fast_config, "config_fast.json")
    print("✓ Fast processing config saved")
    
    # Example 3: Table-focused configuration
    table_config = LoaderConfig(
        custom_partition_kwargs={
            "infer_table_structure": True,
            "include_orig_elements": True,
            "strategy": "hi_res"
        }
    )
    save_config_to_file(table_config, "config_tables.json")
    print("✓ Table-focused config saved")


def cleanup_example_files():
    """Clean up example configuration files"""
    print("\n=== Cleaning Up Example Files ===")
    
    config_files = [
        "config_default.json",
        "config_rag.json", 
        "config_training.json",
        "config_ocr.json",
        "config_minimal.json",
        "config_rag_modified.json",
        "config_pdf_hiRes.json",
        "config_fast.json",
        "config_tables.json"
    ]
    
    for config_file in config_files:
        file_path = Path(config_file)
        if file_path.exists():
            file_path.unlink()
            print(f"✓ Removed {config_file}")


if __name__ == "__main__":
    print("Universal Data Loader Configuration Examples")
    print("=" * 60)
    
    example_create_configs()
    example_load_and_modify_config()
    example_configuration_comparison()
    example_custom_partition_kwargs()
    
    # Ask user if they want to clean up
    response = input("\nClean up example configuration files? (y/n): ")
    if response.lower() == 'y':
        cleanup_example_files()
    
    print("\nConfiguration examples completed!")