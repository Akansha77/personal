# Challenge 1B: Persona-Driven Document Intelligence

## Overview
This system extracts and prioritizes the most relevant sections from document collections based on a specific persona and their job-to-be-done.

## Workflow

### 1. Input Structure
```
Challenge_1b/
├── Collection_1/
│   ├── PDFs/
│   │   ├── doc1.pdf
│   │   ├── doc2.pdf
│   │   └── doc3.pdf
│   ├── challenge1b_input.json
│   └── challenge1b_output.json (expected)
├── Collection_2/
└── Collection_3/
```

### 2. Input Format (challenge1b_input.json)
```json
{
  "documents": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
  "persona": "PhD Researcher in Computational Biology",
  "job_to_be_done": "Prepare comprehensive literature review focusing on methodologies, datasets, and performance benchmarks"
}
```

### 3. Processing Steps
1. **Parse Input**: Extract persona characteristics and job requirements
2. **Document Processing**: Use existing PDF parser and heading detector from Round 1A  
3. **Relevance Scoring**: Score each section based on persona needs and job requirements
4. **Section Ranking**: Rank sections by importance for the specific use case
5. **Output Generation**: Create structured JSON with top relevant sections

### 4. Output Format (challenge1b_output.json)
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf", "doc3.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare comprehensive literature review...",
    "processing_timestamp": "2025-01-22T10:30:00Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "section_title": "Graph Neural Network Architectures",
      "importance_rank": 1
    }
  ],
  "sub_section_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "This section presents novel architectures...",
      "page_number": 3
    }
  ]
}
```

## How to Test

### Step 1: Prepare Test Data
1. Create collections in `Challenge_1b/Collection_X/`
2. Add PDF documents to `PDFs/` subfolder
3. Create `challenge1b_input.json` with persona and job description

### Step 2: Run Analysis
```bash
python persona_driven_analyzer.py
```

### Step 3: Verify Results
- Check generated `challenge1b_output_generated.json`
- Compare with expected `challenge1b_output.json`
- Validate relevance rankings make sense for the persona

## Key Components

1. **PersonaAnalyzer**: Extracts role, expertise areas, and focus keywords
2. **JobAnalyzer**: Identifies required content types and priority keywords  
3. **RelevanceScorer**: Scores sections based on persona needs and job requirements
4. **PersonaDrivenAnalyzer**: Orchestrates the entire process

## Scoring Strategy

- **Section Relevance (60%)**: How well sections match persona + job requirements
- **Sub-section Relevance (40%)**: Quality of granular analysis and ranking

## Technical Constraints

- CPU only processing
- Model size ≤ 1GB  
- Processing time ≤ 60 seconds for 3-5 documents
- No internet access during execution
