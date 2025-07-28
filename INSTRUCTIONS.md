# Challenge 1B: Persona-Driven Document Intelligence

## Running the Solution

This document provides detailed instructions for running the Persona-Driven Document Intelligence solution for Challenge 1B of the Adobe India Hackathon 2025.

### Prerequisites

- Python 3.8 or higher
- Docker (for containerized execution)
- 4GB+ RAM recommended
- CPU with 2+ cores recommended

### Option 1: Running with Docker (Recommended)

This is the recommended approach as it ensures all dependencies are correctly installed and the environment matches the evaluation environment.

1. **Build the Docker image:**

```bash
docker build --platform linux/amd64 -t persona-document-analyzer .
```

2. **Run the container:**

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none persona-document-analyzer
```

On Windows, you may need to use absolute paths:

```bash
docker run --rm -v "C:/path/to/input":/app/input -v "C:/path/to/output":/app/output --network none persona-document-analyzer
```

### Option 2: Running Locally

If you prefer to run the solution without Docker, follow these steps:

1. **Install dependencies:**

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Run the processing script:**

```bash
python run_local.py --input ./input --output ./output
```

Or use the convenience script with more options:

```bash
python run_local.py --mode local --input ./input --output ./output
```

## Input Format

The solution expects input in the following format:

1. A directory containing:
   - JSON file(s) with collection metadata
   - PDF files referenced in the JSON

2. The JSON file should have the following structure:

```json
{
  "collection_name": "Collection_Name",
  "pdf_files": [
    "file1.pdf",
    "file2.pdf",
    "file3.pdf"
  ],
  "persona": {
    "role": "Role Description",
    "expertise": ["Area1", "Area2"],
    "focus_areas": ["Focus1", "Focus2"]
  },
  "job_to_be_done": "Description of the task to accomplish"
}
```

## Output Format

The solution generates output in the following format:

```json
{
  "metadata": {
    "input_documents": ["file1.pdf", "file2.pdf"],
    "persona": { ... },
    "job_to_be_done": "...",
    "processing_timestamp": "2023-09-15T14:32:45.123456"
  },
  "extracted_sections": [
    {
      "document": "file1.pdf",
      "page_number": 5,
      "section_title": "SECTION TITLE",
      "importance_rank": 0.12
    },
    ...
  ],
  "subsection_analysis": [
    {
      "document": "file1.pdf",
      "section_title": "SECTION TITLE",
      "refined_text": "Extracted text...",
      "page_number": 5,
      "relevance_score": 0.92
    },
    ...
  ]
}
```

## Performance Considerations

- The solution is optimized to process 3-5 documents within the 60-second constraint
- For larger document collections, processing time may increase
- The model size is kept under 1GB to meet the competition requirements
- All processing is done offline with no internet access required during execution

## Troubleshooting

### Common Issues

1. **Missing dependencies:**
   - Ensure all dependencies are installed with `pip install -r requirements.txt`
   - For spaCy, run `python -m spacy download en_core_web_sm`

2. **Docker permission issues:**
   - On Linux/Mac, you may need to run Docker commands with `sudo`
   - Ensure the input/output directories have appropriate permissions

3. **Memory issues:**
   - If you encounter memory errors, try processing fewer documents at a time
   - Increase Docker container memory limit if needed

4. **PDF parsing errors:**
   - Some PDFs with complex layouts or security features may not parse correctly
   - Try to use standard PDF files without encryption or special features

## Additional Resources

- See `approach_explanation.md` for details on the methodology
- Check `schema/output_schema.json` for the complete output schema definition
- Sample input and output files are provided in the `input` and `output` directories