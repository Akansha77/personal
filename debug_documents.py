"""
Debug script to check why only one document is being processed
"""
import json
import os

# Check input file
with open('Challenge_1b/Collection_1/challenge1b_input.json', 'r') as f:
    input_config = json.load(f)

print("=== INPUT DOCUMENTS ===")
documents = input_config.get('documents', [])
if documents and isinstance(documents[0], dict):
    doc_names = [doc['filename'] for doc in documents]
else:
    doc_names = documents

for i, doc in enumerate(doc_names):
    print(f"{i+1}. {doc}")
    pdf_path = f"Challenge_1b/Collection_1/PDFs/{doc}"
    exists = os.path.exists(pdf_path)
    print(f"   Exists: {exists}")

print(f"\nTotal documents in input: {len(doc_names)}")
print(f"Available PDF files: {len(os.listdir('Challenge_1b/Collection_1/PDFs'))}")
