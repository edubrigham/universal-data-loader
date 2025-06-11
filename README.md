# Universal Document Loader 📄➡️🤖

**Turn any document into AI-ready data in seconds**

## What does this tool do?

This tool takes your documents (PDFs, Word files, websites, etc.) and converts them into a format that AI systems can understand and use. Think of it as a universal translator between human documents and AI applications.

## Why do you need this?

**The Problem:** AI chatbots and search systems can't directly read your PDF reports, Word documents, or web pages. They need the content broken down into smaller, structured pieces.

**The Solution:** This tool automatically:
- ✅ Reads your documents (PDFs, Word, PowerPoint, websites, etc.)
- ✅ Extracts the text content
- ✅ Breaks it into AI-friendly chunks
- ✅ Saves it in a format ready for AI applications

**Perfect for:**
- Building company chatbots with your documents
- Creating AI-powered search systems
- Training AI models on your data
- Analyzing large collections of documents

---

## 🚀 Quick Start (3 Simple Steps)

### Step 1: Setup (One-time only)
```bash
# Download the tool
git clone <repository-url>
cd unstructured

# Set it up (takes 2-3 minutes)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Convert Your First Document
```bash
# Convert a PDF to AI-ready format
python uloader.py your-document.pdf -o ai-ready-data.json

# That's it! Your document is now ready for AI applications
```

### Step 3: Check Your Results
Your file `ai-ready-data.json` now contains your document in AI-ready format with:
- Text content broken into smart chunks
- Important information like page numbers, document source
- Everything organized for AI systems to use

---

## 📋 Common Tasks

### Process Different File Types
```bash
# PDF documents
python uloader.py report.pdf -o output.json

# Word documents  
python uloader.py presentation.docx -o output.json

# Web pages
python uloader.py https://your-company.com/policies -o output.json

# Text files
python uloader.py notes.txt -o output.json
```

### Process Multiple Documents at Once

**Option 1: Process a whole folder**
```bash
# Convert all documents in a folder
python uloader.py my-documents/ -o all-documents.json --recursive
```

**Option 2: Process a list of websites**
1. Create a text file called `websites.txt` with your URLs:
```
https://your-company.com/about
https://your-company.com/services  
https://your-company.com/policies
```

2. Process all websites at once:
```bash
python uloader.py dummy -o website-data/ --urls-file websites.txt
```

**Option 3: Process mixed sources (files, folders, websites)**
1. Create a text file called `sources.txt`:
```
documents/policies/
reports/annual-report.pdf
https://company.com/handbook
```

2. Process everything together:
```bash
python uloader.py dummy -o company-data/ --sources-file sources.txt
```

### Advanced Batch Processing
For complex projects, create a configuration file `batch-config.json`:
```json
{
  "sources": [
    {
      "type": "directory",
      "path": "company-policies/",
      "output_prefix": "policies"
    },
    {
      "type": "url", 
      "path": "https://company.com/handbook",
      "output_prefix": "handbook"
    },
    {
      "type": "file",
      "path": "important-document.pdf",
      "output_prefix": "important"
    }
  ],
  "output": {
    "base_path": "company-knowledge-base",
    "separate_by_source": true,
    "merge_all": true
  },
  "max_workers": 3,
  "verbose": true
}
```

Then run:
```bash
python uloader.py dummy -o output/ --batch-config batch-config.json
```

---

## 🎯 What You Get

After processing, your documents become structured data that looks like this:

```json
[
  {
    "page_content": "Our company policy states that...",
    "metadata": {
      "filename": "company-policy.pdf",
      "page_number": 1,
      "element_type": "text"
    }
  },
  {
    "page_content": "The next section covers...",
    "metadata": {
      "filename": "company-policy.pdf", 
      "page_number": 2,
      "element_type": "text"
    }
  }
]
```

This format is perfect for:
- ✅ AI chatbots that answer questions about your documents
- ✅ Smart search systems
- ✅ Document analysis tools
- ✅ Any AI application that needs to understand your content

---

## 🛠️ Customization Options

### Control Text Chunk Size
```bash
# Smaller chunks (better for precise search)
python uloader.py document.pdf -o output.json --chunk-size 400

# Larger chunks (better for context)
python uloader.py document.pdf -o output.json --chunk-size 1200
```

### Choose Output Format
```bash
# AI-ready format (default - recommended)
python uloader.py document.pdf -o output.json --format documents

# Plain text only
python uloader.py document.pdf -o output.txt --format text

# Raw data (for technical users)
python uloader.py document.pdf -o output.json --format json
```

### Get Processing Information
```bash
# See what happened during processing
python uloader.py document.pdf -o output.json --verbose --stats
```

---

## 📁 File Types Supported

| Document Type | File Extensions | What It Extracts |
|---------------|----------------|------------------|
| **PDF Documents** | `.pdf` | Text, tables, images (with OCR if needed) |
| **Word Documents** | `.docx`, `.doc` | All text content and formatting |
| **PowerPoint** | `.pptx`, `.ppt` | Slide content and speaker notes |
| **Excel Spreadsheets** | `.xlsx`, `.xls` | Cell content and data |
| **Web Pages** | `http://`, `https://` | Page content (cleaned) |
| **Text Files** | `.txt`, `.md` | All text content |
| **Email Files** | `.eml`, `.msg` | Email content and attachments |
| **CSV Data** | `.csv` | Structured data |

---

## ❓ Troubleshooting

### "Command not found" Error
Make sure you activated the virtual environment:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### "File not found" Error
- Check the file path is correct
- Use quotes around file names with spaces: `"my document.pdf"`

### Processing Takes Too Long
- For large files, add `--chunk-size 2000` to speed up processing
- For many files, the tool processes them in parallel automatically

### PDF Not Reading Properly
- If PDF contains scanned images, the tool automatically uses OCR (text recognition)
- For better results with scanned documents, ensure good image quality

### Need Help?
- Run `python uloader.py --help` to see all options
- Check that your file type is in the supported list above
- Make sure the file isn't corrupted by opening it manually first

---

## 💡 Real-World Examples

### Building a Company Chatbot
```bash
# Step 1: Process all company documents
python uloader.py company-docs/ -o chatbot-data.json --recursive

# Step 2: Use the output file with your AI chatbot platform
# The chatbot can now answer questions about your company documents!
```

### Creating a Searchable Knowledge Base
```bash
# Process documentation from multiple sources
python uloader.py dummy -o knowledge-base/ --sources-file all-sources.txt

# Result: Searchable database of all your important information
```

### Analyzing Customer Feedback
```bash
# Process all feedback files
python uloader.py feedback-forms/ -o analysis-ready.json --chunk-size 200

# Result: Structured data ready for AI analysis
```

---

## 🚀 Next Steps

1. **Start Simple**: Try converting one document first
2. **Scale Up**: Process folders or use batch processing for multiple sources
3. **Integrate**: Use the output files with your AI applications
4. **Customize**: Adjust settings based on your specific needs

**Questions?** The tool is designed to work out-of-the-box for most use cases. Start with the basic commands and expand as needed!