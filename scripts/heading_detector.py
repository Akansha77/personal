"""
Heading Detection Module
Uses multiple heuristics to identify headings in PDF text blocks
"""

import re
import logging
from typing import List, Dict
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
        self.heading_patterns = [
            r'^\d+\.\s+[A-Z]',         # 1. Introduction (main sections)
            r'^\d+\.\d+\s+[A-Z]',      # 2.1 Intended Audience (subsections)
            r'^\d+\.\d+\.\d+\s+[A-Z]', # 2.1.1 Sub-subsections
            r'^[A-Z][A-Z\s]{2,}$',     # INTRODUCTION
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Introduction to AI
            r'^[IVX]+\.?\s+[A-Z]',     # Roman numerals
            r'^[A-Z]\.?\s+[A-Z]',      # A. Section
        ]

        self.heading_keywords = {
            'en': {'introduction', 'conclusion', 'abstract', 'summary', 'overview',
                   'background', 'methodology', 'results', 'discussion', 'references',
                   'chapter', 'section', 'appendix', 'bibliography', 'acknowledgements',
                   'table of contents', 'revision history', 'audience', 'career',
                   'learning', 'objectives', 'requirements', 'structure', 'duration',
                   'current', 'business', 'outcomes', 'content', 'trademarks', 
                   'documents', 'web sites'},
            'ja': {'はじめに', '序論', '概要', '背景', '方法', '結果', '考察', '結論',
                   '参考文献', '付録', '章', '節'},
        }

        self.stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                           'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through'}

        self.ignore_texts = {
            "page", "version", "copyright notice", "date", "time"
        }

    def detect_headings(self, doc_data: DocumentData) -> List[HeadingCandidate]:
        candidates = []
        stats = self._calculate_document_stats(doc_data)

        for block in doc_data.text_blocks:
            if self._is_potential_heading(block, stats):
                candidate = self._analyze_heading_candidate(block, doc_data, stats)
                
                # Debug: log numbered patterns
                text = block.text.strip()
                if re.match(r'^\d+\.\s+', text) or re.match(r'^\d+\.\d+\s+', text):
                    logger.info(f"Found numbered section: '{text}' - confidence: {candidate.confidence:.3f}")
                
                if candidate.confidence > 0.15:  # Lower threshold to catch more headings
                    candidates.append(candidate)

        candidates = self._assign_heading_levels(candidates, doc_data)
        candidates.sort(key=lambda x: (x.text_block.page_num, x.text_block.y_position))

        logger.info(f"Detected {len(candidates)} heading candidates")
        return candidates

    def _calculate_document_stats(self, doc_data: DocumentData) -> Dict:
        font_sizes = [block.font_size for block in doc_data.text_blocks]
        font_size_counts = Counter(font_sizes)
        body_font_size = font_size_counts.most_common(1)[0][0]
        sorted_sizes = sorted(font_sizes)
        n = len(sorted_sizes)

        return {
            'body_font_size': body_font_size,
            'avg_font_size': doc_data.avg_font_size,
            'font_size_75th': sorted_sizes[int(n * 0.75)] if n > 0 else 12,
            'font_size_90th': sorted_sizes[int(n * 0.9)] if n > 0 else 14,
            'max_font_size': max(font_sizes) if font_sizes else 12,
            'common_fonts': doc_data.common_fonts,
            'total_blocks': len(doc_data.text_blocks)
        }

    def _is_potential_heading(self, block: TextBlock, stats: Dict) -> bool:
        text = block.text.strip()

        if len(text) < 3:
            return False

        text_lower = text.lower()
        if text_lower in self.ignore_texts:
            return False

        # High priority headings - always include
        high_priority = [
            # Main numbered sections
            r'^\d+\.\s+\w+',  # "1. Introduction", "2. Introduction", etc.
            # Important document sections
            r'^(overview|foundation level|revision history|table of contents|acknowledgements|references)$',
            # Subsection patterns
            r'^\d+\.\d+\s+[A-Z]',  # "2.1 Intended Audience"
        ]
        
        for pattern in high_priority:
            if re.match(pattern, text, re.IGNORECASE):
                return True

        # Skip very long text that's likely body text
        if len(text) > 100:
            return False

        # Skip pure numbers, dates, and common non-headings
        if (text.isdigit() or 
            re.match(r'^\d+\s+\w+\s+\d{4}$', text) or  # dates like "18 JUNE 2013"
            text in ['Days', 'Syllabus', 'Identifier', 'Reference'] or
            '...........' in text):  # table of contents dots
            return False

        # For remaining text, require significant formatting difference
        if block.font_size > stats['body_font_size'] * 1.1 or block.is_bold:
            # Additional filters for formatted text
            if (text_lower.startswith(('this ', 'the ', 'in ', 'that ', 'each ', 'all ')) or
                text_lower.endswith((' is', ' are', ' will', ' can', ' may')) or
                len(text.split()) > 15):  # Too many words for a heading
                return False
            return True

        return False

    def _analyze_heading_candidate(self, block: TextBlock, doc_data: DocumentData, stats: Dict) -> HeadingCandidate:
        text = block.text.strip()
        features = {}

        size_ratio = block.font_size / stats['body_font_size']
        features['font_size'] = min(size_ratio - 1, 1.0) if size_ratio > 1 else 0
        features['bold'] = 1.0 if block.is_bold else 0.0
        features['left_aligned'] = 1.0 if block.x_position < 100 else 0.5
        features['top_spacing'] = self._calculate_top_spacing(block, doc_data)
        features['pattern_match'] = self._check_heading_patterns(text)
        features['keyword_match'] = self._check_heading_keywords(text)
        features['capitalization'] = self._check_capitalization(text)
        features['length'] = self._calculate_length_score(text)
        features['numbered'] = 1.0 if re.match(r'^\d+\.?\s+', text) or re.match(r'^\d+\.\d+\s+', text) else 0.0

        weights = {
            'font_size': 0.20,
            'bold': 0.15,
            'pattern_match': 0.20,
            'keyword_match': 0.15,
            'capitalization': 0.10,
            'numbered': 0.15,
            'left_aligned': 0.03,
            'top_spacing': 0.02
        }

        confidence = sum(features[key] * weights[key] for key in weights)

        return HeadingCandidate(
            text_block=block,
            confidence=confidence,
            level="H1",  # temp, assigned properly later
            features=features
        )

    def _calculate_top_spacing(self, block: TextBlock, doc_data: DocumentData) -> float:
        same_page_blocks = [b for b in doc_data.text_blocks if b.page_num == block.page_num]
        above_blocks = [b for b in same_page_blocks if b.y_position < block.y_position and abs(b.x_position - block.x_position) < 50]

        if not above_blocks:
            return 1.0

        closest_above = min(above_blocks, key=lambda b: block.y_position - b.y_position)
        spacing = block.y_position - (closest_above.y_position + closest_above.height)
        return min(spacing / 20.0, 1.0) if spacing > 0 else 0.0

    def _check_heading_patterns(self, text: str) -> float:
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return 1.0
        return 0.0

    def _check_heading_keywords(self, text: str) -> float:
        text_lower = text.lower()
        for keyword in self.heading_keywords['en']:
            if keyword in text_lower:
                return 1.0
        for keyword in self.heading_keywords['ja']:
            if keyword in text:
                return 1.0
        return 0.0

    def _check_capitalization(self, text: str) -> float:
        if text.isupper() and len(text) > 3:
            return 1.0
        words = text.split()
        if len(words) > 1:
            title_case_words = sum(1 for word in words if word[0].isupper() and word.lower() not in self.stop_words)
            return title_case_words / len(words)
        return 0.5 if text[0].isupper() else 0.0

    def _calculate_length_score(self, text: str) -> float:
        length = len(text)
        if length <= 50:
            return 1.0
        elif length <= 100:
            return 0.7
        elif length <= 150:
            return 0.3
        else:
            return 0.0

    def _assign_heading_levels(self, candidates: List[HeadingCandidate], doc_data: DocumentData) -> List[HeadingCandidate]:
        if not candidates:
            return candidates

        for candidate in candidates:
            text = candidate.text_block.text.strip()

            # Strict number pattern detection
            if re.match(r'^\d+\.\d+\.\d+\s+', text):  # e.g., 2.1.1
                candidate.level = "H3"
            elif re.match(r'^\d+\.\d+\s+', text):      # e.g., 2.1
                candidate.level = "H2"
            elif re.match(r'^\d+\s', text) or re.match(r'^\d+\.\s', text):  # e.g., 1 or 1.
                candidate.level = "H1"
            else:
                # fallback: font size
                if candidate.text_block.font_size > 1.2 * doc_data.avg_font_size:
                    candidate.level = "H1"
                else:
                    candidate.level = "H2"

        return sorted(candidates, key=lambda x: (x.text_block.page_num, x.text_block.y_position))


if __name__ == "__main__":
    # Test the heading detector with sample data
    from pdf_parser import PDFParser
    import os
    
    print("🔍 Testing Heading Detector...")
    
    # Check if test files exist
    input_dir = "app/input"
    if os.path.exists(input_dir):
        pdf_files = [f for f in os.listdir(input_dir) if f.endswith('.pdf')]
        
        if pdf_files:
            test_file = os.path.join(input_dir, pdf_files[0])
            print(f"📄 Testing with: {pdf_files[0]}")
            
            # Parse PDF
            parser = PDFParser()
            doc_data = parser.parse_pdf(test_file)
            
            if doc_data:
                print(f"📊 Document Stats:")
                print(f"   - Pages: {doc_data.page_count}")
                print(f"   - Text blocks: {len(doc_data.text_blocks)}")
                print(f"   - Average font size: {doc_data.avg_font_size:.2f}")
                print(f"   - Title: {doc_data.title}")
                
                # Detect headings
                detector = HeadingDetector()
                headings = detector.detect_headings(doc_data)
                
                print(f"\n🎯 Detected {len(headings)} headings:")
                for i, heading in enumerate(headings, 1):
                    print(f"   {i}. [{heading.level}] {heading.text_block.text[:50]}{'...' if len(heading.text_block.text) > 50 else ''}")
                    print(f"      Page: {heading.text_block.page_num}, Confidence: {heading.confidence:.3f}")
                
            else:
                print("❌ Failed to parse PDF")
        else:
            print("❌ No PDF files found in app/input")
    else:
        print("❌ Input directory not found")
        
    print("\n✅ Heading Detector test complete!")
