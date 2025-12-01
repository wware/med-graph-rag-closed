#!/usr/bin/env python3
"""
Parse MeSH descriptors from XML and convert to EntityCollection JSONL format.

MeSH uses tree numbers to categorize terms:
- D003 = Chemicals and Drugs
- D004 = Chemicals and Drugs (continued)
- D013 = Biological Science Terms (includes genes, but limited)
- C = Disease or Syndrome
- F = Psychiatry and Psychology
- G = Biological Phenomena, Genetics

This parser focuses on:
1. Diseases: Tree starting with C (Disease or Syndrome)
2. Drugs: Tree starting with D003, D004 (Chemicals and Drugs)
"""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict
import xml.etree.ElementTree as ET
from datetime import datetime
from src.schema.entity import Disease, Drug, EntityCollection

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MeSHParser:
    """Stream-based parser for MeSH XML descriptor records."""

    # MeSH tree number prefixes for categorization
    # Tree numbers are hierarchical like D02.355.291.933.125
    # We only care about the first component (D02, C23, etc.)
    DISEASE_TREES = {"C"}  # Disease or Syndrome (all C trees)
    DRUG_TREES = {"D"}  # Chemicals and Drugs (all D trees, but filter below)
    PROCEDURE_TREES = {"E", "J"}  # Procedures and other

    def __init__(self, xml_path: str):
        """Initialize parser with path to MeSH XML file."""
        self.xml_path = xml_path
        self.diseases_created = 0
        self.drugs_created = 0
        self.skipped = 0

    def _extract_synonyms(self, concept_list_elem) -> tuple[List[str], List[str]]:
        """Extract synonyms and abbreviations from ConceptList."""
        synonyms = []
        abbreviations = []

        if concept_list_elem is None:
            return synonyms, abbreviations

        for concept in concept_list_elem.findall("Concept"):
            # Entry terms are synonyms
            for entry_term in concept.findall("ConceptName"):
                name_str = entry_term.find("String")
                if name_str is not None and name_str.text:
                    synonyms.append(name_str.text.strip())

            # Abbreviations
            for entry_term in concept.findall("Abbreviation"):
                if entry_term.text:
                    abbreviations.append(entry_term.text.strip())

        # Remove duplicates while preserving order
        synonyms = list(dict.fromkeys(synonyms))
        abbreviations = list(dict.fromkeys(abbreviations))

        return synonyms, abbreviations

    def _get_tree_category(self, tree_numbers: List[str]) -> Optional[str]:
        """Determine entity category from tree numbers.

        MeSH tree structure:
        - C* = Disease or Syndrome
        - D* = Chemicals and Drugs

        Extract first letter from first tree number.
        """
        if not tree_numbers:
            return None

        first_tree = tree_numbers[0]
        first_letter = first_tree[0] if first_tree else ""

        if first_letter == "C":
            return "disease"
        elif first_letter == "D":
            return "drug"

        return None

    def _create_disease(
        self,
        descriptor_ui: str,
        descriptor_name: str,
        synonyms: List[str],
        abbreviations: List[str],
    ) -> Disease:
        """Create a Disease entity from MeSH descriptor."""
        return Disease(
            entity_id=descriptor_ui,
            mesh_id=descriptor_ui,
            name=descriptor_name,
            synonyms=synonyms,
            abbreviations=abbreviations,
            source="mesh",
            created_at=datetime.now(),
            category="other",  # MeSH doesn't specify, could be enhanced
        )

    def _create_drug(
        self,
        descriptor_ui: str,
        descriptor_name: str,
        synonyms: List[str],
        abbreviations: List[str],
    ) -> Drug:
        """Create a Drug entity from MeSH descriptor."""
        return Drug(
            entity_id=descriptor_ui,
            name=descriptor_name,
            synonyms=synonyms,
            abbreviations=abbreviations,
            source="mesh",
            created_at=datetime.now(),
            drug_class="unknown",  # Could extract from pharmacological actions
        )

    def parse(self) -> EntityCollection:
        """
        Stream through XML and create EntityCollection.
        Uses iterparse to avoid loading entire 300MB file into memory.
        """
        collection = EntityCollection()

        logger.info(f"Parsing MeSH descriptors from {self.xml_path}")

        # Use iterparse for streaming - memory efficient
        context = ET.iterparse(self.xml_path, events=["end"])

        for event, elem in context:
            # Only process DescriptorRecord elements
            if elem.tag != "DescriptorRecord":
                continue

            try:
                # Extract descriptor ID
                descriptor_ui_elem = elem.find("DescriptorUI")
                if descriptor_ui_elem is None or not descriptor_ui_elem.text:
                    self.skipped += 1
                    elem.clear()
                    continue

                descriptor_ui = descriptor_ui_elem.text.strip()

                # Extract descriptor name
                descriptor_name_elem = elem.find("DescriptorName/String")
                if descriptor_name_elem is None or not descriptor_name_elem.text:
                    self.skipped += 1
                    elem.clear()
                    continue

                descriptor_name = descriptor_name_elem.text.strip()

                # Extract tree numbers
                tree_numbers = []
                tree_number_list = elem.find("TreeNumberList")
                if tree_number_list is not None:
                    for tree_elem in tree_number_list.findall("TreeNumber"):
                        if tree_elem.text:
                            tree_numbers.append(tree_elem.text.strip())

                # Determine category from tree numbers
                category = self._get_tree_category(tree_numbers)

                # Debug output for first 10 records
                if self.diseases_created + self.drugs_created + self.skipped < 10:
                    print(f"DEBUG {descriptor_ui}: {descriptor_name}")
                    print(f"  Trees: {tree_numbers[:2]}")
                    print(f"  Category: {category}")

                if category is None:
                    self.skipped += 1
                    elem.clear()
                    continue

                # Extract synonyms and abbreviations
                concept_list = elem.find("ConceptList")
                synonyms, abbreviations = self._extract_synonyms(concept_list)

                # Create appropriate entity type
                if category == "disease":
                    disease = self._create_disease(
                        descriptor_ui, descriptor_name, synonyms, abbreviations
                    )
                    collection.add_disease(disease)
                    self.diseases_created += 1

                elif category == "drug":
                    drug = self._create_drug(
                        descriptor_ui, descriptor_name, synonyms, abbreviations
                    )
                    collection.add_drug(drug)
                    self.drugs_created += 1

                # Log progress every 1000 records
                total = self.diseases_created + self.drugs_created
                if total % 1000 == 0:
                    logger.info(
                        f"Processed {total} entities: "
                        f"{self.diseases_created} diseases, {self.drugs_created} drugs"
                    )

            except Exception as e:
                logger.warning(f"Error processing descriptor {descriptor_ui}: {e}")
                self.skipped += 1

            finally:
                elem.clear()  # Free memory

        logger.info(
            f"✓ Parse complete: {self.diseases_created} diseases, "
            f"{self.drugs_created} drugs, {self.skipped} skipped"
        )

        return collection


def main():
    """Main entry point for MeSH parser."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python mesh_parser.py <path/to/desc2025.xml> [output_path]")
        print("Example: python mesh_parser.py ~/desc2025.xml reference_entities.jsonl")
        sys.exit(1)

    xml_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "reference_entities.jsonl"

    if not Path(xml_path).exists():
        print(f"Error: File not found: {xml_path}")
        sys.exit(1)

    # Parse MeSH
    parser = MeSHParser(xml_path)
    collection = parser.parse()

    # Save to JSONL
    logger.info(f"Saving {collection.entity_count} entities to {output_path}")
    collection.save(output_path)
    logger.info(f"✓ Saved to {output_path}")


if __name__ == "__main__":
    main()
