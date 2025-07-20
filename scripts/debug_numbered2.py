import fitz

doc = fitz.open('app/input/file02.pdf')
for page_num, page in enumerate(doc, 1):
    text_blocks = page.get_text().split('\n')
    for i, line in enumerate(text_blocks):
        line = line.strip()
        if line in ['1.', '2.', '3.', '4.'] and i + 1 < len(text_blocks):
            next_line = text_blocks[i + 1].strip() if i + 1 < len(text_blocks) else ""
            next_next_line = text_blocks[i + 2].strip() if i + 2 < len(text_blocks) else ""
            print(f'Page {page_num}: "{line}" -> "{next_line}" -> "{next_next_line}"')
doc.close()
