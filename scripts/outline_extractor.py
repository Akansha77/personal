"""
Outline Extraction Module
Creates structured JSON outline from detected headings
"""

import logging
from typing import List, Dict, Any

from pdf_parser import DocumentData
from heading_detector import HeadingCandidate

logger = logging.getLogger(__name__)

class OutlineExtractor:
    """Extracts structured outline from heading candidates."""
    
    def create_outline(self, doc_data: DocumentData, 
                      headings: List[HeadingCandidate]) -> Dict[str, Any]:
        """Create structured outline JSON."""
        
        outline_items = []
        
        for heading in headings:
            item = {
                "level": heading.level,
                "text": self._clean_heading_text(heading.text_block.text),
                "page": heading.text_block.page_num
            }
            outline_items.append(item)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_items = []
        for item in outline_items:
            key = (item["level"], item["text"], item["page"])
            if key not in seen:
                seen.add(key)
                unique_items.append(item)
        
        result = {
            "title": doc_data.title,
            "outline": unique_items
        }
        
        logger.info(f"Created outline with {len(unique_items)} headings")
        return result
    
    def _clean_heading_text(self, text: str) -> str:
        """Clean and normalize heading text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove trailing punctuation except for specific cases
        if text.endswith(('.', ':', ';', ',')):
            text = text[:-1]
        
        return text.strip()
