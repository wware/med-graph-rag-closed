from src.ingestion.triple_hop_query import TripleHopQuery

thq = TripleHopQuery()
print(thq.disease_to_genes_to_drugs("diabetes"))
print(thq.drug_mechanism_analysis("aspirin"))
print(thq.gene_function_profile("TP53"))
print(thq.shared_genetic_mechanism("Alzheimer's disease", "Parkinson's disease"))
