#!/usr/bin/env python3

import os
import json
import time
import fitz  # PyMuPDF
import numpy as np
import spacy
from datetime import datetime
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
MAX_PROCESSING_TIME = 60  # seconds
INPUT_DIR = os.environ.get('INPUT_DIR', 'input')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', 'output')
MODEL_NAME = 'all-MiniLM-L6-v2'  # Small model (<100MB) for sentence embeddings

class PersonaDocumentAnalyzer:
    def __init__(self):
        # Load models
        logger.info("Loading models...")
        self.nlp = spacy.load('en_core_web_sm')  # Small spaCy model for NLP tasks
        self.model = SentenceTransformer(MODEL_NAME)  # Sentence transformer for embeddings
        logger.info("Models loaded successfully")
        
    def process_collection(self, input_json_path):
        """Process a collection of PDFs based on input JSON"""
        start_time = time.time()
        
        # Load input JSON
        with open(input_json_path, 'r') as f:
            input_data = json.load(f)
        
        # Extract input parameters
        collection_name = input_data.get('collection_name', 'Unknown')
        pdf_files = input_data.get('pdf_files', [])
        persona = input_data.get('persona', {})
        job_to_be_done = input_data.get('job_to_be_done', '')
        
        logger.info(f"Processing collection: {collection_name}")
        logger.info(f"Number of PDFs: {len(pdf_files)}")
        logger.info(f"Persona: {persona['role']}")
        logger.info(f"Job to be done: {job_to_be_done}")
        
        # Create persona context embedding
        persona_text = f"Role: {persona['role']}. Expertise: {', '.join(persona['expertise'])}. Focus: {', '.join(persona['focus_areas'])}"
        job_text = job_to_be_done
        context_text = persona_text + " " + job_text
        context_embedding = self.model.encode(context_text)
        
        # Process each PDF in parallel
        pdf_base_dir = os.path.dirname(input_json_path)
        results = []
        
        with ThreadPoolExecutor() as executor:
            futures = []
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_base_dir, pdf_file)
                if os.path.exists(pdf_path):
                    futures.append(executor.submit(self.process_pdf, pdf_path, context_embedding))
                else:
                    logger.warning(f"PDF file not found: {pdf_path}")
            
            for future in futures:
                result = future.result()
                if result:
                    results.extend(result)
        
        # Sort results by importance rank
        results.sort(key=lambda x: x['importance_rank'])
        
        # Prepare output JSON
        output = {
            "metadata": {
                "input_documents": pdf_files,
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "processing_timestamp": datetime.now().isoformat()
            },
            "extracted_sections": results[:10],  # Top 10 most important sections
            "subsection_analysis": self.analyze_subsections(results[:5], context_embedding)  # Analyze top 5 sections
        }
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        
        return output, collection_name
    
    def process_pdf(self, pdf_path, context_embedding):
        """Process a single PDF and extract relevant sections"""
        try:
            logger.info(f"Processing PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            pdf_filename = os.path.basename(pdf_path)
            
            sections = []
            current_section = None
            section_text = ""
            page_numbers = []
            
            # Extract sections from PDF
            for page_num, page in enumerate(doc):
                # Extract text with layout information
                blocks = page.get_text("dict")["blocks"]
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                font_size = span["size"]
                                
                                # Detect section headers based on font size and formatting
                                if font_size > 10 and (text.isupper() or any(c.isdigit() for c in text)):
                                    # Save previous section if exists
                                    if current_section and section_text:
                                        sections.append({
                                            "document": pdf_filename,
                                            "section_title": current_section,
                                            "content": section_text,
                                            "page_numbers": page_numbers
                                        })
                                    
                                    # Start new section
                                    current_section = text
                                    section_text = ""
                                    page_numbers = [page_num + 1]  # 1-indexed page numbers
                                else:
                                    # Add text to current section
                                    if current_section:
                                        section_text += text + " "
                                        if page_num + 1 not in page_numbers:
                                            page_numbers.append(page_num + 1)
            
            # Add the last section
            if current_section and section_text:
                sections.append({
                    "document": pdf_filename,
                    "section_title": current_section,
                    "content": section_text,
                    "page_numbers": page_numbers
                })
            
            # Calculate relevance scores
            results = []
            for i, section in enumerate(sections):
                # Create embedding for section content
                section_text = section["section_title"] + ": " + section["content"]
                section_embedding = self.model.encode(section_text[:1024])  # Limit text length for embedding
                
                # Calculate similarity score
                similarity = np.dot(section_embedding, context_embedding) / (
                    np.linalg.norm(section_embedding) * np.linalg.norm(context_embedding)
                )
                
                # Create result entry
                results.append({
                    "document": section["document"],
                    "page_number": min(section["page_numbers"]),  # Use first page of section
                    "section_title": section["section_title"],
                    "importance_rank": 1 - similarity,  # Lower score = higher importance
                    "content": section["content"],
                    "all_page_numbers": section["page_numbers"]
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return []
    
    def analyze_subsections(self, top_sections, context_embedding):
        """Analyze subsections within top sections"""
        subsections = []
        
        for section in top_sections:
            # Split section content into paragraphs
            paragraphs = re.split(r'\n\n|\r\n\r\n', section['content'])
            
            # Process each paragraph as a potential subsection
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph.strip()) < 50:  # Skip very short paragraphs
                    continue
                
                # Create embedding for paragraph
                paragraph_embedding = self.model.encode(paragraph)
                
                # Calculate similarity score
                similarity = np.dot(paragraph_embedding, context_embedding) / (
                    np.linalg.norm(paragraph_embedding) * np.linalg.norm(context_embedding)
                )
                
                # Create subsection entry
                subsections.append({
                    "document": section["document"],
                    "section_title": section["section_title"],
                    "refined_text": paragraph,
                    "page_number": section["page_number"],
                    "relevance_score": similarity
                })
        
        # Sort subsections by relevance score (higher is better)
        subsections.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return subsections[:15]  # Return top 15 subsections

def process_input_files():
    """Process all input JSON files"""
    analyzer = PersonaDocumentAnalyzer()
    
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Find all input JSON files
    input_files = []
    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.endswith('.json') and not file.endswith('_output.json'):
                input_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(input_files)} input JSON files")
    
    # Process each input file
    for input_file in input_files:
        try:
            logger.info(f"Processing input file: {input_file}")
            output_data, collection_name = analyzer.process_collection(input_file)
            
            # Write output JSON
            output_file = os.path.join(OUTPUT_DIR, f"{collection_name}_output.json")
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Output written to: {output_file}")
        
        except Exception as e:
            logger.error(f"Error processing input file {input_file}: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting PDF processing")
    process_input_files()
    logger.info("PDF processing completed")