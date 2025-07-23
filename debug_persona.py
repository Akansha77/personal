"""
Debug script to test persona parsing
"""
import sys
sys.path.append('scripts')

import json
from persona_driven_analyzer import PersonaAnalyzer, JobAnalyzer

# Load the actual input
with open('Challenge_1b/Collection_1/challenge1b_input.json', 'r') as f:
    input_config = json.load(f)

print("=== INPUT CONFIG ===")
print(json.dumps(input_config, indent=2))

# Test persona parsing
persona_analyzer = PersonaAnalyzer()
persona_text = input_config['persona']['role'] if isinstance(input_config['persona'], dict) else str(input_config['persona'])
print(f"\n=== PERSONA TEXT ===")
print(f"'{persona_text}'")

persona = persona_analyzer.parse_persona(persona_text)
print(f"\n=== PARSED PERSONA ===")
print(f"Role: {persona.role}")
print(f"Expertise areas: {persona.expertise_areas}")
print(f"Focus keywords: {persona.focus_keywords}")

# Test job parsing
job_analyzer = JobAnalyzer()
job_text = input_config['job_to_be_done']['task'] if isinstance(input_config['job_to_be_done'], dict) else str(input_config['job_to_be_done'])
print(f"\n=== JOB TEXT ===")
print(f"'{job_text}'")

job = job_analyzer.parse_job(job_text)
print(f"\n=== PARSED JOB ===")
print(f"Task: {job.task_description}")
print(f"Content types: {job.required_content_types}")
print(f"Priority keywords: {job.priority_keywords}")
print(f"Output type: {job.expected_output_type}")

# Test document list parsing
documents = input_config.get('documents', [])
if documents and isinstance(documents[0], dict):
    doc_names = [doc['filename'] for doc in documents]
else:
    doc_names = documents

print(f"\n=== DOCUMENT NAMES ===")
for doc in doc_names:
    print(f"  - {doc}")
