import weaviate
import json
from pathlib import Path
import logging
from typing import List, Dict, Any
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeaviateImporter:
    def __init__(self):
        self.client = weaviate.Client(
            url="http://localhost:8080",
        )
        self.setup_schema()

    def setup_schema(self):
        """Set up the Weaviate schema for USCIS policy manual content"""
        schema = {
            "class": "USCIS_Policy_Manual",
            "description": "Content from the USCIS Policy Manual",
            "vectorizer": "text2vec-ollama",
            "moduleConfig": {
                "text2vec-ollama": {
                    "model": "nomic-embed-text",
                    "apiEndpoint": "http://host.docker.internal:11434"
                },
                "generative-ollama": {
                    "model": "llama3.2",
                    "apiEndpoint": "http://host.docker.internal:11434"
                }
            },
            "properties": [
                {
                    "name": "url",
                    "dataType": ["string"],
                    "description": "Source URL of the content",
                    "skip_vectorization": True
                },
                {
                    "name": "title",
                    "dataType": ["string"],
                    "description": "Title of the page",
                    "vectorize_property_name": True
                },
                {
                    "name": "volume_number",
                    "dataType": ["string"],
                    "description": "Volume number from metadata",
                    "skip_vectorization": True
                },
                {
                    "name": "part_letter",
                    "dataType": ["string"],
                    "description": "Part letter from metadata",
                    "skip_vectorization": True
                },
                {
                    "name": "chapter_number",
                    "dataType": ["string"],
                    "description": "Chapter number from metadata",
                    "skip_vectorization": True
                },
                {
                    "name": "last_updated",
                    "dataType": ["string"],
                    "description": "Last updated date",
                    "skip_vectorization": True
                },
                {
                    "name": "section_header",
                    "dataType": ["string"],
                    "description": "Header of the section",
                    "vectorize_property_name": True
                },
                {
                    "name": "subsection_header",
                    "dataType": ["string"],
                    "description": "Header of the subsection",
                    "vectorize_property_name": True
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "The actual content",
                    "vectorize_property_name": True
                },
                {
                    "name": "timestamp",
                    "dataType": ["string"],
                    "description": "Processing timestamp",
                    "skip_vectorization": True
                }
            ]
        }

        try:
            self.client.schema.delete_class("USCIS_Policy_Manual")
            logger.info("Deleted existing schema")
        except:
            pass

        self.client.schema.create_class(schema)
        logger.info("Created new schema")

    def get_latest_chunks_file(self) -> Path:
        """Get the most recent chunks file"""
        chunks_dir = Path('scrape/raw_data/chunks')
        files = list(chunks_dir.glob('*.jsonl'))
        if not files:
            raise FileNotFoundError("No chunks files found")
        return max(files, key=lambda x: x.stat().st_mtime)

    def import_chunks(self):
        """Import chunks from the latest JSONL file into Weaviate"""
        chunks_file = self.get_latest_chunks_file()
        logger.info(f"Importing chunks from {chunks_file}")
        
        batch_size = 100
        current_batch = []
        
        with open(chunks_file, 'r', encoding='utf-8') as f:
            for line in f:
                chunk = json.loads(line.strip())
                
                # Prepare object data
                object_data = {
                    "url": chunk["url"],
                    "title": chunk["title"],
                    "volume_number": chunk.get("volume_number", ""),
                    "part_letter": chunk.get("part_letter", ""),
                    "chapter_number": chunk.get("chapter_number", ""),
                    "last_updated": chunk.get("last_updated", ""),
                    "section_header": chunk.get("section_header"),
                    "subsection_header": chunk.get("subsection_header"),
                    "content": chunk.get("content", ""),
                    "timestamp": chunk.get("timestamp", "")
                }
                
                current_batch.append(object_data)
                
                if len(current_batch) >= batch_size:
                    self._import_batch(current_batch)
                    current_batch = []
            
            # Import any remaining items
            if current_batch:
                self._import_batch(current_batch)

    def _import_batch(self, batch: List[Dict[str, Any]]):
        """Import a batch of objects into Weaviate"""
        with self.client.batch as batch_context:
            for item in batch:
                batch_context.add_data_object(
                    data_object=item,
                    class_name="USCIS_Policy_Manual"
                )
        logger.info(f"Imported batch of {len(batch)} items")

def main():
    importer = WeaviateImporter()
    importer.import_chunks()
    logger.info("Import completed")

if __name__ == "__main__":
    main()
