#!/usr/bin/env python3

import os
import json
import argparse
import time
import subprocess
from pathlib import Path

# Sample test collections
TEST_COLLECTIONS = {
    "academic_research": {
        "collection_name": "Academic_Research",
        "pdf_files": ["pdf1.pdf", "pdf2.pdf", "pdf3.pdf", "pdf4.pdf"],
        "persona": {
            "role": "PhD Researcher in Computational Biology",
            "expertise": ["Machine Learning", "Molecular Biology", "Drug Discovery"],
            "focus_areas": ["Graph Neural Networks", "Protein-Ligand Interactions", "Biomarker Discovery"]
        },
        "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks for Graph Neural Networks in Drug Discovery"
    },
    "business_analysis": {
        "collection_name": "Business_Analysis",
        "pdf_files": ["report1.pdf", "report2.pdf", "report3.pdf"],
        "persona": {
            "role": "Investment Analyst",
            "expertise": ["Financial Modeling", "Market Research", "Competitive Analysis"],
            "focus_areas": ["Technology Sector", "Revenue Forecasting", "Strategic Investments"]
        },
        "job_to_be_done": "Analyze revenue trends, R&D investments, and market positioning strategies across competing tech companies"
    },
    "educational_content": {
        "collection_name": "Educational_Content",
        "pdf_files": ["chapter1.pdf", "chapter2.pdf", "chapter3.pdf", "chapter4.pdf", "chapter5.pdf"],
        "persona": {
            "role": "Undergraduate Chemistry Student",
            "expertise": ["General Chemistry", "Basic Organic Chemistry"],
            "focus_areas": ["Reaction Mechanisms", "Exam Preparation", "Laboratory Techniques"]
        },
        "job_to_be_done": "Identify key concepts and mechanisms for exam preparation on reaction kinetics"
    }
}

def create_test_collection(collection_key, output_dir):
    """Create a test collection JSON file"""
    if collection_key not in TEST_COLLECTIONS:
        print(f"Error: Collection '{collection_key}' not found. Available collections: {list(TEST_COLLECTIONS.keys())}")
        return False
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Write collection JSON
    collection_data = TEST_COLLECTIONS[collection_key]
    output_file = os.path.join(output_dir, f"{collection_key}_input.json")
    
    with open(output_file, 'w') as f:
        json.dump(collection_data, f, indent=2)
    
    print(f"Created test collection: {output_file}")
    print("Note: You need to provide the actual PDF files referenced in the collection.")
    
    return True

def run_test(collection_key, input_dir, output_dir, mode="local"):
    """Run a test on a specific collection"""
    if collection_key not in TEST_COLLECTIONS:
        print(f"Error: Collection '{collection_key}' not found. Available collections: {list(TEST_COLLECTIONS.keys())}")
        return False
    
    # Create input JSON if it doesn't exist
    input_file = os.path.join(input_dir, f"{collection_key}_input.json")
    if not os.path.exists(input_file):
        create_test_collection(collection_key, input_dir)
    
    # Check if PDF files exist
    collection_data = TEST_COLLECTIONS[collection_key]
    missing_pdfs = []
    for pdf_file in collection_data["pdf_files"]:
        pdf_path = os.path.join(input_dir, pdf_file)
        if not os.path.exists(pdf_path):
            missing_pdfs.append(pdf_file)
    
    if missing_pdfs:
        print(f"Warning: The following PDF files are missing from {input_dir}:")
        for pdf in missing_pdfs:
            print(f"  - {pdf}")
        print("Please add these files before running the test.")
        return False
    
    # Run the test
    start_time = time.time()
    
    if mode == "local":
        # Run locally
        cmd = ["python", "run_local.py", "--mode", "local", "--input", input_dir, "--output", output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running test:")
            print(result.stderr)
            return False
        print(result.stdout)
    else:
        # Run with Docker
        cmd = ["python", "run_local.py", "--mode", "docker", "--input", input_dir, "--output", output_dir]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("Error running test:")
            print(result.stderr)
            return False
        print(result.stdout)
    
    processing_time = time.time() - start_time
    print(f"Test completed in {processing_time:.2f} seconds")
    
    # Check if output was generated
    output_file = os.path.join(output_dir, f"{collection_data['collection_name']}_output.json")
    if os.path.exists(output_file):
        print(f"Output generated: {output_file}")
        return True
    else:
        print(f"Error: Output file not generated: {output_file}")
        return False

def list_collections():
    """List available test collections"""
    print("Available test collections:")
    for key, collection in TEST_COLLECTIONS.items():
        print(f"\n{key}:")
        print(f"  Collection Name: {collection['collection_name']}")
        print(f"  PDF Files: {', '.join(collection['pdf_files'])}")
        print(f"  Persona: {collection['persona']['role']}")
        print(f"  Job: {collection['job_to_be_done'][:60]}...")

def main():
    parser = argparse.ArgumentParser(description="Test the Persona-Driven Document Intelligence solution with sample collections")
    parser.add_argument("--list", action="store_true", help="List available test collections")
    parser.add_argument("--create", metavar="COLLECTION", help="Create a test collection JSON file")
    parser.add_argument("--run", metavar="COLLECTION", help="Run a test on a specific collection")
    parser.add_argument("--mode", choices=["local", "docker"], default="local", help="Run mode: local or docker")
    parser.add_argument("--input", default="input", help="Input directory")
    parser.add_argument("--output", default="output", help="Output directory")
    
    args = parser.parse_args()
    
    if args.list:
        list_collections()
    elif args.create:
        create_test_collection(args.create, args.input)
    elif args.run:
        run_test(args.run, args.input, args.output, args.mode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()