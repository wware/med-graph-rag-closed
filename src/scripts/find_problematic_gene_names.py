"""
Find gene symbols that match common English words (potential false positives).

Usage:
    python -m src.scripts.find_problematic_gene_names
"""

from src.schema.entity import EntityCollection


def find_problematic_gene_names(filepath: str = "reference_entities.jsonl"):
    """Find genes whose symbols might cause false positive matches."""

    # Common English words that might conflict with gene symbols
    COMMON_WORDS = {
        "A",
        "AN",
        "AND",
        "AS",
        "AT",
        "BE",
        "BY",
        "FOR",
        "FROM",
        "HAS",
        "HE",
        "IF",
        "IN",
        "IS",
        "IT",
        "ITS",
        "OF",
        "ON",
        "OR",
        "THAT",
        "THE",
        "TO",
        "WAS",
        "WILL",
        "WITH",
        "ARE",
        "NOT",
        "BUT",
        "CAN",
        "HAD",
        "HER",
        "WE",
        "WHEN",
        "WHERE",
        "WHO",
        "MAY",
        "SO",
        "UP",
        "OUT",
        "NO",
        "THAN",
        "ALL",
        "BEEN",
        "WERE",
        "THEIR",
        "THERE",
        "ABOUT",
        "INTO",
        "AFTER",
        "ALSO",
    }

    print(f"Loading entity collection from {filepath}...")
    collection = EntityCollection.load(filepath)

    print(f"Checking {len(collection.genes)} genes...\n")

    problematic = []

    for gene_id, gene in collection.genes.items():
        # Check canonical name
        if gene.name.upper() in COMMON_WORDS:
            problematic.append(
                {
                    "id": gene_id,
                    "name": gene.name,
                    "type": "canonical_name",
                    "conflict": gene.name,
                }
            )

        # Check synonyms
        for syn in gene.synonyms:
            if syn.upper() in COMMON_WORDS:
                problematic.append(
                    {
                        "id": gene_id,
                        "name": gene.name,
                        "type": "synonym",
                        "conflict": syn,
                    }
                )

    # Display results
    print(f"{'='*80}")
    print(f"Found {len(problematic)} potential conflicts")
    print(f"{'='*80}\n")

    if problematic:
        # Group by conflict word
        by_word = {}
        for p in problematic:
            word = p["conflict"].upper()
            if word not in by_word:
                by_word[word] = []
            by_word[word].append(p)

        # Show top conflicts
        sorted_words = sorted(by_word.items(), key=lambda x: len(x[1]), reverse=True)

        print("Top conflicting words:\n")
        for word, conflicts in sorted_words[:20]:
            print(f"{word:15s} → {len(conflicts)} genes")
            for c in conflicts[:3]:
                print(f"  - {c['name']} ({c['id']}) [{c['type']}]")
            if len(conflicts) > 3:
                print(f"  ... and {len(conflicts) - 3} more")
            print()

    return problematic


if __name__ == "__main__":
    find_problematic_gene_names()
