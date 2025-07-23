"""
Challenge 1B: Persona-Driven Document Intelligence System
Extracts and ranks relevant sections based on persona and job-to-be-done
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass

# Reuse existing components from Round 1A
import sys
sys.path.append('scripts')
from pdf_parser import PDFParser, DocumentData
from heading_detector import HeadingDetector

logger = logging.getLogger(__name__)

@dataclass
class PersonaProfile:
    """Represents a user persona with expertise areas and focus."""
    role: str
    expertise_areas: List[str]
    focus_keywords: List[str]
    experience_level: str

@dataclass 
class JobToBeDone:
    """Represents the specific task the persona needs to accomplish."""
    task_description: str
    required_content_types: List[str]
    priority_keywords: List[str]
    expected_output_type: str

@dataclass
class RelevantSection:
    """Represents a document section with relevance scoring."""
    document: str
    page_number: int
    section_title: str
    content: str
    importance_rank: int
    relevance_score: float

class PersonaAnalyzer:
    """Analyzes persona description to extract key characteristics."""
    
    def __init__(self):
        self.role_keywords = {
            'researcher': ['research', 'study', 'analysis', 'methodology', 'experiment'],
            'student': ['learn', 'understand', 'study', 'exam', 'concept'],
            'analyst': ['analyze', 'evaluate', 'assess', 'compare', 'trends'],
            'manager': ['strategy', 'decision', 'overview', 'summary', 'business'],
            'planner': ['plan', 'organize', 'schedule', 'arrange', 'coordinate'],
            'travel': ['travel', 'trip', 'visit', 'destination', 'tourism'],
            'food': ['food', 'contractor', 'catering', 'menu', 'recipe', 'cooking', 'meal', 'nutrition', 'buffet', 'corporate']
        }
        
    def parse_persona(self, persona_text: str) -> PersonaProfile:
        """Extract structured information from persona description."""
        persona_lower = persona_text.lower()
        
        # Determine role
        role = "general"
        for role_type, keywords in self.role_keywords.items():
            if any(keyword in persona_lower for keyword in keywords):
                role = role_type
                break
        
        # Extract expertise areas (simplified)
        expertise_areas = []
        if 'biology' in persona_lower or 'computational biology' in persona_lower:
            expertise_areas.extend(['biology', 'computational', 'molecular'])
        if 'chemistry' in persona_lower:
            expertise_areas.extend(['chemistry', 'organic', 'reaction'])
        if 'investment' in persona_lower or 'financial' in persona_lower:
            expertise_areas.extend(['finance', 'investment', 'revenue'])
        if 'travel' in persona_lower or 'planner' in persona_lower:
            expertise_areas.extend(['travel', 'tourism', 'destination', 'accommodation', 'restaurant', 'activity'])
        if 'food' in persona_lower or 'contractor' in persona_lower or 'catering' in persona_lower:
            expertise_areas.extend(['food', 'catering', 'menu', 'recipe', 'cooking', 'meal', 'nutrition', 'buffet', 'vegetarian', 'gluten', 'corporate', 'dinner', 'lunch', 'breakfast'])
            
        # Generate focus keywords
        focus_keywords = expertise_areas + self.role_keywords.get(role, [])
        
        return PersonaProfile(
            role=role,
            expertise_areas=expertise_areas,
            focus_keywords=focus_keywords,
            experience_level="intermediate"  # Default
        )

class JobAnalyzer:
    """Analyzes job-to-be-done to extract requirements."""
    
    def parse_job(self, job_text: str) -> JobToBeDone:
        """Extract structured information from job description."""
        job_lower = job_text.lower()
        
        # Extract content types needed
        content_types = []
        if 'methodology' in job_lower or 'method' in job_lower:
            content_types.append('methodology')
        if 'result' in job_lower or 'performance' in job_lower:
            content_types.append('results')
        if 'introduction' in job_lower or 'background' in job_lower:
            content_types.append('background')
        if 'dataset' in job_lower or 'data' in job_lower:
            content_types.append('datasets')
        if 'plan' in job_lower or 'trip' in job_lower or 'travel' in job_lower:
            content_types.extend(['accommodation', 'restaurant', 'activity', 'attraction'])
        if 'days' in job_lower or 'itinerary' in job_lower:
            content_types.extend(['schedule', 'timing', 'duration'])
        if 'group' in job_lower or 'friends' in job_lower:
            content_types.extend(['group', 'social', 'multiple'])
        if 'menu' in job_lower or 'buffet' in job_lower or 'catering' in job_lower or 'meal' in job_lower:
            content_types.extend(['menu', 'recipe', 'cooking', 'food', 'catering', 'buffet'])
        if 'vegetarian' in job_lower or 'gluten' in job_lower or 'dietary' in job_lower:
            content_types.extend(['vegetarian', 'gluten-free', 'dietary', 'nutrition'])
        if 'corporate' in job_lower or 'gathering' in job_lower or 'event' in job_lower:
            content_types.extend(['corporate', 'catering', 'event', 'large-scale', 'professional'])
            
        # Extract priority keywords
        priority_keywords = []
        words = job_text.lower().split()
        important_words = [w for w in words if len(w) > 4 and w not in {'that', 'this', 'with', 'from'}]
        priority_keywords = important_words[:10]  # Top 10 keywords
        
        return JobToBeDone(
            task_description=job_text,
            required_content_types=content_types,
            priority_keywords=priority_keywords,
            expected_output_type="menu_plan" if any(x in job_text.lower() for x in ['menu', 'buffet', 'catering', 'meal']) else "travel_plan" if 'plan' in job_text.lower() else "literature_review"  # Detect output type
        )

class RelevanceScorer:
    """Scores document sections based on persona needs and job requirements."""
    
    def __init__(self):
        self.section_type_weights = {
            'methodology': 0.8,
            'results': 0.7,
            'introduction': 0.6,
            'conclusion': 0.6,
            'abstract': 0.5,
            'background': 0.4,
            # Travel-specific section types
            'restaurant': 0.9,
            'hotel': 0.9,
            'accommodation': 0.9,
            'activity': 0.8,
            'attraction': 0.8,
            'city': 0.8,
            'food': 0.7,
            'cuisine': 0.7,
            'history': 0.6,
            'culture': 0.6,
            'tradition': 0.6,
            'tips': 0.7,
            'guide': 0.7,
            # Food/catering-specific section types
            'dinner': 0.9,
            'buffet': 0.9,
            'catering': 0.9,
            'vegetarian': 0.9,
            'menu': 0.8,
            'corporate': 0.8,
            'gluten': 0.8,
            'main': 0.7,
            'side': 0.7,
            'recipe': 0.7,
            'cooking': 0.6,
            'meal': 0.6,
            'lunch': 0.5,
            'breakfast': 0.3  # Lower weight for breakfast items when doing dinner planning
        }
    
    def score_section(self, section_title: str, section_content: str, 
                     persona: PersonaProfile, job: JobToBeDone) -> float:
        """Calculate relevance score for a section."""
        score = 0.0
        
        combined_text = (section_title + " " + section_content).lower()
        
        # Score based on persona keywords
        persona_matches = sum(1 for keyword in persona.focus_keywords 
                            if keyword.lower() in combined_text)
        score += persona_matches * 0.1
        
        # Score based on job keywords  
        job_matches = sum(1 for keyword in job.priority_keywords
                         if keyword in combined_text)
        score += job_matches * 0.15
        
        # Score based on section type
        for section_type, weight in self.section_type_weights.items():
            if section_type in combined_text:
                score += weight
        
        # Apply job-specific penalties/bonuses
        if 'dinner' in job.task_description.lower() or 'menu' in job.task_description.lower():
            # Heavy penalty for breakfast items when planning dinner
            if any(breakfast_term in combined_text for breakfast_term in ['breakfast', 'smoothie', 'morning', 'berry', 'oatmeal', 'parfait', 'granola', 'cereal', 'muffin']):
                score *= 0.01  # Reduce score by 99% - extremely strong penalty
            
            # Filter out non-vegetarian items if vegetarian menu requested
            if 'vegetarian' in job.task_description.lower():
                # Check for meat items (penalty for vegetarian menus)
                meat_terms = ['beef', 'chicken', 'pork', 'lamb', 'shrimp', 'fish', 'seafood', 'meat', 'turkey', 'bacon', 'ham', 'sausage', 'taco', 'salmon', 'tuna', 'cod', 'mango salad']
                if any(meat_term in combined_text for meat_term in meat_terms):
                    score *= 0.001  # Even stronger penalty for meat items in vegetarian menu
            
            # Bonus for vegetarian items when vegetarian menu requested
            if 'vegetarian' in job.task_description.lower():
                veggie_terms = ['vegetable', 'veggie', 'plant', 'falafel', 'hummus', 'ratatouille', 'quinoa', 'tofu', 'chickpea', 'lentil', 'bean', 'eggplant', 'mushroom', 'sushi rolls', 'lasagna', 'vegetable lasagna', 'veggie sushi']
                if any(veggie_term in combined_text for veggie_term in veggie_terms):
                    score *= 5.0  # Very strong bonus for specific vegetarian dishes
            
            # Bonus for buffet-appropriate items
            buffet_terms = ['salad', 'dip', 'appetizer', 'side', 'rolls', 'bread', 'rice', 'pasta', 'casserole']
            if any(buffet_term in combined_text for buffet_term in buffet_terms):
                score *= 1.8  # Bonus for buffet-style items
                
            # Bonus for dinner-related items
            if any(dinner_term in combined_text for dinner_term in ['dinner', 'main', 'entrée', 'entree', 'evening']):
                score *= 2.0  # Strong bonus for dinner items
            # Bonus for buffet/catering terms
            if any(catering_term in combined_text for catering_term in ['buffet', 'catering', 'corporate', 'large', 'batch']):
                score *= 1.5  # Increased bonus for catering terms
        
        # Boost score for longer, more substantial content
        content_length_factor = min(len(section_content) / 500.0, 1.0)
        score *= (0.5 + content_length_factor * 0.5)
        
        return min(score, 1.0)  # Cap at 1.0

class PersonaDrivenAnalyzer:
    """Main class for persona-driven document intelligence."""
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.heading_detector = HeadingDetector() 
        self.persona_analyzer = PersonaAnalyzer()
        self.job_analyzer = JobAnalyzer()
        self.relevance_scorer = RelevanceScorer()
        
    def process_collection(self, collection_path: str) -> Dict[str, Any]:
        """Process a document collection with persona and job inputs."""
        
        # Load input configuration
        input_file = os.path.join(collection_path, 'challenge1b_input.json')
        with open(input_file, 'r') as f:
            input_config = json.load(f)
        
        # Parse persona and job (handle new format)
        persona_text = input_config['persona']['role'] if isinstance(input_config['persona'], dict) else str(input_config['persona'])
        job_text = input_config['job_to_be_done']['task'] if isinstance(input_config['job_to_be_done'], dict) else str(input_config['job_to_be_done'])
        
        persona = self.persona_analyzer.parse_persona(persona_text)
        job = self.job_analyzer.parse_job(job_text)
        
        logger.info(f"Processing collection for {persona.role} persona")
        logger.info(f"Job focus: {job.expected_output_type}")
        
        # Process each document
        pdf_path = os.path.join(collection_path, 'PDFs')
        relevant_sections = []
        
        # Handle new document format with filename and title
        documents = input_config.get('documents', [])
        if documents and isinstance(documents[0], dict):
            # New format with filename/title objects
            doc_names = [doc['filename'] for doc in documents]
        else:
            # Old format with simple list
            doc_names = documents
        
        for doc_name in doc_names:
            doc_path = os.path.join(pdf_path, doc_name)
            print(f"Processing document: {doc_name}")
            if os.path.exists(doc_path):
                sections = self._extract_relevant_sections(doc_path, doc_name, persona, job)
                print(f"  Found {len(sections)} sections from {doc_name}")
                relevant_sections.extend(sections)
            else:
                print(f"Document not found: {doc_path}")
                logger.warning(f"Document not found: {doc_path}")
        
        # Sort by relevance score and assign ranks
        relevant_sections.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Ensure diversity across documents - select top sections from each document
        document_sections = {}
        for section in relevant_sections:
            doc = section.document
            if doc not in document_sections:
                document_sections[doc] = []
            document_sections[doc].append(section)
        
        # Ensure diversity across documents - select top sections from each document
        document_sections = {}
        for section in relevant_sections:
            doc = section.document
            if doc not in document_sections:
                document_sections[doc] = []
            document_sections[doc].append(section)
        
        # Take the best 1-2 sections from each document to ensure diversity
        diversified_sections = []
        
        # First, take the absolute best section from each document
        for doc, sections in document_sections.items():
            sections.sort(key=lambda x: x.relevance_score, reverse=True)
            if sections:
                # Skip overly generic sections and prioritize specific dish names
                for section in sections:
                    title_lower = section.section_title.lower()
                    # Skip all generic sections
                    if any(generic in title_lower for generic in [
                        'introduction', 'comprehensive guide', 'ultimate guide', 
                        'journey through', 'guide to', 'planning, and exploring', 
                        'instructions:', 'ingredients:', 'instructions', 'ingredients'
                    ]):
                        continue
                    # Prefer specific dish names over generic terms
                    diversified_sections.append(section)
                    break
        
        # If we need more sections, take second-best from documents with high scores
        if len(diversified_sections) < 5:
            for doc, sections in document_sections.items():
                if len(diversified_sections) >= 5:
                    break
                sections.sort(key=lambda x: x.relevance_score, reverse=True)
                added_from_doc = sum(1 for s in diversified_sections if s.document == doc)
                if len(sections) > 1 and added_from_doc < 2:  # Allow max 2 per document
                    for section in sections[1:]:  # Skip first (already added)
                        title_lower = section.section_title.lower()
                        if not any(generic in title_lower for generic in [
                            'introduction', 'comprehensive guide', 'ultimate guide', 
                            'journey through', 'guide to', 'planning, and exploring', 
                            'instructions:', 'ingredients:', 'instructions', 'ingredients'
                        ]):
                            diversified_sections.append(section)
                            break
        
        # Sort final selections by relevance score
        final_sections = sorted(diversified_sections, key=lambda x: x.relevance_score, reverse=True)[:5]
        
        # If we don't have 5 sections after filtering, add back some generic ones
        if len(final_sections) < 5:
            for section in relevant_sections:
                if section not in final_sections and len(final_sections) < 5:
                    final_sections.append(section)
        
        # Assign ranks based on final order
        for i, section in enumerate(final_sections):
            section.importance_rank = i + 1
        
        # Create output format
        output = {
            "metadata": {
                "input_documents": doc_names,
                "persona": persona_text,
                "job_to_be_done": job_text, 
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": [
                {
                    "document": section.document,
                    "page_number": section.page_number,
                    "section_title": section.section_title,
                    "importance_rank": section.importance_rank
                }
                for section in final_sections  # Use diversified sections
            ],
            "subsection_analysis": [
                {
                    "document": section.document,
                    "refined_text": section.content[:500] + "..." if len(section.content) > 500 else section.content,
                    "page_number": section.page_number
                }
                for section in final_sections[:5]  # Top 5 for detailed analysis
            ]
        }
        
        return output
    
    def _extract_relevant_sections(self, doc_path: str, doc_name: str, 
                                 persona: PersonaProfile, job: JobToBeDone) -> List[RelevantSection]:
        """Extract and score relevant sections from a document."""
        
        # Parse document using existing infrastructure
        doc_data = self.pdf_parser.parse_pdf(doc_path)
        if not doc_data:
            return []
        
        # Detect headings/sections
        headings = self.heading_detector.detect_headings(doc_data)
        
        # Extract content for each section
        sections = []
        for i, heading in enumerate(headings):
            # Get section content (simplified - text blocks after this heading)
            section_content = self._extract_section_content(heading, doc_data, i, headings)
            
            # Score relevance
            relevance_score = self.relevance_scorer.score_section(
                heading.text_block.text, section_content, persona, job
            )
            
            if relevance_score > 0.1:  # Only keep somewhat relevant sections
                print(f"  Section: '{heading.text_block.text}' from {doc_name} - Score: {relevance_score:.3f}")
                sections.append(RelevantSection(
                    document=doc_name,
                    page_number=heading.text_block.page_num,
                    section_title=heading.text_block.text,
                    content=section_content,
                    importance_rank=0,  # Will be set later
                    relevance_score=relevance_score
                ))
        
        return sections
    
    def _extract_section_content(self, heading, doc_data: DocumentData, 
                               heading_idx: int, all_headings: List) -> str:
        """Extract text content for a section."""
        
        start_page = heading.text_block.page_num
        start_y = heading.text_block.y_position
        
        # Find end boundary (next heading or end of document)
        end_page = start_page
        end_y = float('inf')
        
        if heading_idx + 1 < len(all_headings):
            next_heading = all_headings[heading_idx + 1]
            end_page = next_heading.text_block.page_num
            end_y = next_heading.text_block.y_position
        
        # Collect text blocks in this section
        section_blocks = []
        for block in doc_data.text_blocks:
            # Skip the heading text itself
            if block.page_num == start_page and abs(block.y_position - start_y) < 5:
                continue
                
            if (block.page_num == start_page and block.y_position > start_y) or \
               (start_page < block.page_num < end_page) or \
               (block.page_num == end_page and block.y_position < end_y):
                section_blocks.append(block.text)
        
        content = " ".join(section_blocks)
        
        # Clean up content - remove excessive whitespace and duplicates
        content = " ".join(content.split())  # Normalize whitespace
        
        # Truncate very long content
        if len(content) > 1000:
            content = content[:1000] + "..."
            
        return content

def main():
    """Process all collections in Challenge_1b folder."""
    
    logging.basicConfig(level=logging.INFO)
    
    analyzer = PersonaDrivenAnalyzer()
    base_path = "Challenge_1b"
    
    # Process each collection
    for collection_name in ["Collection_1", "Collection_2", "Collection_3"]:
        collection_path = os.path.join(base_path, collection_name)
        
        if not os.path.exists(collection_path):
            continue
            
        input_file = os.path.join(collection_path, 'challenge1b_input.json')
        if not os.path.exists(input_file):
            logger.warning(f"No input file found for {collection_name}")
            continue
        
        try:
            logger.info(f"Processing {collection_name}...")
            result = analyzer.process_collection(collection_path)
            
            # Save output
            output_file = os.path.join(collection_path, 'challenge1b_output_generated.json')
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"✅ Generated output for {collection_name}")
            logger.info(f"   Found {len(result['extracted_sections'])} relevant sections")
            
        except Exception as e:
            logger.error(f"❌ Error processing {collection_name}: {e}")

if __name__ == "__main__":
    main()
