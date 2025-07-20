from pdf_parser import PDFParser
from heading_detector import HeadingDetector

parser = PDFParser()
detector = HeadingDetector()

doc_data = parser.parse_pdf('app/input/file01.pdf')
if doc_data:
    candidates = detector.detect_headings(doc_data)
    print(f'File01 has {len(candidates)} candidates:')
    for c in candidates[:10]:
        print(f'  "{c.text_block.text[:60]}" (confidence: {c.confidence:.3f})')
else:
    print("Could not parse file01.pdf")
