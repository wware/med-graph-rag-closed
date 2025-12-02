#!/usr/bin/env python3
"""
Merge entity JSONL files by directly parsing JSON and reconstructing objects.
Works around Pydantic deserialization issues.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from src.schema.entity import (
    EntityCollection,
    Disease,
    Gene,
    Drug,
    Protein,
    Symptom,
    Procedure,
    Biomarker,
    Pathway,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Map type strings to classes
TYPE_TO_CLASS = {
    "disease": Disease,
    "gene": Gene,
    "drug": Drug,
    "protein": Protein,
    "symptom": Symptom,
    "procedure": Procedure,
    "biomarker": Biomarker,
    "pathway": Pathway,
}


def load_jsonl_raw(path: str) -> EntityCollection:
    """Load JSONL by parsing JSON directly and reconstructing objects."""
    collection = EntityCollection()

    with open(path, "r") as f:
        for line_num, line in enumerate(f, start=1):
            try:
                record = json.loads(line)
                entity_type = record.get("type")
                data = record.get("data", {})

                if not entity_type:
                    logger.warning(f"  Line {line_num}: Missing type field")
                    continue

                # Convert created_at string back to datetime if present
                if "created_at" in data and isinstance(data["created_at"], str):
                    try:
                        data["created_at"] = datetime.fromisoformat(data["created_at"])
                    except:
                        data["created_at"] = datetime.now()

                # Get the class for this type
                entity_class = TYPE_TO_CLASS.get(entity_type)
                if not entity_class:
                    logger.warning(f"  Line {line_num}: Unknown type '{entity_type}'")
                    continue

                # Reconstruct the object
                entity = entity_class(**data)

                # Add to appropriate collection
                if entity_type == "disease":
                    collection.diseases[entity.entity_id] = entity
                elif entity_type == "gene":
                    collection.genes[entity.entity_id] = entity
                elif entity_type == "drug":
                    collection.drugs[entity.entity_id] = entity
                elif entity_type == "protein":
                    collection.proteins[entity.entity_id] = entity
                elif entity_type == "symptom":
                    collection.symptoms[entity.entity_id] = entity
                elif entity_type == "procedure":
                    collection.procedures[entity.entity_id] = entity
                elif entity_type == "biomarker":
                    collection.biomarkers[entity.entity_id] = entity
                elif entity_type == "pathway":
                    collection.pathways[entity.entity_id] = entity

            except Exception as e:
                logger.warning(f"  Line {line_num}: {e}")
                continue

    return collection


def merge_collections(input_files: list[str], output_file: str) -> None:
    """Merge multiple JSONL files into a single EntityCollection."""

    collection = EntityCollection()

    for input_file in input_files:
        if not Path(input_file).exists():
            logger.warning(f"File not found, skipping: {input_file}")
            continue

        logger.info(f"Loading {input_file}...")
        try:
            sub_collection = load_jsonl_raw(input_file)

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
            logger.info(f"  ✓ Loaded {count} entities")
        except Exception as e:
            logger.error(f"  Error loading {input_file}: {e}")
            raise

    logger.info(f"\nMerged collection:")
    logger.info(f"  Diseases: {len(collection.diseases)}")
    logger.info(f"  Genes: {len(collection.genes)}")
    logger.info(f"  Drugs: {len(collection.drugs)}")
    logger.info(f"  Proteins: {len(collection.proteins)}")
    logger.info(f"  Total: {collection.entity_count}")

    # Save merged collection
    logger.info(f"\nSaving to {output_file}...")
    collection.save(output_file)

    logger.info(f"✓ Merge complete")


def main():
    import sys

    if len(sys.argv) < 3:
        print(
            "Usage: python merge_entities_manual.py <output_file> <input_file1> [input_file2] ..."
        )
        print(
            "Example: python merge_entities_manual.py reference_entities_complete.jsonl reference_entities.jsonl hgnc_genes.jsonl"
        )
        sys.exit(1)

    output_file = sys.argv[1]
    input_files = sys.argv[2:]

    merge_collections(input_files, output_file)


if __name__ == "__main__":
    main()
