"""
Basic usage examples for the Universal Data Loader
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path to import our module
sys.path.append(str(Path(__file__).parent.parent))

from universal_loader import UniversalDataLoader, LoaderConfig
from universal_loader.utils import create_default_config, create_config_for_rag


def example_basic_usage():
    """Example of basic file loading"""
    print("=== Basic Usage Example ===")
    
    # Create a loader with default configuration
    loader = UniversalDataLoader()
    
    # Create a sample text file for demonstration
    sample_file = Path("sample.txt")
    sample_file.write_text("This is a sample document.\n\nIt has multiple paragraphs.\n\nFor testing purposes.")
    
    try:
        # Load the file
        elements = loader.load_file(sample_file)
        
        print(f"Loaded {len(elements)} elements from {sample_file}")
        for i, element in enumerate(elements[:3]):  # Show first 3 elements
            print(f"Element {i+1}: {element}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        if sample_file.exists():
            sample_file.unlink()


def example_custom_config():
    """Example with custom configuration"""
    print("\n=== Custom Configuration Example ===")
    
    # Create custom configuration - no chunking by default
    config = LoaderConfig(
        output_format="text",
        min_text_length=20,
        include_metadata=True
    )
    
    loader = UniversalDataLoader(config)
    
    # Create a larger sample file
    sample_content = """
    # Introduction
    
    This is a longer document for testing document processing capabilities.
    
    ## Section 1
    
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor 
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis 
    nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    
    ## Section 2
    
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore 
    eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt 
    in culpa qui officia deserunt mollit anim id est laborum.
    
    ## Conclusion
    
    This concludes our sample document for testing purposes.
    """
    
    sample_file = Path("sample_long.txt")
    sample_file.write_text(sample_content)
    
    try:
        elements = loader.load_file(sample_file)
        
        print(f"Loaded {len(elements)} elements with custom config")
        for i, element in enumerate(elements):
            print(f"Element {i+1}: {element[:100]}..." if len(str(element)) > 100 else f"Element {i+1}: {element}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if sample_file.exists():
            sample_file.unlink()


def example_rag_config():
    """Example with RAG-optimized configuration"""
    print("\n=== RAG Configuration Example ===")
    
    # Use pre-configured RAG settings
    config = create_config_for_rag()
    loader = UniversalDataLoader(config)
    
    sample_content = """
    # Machine Learning Fundamentals
    
    Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.
    
    ## Supervised Learning
    
    Supervised learning uses labeled training data to learn a mapping function from inputs to outputs. Common algorithms include:
    - Linear Regression
    - Decision Trees
    - Random Forest
    - Support Vector Machines
    
    ## Unsupervised Learning
    
    Unsupervised learning finds hidden patterns in data without labeled examples. Key techniques include:
    - Clustering (K-means, Hierarchical)
    - Dimensionality Reduction (PCA, t-SNE)
    - Association Rules
    
    ## Deep Learning
    
    Deep learning uses neural networks with multiple layers to learn complex patterns in data. Popular architectures include:
    - Convolutional Neural Networks (CNNs)
    - Recurrent Neural Networks (RNNs)
    - Transformers
    """
    
    sample_file = Path("ml_guide.txt")
    sample_file.write_text(sample_content)
    
    try:
        elements = loader.load_file(sample_file)
        
        print(f"RAG-optimized processing: {len(elements)} chunks created")
        for i, element in enumerate(elements):
            text = element.get('text', str(element)) if isinstance(element, dict) else str(element)
            print(f"\nChunk {i+1} ({len(text)} chars):")
            print(text[:200] + "..." if len(text) > 200 else text)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if sample_file.exists():
            sample_file.unlink()


def example_save_output():
    """Example of saving processed output"""
    print("\n=== Save Output Example ===")
    
    loader = UniversalDataLoader()
    
    sample_content = "This is sample content for saving.\n\nIt will be processed and saved to a file."
    sample_file = Path("input.txt")
    output_file = Path("output.json")
    
    sample_file.write_text(sample_content)
    
    try:
        # Process the file
        elements = loader.load_file(sample_file)
        
        # Save the output
        loader.save_output(elements, output_file)
        
        print(f"Processed content saved to {output_file}")
        
        # Show the saved content
        if output_file.exists():
            with open(output_file, 'r') as f:
                saved_content = f.read()
            print(f"Saved content preview:\n{saved_content[:300]}...")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        for file in [sample_file, output_file]:
            if file.exists():
                file.unlink()


if __name__ == "__main__":
    print("Universal Data Loader Examples")
    print("=" * 50)
    
    example_basic_usage()
    example_custom_config()
    example_rag_config()
    example_save_output()
    
    print("\n" + "=" * 50)
    print("Examples completed!")