# PDF Outline Extractor

A Python-based solution for extracting structured outlines from PDF documents in a Dockerized offline environment.

## Overview

This tool processes PDF files and extracts hierarchical outlines including document titles and headings (H1, H2, H3) with their corresponding page numbers. It uses advanced heuristics to detect headings accurately, even when fonts and sizes are inconsistent.

## Features

- **Fully Offline**: No internet connection or API calls required
- **Fast Processing**: ≤10 seconds per 50-page PDF
- **Accurate Detection**: Multi-feature heading detection algorithm
- **Multilingual Support**: Handles English and Japanese documents
- **Robust Parsing**: Works with inconsistent formatting
- **Docker Ready**: Runs in linux/amd64 containers

## Architecture

The solution consists of four main modules:

### 1. PDF Parser (`pdf_parser.py`)
- Uses PyMuPDF (fitz) for fast PDF parsing
- Extracts text blocks with detailed font and positioning information
- Calculates document statistics for heading detection

### 2. Heading Detector (`heading_detector.py`)
- Multi-feature heuristic algorithm for heading detection
- Analyzes font size, weight, positioning, patterns, and keywords
- Assigns confidence scores and heading levels (H1, H2, H3)

### 3. Outline Extractor (`outline_extractor.py`)
- Creates structured JSON output from detected headings
- Removes duplicates and cleans heading text
- Maintains hierarchical structure

### 4. Main Processor (`main.py`)
- Orchestrates the entire pipeline
- Handles batch processing of multiple PDFs
- Provides logging and error handling

## Heading Detection Algorithm

The system uses multiple features to identify headings:

1. **Font Analysis**: Size relative to body text, bold formatting
2. **Positioning**: Left alignment, spacing above text
3. **Text Patterns**: Numbering schemes, capitalization patterns
4. **Keywords**: Common heading words in multiple languages
5. **Structure**: Document hierarchy and context

Each feature contributes to a weighted confidence score, with candidates above the threshold classified as headings.

## Usage

### Building the Docker Image

\`\`\`bash
docker build -t pdf-outline-extractor .
\`\`\`

### Running the Container

\`\`\`bash
docker run -v /path/to/input:/app/input -v /path/to/output:/app/output pdf-outline-extractor
\`\`\`

### Input/Output

- **Input**: Place PDF files in `/app/input` directory
- **Output**: JSON files generated in `/app/output` directory

### Output Format

\`\`\`json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
\`\`\`

## Technical Specifications

- **Platform**: linux/amd64
- **Runtime**: Python 3.10
- **Memory**: Optimized for 16GB RAM systems
- **CPU**: Utilizes up to 8 CPU cores
- **Model Size**: All components under 200MB
- **Dependencies**: PyMuPDF only (lightweight, fast)

## Performance

- **Speed**: ≤10 seconds per 50-page PDF
- **Accuracy**: High precision and recall for heading detection
- **Resource Efficient**: Minimal memory footprint
- **Scalable**: Handles batch processing efficiently

## Multilingual Support

The system includes built-in support for:
- **English**: Common academic and technical document patterns
- **Japanese**: Native heading keywords and text patterns
- **Extensible**: Easy to add support for additional languages

## Error Handling

- Graceful handling of corrupted or invalid PDFs
- Comprehensive logging for debugging
- Fallback mechanisms for edge cases
- Detailed error reporting

## Modular Design

The codebase is designed for extensibility:
- Clear separation of concerns
- Well-defined interfaces between modules
- Easy to add new features or detection algorithms
- Comprehensive documentation and type hints

This foundation makes it straightforward to extend the system with additional features in future iterations.
