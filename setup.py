"""
Setup script for Universal Data Loader
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
README = Path("README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="universal-data-loader",
    version="0.1.0",
    description="Universal Data Loader for LLMs using Unstructured",
    long_description=README,
    long_description_content_type="text/markdown",
    author="edubrigham",
    author_email="edubrigham@gmail.com",
    url="https://github.com/edubrigham/universal-data-loader",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "uloader=universal_loader.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="llm, ai, nlp, document-processing, rag, unstructured, pdf, docx, html",
    project_urls={
        "Bug Reports": "https://github.com/edubrigham/universal-data-loader/issues",
        "Source": "https://github.com/edubrigham/universal-data-loader",
        "Documentation": "https://github.com/edubrigham/universal-data-loader#readme",
    },
)