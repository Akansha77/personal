#!/usr/bin/env python3
"""
PDF Outline Extractor - Main processing script
Extracts structured outlines from PDFs in /app/input and outputs JSON to /app/output
"""

import os
import json
import time
import logging
from pathlib import Path

from typing import List, Dict, Any

from pdf_parser import PDFParser
from heading_detector import HeadingDetector
from outline_extractor import OutlineExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_pdf_file(input_path: str, output_path: str) -> bool:
    """Process a single PDF file and extract its outline."""
    try:
        start_time = time.time()
        logger.info(f"Starting processing: {os.path.basename(input_path)}")
        
        # Validate input file
        if not os.path.exists(input_path):
            logger.error(f"Input file does not exist: {input_path}")
            return False
            
        file_size = os.path.getsize(input_path)
        if file_size == 0:
            logger.error(f"Input file is empty: {input_path}")
            return False
            
        logger.debug(f"Processing PDF file: {file_size} bytes")
        
        # Parse PDF
        parser = PDFParser()
        document_data = parser.parse_pdf(input_path)
        
        if not document_data:
            logger.error(f"Failed to parse PDF: {input_path}")
            return False
        
        logger.debug(f"Parsed PDF with {document_data.page_count} pages, {len(document_data.text_blocks)} text blocks")
        
        # Detect headings
        detector = HeadingDetector()
        headings = detector.detect_headings(document_data)
        
        if not headings:
            logger.warning(f"No headings detected in: {input_path}")
            # Still create output with empty outline
            headings = []
        
        # Extract structured outline
        extractor = OutlineExtractor()
        outline = extractor.create_outline(document_data, headings)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to JSON with proper encoding
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(outline, f, indent=2, ensure_ascii=False)
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Processed {os.path.basename(input_path)} in {processing_time:.2f}s → {len(outline['outline'])} headings")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {input_path}: {str(e)}")
        return False

def main():
    """Main processing function."""
    input_dir = Path("C:/Users/ANSHU/personal/personal/scripts/app/input") 
    print(f"Resolved input directory path: {input_dir.resolve()}")     
    output_dir = Path("C:/Users/ANSHU/personal/personal/scripts/app/output")

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    success_count = 0
    total_start_time = time.time()
    
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.json"
        
        logger.info(f"Processing: {pdf_file.name}")
        
        if process_pdf_file(str(pdf_file), str(output_file)):
            success_count += 1
        else:
            logger.error(f"Failed to process: {pdf_file.name}")
    
    total_time = time.time() - total_start_time
    logger.info(f"Completed processing {success_count}/{len(pdf_files)} files in {total_time:.2f}s")

if __name__ == "__main__":
    main()
