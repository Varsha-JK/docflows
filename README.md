# docflow

A production-style document ingestion pipeline built around a reusable, independent document extraction service, designed for downstream RAG systems.

It focuses on:

- Structured extraction of PDF documents
- Clean API contracts between services
- Deterministic batch processing
- RAG-ready structured outputs

## Document Extractor Service (Independent and Reusable)

### Purpose:

A FastAPI-based microservice that:

- Accepts PDF uploads
- Extracts text and structural metadata
- Generates SHA256-based document identity
- Returns a strictly validated response schema

The response includes:

- Document metadata
- Extraction metadata
- Structured content sections

This service is reusable and independent of any specific pipeline.

### API

1. POST /extract
   - accepts a pdf file
   - output: json

### Output structure (json)

- document_metadata
  - filename
  - date
  - mime_type
  - pages
  - version
- extractor_metadata
  - extractor_version
  - service_used
  - service_version
- content
  - full_text
  - sections
    - headings
    - page_no
    - text

## Ingestion Pipeline

A lightweight batch runner that:

- Iterates over local PDF files
- Calls the extraction service
- Stores structured JSON outputs
- Uses SHA-based idempotency to prevent reprocessing

The pipeline is deterministic and safe to rerun.
