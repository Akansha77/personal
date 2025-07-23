import json
import os

# Test file path
file_path = "Challenge_1b/Collection_1/challenge1b_input.json"
print(f"Trying to read: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    print("File contents:")
    print(json.dumps(data, indent=2))
else:
    print("File not found!")
    
# Try absolute path
abs_path = os.path.abspath(file_path)
print(f"Absolute path: {abs_path}")
print(f"Absolute exists: {os.path.exists(abs_path)}")
