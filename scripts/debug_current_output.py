import json

with open('app/output/file02.json') as f:
    data = json.load(f)
    
print(f"Title: {data['title']}")
print(f"Number of headings: {len(data['outline'])}")
print("\nHeadings:")
for item in data['outline']:
    print(f"Level: {item['level']}, Text: \"{item['text']}\"")
