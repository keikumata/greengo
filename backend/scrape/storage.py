from pathlib import Path
import json
from datetime import datetime
from typing import Optional
from content_processor import ProcessedContent

class StorageManager:
    def __init__(self):
        self.base_dir = Path('scrape/raw_data')
        self.html_dir = self.base_dir / 'html'
        self.chunks_dir = self.base_dir / 'chunks'
        
        # Create directories
        self.html_dir.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamp once for this run
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_chunks_file = self.chunks_dir / f"{self.run_timestamp}_content_chunks.jsonl"
    
    def get_html_content(self, url: str) -> Optional[str]:
        """Get HTML content from local storage"""
        file_path = self._get_html_path(url)
        if file_path.exists():
            return file_path.read_text(encoding='utf-8')
        return None
    
    def save_html_content(self, url: str, content: str):
        """Save HTML content to local storage"""
        file_path = self._get_html_path(url)
        file_path.write_text(content, encoding='utf-8')
    
    def save_processed_content(self, processed_content: ProcessedContent):
        """Save processed content to the current run's chunks file"""
        with open(self.current_chunks_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                'url': processed_content.url,
                'title': processed_content.title,
                'volume_number': processed_content.volume_number,
                'part_letter': processed_content.part_letter,
                'chapter_number': processed_content.chapter_number,
                'last_updated': processed_content.last_updated,
                'section_header': processed_content.section_header,
                'subsection_header': processed_content.subsection_header,
                'content': processed_content.content,
                'timestamp': self.run_timestamp
            }) + '\n')
    
    def _get_html_path(self, url: str) -> Path:
        """Convert URL to file path"""
        safe_filename = url.replace('https://', '').replace('/', '_') + '.html'
        return self.html_dir / safe_filename