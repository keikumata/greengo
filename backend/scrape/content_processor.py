from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from dataclasses import dataclass
import re
from datetime import datetime

@dataclass
class ProcessedContent:
    url: str
    title: str
    volume_number: str
    part_letter: str
    chapter_number: str
    last_updated: str
    section_header: str
    subsection_header: Optional[str]
    content: str
    timestamp: str

class ContentProcessor:
    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, str]:
        metadata = {
            'title': '',
            'volume_number': '',
            'part_letter': '',
            'chapter_number': '',
            'last_updated': ''
        }
        
        # Extract title
        title = soup.find('h1')
        if title:
            metadata['title'] = title.get_text(strip=True)
        
        # Extract breadcrumb metadata
        breadcrumbs = soup.find('nav', class_='breadcrumb')
        if breadcrumbs:
            text = breadcrumbs.get_text()
            volume_match = re.search(r'Volume\s+(\d+)', text)
            part_match = re.search(r'Part\s+([A-Z])', text)
            chapter_match = re.search(r'Chapter\s+(\d+)', text)
            
            if volume_match:
                metadata['volume_number'] = volume_match.group(1)
            if part_match:
                metadata['part_letter'] = part_match.group(1)
            if chapter_match:
                metadata['chapter_number'] = chapter_match.group(1)
        
        # Extract last updated date
        last_updated = soup.find('div', class_='last-updated')
        if last_updated:
            metadata['last_updated'] = last_updated.get_text(strip=True)
            
        return metadata

    def process_content(self, soup: BeautifulSoup, url: str) -> List[ProcessedContent]:
        processed_contents = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extract metadata
        metadata = self.extract_metadata(soup, url)
        
        # Find main content
        content = soup.find('section', id='book-content')
        if not content:
            return []
            
        main_content = content.find('div', class_='field--name-body')
        if not main_content:
            return []
        
        current_section = None
        current_section_header = None
        current_section_content = []
        
        # Process all h2, h3, and p elements
        for element in main_content.find_all(['h2', 'h3', 'p']):
            if element.name == 'h2':
                # Save previous section if exists
                if current_section_header and current_section_content:
                    processed_contents.append(
                        ProcessedContent(
                            url=url,
                            title=metadata['title'],
                            volume_number=metadata['volume_number'],
                            part_letter=metadata['part_letter'],
                            chapter_number=metadata['chapter_number'],
                            last_updated=metadata['last_updated'],
                            section_header=current_section_header,
                            subsection_header=None,
                            content='\n\n'.join(current_section_content),
                            timestamp=timestamp
                        )
                    )
                
                current_section_header = element.get_text(strip=True)
                current_section = {'content': [], 'subsections': []}
                current_section_content = []
                
            elif element.name == 'h3' and current_section_header:
                # Save previous subsection content to main section
                if current_section_content:
                    processed_contents.append(
                        ProcessedContent(
                            url=url,
                            title=metadata['title'],
                            volume_number=metadata['volume_number'],
                            part_letter=metadata['part_letter'],
                            chapter_number=metadata['chapter_number'],
                            last_updated=metadata['last_updated'],
                            section_header=current_section_header,
                            subsection_header=None,
                            content='\n\n'.join(current_section_content),
                            timestamp=timestamp
                        )
                    )
                    current_section_content = []
                
                # Start new subsection
                subsection_header = element.get_text(strip=True)
                current_section['subsections'].append({
                    'header': subsection_header,
                    'content': []
                })
                
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    current_section_content.append(text)
        
        # Add final section/subsection
        if current_section_header and current_section_content:
            processed_contents.append(
                ProcessedContent(
                    url=url,
                    title=metadata['title'],
                    volume_number=metadata['volume_number'],
                    part_letter=metadata['part_letter'],
                    chapter_number=metadata['chapter_number'],
                    last_updated=metadata['last_updated'],
                    section_header=current_section_header,
                    subsection_header=None,
                    content='\n\n'.join(current_section_content),
                    timestamp=timestamp
                )
            )
        
        return processed_contents