import json

# Check file01.json
with open('app/output/file01.json') as f:
    data1 = json.load(f)

print("=== FILE01.JSON ===")
print(f"Title: {data1['title']}")
print(f"Headings: {len(data1['outline'])}")
for item in data1['outline']:
    print(f"  {item['level']}: \"{item['text']}\" (page {item['page']})")

print()

# Check file02.json  
with open('app/output/file02.json') as f:
    data2 = json.load(f)

print("=== FILE02.JSON ===")
print(f"Title: {data2['title']}")
print(f"Headings: {len(data2['outline'])}")
for item in data2['outline']:
    print(f"  {item['level']}: \"{item['text']}\" (page {item['page']})")
