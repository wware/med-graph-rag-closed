#!/bin/bash

rm -f reference_entities.jsonl

uv run python src/scripts/mesh_parser.py desc2025.xml reference_entities_mesh.jsonl
uv run python src/scripts/hgnc_parser.py hgnc_complete_set.tsv reference_entities_hgnc.jsonl
uv run python src/scripts/merge_entities.py reference_entities.jsonl reference_entities_mesh.jsonl reference_entities_hgnc.jsonl

rm -f reference_entities_hgnc.jsonl
rm -f reference_entities_mesh.jsonl
