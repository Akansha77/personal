"""
PDF Parser Module
Handles PDF parsing and text extraction with detailed font and positioning information
"""

import fitz  # PyMuPDF
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TextBlock:
    """Represents a text block with formatting and position information."""
    text: str
    page_num: int
    bbox: tuple  # (x0, y0, x1, y1)
    font_name: str
    font_size: float
    font_flags: int  # Bold, italic, etc.
    line_height: float
    
    @property
    def is_bold(self) -> bool:
        """Check if text is bold."""
        return bool(self.font_flags & 2**4)
    
    @property
    def is_italic(self) -> bool:
        """Check if text is italic."""
        return bool(self.font_flags & 2**1)
    
    @property
    def x_position(self) -> float:
        """Get x position (left edge)."""
        return self.bbox[0]
    
    @property
    def y_position(self) -> float:
        """Get y position (top edge)."""
        return self.bbox[1]
    
    @property
    def width(self) -> float:
        """Get text width."""
        return self.bbox[2] - self.bbox[0]
    
    @property
    def height(self) -> float:
        """Get text height."""
        return self.bbox[3] - self.bbox[1]

@dataclass
class DocumentData:
    """Container for parsed document data."""
    title: str
    text_blocks: List[TextBlock]
    page_count: int
    avg_font_size: float
    common_fonts: Dict[str, int]

class PDFParser:
    """PDF parsing class using PyMuPDF."""
    
    def __init__(self):
        self.min_font_size = 6.0  # Ignore very small text
        self.max_font_size = 72.0  # Ignore very large text
    
    def parse_pdf(self, pdf_path: str) -> Optional[DocumentData]:
        """Parse PDF and extract structured text data."""
        try:
            doc = fitz.open(pdf_path)
            
            if doc.page_count == 0:
                logger.warning(f"PDF has no pages: {pdf_path}")
                return None
            
            # Extract title from metadata or first page
            title = self._extract_title(doc)
            
            # Extract all text blocks
            text_blocks = []
            font_sizes = []
            font_counts = {}
            
            for page_num in range(min(doc.page_count, 50)):  # Limit to 50 pages
                page = doc[page_num]
                blocks = self._extract_page_blocks(page, page_num + 1)
                text_blocks.extend(blocks)
                
                # Collect font statistics
                for block in blocks:
                    font_sizes.append(block.font_size)
                    font_counts[block.font_name] = font_counts.get(block.font_name, 0) + 1
            
            doc.close()
            
            if not text_blocks:
                logger.warning(f"No text blocks found in PDF: {pdf_path}")
                return None
            
            # Calculate average font size
            avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12.0
            
            return DocumentData(
                title=title,
                text_blocks=text_blocks,
                page_count=min(doc.page_count, 50),
                avg_font_size=avg_font_size,
                common_fonts=font_counts
            )
            
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {str(e)}")
            return None
    
    def _extract_title(self, doc: fitz.Document) -> str:
        """Extract document title from metadata or first page."""
        # Try metadata first
        metadata = doc.metadata
        if metadata.get('title'):
            return metadata['title'].strip()
        
        # Try first page - look for largest text or first line
        if doc.page_count > 0:
            page = doc[0]
            blocks = page.get_text("dict")
            
            largest_text = ""
            largest_size = 0
            
            for block in blocks.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            size = span.get("size", 0)
                            
                            if text and size > largest_size and len(text) > 3:
                                largest_text = text
                                largest_size = size
            
            if largest_text:
                return largest_text
        
        return "Untitled Document"
    
    def _extract_page_blocks(self, page: fitz.Page, page_num: int) -> List[TextBlock]:
        """Extract text blocks from a single page."""
        blocks = []
        
        try:
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" not in block:
                    continue
                
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        
                        if not text or len(text) < 2:
                            continue
                        
                        font_size = span.get("size", 12.0)
                        
                        # Filter by font size
                        if font_size < self.min_font_size or font_size > self.max_font_size:
                            continue
                        
                        bbox = span.get("bbox", (0, 0, 0, 0))
                        font_name = span.get("font", "unknown")
                        font_flags = span.get("flags", 0)
                        
                        # Calculate line height from bbox
                        line_height = bbox[3] - bbox[1] if bbox[3] > bbox[1] else font_size
                        
                        block = TextBlock(
                            text=text,
                            page_num=page_num,
                            bbox=bbox,
                            font_name=font_name,
                            font_size=font_size,
                            font_flags=font_flags,
                            line_height=line_height
                        )
                        
                        blocks.append(block)
        
        except Exception as e:
            logger.error(f"Error extracting blocks from page {page_num}: {str(e)}")
        
        return blocks
