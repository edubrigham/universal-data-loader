#!/usr/bin/env python3
"""
Universal Data Loader CLI Entry Point
"""

import sys
from pathlib import Path

# Add the current directory to Python path to import our module
sys.path.insert(0, str(Path(__file__).parent))

from universal_loader.cli import main

if __name__ == "__main__":
    main()