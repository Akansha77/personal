import fitz

doc = fitz.open('app/input/file02.pdf')
for page_num, page in enumerate(doc, 1):
    blocks = page.get_text('dict')['blocks']
    for block in blocks:
        if 'lines' in block:
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if text and text.startswith(('1.', '2.', '3.', '4.')):
                        print(f'Page {page_num}: "{text}" (size: {span["size"]:.1f}, bold: {"bold" in str(span["flags"])}, font: {span["font"]})')
doc.close()
