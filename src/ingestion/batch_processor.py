import os
import json
import logging
from pathlib import Path
from typing import List, Optional
from tqdm import tqdm

from src.ingestion.jats_parser import JATSParser
from src.ingestion.extractor import (
    EntityExtractor,
    RelationshipExtractor,
    aggregate_entity_mentions,
)
from src.schema.entity import EntityCollection, ProcessedPaper
from src.ingestion.embedding_cache import EmbeddingCache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("batch_ingestion.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        entity_collection_path: str = "reference_entities.jsonl",
        redis_url: str = "redis://localhost:6379",
    ):
        """
        Initialize the batch processor.

        Args:
            input_dir: Directory containing .xml files
            output_dir: Directory to save .json files
            entity_collection_path: Path to reference entities file
            redis_url: URL for Redis cache
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        logger.info("Initializing components...")
        try:
            self.cache = EmbeddingCache(redis_url)
            # Check if entity collection exists, if not create empty one for now
            if os.path.exists(entity_collection_path):
                self.entity_collection = EntityCollection.load(entity_collection_path)
            else:
                logger.warning(
                    f"Entity collection not found at {entity_collection_path}. Using empty collection."
                )
                self.entity_collection = EntityCollection()

            self.entity_extractor = EntityExtractor(self.entity_collection, self.cache)
            self.relationship_extractor = RelationshipExtractor()
            logger.info("Components initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise

    def process_file(self, xml_path: Path) -> Optional[ProcessedPaper]:
        """Process a single XML file."""
        try:
            pmc_id = xml_path.stem
            logger.debug(f"Processing {pmc_id}...")

            # 1. Parse XML
            parser = JATSParser(str(xml_path))
            paper = parser.parse()

            # 2. Extract Entities
            entities = []
            for chunk in paper.chunks:
                chunk_entities = self.entity_extractor.extract_entities(
                    chunk.text, chunk.chunk_id
                )
                entities.extend(chunk_entities)

            # 3. Extract Relationships
            relationships = []
            for chunk in paper.chunks:
                chunk_rels = self.relationship_extractor.extract_relationships(
                    entities, chunk.text, chunk.chunk_id
                )
                relationships.extend(chunk_rels)

            # 4. Create ProcessedPaper
            processed = ProcessedPaper(
                pmc_id=paper.metadata.pmc_id or pmc_id,
                pmid=paper.metadata.pmid,
                doi=paper.metadata.doi,
                title=paper.metadata.title,
                abstract=paper.metadata.abstract,
                authors=paper.metadata.authors,
                publication_date=paper.metadata.publication_date,
                journal=paper.metadata.journal,
                entities=aggregate_entity_mentions(entities),
                relationships=relationships,
                entity_count=len(entities),
                relationship_count=len(relationships),
                full_text=paper.full_text,
            )

            return processed

        except Exception as e:
            logger.error(f"Error processing {xml_path.name}: {e}")
            return None

    def run(self):
        """Run batch processing on all XML files in input directory."""
        xml_files = list(self.input_dir.glob("*.xml"))
        logger.info(f"Found {len(xml_files)} XML files in {self.input_dir}")

        success_count = 0
        failure_count = 0

        for xml_file in tqdm(xml_files, desc="Processing papers"):
            processed_paper = self.process_file(xml_file)

            if processed_paper:
                # Save to JSON
                output_path = self.output_dir / f"{xml_file.stem}.json"
                with open(output_path, "w") as f:
                    f.write(processed_paper.model_dump_json(indent=2))
                success_count += 1
            else:
                failure_count += 1

        logger.info(
            f"Batch processing complete. Success: {success_count}, Failed: {failure_count}"
        )


if __name__ == "__main__":
    # Default paths
    INPUT_DIR = "papers/raw"
    OUTPUT_DIR = "papers/processed"

    processor = BatchProcessor(INPUT_DIR, OUTPUT_DIR)
    processor.run()
