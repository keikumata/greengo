from typing import List, Dict
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag

@dataclass
class Section:
    header: str
    content: str
    subsections: List['Section']
    level: int

class ContentChunker:
    def __init__(self, max_length: int = 1500, overlap: int = 200):
        self.max_length = max_length
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        """Split text into smaller chunks with overlap"""
        chunks = []
        
        # Clean the text first
        text = self.clean_text(text)
        
        if len(text) <= self.max_length:
            return [text]
        
        start = 0
        while start < len(text):
            end = start + self.max_length
            
            if end < len(text):
                # Look for paragraph breaks first
                next_para = text[start:min(end + self.overlap, len(text))].find('\n\n')
                if next_para != -1 and (start + next_para) < end:
                    end = start + next_para
                else:
                    # Look for sentence end with word boundary
                    search_area = text[start:min(end + self.overlap, len(text))]
                    sentence_end = re.search(r'[.!?]\s+\w', search_area)
                    if sentence_end:
                        end = start + sentence_end.start() + 1
                    else:
                        # Fall back to word boundary
                        word_boundary = text[start:end].rindex(' ')
                        if word_boundary != -1:
                            end = start + word_boundary
            
            chunk = text[start:end].strip()
            # Replace single newlines with spaces
            chunk = re.sub(r'\n(?!\n)', ' ', chunk)
            # Normalize multiple spaces
            chunk = re.sub(r'\s+', ' ', chunk)
            
            chunks.append(chunk)
            
            # Move start pointer but ensure we don't create partial words
            if end < len(text):
                next_start = text[end:].find(' ')
                if next_start != -1:
                    start = end + next_start
                else:
                    start = end
            else:
                start = end
        
        return chunks

    def clean_text(self, text: str) -> str:
        """Clean text before chunking"""
        # Normalize newlines
        text = text.replace('\r\n', '\n')
        
        # Preserve paragraph breaks but convert other newlines to spaces
        text = re.sub(r'\n{3,}', '\n\n', text)  # Normalize multiple newlines to double
        
        # Remove excessive whitespace
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\n]', '', text)
        
        return text.strip()