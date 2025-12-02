"""
Load HGNC gene entities and create reference_entities.jsonl

Usage:
    python -m src.ingestion.load_hgnc_genes data/reference/hgnc_complete_set.txt
"""

import csv
import sys
from pathlib import Path
from src.schema.entity import BaseMedicalEntity as Entity, EntityCollection


def load_hgnc_genes(filepath: str) -> dict:
    """Load genes from HGNC TSV file."""
    genes = {}

    print(f"Loading HGNC genes from {filepath}...")

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")

        for row in reader:
            # Skip withdrawn genes
            if row.get("status") == "Approved":
                gene_id = row["hgnc_id"]
                symbol = row["symbol"]
                name = row["name"]

                # Collect synonyms
                synonyms = []
                if row.get("alias_symbol"):
                    synonyms.extend(
                        [s.strip() for s in row["alias_symbol"].split("|") if s.strip()]
                    )
                if row.get("prev_symbol"):
                    synonyms.extend(
                        [s.strip() for s in row["prev_symbol"].split("|") if s.strip()]
                    )

                genes[gene_id] = Entity(
                    entity_id=gene_id,
                    name=symbol,
                    entity_type="gene",
                    synonyms=synonyms,
                    abbreviations=[],
                    description=name,
                )

    print(f"  Loaded {len(genes)} approved genes")
    return genes


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.ingestion.load_hgnc_genes <hgnc_file.txt>")
        print("\nExample:")
        print(
            "  python -m src.ingestion.load_hgnc_genes data/reference/hgnc_complete_set.txt"
        )
        sys.exit(1)

    hgnc_file = sys.argv[1]

    if not Path(hgnc_file).exists():
        print(f"Error: File not found: {hgnc_file}")
        sys.exit(1)

    # Load genes
    genes = load_hgnc_genes(hgnc_file)

    # Try to load existing entities (diseases/drugs)
    print("\nChecking for existing entity collection...")
    try:
        existing = EntityCollection.load("reference_entities.jsonl")
        diseases = existing.diseases
        drugs = existing.drugs
        print(f"  Found existing: {len(diseases)} diseases, {len(drugs)} drugs")
    except Exception as e:
        print(f"  No existing collection found, starting fresh")
        diseases = {}
        drugs = {}

    # Create merged collection
    collection = EntityCollection(
        diseases=diseases, drugs=drugs, genes=genes, proteins={}  # Empty for now
    )

    # Save
    output_path = "reference_entities.jsonl"
    collection.save(output_path)

    print(f"\n✅ Saved entity collection to {output_path}")
    print(f"   Total entities: {len(diseases) + len(drugs) + len(genes)}")
    print(f"   - Diseases: {len(diseases)}")
    print(f"   - Drugs: {len(drugs)}")
    print(f"   - Genes: {len(genes)}")
    print(f"   - Proteins: 0")

    print(f"\n📝 Next steps:")
    print(f"   1. Re-run ingestion to extract genes:")
    print(
        f"      uv run python -m src.ingestion.pipeline --input-dir papers/raw --batch-size 10"
    )
    print(f"   2. Verify gene extraction:")
    print(f"      uv run python -m src.ingestion.query_index --entity-type gene")


if __name__ == "__main__":
    main()
