#!/usr/bin/env python3
"""
Parse HGNC gene nomenclature data from TSV and convert to EntityCollection JSONL format.

HGNC (HUGO Gene Nomenclature Committee) provides a complete dataset of approved
human gene symbols with identifiers, chromosomal locations, and synonyms.

Download the complete dataset from:
https://www.genenames.org/download/statistics-and-files/

Look for: hgnc_complete_set.tsv
"""

import csv
import logging
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from src.schema.entity import Gene, EntityCollection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HGNCParser:
    """Parser for HGNC TSV gene nomenclature data."""
    
    def __init__(self, tsv_path: str):
        """Initialize parser with path to HGNC TSV file."""
        self.tsv_path = tsv_path
        self.genes_created = 0
        self.skipped = 0
        
    def _parse_synonyms(self, alias_field: Optional[str], prev_symbol_field: Optional[str]) -> List[str]:
        """Extract synonyms from alias and previous symbol fields.
        
        HGNC uses pipe-delimited values for multiple entries.
        """
        synonyms = []
        
        # Aliases (alternative names used to refer to this gene)
        if alias_field:
            aliases = [a.strip() for a in alias_field.split('|') if a.strip()]
            synonyms.extend(aliases)
        
        # Previous symbols (historically approved symbols)
        if prev_symbol_field:
            prev = [p.strip() for p in prev_symbol_field.split('|') if p.strip()]
            synonyms.extend(prev)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(synonyms))
    
    def _create_gene(self, hgnc_id: str, symbol: str, name: str, 
                    synonyms: List[str], chromosome: Optional[str],
                    entrez_id: Optional[str]) -> Gene:
        """Create a Gene entity from HGNC data."""
        # Filter synonyms to only keep all-caps (likely gene symbols)
        # This avoids matching common English words
        filtered_synonyms = [s for s in synonyms if s.isupper()]
        
        return Gene(
            entity_id=hgnc_id,
            hgnc_id=hgnc_id,
            name=name,
            symbol=symbol,
            synonyms=filtered_synonyms,
            abbreviations=[symbol] if symbol.isupper() else [],  # Only if symbol is all-caps
            chromosome=chromosome,
            entrez_id=entrez_id,
            source='hgnc',
            created_at=datetime.now()
        )
    
    def parse(self) -> EntityCollection:
        """
        Parse HGNC TSV and create EntityCollection.
        """
        collection = EntityCollection()
        
        logger.info(f"Parsing HGNC genes from {self.tsv_path}")
        
        try:
            with open(self.tsv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                
                # Expected columns in HGNC TSV
                # hgnc_id, symbol, name, locus_group, locus_type, status, 
                # location, location_sortable, alias_symbol, alias_name,
                # prev_symbol, prev_name, gene_family, gene_family_id,
                # date_approved_reserved, date_symbol_changed, date_name_changed,
                # date_modified, entrez_id, vega_id, ucsc_id, ena,
                # refseq_accession, ccds_id, uniprot_ids, pubmed_id, mgd_id,
                # lsdb, lsdb_links, ena, refseq_accession, ccds_id, uniprot_ids, ...
                
                for row_num, row in enumerate(reader, start=2):
                    try:
                        # Extract required fields
                        hgnc_id = row.get('hgnc_id', '').strip()
                        symbol = row.get('symbol', '').strip()
                        name = row.get('name', '').strip()
                        status = row.get('status', 'Approved').strip()
                        
                        # Skip withdrawn genes
                        if status != 'Approved':
                            self.skipped += 1
                            continue
                        
                        # Skip if missing critical fields
                        if not hgnc_id or not symbol or not name:
                            self.skipped += 1
                            continue
                        
                        # Extract optional fields
                        chromosome = row.get('location', '').strip() or None
                        entrez_id = row.get('entrez_id', '').strip() or None
                        
                        # Extract synonyms
                        alias_symbol = row.get('alias_symbol', '').strip()
                        prev_symbol = row.get('prev_symbol', '').strip()
                        synonyms = self._parse_synonyms(alias_symbol, prev_symbol)
                        
                        # Create gene entity
                        gene = self._create_gene(
                            hgnc_id, symbol, name, synonyms,
                            chromosome, entrez_id
                        )
                        
                        collection.add_gene(gene)
                        self.genes_created += 1
                        
                        # Log progress every 5000 records
                        if self.genes_created % 5000 == 0:
                            logger.info(f"Processed {self.genes_created} genes")
                    
                    except Exception as e:
                        logger.warning(f"Error processing row {row_num}: {e}")
                        self.skipped += 1
                        continue
        
        except FileNotFoundError:
            logger.error(f"File not found: {self.tsv_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise
        
        logger.info(f"✓ Parse complete: {self.genes_created} genes, {self.skipped} skipped")
        
        return collection


def main():
    """Main entry point for HGNC parser."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python hgnc_parser.py <path/to/hgnc_complete_set.tsv> [output_path]")
        print("Example: python hgnc_parser.py ~/hgnc_complete_set.tsv hgnc_genes.jsonl")
        print()
        print("Download HGNC data from:")
        print("  https://www.genenames.org/download/statistics-and-files/")
        sys.exit(1)
    
    tsv_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'hgnc_genes.jsonl'
    
    if not Path(tsv_path).exists():
        print(f"Error: File not found: {tsv_path}")
        sys.exit(1)
    
    # Parse HGNC
    parser = HGNCParser(tsv_path)
    collection = parser.parse()
    
    # Save to JSONL
    logger.info(f"Saving {collection.entity_count} entities to {output_path}")
    collection.save(output_path)
    logger.info(f"✓ Saved to {output_path}")


if __name__ == '__main__':
    main()
