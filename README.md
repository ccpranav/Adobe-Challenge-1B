# Challenge 1B: Persona-Driven Document Intelligence

## Overview
This solution implements an intelligent document analysis system that extracts and prioritizes the most relevant sections from a collection of PDF documents based on a specific persona and their job-to-be-done. The system analyzes document content, identifies key sections, and ranks them according to their relevance to the user's needs.

## Approach Explanation

Our approach to persona-driven document intelligence combines several key techniques:

1. **Document Processing Pipeline**: We extract text and structure from PDFs using PyMuPDF (fitz), which provides efficient access to document content while maintaining structural information.

2. **Content Analysis**: We implement a multi-stage analysis process:
   - Text extraction with layout preservation
   - Section identification and boundary detection
   - Semantic representation of content using sentence transformers

3. **Persona-Based Relevance Ranking**: We use a contextual matching algorithm that:
   - Creates vector representations of the persona description and job-to-be-done
   - Computes similarity scores between document sections and the user context
   - Ranks sections based on relevance scores and structural importance

4. **Subsection Extraction**: For the most relevant sections, we perform deeper analysis to extract key subsections that directly address the user's needs.

5. **Offline Processing**: All processing is done on-device without internet access, using pre-trained models that are optimized for CPU execution.

## Technical Implementation

- **Core Libraries**: PyMuPDF, sentence-transformers, numpy, spaCy
- **Model**: We use a distilled version of SBERT (Sentence-BERT) for semantic text representation, optimized to stay under the 1GB model size constraint
- **Performance Optimization**: Multi-threading for parallel document processing, caching of intermediate results, and efficient text chunking

## Key Features

- Handles diverse document types and domains
- Adapts to different personas and tasks without hardcoded rules
- Provides structured JSON output with ranked sections and subsections
- Processes document collections within the 60-second time constraint
- Works completely offline with no network dependencies

## Usage

The solution is containerized using Docker and can be run with the following commands:

```bash
# Build the Docker image
docker build --platform linux/amd64 -t persona-document-analyzer .

# Run the container
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none persona-document-analyzer
```

The system will process all PDFs in the input directory and generate corresponding JSON output files with the analysis results.