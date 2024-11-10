from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PageContent:
    url: str
    title: str
    raw_html: str
    web_content: str
    pdf_content: List[Dict[str, str]]
    sections: List[Dict[str, str]]
    metadata: Dict[str, str]
    last_scraped: str

@dataclass
class ChunkedContent:
    url: str
    title: str
    content_type: str  # 'web_content', 'section', or 'pdf'
    text: str
    chunk_index: int
    total_chunks: int
    metadata: Dict[str, str]
    section_header: str = None
    subsection_header: str = None
    pdf_url: str = None
    