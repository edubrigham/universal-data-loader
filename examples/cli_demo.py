#!/usr/bin/env python3
"""
CLI Demo Script - Demonstrates various CLI options with the test PDF
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a CLI command and show the results"""
    print(f"\n{'='*60}")
    print(f"🔸 {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        print(result.stdout)
        if result.stderr:
            print(f"stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    """Run CLI demonstrations"""
    print("🚀 Universal Data Loader CLI Demonstration")
    print("Using test PDF: examples/test_data/20250412000218756416-00163124-Fiscaal_attest-2024.pdf")
    
    # Check if test PDF exists
    test_pdf = "examples/test_data/20250412000218756416-00163124-Fiscaal_attest-2024.pdf"
    if not Path(f"../{test_pdf}").exists():
        print(f"❌ Test PDF not found: {test_pdf}")
        return
    
    # Base command setup
    base_cmd = ["python", "uloader.py"]
    python_cmd = [sys.executable, "uloader.py"]
    
    # Demo commands
    demos = [
        {
            "cmd": python_cmd + [test_pdf, "-o", "examples/test_data/demo_basic.json", "--stats"],
            "desc": "Basic PDF processing with statistics"
        },
        {
            "cmd": python_cmd + [test_pdf, "-o", "examples/test_data/demo_rag.json", "--preset", "rag", "--chunk-size", "400", "--verbose"],
            "desc": "RAG-optimized processing with custom chunk size"
        },
        {
            "cmd": python_cmd + [test_pdf, "-o", "examples/test_data/demo_text.txt", "--format", "text", "--no-metadata"],
            "desc": "Text-only output without metadata"
        },
        {
            "cmd": python_cmd + [test_pdf, "-o", "examples/test_data/demo_training.json", "--preset", "training", "--chunk-size", "1000"],
            "desc": "Training-optimized preset with large chunks"
        },
        {
            "cmd": python_cmd + [test_pdf, "-o", "examples/test_data/demo_minimal.json", "--chunk-size", "300", "--chunk-overlap", "50", "--min-length", "20"],
            "desc": "Custom chunking settings"
        }
    ]
    
    # Run demonstrations
    successful = 0
    for demo in demos:
        if run_command(demo["cmd"], demo["desc"]):
            successful += 1
    
    print(f"\n🎉 Demo completed! {successful}/{len(demos)} commands successful")
    
    # Show file sizes of outputs
    print(f"\n📊 Generated Output Files:")
    output_dir = Path("../examples/test_data")
    for file_pattern in ["demo_*.json", "demo_*.txt"]:
        for file_path in output_dir.glob(file_pattern):
            size = file_path.stat().st_size
            print(f"  {file_path.name}: {size:,} bytes")
    
    # Cleanup option
    response = input("\n🗑️  Clean up demo output files? (y/n): ")
    if response.lower() == 'y':
        for file_pattern in ["demo_*.json", "demo_*.txt"]:
            for file_path in output_dir.glob(file_pattern):
                try:
                    file_path.unlink()
                    print(f"  ✓ Removed {file_path.name}")
                except Exception as e:
                    print(f"  ❌ Failed to remove {file_path.name}: {e}")

if __name__ == "__main__":
    main()