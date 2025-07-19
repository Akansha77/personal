"""
Heading Detection Module
Uses multiple heuristics to identify headings in PDF text blocks
"""

import re
import logging
from typing import List, Dict, Set
from collections import Counter
from dataclasses import dataclass

from pdf_parser import DocumentData, TextBlock

logger = logging.getLogger(__name__)

@dataclass
class HeadingCandidate:
    """Represents a potential heading with confidence score."""
    text_block: TextBlock
    confidence: float
    level: str  # H1, H2, H3
    features: Dict[str, float]

class HeadingDetector:
    """Detects headings using multiple heuristic features."""
    
    def __init__(self):
        # Heading patterns (case-insensitive)
        self.heading_patterns = [
            r'^\d+\.?\s+[A-Z]',  # "1. Introduction" or "1 Introduction"
            r'^[A-Z][A-Z\s]{2,}$',  # "INTRODUCTION"
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # "Introduction to AI"
            r'^\d+\.\d+\.?\s+',  # "1.1 Subsection"
            r'^[IVX]+\.?\s+[A-Z]',  # Roman numerals
            r'^[A-Z]\.?\s+[A-Z]',  # "A. Section"
        ]
        
        # Common heading words (multilingual support)
        self.heading_keywords = {
            'en': {'introduction', 'conclusion', 'abstract', 'summary', 'overview', 
                   'background', 'methodology', 'results', 'discussion', 'references',
                   'chapter', 'section', 'appendix', 'bibliography'},
            'ja': {'はじめに', '序論', '概要', '背景', '方法', '結果', '考察', '結論', 
                   '参考文献', '付録', '章', '節'},
        }
        
        # Stop words to exclude
        self.stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                          'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through'}
    
    def detect_headings(self, doc_data: DocumentData) -> List[HeadingCandidate]:
        """Detect headings in document using multiple heuristics."""
        candidates = []
        
        # Calculate document statistics
        stats = self._calculate_document_stats(doc_data)
        
        # Analyze each text block
        for block in doc_data.text_blocks:
            if self._is_potential_heading(block, stats):
                candidate = self._analyze_heading_candidate(block, doc_data, stats)
                if candidate.confidence > 0.3:  # Minimum confidence threshold
                    candidates.append(candidate)
        
        # Post-process and assign levels
        candidates = self._assign_heading_levels(candidates)
        
        # Sort by page and position
        candidates.sort(key=lambda x: (x.text_block.page_num, x.text_block.y_position))
        
        logger.info(f"Detected {len(candidates)} heading candidates")
        return candidates
    
    def _calculate_document_stats(self, doc_data: DocumentData) -> Dict:
        """Calculate document-wide statistics for comparison."""
        font_sizes = [block.font_size for block in doc_data.text_blocks]
        font_size_counts = Counter(font_sizes)
        
        # Find most common (body) font size
        body_font_size = font_size_counts.most_common(1)[0][0]
        
        # Calculate percentiles
        sorted_sizes = sorted(font_sizes)
        n = len(sorted_sizes)
        
        stats = {
            'body_font_size': body_font_size,
            'avg_font_size': doc_data.avg_font_size,
            'font_size_75th': sorted_sizes[int(n * 0.75)] if n > 0 else 12,
            'font_size_90th': sorted_sizes[int(n * 0.9)] if n > 0 else 14,
            'max_font_size': max(font_sizes) if font_sizes else 12,
            'common_fonts': doc_data.common_fonts,
            'total_blocks': len(doc_data.text_blocks)
        }
        
        return stats
    
    def _is_potential_heading(self, block: TextBlock, stats: Dict) -> bool:
        """Quick filter for potential headings."""
        text = block.text.strip()
        
        # Basic filters
        if len(text) < 3 or len(text) > 200:
            return False
        
        # Must be significantly larger than body text or bold
        if block.font_size <= stats['body_font_size'] and not block.is_bold:
            return False
        
        # Skip if looks like body text (too long, ends with period)
        if len(text) > 100 and text.endswith('.'):
            return False
        
        return True
    
    def _analyze_heading_candidate(self, block: TextBlock, doc_data: DocumentData, 
                                 stats: Dict) -> HeadingCandidate:
        """Analyze a text block and calculate heading confidence."""
        features = {}
        text = block.text.strip()
        
        # Font size feature (0-1)
        size_ratio = block.font_size / stats['body_font_size']
        features['font_size'] = min(size_ratio - 1, 1.0) if size_ratio > 1 else 0
        
        # Bold feature
        features['bold'] = 1.0 if block.is_bold else 0.0
        
        # Position features
        features['left_aligned'] = 1.0 if block.x_position < 100 else 0.5
        features['top_spacing'] = self._calculate_top_spacing(block, doc_data)
        
        # Text pattern features
        features['pattern_match'] = self._check_heading_patterns(text)
        features['keyword_match'] = self._check_heading_keywords(text)
        features['capitalization'] = self._check_capitalization(text)
        features['length'] = self._calculate_length_score(text)
        
        # Numbering feature
        features['numbered'] = 1.0 if re.match(r'^\d+\.?\s+', text) else 0.0
        
        # Calculate weighted confidence
        weights = {
            'font_size': 0.25,
            'bold': 0.20,
            'pattern_match': 0.15,
            'keyword_match': 0.10,
            'capitalization': 0.10,
            'numbered': 0.10,
            'left_aligned': 0.05,
            'top_spacing': 0.05
        }
        
        confidence = sum(features[key] * weights[key] for key in weights)
        
        return HeadingCandidate(
            text_block=block,
            confidence=confidence,
            level="H1",  # Will be assigned later
            features=features
        )
    
    def _calculate_top_spacing(self, block: TextBlock, doc_data: DocumentData) -> float:
        """Calculate spacing above the text block."""
        same_page_blocks = [b for b in doc_data.text_blocks if b.page_num == block.page_num]
        
        # Find blocks above this one
        above_blocks = [b for b in same_page_blocks 
                       if b.y_position < block.y_position and 
                       abs(b.x_position - block.x_position) < 50]
        
        if not above_blocks:
            return 1.0  # Top of page
        
        closest_above = min(above_blocks, key=lambda b: block.y_position - b.y_position)
        spacing = block.y_position - (closest_above.y_position + closest_above.height)
        
        # Normalize spacing (larger spacing = higher score)
        return min(spacing / 20.0, 1.0) if spacing > 0 else 0.0
    
    def _check_heading_patterns(self, text: str) -> float:
        """Check if text matches common heading patterns."""
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return 1.0
        return 0.0
    
    def _check_heading_keywords(self, text: str) -> float:
        """Check if text contains heading keywords."""
        text_lower = text.lower()
        
        # Check English keywords
        for keyword in self.heading_keywords['en']:
            if keyword in text_lower:
                return 1.0
        
        # Check Japanese keywords
        for keyword in self.heading_keywords['ja']:
            if keyword in text:
                return 1.0
        
        return 0.0
    
    def _check_capitalization(self, text: str) -> float:
        """Analyze capitalization patterns."""
        if text.isupper() and len(text) > 3:
            return 1.0
        
        # Title case
        words = text.split()
        if len(words) > 1:
            title_case_words = sum(1 for word in words 
                                 if word[0].isupper() and word.lower() not in self.stop_words)
            return title_case_words / len(words)
        
        return 0.5 if text[0].isupper() else 0.0
    
    def _calculate_length_score(self, text: str) -> float:
        """Calculate score based on text length (headings are usually short)."""
        length = len(text)
        if length <= 50:
            return 1.0
        elif length <= 100:
            return 0.7
        elif length <= 150:
            return 0.3
        else:
            return 0.0
    
    def _assign_heading_levels(self, candidates: List[HeadingCandidate]) -> List[HeadingCandidate]:
        """Assign H1, H2, H3 levels based on font size and structure."""
        if not candidates:
            return candidates
        
        # Sort by font size (descending) and confidence
        sorted_candidates = sorted(candidates, 
                                 key=lambda x: (x.text_block.font_size, x.confidence), 
                                 reverse=True)
        
        # Group by font size
        font_sizes = [c.text_block.font_size for c in sorted_candidates]
        unique_sizes = sorted(set(font_sizes), reverse=True)
        
        # Assign levels based on font size tiers
        for candidate in candidates:
            size = candidate.text_block.font_size
            
            if len(unique_sizes) >= 3:
                if size >= unique_sizes[0]:
                    candidate.level = "H1"
                elif size >= unique_sizes[1]:
                    candidate.level = "H2"
                else:
                    candidate.level = "H3"
            elif len(unique_sizes) >= 2:
                if size >= unique_sizes[0]:
                    candidate.level = "H1"
                else:
                    candidate.level = "H2"
            else:
                candidate.level = "H1"
        
        return candidates
