#!/usr/bin/env python3
"""
Merge multiple entity JSONL files into a single reference collection.
"""

import json
import logging
from pathlib import Path
from src.schema.entity import EntityCollection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def merge_jsonl_files(input_files: list[str], output_file: str) -> None:
    """Merge multiple JSONL files into a single EntityCollection."""
    
    collection = EntityCollection()
    total_entities = 0
    
    for input_file in input_files:
        if not Path(input_file).exists():
            logger.warning(f"File not found, skipping: {input_file}")
            continue
        
        logger.info(f"Loading {input_file}...")
        sub_collection = EntityCollection.load(input_file)
        
        # Merge into main collection
        collection.diseases.update(sub_collection.diseases)
        collection.genes.update(sub_collection.genes)
        collection.drugs.update(sub_collection.drugs)
        collection.proteins.update(sub_collection.proteins)
        collection.symptoms.update(sub_collection.symptoms)
        collection.procedures.update(sub_collection.procedures)
        collection.biomarkers.update(sub_collection.biomarkers)
        collection.pathways.update(sub_collection.pathways)
        
        count = sub_collection.entity_count
        total_entities += count
        logger.info(f"  Added {count} entities")
    
    logger.info(f"Total merged entities: {total_entities}")
    
    # Save merged collection
    logger.info(f"Saving to {output_file}...")
    collection.save(output_file)
    
    logger.info(f"✓ Merge complete: {collection.entity_count} total entities in {output_file}")


def main():
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python merge_entities.py <output_file> <input_file1> [input_file2] ...")
        print("Example: python merge_entities.py reference_entities_complete.jsonl reference_entities.jsonl hgnc_genes.jsonl")
        sys.exit(1)
    
    output_file = sys.argv[1]
    input_files = sys.argv[2:]
    
    merge_jsonl_files(input_files, output_file)


if __name__ == '__main__':
    main()
