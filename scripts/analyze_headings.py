"""
Debug script to understand heading detection process
Shows step-by-step how headings are identified and scored
"""
from pdf_parser import PDFParser
from heading_detector import HeadingDetector
import re

def analyze_heading_detection(pdf_file):
    print(f"\n{'='*60}")
    print(f"ANALYZING HEADING DETECTION FOR: {pdf_file}")
    print(f"{'='*60}")
    
    # Parse PDF
    parser = PDFParser()
    doc_data = parser.parse_pdf(f'app/input/{pdf_file}')
    
    if not doc_data:
        print("Failed to parse PDF")
        return
    
    print(f"\n📄 DOCUMENT INFO:")
    print(f"   Title: {doc_data.title}")
    print(f"   Total text blocks: {len(doc_data.text_blocks)}")
    print(f"   Average font size: {doc_data.avg_font_size:.1f}")
    
    # Get document stats  
    detector = HeadingDetector()
    stats = detector._calculate_document_stats(doc_data)
    
    print(f"\n📊 DOCUMENT STATISTICS:")
    print(f"   Body font size: {stats['body_font_size']:.1f}")
    print(f"   75th percentile font: {stats['font_size_75th']:.1f}")
    print(f"   90th percentile font: {stats['font_size_90th']:.1f}")
    print(f"   Max font size: {stats['max_font_size']:.1f}")
    
    print(f"\n🔍 TEXT BLOCK ANALYSIS (first 30 blocks):")
    print(f"{'#':>3} {'Page':>4} {'Font':>5} {'Bold':>4} {'X-Pos':>5} {'Potential':>9} {'Text'}")
    print("-" * 80)
    
    potential_headings = []
    
    for i, block in enumerate(doc_data.text_blocks[:30]):
        is_potential = detector._is_potential_heading(block, stats)
        if is_potential:
            potential_headings.append(block)
            
        print(f"{i:>3} {block.page_num:>4} {block.font_size:>5.1f} {'YES' if block.is_bold else 'NO':>4} {block.x_position:>5.0f} {'✅' if is_potential else '❌':>9} \"{block.text[:50]}{'...' if len(block.text) > 50 else ''}\"")
    
    if len(doc_data.text_blocks) > 30:
        print(f"... (showing first 30 of {len(doc_data.text_blocks)} total blocks)")
    
    print(f"\n🎯 POTENTIAL HEADINGS FOUND: {len(potential_headings)}")
    
    # Analyze each potential heading
    candidates = []
    for block in potential_headings:
        candidate = detector._analyze_heading_candidate(block, doc_data, stats)
        candidates.append(candidate)
    
    # Show detailed analysis
    print(f"\n📋 DETAILED CONFIDENCE ANALYSIS:")
    print(f"{'Text':<50} {'Conf':>5} {'Font':>5} {'Bold':>4} {'Pattern':>7} {'Keyword':>7} {'Numbered':>8}")
    print("-" * 95)
    
    for candidate in sorted(candidates, key=lambda x: x.confidence, reverse=True):
        features = candidate.features
        text = candidate.text_block.text[:47] + "..." if len(candidate.text_block.text) > 50 else candidate.text_block.text
        
        print(f"{text:<50} {candidate.confidence:>5.3f} {features.get('font_size', 0):>5.2f} {'YES' if features.get('bold', 0) > 0 else 'NO':>4} {features.get('pattern_match', 0):>7.2f} {features.get('keyword_match', 0):>7.2f} {features.get('numbered', 0):>8.2f}")
    
    # Show final headings (after threshold filter)
    final_candidates = [c for c in candidates if c.confidence > 0.15]
    print(f"\n✅ FINAL HEADINGS (confidence > 0.15): {len(final_candidates)}")
    
    for candidate in final_candidates:
        print(f"   • Page {candidate.text_block.page_num}: \"{candidate.text_block.text}\" (confidence: {candidate.confidence:.3f})")

# Test each file
files_to_analyze = ['file01.pdf', 'file02.pdf', 'file03.pdf', 'file04.pdf', 'file05.pdf']

for pdf_file in files_to_analyze:
    try:
        analyze_heading_detection(pdf_file)
    except Exception as e:
        print(f"Error analyzing {pdf_file}: {e}")
        
print(f"\n{'='*60}")
print("ANALYSIS COMPLETE")
print(f"{'='*60}")
