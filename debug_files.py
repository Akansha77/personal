"""
Test reading all 7 documents
"""
import json
import os

with open('Challenge_1b/Collection_1/challenge1b_input.json', 'r') as f:
    input_config = json.load(f)

documents = input_config.get('documents', [])
doc_names = [doc['filename'] for doc in documents]

print(f"Documents in input file: {len(doc_names)}")
for i, doc_name in enumerate(doc_names):
    print(f"{i+1}. '{doc_name}'")
    
pdf_path = 'Challenge_1b/Collection_1/PDFs'
print(f"\nChecking file existence:")
for doc_name in doc_names:
    doc_path = os.path.join(pdf_path, doc_name)
    exists = os.path.exists(doc_path)
    print(f"'{doc_name}' -> {exists}")
    if not exists:
        print(f"   Full path: {doc_path}")

# List all files in PDFs directory  
print(f"\nAll files in PDFs directory:")
all_files = os.listdir(pdf_path)
for i, f in enumerate(all_files):
    print(f"{i+1}. '{f}'")
