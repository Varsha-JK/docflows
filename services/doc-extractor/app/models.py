# services/doc_extractor/app/models.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class Section(BaseModel):
    path: Optional[str]
    heading: Optional[str]
    level: Optional[int]
    page_start: Optional[int]
    page_end: Optional[int]
    text: str


class Content(BaseModel):
    full_text: str
    sections: List[Section]


class ExtractionMeta(BaseModel):
    extractor_version: str
    service_used: str
    service_version: Optional[str]
    warnings: List[str]


class DocumentMeta(BaseModel):
    filename: str
    processed_on: date
    mime_type: str
    pages: Optional[int]
    sha256: Optional[str]
    version: str


class ExtractResponse(BaseModel):
    document_metadata: DocumentMeta
    extraction_metadata: ExtractionMeta
    content: Content
