# Universal Data Loader for LLMs

A Python library that provides a universal interface for loading and processing various document types using the Unstructured library. Designed specifically for LLM applications including RAG systems, model training, and document analysis.

## Features

- **Multi-format Support**: Process PDF, DOCX, HTML, TXT, CSV, XLSX, PPTX, EML, and more
- **Flexible Configuration**: Customizable processing options for different use cases
- **Chunking Strategies**: Multiple chunking approaches for optimal text segmentation
- **OCR Support**: Multi-language OCR capabilities for image-based documents
- **RAG-Optimized**: Pre-configured settings for Retrieval-Augmented Generation
- **Batch Processing**: Process entire directories of documents
- **URL Support**: Load and process content directly from URLs

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd unstructured
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Command Line Interface

The easiest way to use the Universal Data Loader is through the command line:

```bash
# Basic usage - load a PDF and save as JSON
python uloader.py document.pdf -o output.json

# With RAG-optimized settings
python uloader.py document.pdf -o output.json --preset rag

# Process with custom chunk size and show statistics
python uloader.py document.pdf -o output.json --chunk-size 800 --stats

# Process entire directory
python uloader.py documents/ -o results.json --recursive

# Load from URL
python uloader.py https://example.com/article -o article.json
```

### Python API

```python
from universal_loader import UniversalDataLoader, LoaderConfig

# Basic usage with default settings
loader = UniversalDataLoader()
elements = loader.load_file("document.pdf")

# Save processed output
loader.save_output(elements, "output.json")
```

## Configuration Options

### Pre-configured Settings

```python
from universal_loader.utils import create_config_for_rag, create_config_for_training

# RAG-optimized configuration
rag_config = create_config_for_rag()
loader = UniversalDataLoader(rag_config)

# Training-optimized configuration  
training_config = create_config_for_training()
loader = UniversalDataLoader(training_config)
```

### Custom Configuration

```python
from universal_loader.config import LoaderConfig, OutputFormat, ChunkingStrategy

config = LoaderConfig(
    output_format=OutputFormat.JSON,
    chunking_strategy=ChunkingStrategy.BY_TITLE,
    max_chunk_size=1000,
    chunk_overlap=100,
    ocr_languages=["eng", "fra"],
    extract_images=True,
    min_text_length=50,
    remove_headers_footers=True
)

loader = UniversalDataLoader(config)
```

## Usage Examples

### Single File Processing

```python
# Load a PDF document
elements = loader.load_file("research_paper.pdf")

# Load a Word document with custom settings
config = LoaderConfig(chunking_strategy=ChunkingStrategy.BASIC, max_chunk_size=500)
loader = UniversalDataLoader(config)
elements = loader.load_file("report.docx")
```

### Directory Processing

```python
# Process all supported files in a directory
elements = loader.load_directory("documents/", recursive=True)

# Process with filtering
for element in elements:
    if element.get('source_file', '').endswith('.pdf'):
        # Handle PDF-specific processing
        pass
```

### URL Processing

```python
# Load content from a web page
elements = loader.load_url("https://example.com/article")
```

### Output Formats

```python
# JSON output (default)
config = LoaderConfig(output_format=OutputFormat.JSON)

# Plain text output
config = LoaderConfig(output_format=OutputFormat.TEXT)

# Raw elements
config = LoaderConfig(output_format=OutputFormat.ELEMENTS)
```

## Configuration Management

### Save and Load Configurations

```python
from universal_loader.utils import save_config_to_file, load_config_from_file

# Save configuration
save_config_to_file(config, "my_config.json")

# Load configuration
config = load_config_from_file("my_config.json")
```

### Configuration Presets

| Preset | Use Case | Key Features |
|--------|----------|--------------|
| `create_default_config()` | General purpose | Balanced settings for most documents |
| `create_config_for_rag()` | RAG systems | Optimized chunking for retrieval |
| `create_config_for_training()` | Model training | Clean text output, larger chunks |

## Supported File Types

| Format | Extensions | Features |
|--------|------------|----------|
| PDF | `.pdf` | OCR, table extraction, image extraction |
| Word | `.docx`, `.doc` | Full formatting preservation |
| PowerPoint | `.pptx`, `.ppt` | Slide content extraction |
| Excel | `.xlsx`, `.xls` | Sheet and cell processing |
| Web | `.html`, `.htm` | HTML parsing and cleaning |
| Text | `.txt`, `.md` | Plain text processing |
| Email | `.eml`, `.msg` | Email content and metadata |
| CSV | `.csv` | Structured data processing |

## Advanced Features

### OCR Configuration

```python
config = LoaderConfig(
    ocr_languages=["eng", "fra", "deu"],  # Multiple languages
    extract_images=True,
    custom_partition_kwargs={
        "strategy": "hi_res",  # High resolution for better OCR
        "infer_table_structure": True
    }
)
```

### Custom Processing

```python
config = LoaderConfig(
    custom_partition_kwargs={
        "strategy": "hi_res",
        "infer_table_structure": True,
        "include_page_breaks": True,
        "skip_infer_table_types": False
    }
)
```

### Filtering and Utilities

```python
from universal_loader.utils import (
    filter_elements_by_type,
    extract_text_only,
    count_elements_by_type
)

# Filter by element type
text_elements = filter_elements_by_type(elements, ["NarrativeText", "Title"])

# Extract just the text
texts = extract_text_only(elements)

# Get statistics
stats = count_elements_by_type(elements)
```

## Command Line Interface

### Installation for CLI

To use the CLI globally, you can install the package:

```bash
# Install in development mode
pip install -e .

# Now you can use 'uloader' command anywhere
uloader document.pdf -o output.json
```

### CLI Examples

```bash
# Basic document processing
uloader document.pdf -o output.json

# RAG-optimized processing with statistics
uloader research_paper.pdf -o chunks.json --preset rag --stats

# Process with custom settings
uloader document.docx -o output.json \
  --chunk-strategy by_title \
  --chunk-size 1000 \
  --chunk-overlap 150 \
  --ocr-lang eng,fra

# Process entire directory
uloader documents/ -o all_docs.json --recursive --verbose

# Extract text only (no metadata)
uloader document.pdf -o text_only.json --format text --no-metadata

# Process URL content
uloader https://en.wikipedia.org/wiki/Artificial_intelligence -o ai_article.json

# Use custom configuration file
uloader document.pdf -o output.json --config my_config.json

# Fast processing for large files
uloader large_document.pdf -o output.json --preset training --no-metadata
```

### CLI Options

| Option | Description | Example |
|--------|-------------|---------|
| `--preset` | Use predefined configuration | `--preset rag` |
| `--format` | Output format (json/text/elements) | `--format text` |
| `--chunk-strategy` | Chunking method | `--chunk-strategy by_title` |
| `--chunk-size` | Maximum chunk size | `--chunk-size 800` |
| `--chunk-overlap` | Overlap between chunks | `--chunk-overlap 100` |
| `--ocr-lang` | OCR languages | `--ocr-lang eng,fra,deu` |
| `--extract-images` | Extract images from docs | `--extract-images` |
| `--stats` | Show processing statistics | `--stats` |
| `--verbose` | Detailed output | `--verbose` |

## Python API Examples

Run the example scripts to see the library in action:

```bash
# Basic usage examples
python examples/basic_usage.py

# Configuration examples
python examples/config_examples.py
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

- `unstructured[all-docs]>=0.17.0` - Core document processing
- `python-magic` - File type detection
- `pydantic>=2.0.0` - Configuration validation
- `pathlib` - Path handling
- `typing-extensions` - Type hints

## Troubleshooting

### Common Issues

1. **OCR not working**: Ensure tesseract is installed on your system
2. **PDF processing slow**: Try using `strategy="fast"` in custom_partition_kwargs
3. **Memory issues**: Reduce `max_chunk_size` or process files individually
4. **File type not supported**: Check the SUPPORTED_EXTENSIONS set in the loader

### Performance Tips

- Use `strategy="fast"` for quicker processing of large documents
- Set `include_metadata=False` if metadata is not needed
- Adjust chunk sizes based on your downstream application requirements
- Process files in batches rather than all at once for large directories