# docflow

A production-style document ingestion pipeline built around a reusable,
independent document extraction service, designed for downstream RAG systems.

## Extractor Service (Independent and Reusable)

### Purpose:

Convert an input PDF into structured, normalized content for downstream systems (RAG, search, etc).

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
