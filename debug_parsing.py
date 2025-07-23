"""
Debug the document parsing in persona analyzer
"""
import json

# Load and parse like the system does
with open('Challenge_1b/Collection_1/challenge1b_input.json', 'r') as f:
    input_config = json.load(f)

print("=== RAW INPUT CONFIG ===")
print(json.dumps(input_config['documents'][:2], indent=2))

# Simulate the parsing logic
documents = input_config.get('documents', [])
print(f"\nTotal documents found: {len(documents)}")

if documents and isinstance(documents[0], dict):
    # New format with filename/title objects
    doc_names = [doc['filename'] for doc in documents]
    print("Using new format (filename/title objects)")
else:
    # Old format with simple list
    doc_names = documents
    print("Using old format (simple list)")

print("\nExtracted document names:")
for i, name in enumerate(doc_names):
    print(f"{i+1}. {name}")

print(f"\nTotal extracted: {len(doc_names)}")
