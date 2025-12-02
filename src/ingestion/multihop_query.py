"""
Multi-hop query using diseases and drugs (no gene data required).

Demonstrates queries that work with the current entity extraction:
1. Disease → Related Diseases (via co-occurrence)
2. Drug → Diseases → Related Drugs
3. Disease Comorbidity Analysis
"""

from src.ingestion.pipeline import OpenSearchIndexer
from src.ingestion.embedding_generator import EmbeddingGenerator
from collections import defaultdict, Counter
from typing import List, Dict, Set


class DiseaseDrugMultiHop:
    def __init__(self):
        self.indexer = OpenSearchIndexer(create_index=False)
        self.embedder = EmbeddingGenerator()

    def find_related_diseases(self, disease_name: str, top_k: int = 10):
        """
        Find diseases that frequently co-occur with the target disease.
        This can reveal comorbidities or related conditions.
        """
        print(f"\n{'='*80}")
        print(f"QUERY: Diseases Related to '{disease_name}'")
        print(f"{'='*80}\n")

        # Find papers mentioning the disease
        query_embedding = self.embedder.embed_text(disease_name)
        results = self.indexer.search_hybrid(
            query_text=disease_name,
            query_embedding=query_embedding,
            k=30,
            vector_weight=0.7,
        )

        print(f"Analyzing {len(results)} papers mentioning '{disease_name}'...\n")

        # Extract co-occurring diseases
        related_diseases = Counter()

        for result in results:
            entities = result["source"].get("entities", [])
            diseases_in_chunk = set()

            for entity in entities:
                if entity["type"] == "disease":
                    disease_text = entity["text"].lower()
                    if disease_text != disease_name.lower():
                        diseases_in_chunk.add(entity["text"])

            # Count co-occurrences
            for disease in diseases_in_chunk:
                related_diseases[disease] += 1

        # Display results
        print(f"{'='*80}")
        print(f"Top {top_k} Related Diseases (by co-occurrence)")
        print(f"{'='*80}\n")

        for i, (disease, count) in enumerate(related_diseases.most_common(top_k), 1):
            print(f"{i:2d}. {disease:40s} (co-occurs {count} times)")

        return related_diseases.most_common(top_k)

    def drug_disease_network(self, drug_name: str):
        """
        Multi-hop: Drug → Diseases → Related Drugs

        1. Find diseases treated by the drug
        2. Find other drugs mentioned for those diseases
        3. Identify potential combination therapies or alternatives
        """
        print(f"\n{'='*80}")
        print(f"MULTI-HOP: Drug Network for '{drug_name}'")
        print(f"{'='*80}\n")

        # Step 1: Find papers mentioning the drug
        print(f"Step 1: Finding papers about {drug_name}...")
        drug_embedding = self.embedder.embed_text(drug_name)
        drug_results = self.indexer.search_hybrid(
            query_text=drug_name,
            query_embedding=drug_embedding,
            k=20,
            vector_weight=0.6,
        )

        print(f"   Found {len(drug_results)} papers\n")

        # Extract diseases mentioned with this drug
        print("Step 2: Extracting diseases mentioned with this drug...")
        diseases_with_drug = Counter()

        for result in drug_results:
            entities = result["source"].get("entities", [])
            for entity in entities:
                if entity["type"] == "disease":
                    diseases_with_drug[entity["text"]] += 1

        top_diseases = diseases_with_drug.most_common(5)
        print(f"   Top indications: {[d[0] for d in top_diseases]}\n")

        # Step 3: For each disease, find other drugs
        print("Step 3: Finding alternative/complementary drugs...")
        related_drugs = Counter()

        for disease, _ in top_diseases[:3]:  # Top 3 diseases
            disease_embedding = self.embedder.embed_text(disease)
            disease_results = self.indexer.search_hybrid(
                query_text=disease,
                query_embedding=disease_embedding,
                k=15,
                vector_weight=0.6,
            )

            for result in disease_results:
                entities = result["source"].get("entities", [])
                for entity in entities:
                    if entity["type"] == "drug":
                        drug_text = entity["text"].lower()
                        if drug_text != drug_name.lower():
                            related_drugs[entity["text"]] += 1

        # Display results
        print(f"\n{'='*80}")
        print("RESULTS: Drug Network Analysis")
        print(f"{'='*80}\n")

        print(f"Primary Indications for {drug_name}:")
        for i, (disease, count) in enumerate(top_diseases, 1):
            print(f"  {i}. {disease} ({count} mentions)")

        print(f"\nRelated/Alternative Drugs:")
        for i, (drug, count) in enumerate(related_drugs.most_common(10), 1):
            print(f"  {i}. {drug} ({count} mentions)")

        return {
            "drug": drug_name,
            "indications": [d[0] for d in top_diseases],
            "related_drugs": [d[0] for d in related_drugs.most_common(10)],
        }

    def disease_comorbidity_analysis(self, disease1: str, disease2: str):
        """
        Analyze the relationship between two diseases.
        Find papers discussing both and extract shared drug treatments.
        """
        print(f"\n{'='*80}")
        print(f"COMORBIDITY ANALYSIS: {disease1} + {disease2}")
        print(f"{'='*80}\n")

        # Build query for papers mentioning both diseases
        combined_query = f"{disease1} {disease2}"
        query_embedding = self.embedder.embed_text(combined_query)

        results = self.indexer.search_hybrid(
            query_text=combined_query,
            query_embedding=query_embedding,
            k=20,
            vector_weight=0.7,
        )

        # Filter for papers actually mentioning both
        papers_with_both = []
        for result in results:
            entities = result["source"].get("entities", [])
            disease_mentions = {
                e["text"].lower() for e in entities if e["type"] == "disease"
            }

            if (
                disease1.lower() in disease_mentions
                and disease2.lower() in disease_mentions
            ):
                papers_with_both.append(result)

        print(f"Found {len(papers_with_both)} papers discussing both conditions\n")

        if not papers_with_both:
            print("No papers found discussing both conditions together.")
            return None

        # Extract drugs mentioned in these papers
        shared_drugs = Counter()
        for result in papers_with_both:
            entities = result["source"].get("entities", [])
            for entity in entities:
                if entity["type"] == "drug":
                    shared_drugs[entity["text"]] += 1

        # Display results
        print(f"{'='*80}")
        print("RESULTS: Comorbidity Insights")
        print(f"{'='*80}\n")

        print(f"Papers discussing both {disease1} and {disease2}:")
        for i, result in enumerate(papers_with_both[:3], 1):
            source = result["source"]
            print(f"\n{i}. {source.get('title', 'N/A')[:80]}...")
            print(f"   PMC: {source.get('pmc_id', 'N/A')}")
            print(f"   Section: {source.get('section', 'N/A')}")

        if shared_drugs:
            print(f"\nDrugs mentioned in comorbidity context:")
            for i, (drug, count) in enumerate(shared_drugs.most_common(10), 1):
                print(f"  {i}. {drug} ({count} mentions)")

        return {
            "disease1": disease1,
            "disease2": disease2,
            "papers_found": len(papers_with_both),
            "shared_drugs": [d[0] for d in shared_drugs.most_common(10)],
        }


def main():
    """Run example queries"""
    mhq = DiseaseDrugMultiHop()

    print("\n" + "=" * 80)
    print("MEDICAL LITERATURE MULTI-HOP QUERIES")
    print("(Using Disease and Drug Entities)")
    print("=" * 80)

    # Example 1: Related diseases
    print("\n\n### EXAMPLE 1: Finding related diseases ###")
    mhq.find_related_diseases("breast cancer", top_k=10)

    # Example 2: Drug network
    print("\n\n### EXAMPLE 2: Drug treatment network ###")
    mhq.drug_disease_network("aspirin")

    # Example 3: Comorbidity analysis
    print("\n\n### EXAMPLE 3: Disease comorbidity ###")
    mhq.disease_comorbidity_analysis("diabetes", "cancer")


if __name__ == "__main__":
    main()
