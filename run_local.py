#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fitz
        import numpy
        import spacy
        from sentence_transformers import SentenceTransformer
        print("All required dependencies are installed.")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required dependencies using: pip install -r requirements.txt")
        return False

def run_local_processing(input_dir, output_dir):
    """Run the PDF processing locally without Docker"""
    # Set environment variables
    os.environ['INPUT_DIR'] = input_dir
    os.environ['OUTPUT_DIR'] = output_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Start timer
    start_time = time.time()
    
    # Run the processing script
    print(f"Processing PDFs from {input_dir}...")
    import process_pdfs
    process_pdfs.process_input_files()
    
    # Calculate and display processing time
    processing_time = time.time() - start_time
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Results saved to {output_dir}")

def build_docker_image():
    """Build the Docker image"""
    print("Building Docker image...")
    result = subprocess.run(
        ["docker", "build", "--platform", "linux/amd64", "-t", "persona-document-analyzer", "."],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error building Docker image:")
        print(result.stderr)
        return False
    
    print("Docker image built successfully.")
    return True

def run_docker_container(input_dir, output_dir):
    """Run the Docker container"""
    # Get absolute paths
    input_abs_path = os.path.abspath(input_dir)
    output_abs_path = os.path.abspath(output_dir)
    
    print(f"Running Docker container with input from {input_abs_path} and output to {output_abs_path}...")
    
    # Run the container
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "-v", f"{input_abs_path}:/app/input",
            "-v", f"{output_abs_path}:/app/output",
            "--network", "none",
            "persona-document-analyzer"
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error running Docker container:")
        print(result.stderr)
        return False
    
    print("Docker container executed successfully.")
    print(result.stdout)
    return True

def main():
    parser = argparse.ArgumentParser(description="Run the Persona-Driven Document Intelligence solution")
    parser.add_argument("--mode", choices=["local", "docker"], default="local",
                        help="Run mode: local (without Docker) or docker (with Docker)")
    parser.add_argument("--input", default="input",
                        help="Input directory containing JSON files and PDFs")
    parser.add_argument("--output", default="output",
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    if args.mode == "local":
        if check_dependencies():
            run_local_processing(args.input, args.output)
    else:  # docker mode
        if build_docker_image():
            run_docker_container(args.input, args.output)

if __name__ == "__main__":
    main()