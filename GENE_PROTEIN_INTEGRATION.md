# Gene and Protein Entity Integration Guide

## Overview

This guide explains how to integrate gene (HGNC) and protein (UniProt) entities into the existing entity extraction pipeline to enable gene-disease and protein-drug relationship discovery.

## Current Status

**Entities Currently Extracted:**
- ✅ **Diseases**: 9,399 entities across 6,614 chunks
- ✅ **Drugs**: 8,768 entities across 6,614 chunks
- ❌ **Genes**: Not yet integrated
- ❌ **Proteins**: Not yet integrated

## Data Sources

### HGNC (HUGO Gene Nomenclature Committee)
- **Purpose**: Official gene symbols and names for human genes
- **Download**: https://www.genenames.org/download/statistics-and-files/
- **File**: `hgnc_complete_set.txt` (TSV format)
- **Key Fields**:
  - `symbol`: Official gene symbol (e.g., "BRCA1")
  - `name`: Full gene name
  - `alias_symbol`: Alternative symbols
  - `prev_symbol`: Previous symbols
  - `hgnc_id`: Unique identifier

### UniProt (Universal Protein Resource)
- **Purpose**: Protein sequences and functional information
- **Download**: https://www.uniprot.org/downloads
- **File**: `uniprot_sprot_human.dat` or use REST API
- **Key Fields**:
  - `entry_name`: Protein name
  - `protein_names`: Recommended and alternative names
  - `gene_names`: Associated gene symbols
  - `accession`: UniProt ID (e.g., "P38398")

## Implementation Steps

### 1. Download Reference Data

```bash
# Create data directory
mkdir -p data/reference

# Download HGNC data
wget -O data/reference/hgnc_complete_set.txt \
  "https://www.genenames.org/cgi-bin/download/custom?col=gd_hgnc_id&col=gd_app_sym&col=gd_app_name&col=gd_prev_sym&col=gd_aliases&status=Approved&hgnc_dbtag=on&order_by=gd_app_sym_sort&format=text&submit=submit"

# Download UniProt human proteins (reviewed/Swiss-Prot)
wget -O data/reference/uniprot_human.txt.gz \
  "https://rest.uniprot.org/uniprotkb/stream?format=tsv&query=(organism_id:9606)%20AND%20(reviewed:true)&fields=accession,id,gene_names,protein_name,gene_synonym"

gunzip data/reference/uniprot_human.txt.gz
```

### 2. Create Entity Loader Script

Create `src/ingestion/load_gene_protein_entities.py`:

```python
"""Load gene and protein entities from HGNC and UniProt."""

import csv
from src.schema.entity import Entity, EntityCollection

def load_hgnc_genes(filepath: str) -> dict:
    """Load genes from HGNC TSV file."""
    genes = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            gene_id = row['hgnc_id']
            symbol = row['symbol']
            name = row['name']
            
            # Collect synonyms
            synonyms = []
            if row.get('alias_symbol'):
                synonyms.extend(row['alias_symbol'].split('|'))
            if row.get('prev_symbol'):
                synonyms.extend(row['prev_symbol'].split('|'))
            
            genes[gene_id] = Entity(
                entity_id=gene_id,
                name=symbol,
                entity_type='gene',
                synonyms=[s.strip() for s in synonyms if s.strip()],
                abbreviations=[],
                description=name
            )
    
    return genes

def load_uniprot_proteins(filepath: str) -> dict:
    """Load proteins from UniProt TSV file."""
    proteins = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            accession = row['Entry']
            entry_name = row['Entry Name']
            protein_name = row['Protein names']
            gene_names = row.get('Gene Names', '')
            
            # Parse protein names (format: "Name1 (Name2) (Name3)")
            synonyms = []
            if '(' in protein_name:
                parts = protein_name.split('(')
                main_name = parts[0].strip()
                synonyms = [p.strip(') ') for p in parts[1:]]
            else:
                main_name = protein_name.strip()
            
            # Add gene names as synonyms
            if gene_names:
                synonyms.extend(gene_names.split())
            
            proteins[accession] = Entity(
                entity_id=accession,
                name=main_name,
                entity_type='protein',
                synonyms=[s for s in synonyms if s],
                abbreviations=[],
                description=entry_name
            )
    
    return proteins

def main():
    """Load all entities and save to reference_entities.jsonl."""
    print("Loading HGNC genes...")
    genes = load_hgnc_genes('data/reference/hgnc_complete_set.txt')
    print(f"  Loaded {len(genes)} genes")
    
    print("Loading UniProt proteins...")
    proteins = load_uniprot_proteins('data/reference/uniprot_human.txt')
    print(f"  Loaded {len(proteins)} proteins")
    
    # Create entity collection
    collection = EntityCollection(
        diseases={},  # Load existing if available
        drugs={},     # Load existing if available
        genes=genes,
        proteins=proteins
    )
    
    # Save to file
    output_path = 'reference_entities.jsonl'
    collection.save(output_path)
    print(f"\nSaved entity collection to {output_path}")
    print(f"Total entities: {len(genes) + len(proteins)}")

if __name__ == "__main__":
    main()
```

### 3. Merge with Existing Entities

If you already have disease/drug entities, merge them:

```python
# Load existing entities
try:
    existing = EntityCollection.load('reference_entities.jsonl')
    diseases = existing.diseases
    drugs = existing.drugs
except:
    diseases = {}
    drugs = {}

# Create merged collection
collection = EntityCollection(
    diseases=diseases,
    drugs=drugs,
    genes=genes,
    proteins=proteins
)
```

### 4. Re-run Entity Extraction

After loading the reference entities:

```bash
# Re-process papers with gene/protein extraction
uv run python -m src.ingestion.pipeline \
    --input-dir papers/raw \
    --batch-size 10
```

## Expected Results

After integration, you'll be able to:

### Multi-Hop Queries
- **Disease → Genes → Drugs**: Find therapeutic targets
- **Gene → Diseases**: Discover disease associations
- **Protein → Drugs**: Identify drug-protein interactions

### Example Queries
```python
# Find genes associated with breast cancer
mhq.disease_to_genes("breast cancer")

# Find drugs targeting BRCA1
mhq.gene_to_drugs("BRCA1")

# Shared genes between diseases
mhq.shared_genetic_associations("diabetes", "obesity")
```

## Performance Considerations

**Entity Counts (Estimated):**
- HGNC Genes: ~40,000 entries
- UniProt Human Proteins: ~20,000 reviewed entries
- Total: ~60,000 additional entities

**FlashText Performance:**
- Current: 9,399 diseases + 8,768 drugs = 18,167 entities
- After: 18,167 + 60,000 = ~78,000 entities
- FlashText scales linearly (O(N)), so extraction time will increase proportionally
- Expected: ~4x slower entity extraction, but still much faster than regex

**Optimization Tips:**
1. Filter to high-confidence genes (e.g., only approved HGNC symbols)
2. Limit proteins to those with drug interactions
3. Use case-sensitive matching for gene symbols (e.g., "TP53" vs "tp53")

## Validation

After integration, verify extraction:

```bash
# Check entity type distribution
curl -s "localhost:9200/medical-papers/_search?pretty" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "entity_types": {
      "nested": { "path": "entities" },
      "aggs": {
        "types": { "terms": { "field": "entities.type" } }
      }
    }
  }
}'

# Search for specific gene
uv run python -m src.ingestion.query_index --entity-type gene --entity-text "BRCA1"
```

## Next Steps

1. Download HGNC and UniProt data
2. Create and run the loader script
3. Re-index papers with gene/protein extraction
4. Test multi-hop queries with gene relationships
5. Build knowledge graph with gene-disease-drug networks
