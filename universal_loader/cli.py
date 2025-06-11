"""
Command Line Interface for Universal Data Loader
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .loader import UniversalDataLoader
from .config import LoaderConfig, OutputFormat, ChunkingStrategy
from .utils import (
    create_default_config, 
    create_config_for_rag, 
    create_config_for_training,
    load_config_from_file,
    get_file_stats,
    count_elements_by_type
)


def setup_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Universal Data Loader for LLMs - Process documents for AI applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load a PDF and save as JSON
  uloader document.pdf -o output.json
  
  # Process with RAG-optimized settings
  uloader document.pdf -o output.json --preset rag
  
  # Process directory with custom chunk size
  uloader docs/ -o results.json --chunk-size 800
  
  # Load URL content
  uloader https://example.com/article -o article.json
  
  # Use custom configuration file
  uloader document.pdf -o output.json --config my_config.json
  
  # Process with OCR for multiple languages
  uloader document.pdf -o output.json --ocr-lang eng,fra,deu
"""
    )
    
    # Input source
    parser.add_argument(
        "input",
        help="Input file, directory, or URL to process"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output file path"
    )
    
    parser.add_argument(
        "--format",
        choices=["json", "text", "elements"],
        default="json",
        help="Output format (default: json)"
    )
    
    # Configuration presets
    parser.add_argument(
        "--preset",
        choices=["default", "rag", "training"],
        help="Use predefined configuration preset"
    )
    
    parser.add_argument(
        "--config",
        help="Path to custom configuration JSON file"
    )
    
    # Processing options
    parser.add_argument(
        "--chunk-strategy",
        choices=["basic", "by_title", "by_page"],
        help="Chunking strategy to use"
    )
    
    parser.add_argument(
        "--chunk-size",
        type=int,
        help="Maximum chunk size in characters"
    )
    
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        help="Overlap between chunks in characters"
    )
    
    parser.add_argument(
        "--min-length",
        type=int,
        help="Minimum text length to include"
    )
    
    # OCR options
    parser.add_argument(
        "--ocr-lang",
        help="OCR languages (comma-separated, e.g., 'eng,fra,deu')"
    )
    
    parser.add_argument(
        "--extract-images",
        action="store_true",
        help="Extract images from documents"
    )
    
    # Filtering options
    parser.add_argument(
        "--include-metadata",
        action="store_true",
        default=True,
        help="Include metadata in output (default: True)"
    )
    
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Exclude metadata from output"
    )
    
    parser.add_argument(
        "--keep-headers",
        action="store_true",
        help="Keep headers and footers (default: remove them)"
    )
    
    # Directory processing
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=True,
        help="Process directories recursively (default: True)"
    )
    
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't process directories recursively"
    )
    
    # Utility options
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show processing statistics"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Universal Data Loader 0.1.0"
    )
    
    return parser


def create_config_from_args(args) -> LoaderConfig:
    """Create configuration from command line arguments"""
    
    # Start with preset or default configuration
    if args.config:
        config = load_config_from_file(args.config)
    elif args.preset == "rag":
        config = create_config_for_rag()
    elif args.preset == "training":
        config = create_config_for_training()
    else:
        config = create_default_config()
    
    # Override with command line arguments
    if args.format:
        config.output_format = OutputFormat(args.format)
    
    if args.chunk_strategy:
        config.chunking_strategy = ChunkingStrategy(args.chunk_strategy)
    
    if args.chunk_size:
        config.max_chunk_size = args.chunk_size
    
    if args.chunk_overlap:
        config.chunk_overlap = args.chunk_overlap
    
    if args.min_length:
        config.min_text_length = args.min_length
    
    if args.ocr_lang:
        config.ocr_languages = args.ocr_lang.split(",")
    
    if args.extract_images:
        config.extract_images = True
    
    if args.no_metadata:
        config.include_metadata = False
    
    if args.keep_headers:
        config.remove_headers_footers = False
    
    return config


def process_input(loader: UniversalDataLoader, input_path: str, args) -> list:
    """Process the input (file, directory, or URL)"""
    
    if input_path.startswith(("http://", "https://")):
        # URL processing
        if args.verbose:
            print(f"Processing URL: {input_path}")
        return loader.load_url(input_path)
    
    input_path_obj = Path(input_path)
    
    if not input_path_obj.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")
    
    if input_path_obj.is_file():
        # Single file processing
        if args.verbose:
            stats = get_file_stats(input_path_obj)
            print(f"Processing file: {stats['file_name']} ({stats['file_size']} bytes)")
        return loader.load_file(input_path_obj)
    
    elif input_path_obj.is_dir():
        # Directory processing
        recursive = args.recursive and not args.no_recursive
        if args.verbose:
            print(f"Processing directory: {input_path_obj} (recursive: {recursive})")
        return loader.load_directory(input_path_obj, recursive=recursive)
    
    else:
        raise ValueError(f"Invalid input type: {input_path}")


def show_statistics(elements: list, verbose: bool = False):
    """Show processing statistics"""
    print(f"\nProcessing Statistics:")
    print(f"Total elements: {len(elements)}")
    
    if elements:
        # Count by type
        type_counts = count_elements_by_type(elements)
        print("Elements by type:")
        for element_type, count in sorted(type_counts.items()):
            print(f"  {element_type}: {count}")
        
        if verbose:
            # Calculate text statistics
            total_chars = 0
            total_words = 0
            
            for element in elements:
                if isinstance(element, dict):
                    text = element.get('text', '')
                else:
                    text = str(element)
                
                total_chars += len(text)
                total_words += len(text.split())
            
            print(f"\nText Statistics:")
            print(f"Total characters: {total_chars:,}")
            print(f"Total words: {total_words:,}")
            print(f"Average chars per element: {total_chars / len(elements):.1f}")
            print(f"Average words per element: {total_words / len(elements):.1f}")


def main():
    """Main CLI entry point"""
    parser = setup_parser()
    args = parser.parse_args()
    
    try:
        # Create configuration
        if args.verbose:
            print("Creating configuration...")
        config = create_config_from_args(args)
        
        # Initialize loader
        loader = UniversalDataLoader(config)
        
        # Process input
        if args.verbose:
            print(f"Processing input: {args.input}")
        elements = process_input(loader, args.input, args)
        
        # Save output
        if args.verbose:
            print(f"Saving output to: {args.output}")
        loader.save_output(elements, args.output)
        
        # Show statistics if requested
        if args.stats or args.verbose:
            show_statistics(elements, verbose=args.verbose)
        
        print(f"✓ Successfully processed and saved to {args.output}")
        
    except KeyboardInterrupt:
        print("\n❌ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()