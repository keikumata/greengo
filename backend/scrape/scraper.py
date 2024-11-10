import requests
from bs4 import BeautifulSoup
import time
import logging
from pathlib import Path
from typing import Dict, Optional, List
from content_processor import ContentProcessor
from storage import StorageManager

# Set up logging
logs_path = Path('scrape/logs')
logs_path.mkdir(parents=True, exist_ok=True)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Set up file handler
file_handler = logging.FileHandler(logs_path / 'scraper.log')
file_handler.setFormatter(formatter)

# Set up console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Configure root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class USCISManualScraper:
    def __init__(self):
        self.storage = StorageManager()
        self.processor = ContentProcessor()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        # Define valid volumes and their titles
        self.volume_structure = {
            1: "General Policies and Procedures",
            2: "Nonimmigrants",
            3: "Humanitarian Protection and Parole",
            4: "Refugees and Asylees",
            5: "Adoptions",
            6: "Immigrants",
            7: "Adjustment of Status",
            8: "Admissibility",
            9: "Waivers and Other Forms of Relief",
            10: "Employment Authorization",
            11: "Travel and Identity Documents",
            12: "Citizenship and Naturalization"
        }

    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a webpage"""
        try:
            # Check local storage first
            cached_content = self.storage.get_html_content(url)
            if cached_content:
                logger.info(f"Using cached content for {url}")
                return BeautifulSoup(cached_content, 'html.parser')
            
            # If not found locally, fetch from web
            logger.info(f"Fetching from web: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Save the HTML content
            self.storage.save_html_content(url, response.text)
            
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def fetch_volume_parts(self, volume: int) -> List[Dict[str, str]]:
        """Fetch all parts from a volume's sitemap"""
        url = f"https://www.uscis.gov/policy-manual/volume-{volume}"
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        parts = []
        nav_tree = soup.find('nav', class_='nav-sub-tree')
        
        if nav_tree:
            for link in nav_tree.find_all('a', href=True):
                href = link['href']
                if f'/policy-manual/volume-{volume}-part-' in href:
                    part_letter = href.split('-part-')[-1].upper()
                    title = link.get_text(strip=True)
                    full_url = 'https://www.uscis.gov' + href if href.startswith('/') else href
                    parts.append({
                        'volume': volume,
                        'part': part_letter,
                        'title': title,
                        'url': full_url
                    })
                    logger.info(f"Found part {part_letter} in volume {volume}: {title}")
        
        if not parts:
            logger.warning(f"No parts found for volume {volume}")
            
        return parts

    def fetch_part_chapters(self, volume: int, part: str) -> List[Dict[str, str]]:
        """Fetch all chapters from a part's sitemap"""
        url = f"https://www.uscis.gov/policy-manual/volume-{volume}-part-{part}"
        soup = self.fetch_page(url)
        if not soup:
            return []
        
        chapters = []
        nav_tree = soup.find('nav', class_='nav-sub-tree')
        
        if nav_tree:
            for link in nav_tree.find_all('a', href=True):
                href = link['href']
                if f'/policy-manual/volume-{volume}-part-{part.lower()}-chapter-' in href:
                    chapter_num = href.split('-chapter-')[-1]
                    title = link.get_text(strip=True)
                    full_url = 'https://www.uscis.gov' + href if href.startswith('/') else href
                    chapters.append({
                        'volume': volume,
                        'part': part,
                        'chapter': chapter_num,
                        'title': title,
                        'url': full_url
                    })
                    logger.info(f"Found chapter {chapter_num} in volume {volume} part {part}: {title}")
        
        if not chapters:
            logger.warning(f"No chapters found for volume {volume} part {part}")
            
        return chapters

    def process_chapter(self, url: str):
        """Process a single chapter"""
        try:
            soup = self.fetch_page(url)
            if not soup:
                return
            
            # Process content
            processed_contents = self.processor.process_content(soup, url)
            
            # Save each processed content
            for content in processed_contents:
                self.storage.save_processed_content(content)
                
            logger.info(f"Successfully processed: {url}")
            
        except Exception as e:
            logger.error(f"Error processing chapter {url}: {e}")

    def main(self):
        print("Starting scraper...")
        try:
            # Iterate through all volumes
            for volume_num, volume_title in self.volume_structure.items():
                logger.info(f"Processing Volume {volume_num}: {volume_title}")
                
                # Get all parts in this volume
                parts = self.fetch_volume_parts(volume_num)
                
                for part in parts:
                    logger.info(f"Processing Volume {volume_num} Part {part['part']}: {part['title']}")
                    
                    # Get all chapters in this part
                    chapters = self.fetch_part_chapters(volume_num, part['part'])
                    
                    for chapter in chapters:
                        try:
                            logger.info(f"Processing chapter: {chapter['url']}")
                            self.process_chapter(chapter['url'])
                            time.sleep(1)  # Be nice to the server
                                
                        except Exception as e:
                            logger.error(f"Error processing chapter {chapter['url']}: {e}")
                            continue
                    
                    time.sleep(2)  # Additional delay between parts
                
                time.sleep(5)  # Additional delay between volumes
                        
        except Exception as e:
            logger.error(f"Fatal error in main: {e}")

if __name__ == '__main__':
    scraper = USCISManualScraper()
    scraper.main()