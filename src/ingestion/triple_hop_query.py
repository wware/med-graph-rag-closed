"""
Disease-Drug-Gene Multi-Hop Queries

Demonstrates powerful queries combining all three entity types:
1. Disease → Genes → Drugs (therapeutic target discovery)
2. Drug → Genes → Diseases (mechanism of action & repurposing)
3. Gene → Diseases + Drugs (gene function analysis)
4. Disease Triangle: Disease A → Shared Genes → Disease B
"""

from src.ingestion.pipeline import OpenSearchIndexer
from src.ingestion.embedding_generator import EmbeddingGenerator
from collections import Counter
from typing import Dict, List, Set


class TripleHopQuery:
    def __init__(self):
        self.indexer = OpenSearchIndexer(create_index=False)
        self.embedder = EmbeddingGenerator()
    
    def disease_to_genes_to_drugs(self, disease: str, top_genes: int = 5):
        """
        Disease → Genes → Drugs
        
        Find therapeutic targets by:
        1. Identify genes associated with disease
        2. Find drugs that target those genes
        
        Clinical Value: Drug discovery and target validation
        """
        print(f"\n{'='*80}")
        print(f"THERAPEUTIC TARGET DISCOVERY: {disease}")
        print(f"{'='*80}\n")
        
        # Step 1: Find papers about the disease
        print(f"Step 1: Finding papers about {disease}...")
        query_emb = self.embedder.embed_text(disease)
        disease_papers = self.indexer.search_hybrid(
            query_text=disease,
            query_embedding=query_emb,
            k=30,
            vector_weight=0.7
        )
        print(f"   Found {len(disease_papers)} papers\n")
        
        # Step 2: Extract genes from disease papers
        print("Step 2: Extracting genes associated with disease...")
        gene_counts = Counter()
        
        for paper in disease_papers:
            entities = paper['source'].get('entities', [])
            for entity in entities:
                if entity['type'] == 'gene':
                    gene_counts[entity['text']] += 1
        
        if not gene_counts:
            print("   ⚠️  No genes found. Check if gene entities are loaded.\n")
            return None
        
        top_genes_list = gene_counts.most_common(top_genes)
        print(f"   Top genes: {[g[0] for g in top_genes_list]}\n")
        
        # Step 3: For each gene, find drugs
        print("Step 3: Finding drugs targeting these genes...")
        gene_drug_map = {}
        
        for gene, count in top_genes_list:
            # Search for papers mentioning this gene + drugs
            gene_emb = self.embedder.embed_text(gene)
            gene_papers = self.indexer.search_hybrid(
                query_text=gene,
                query_embedding=gene_emb,
                k=15,
                vector_weight=0.6
            )
            
            drugs = set()
            for paper in gene_papers:
                entities = paper['source'].get('entities', [])
                for entity in entities:
                    if entity['type'] == 'drug':
                        drugs.add(entity['text'])
            
            if drugs:
                gene_drug_map[gene] = {
                    'mentions': count,
                    'drugs': list(drugs)[:5]
                }
        
        # Display results
        print(f"\n{'='*80}")
        print("RESULTS: Therapeutic Targets")
        print(f"{'='*80}\n")
        
        for gene, data in gene_drug_map.items():
            print(f"🧬 {gene} (mentioned {data['mentions']}x in {disease} papers)")
            print(f"   💊 Targeting drugs: {', '.join(data['drugs'])}")
            print()
        
        return gene_drug_map
    
    def drug_mechanism_analysis(self, drug: str):
        """
        Drug → Genes → Diseases
        
        Understand drug mechanism by:
        1. Find genes affected by drug
        2. Find diseases associated with those genes
        
        Clinical Value: Mechanism of action, side effects, repurposing
        """
        print(f"\n{'='*80}")
        print(f"MECHANISM OF ACTION: {drug}")
        print(f"{'='*80}\n")
        
        # Step 1: Find papers about the drug
        print(f"Step 1: Finding papers about {drug}...")
        drug_emb = self.embedder.embed_text(drug)
        drug_papers = self.indexer.search_hybrid(
            query_text=drug,
            query_embedding=drug_emb,
            k=25,
            vector_weight=0.6
        )
        print(f"   Found {len(drug_papers)} papers\n")
        
        # Step 2: Extract genes mentioned with drug
        print("Step 2: Extracting genes affected by drug...")
        gene_counts = Counter()
        
        for paper in drug_papers:
            entities = paper['source'].get('entities', [])
            for entity in entities:
                if entity['type'] == 'gene':
                    gene_counts[entity['text']] += 1
        
        if not gene_counts:
            print("   ⚠️  No genes found.\n")
            return None
        
        top_genes = gene_counts.most_common(5)
        print(f"   Target genes: {[g[0] for g in top_genes]}\n")
        
        # Step 3: For each gene, find associated diseases
        print("Step 3: Finding diseases associated with these genes...")
        gene_disease_map = {}
        
        for gene, count in top_genes:
            gene_emb = self.embedder.embed_text(gene)
            gene_papers = self.indexer.search_hybrid(
                query_text=gene,
                query_embedding=gene_emb,
                k=15,
                vector_weight=0.7
            )
            
            diseases = Counter()
            for paper in gene_papers:
                entities = paper['source'].get('entities', [])
                for entity in entities:
                    if entity['type'] == 'disease':
                        diseases[entity['text']] += 1
            
            if diseases:
                gene_disease_map[gene] = {
                    'drug_mentions': count,
                    'diseases': diseases.most_common(3)
                }
        
        # Display results
        print(f"\n{'='*80}")
        print("RESULTS: Drug Mechanism & Indications")
        print(f"{'='*80}\n")
        
        for gene, data in gene_disease_map.items():
            print(f"🧬 {gene} (mentioned {data['drug_mentions']}x with {drug})")
            print(f"   🏥 Associated diseases:")
            for disease, count in data['diseases']:
                print(f"      - {disease} ({count} papers)")
            print()
        
        return gene_disease_map
    
    def gene_function_profile(self, gene: str):
        """
        Gene → Diseases + Drugs
        
        Comprehensive gene profile:
        1. Diseases associated with gene
        2. Drugs targeting gene
        
        Clinical Value: Gene function, disease mechanisms, drug targets
        """
        print(f"\n{'='*80}")
        print(f"GENE FUNCTION PROFILE: {gene}")
        print(f"{'='*80}\n")
        
        # Find papers mentioning the gene
        print(f"Analyzing papers mentioning {gene}...")
        gene_emb = self.embedder.embed_text(gene)
        gene_papers = self.indexer.search_hybrid(
            query_text=gene,
            query_embedding=gene_emb,
            k=30,
            vector_weight=0.6
        )
        print(f"   Found {len(gene_papers)} papers\n")
        
        # Extract diseases and drugs
        diseases = Counter()
        drugs = Counter()
        
        for paper in gene_papers:
            entities = paper['source'].get('entities', [])
            for entity in entities:
                if entity['type'] == 'disease':
                    diseases[entity['text']] += 1
                elif entity['type'] == 'drug':
                    drugs[entity['text']] += 1
        
        # Display results
        print(f"{'='*80}")
        print(f"RESULTS: {gene} Function Profile")
        print(f"{'='*80}\n")
        
        print("🏥 Associated Diseases:")
        for disease, count in diseases.most_common(10):
            print(f"   {disease:40s} ({count} papers)")
        
        print("\n💊 Targeting Drugs:")
        for drug, count in drugs.most_common(10):
            print(f"   {drug:40s} ({count} papers)")
        
        return {
            'gene': gene,
            'diseases': diseases.most_common(10),
            'drugs': drugs.most_common(10)
        }
    
    def shared_genetic_mechanism(self, disease1: str, disease2: str):
        """
        Disease Triangle: Disease A → Shared Genes → Disease B
        
        Find genes that connect two diseases:
        1. Get genes for disease A
        2. Get genes for disease B
        3. Find intersection (shared mechanisms)
        
        Clinical Value: Comorbidity, drug repurposing, shared pathways
        """
        print(f"\n{'='*80}")
        print(f"SHARED GENETIC MECHANISMS")
        print(f"{disease1} ↔ {disease2}")
        print(f"{'='*80}\n")
        
        def get_genes_for_disease(disease: str) -> Counter:
            query_emb = self.embedder.embed_text(disease)
            papers = self.indexer.search_hybrid(
                query_text=disease,
                query_embedding=query_emb,
                k=20,
                vector_weight=0.7
            )
            
            genes = Counter()
            for paper in papers:
                entities = paper['source'].get('entities', [])
                for entity in entities:
                    if entity['type'] == 'gene':
                        genes[entity['text']] += 1
            
            return genes
        
        print(f"Finding genes for {disease1}...")
        genes1 = get_genes_for_disease(disease1)
        print(f"   Found {len(genes1)} genes\n")
        
        print(f"Finding genes for {disease2}...")
        genes2 = get_genes_for_disease(disease2)
        print(f"   Found {len(genes2)} genes\n")
        
        # Find shared genes
        shared = set(genes1.keys()) & set(genes2.keys())
        
        print(f"{'='*80}")
        print(f"RESULTS: {len(shared)} Shared Genes")
        print(f"{'='*80}\n")
        
        if shared:
            print("🧬 Shared genetic mechanisms:")
            for gene in sorted(shared)[:15]:
                print(f"   {gene:20s} ({disease1}: {genes1[gene]}x, {disease2}: {genes2[gene]}x)")
            
            # Find drugs targeting shared genes
            print(f"\n💊 Drugs targeting shared mechanisms:")
            shared_gene_drugs = Counter()
            
            for gene in list(shared)[:5]:  # Top 5 shared genes
                gene_emb = self.embedder.embed_text(gene)
                papers = self.indexer.search_hybrid(
                    query_text=gene,
                    query_embedding=gene_emb,
                    k=10,
                    vector_weight=0.6
                )
                
                for paper in papers:
                    entities = paper['source'].get('entities', [])
                    for entity in entities:
                        if entity['type'] == 'drug':
                            shared_gene_drugs[entity['text']] += 1
            
            for drug, count in shared_gene_drugs.most_common(10):
                print(f"   {drug:30s} ({count} mentions)")
        else:
            print("No shared genes found in current dataset.")
        
        return {
            'disease1': disease1,
            'disease2': disease2,
            'shared_genes': list(shared),
            'genes1_count': len(genes1),
            'genes2_count': len(genes2)
        }


def main():
    """Run example queries"""
    thq = TripleHopQuery()
    
    print("\n" + "="*80)
    print("DISEASE-DRUG-GENE MULTI-HOP QUERIES")
    print("="*80)
    
    # Example 1: Therapeutic target discovery
    print("\n\n### EXAMPLE 1: Therapeutic Target Discovery ###")
    thq.disease_to_genes_to_drugs("breast cancer", top_genes=5)
    
    # Example 2: Drug mechanism analysis
    print("\n\n### EXAMPLE 2: Drug Mechanism of Action ###")
    thq.drug_mechanism_analysis("cisplatin")
    
    # Example 3: Gene function profile
    print("\n\n### EXAMPLE 3: Gene Function Profile ###")
    thq.gene_function_profile("BRCA1")
    
    # Example 4: Shared genetic mechanisms
    print("\n\n### EXAMPLE 4: Shared Genetic Mechanisms ###")
    thq.shared_genetic_mechanism("breast cancer", "ovarian cancer")


if __name__ == "__main__":
    main()
