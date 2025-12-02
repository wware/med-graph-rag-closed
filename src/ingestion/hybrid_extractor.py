"""
Hybrid entity extraction with both FlashText (fast) and BioBERT (accurate) options.

This module provides two extraction strategies:
1. FlashTextExtractor: Fast Aho-Corasick matching, good for preprocessing
2. BioBERTExtractor: Context-aware BERT-based NER, handles ambiguous cases
3. HybridExtractor: Uses both - BioBERT for accuracy, FlashText as fallback
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging
from src.schema.entity import EntityMention, EntityCollection, ExtractedEntity
from src.schema.relationship import Relationship
from src.ingestion.embedding_cache import EmbeddingCache
from src.ingestion.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)


class BaseEntityExtractor(ABC):
    """Base class for entity extractors"""

    def __init__(self, entity_collection: EntityCollection, cache: EmbeddingCache):
        self.entities = entity_collection
        self.cache = cache
        self.embedder = EmbeddingGenerator()

    @abstractmethod
    def extract_entities(self, text: str, chunk_id: str) -> List[ExtractedEntity]:
        """Extract entities from text"""
        pass


class FlashTextExtractor(BaseEntityExtractor):
    """Fast entity extraction using FlashText (Aho-Corasick algorithm).

    Pros: Very fast, no GPU needed, deterministic
    Cons: No context awareness, prone to false positives on ambiguous terms
    """

    def __init__(self, entity_collection: EntityCollection, cache: EmbeddingCache):
        super().__init__(entity_collection, cache)
        self._build_lookup_index()

    def _build_lookup_index(self):
        """Pre-build FlashText processor for fast entity extraction"""
        from flashtext import KeywordProcessor

        # Stopwords - common English words that are also gene symbols
        GENE_STOPWORDS = {
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
            "HR",
            "ER",
            "CI",
            "SD",
            "SE",
            "OR",
            "VS",  # Add common biomedical abbreviations
        }

        # Use case-insensitive processor for diseases/drugs
        self.keyword_processor = KeywordProcessor(case_sensitive=False)

        # Use case-sensitive processor for genes (genes are UPPERCASE in papers)
        self.gene_processor = KeywordProcessor(case_sensitive=True)

        for entity_type, collection in [
            ("disease", self.entities.diseases),
            ("gene", self.entities.genes),
            ("drug", self.entities.drugs),
            ("protein", self.entities.proteins),
        ]:
            for entity in collection.values():
                # We use a composite key of "id|type" as the clean name
                clean_name = f"{entity.entity_id}|{entity_type}"

                if entity_type == "gene":
                    pass  # The flash text processor is not used for genes
                else:
                    # Diseases/drugs: case-insensitive, standard filtering
                    self.keyword_processor.add_keyword(entity.name, clean_name)
                    for variant in entity.synonyms + entity.abbreviations:
                        if len(variant) > 2:
                            self.keyword_processor.add_keyword(variant, clean_name)

    def extract_entities(self, text: str, chunk_id: str) -> List[ExtractedEntity]:
        """Extract biomedical entities from text using FlashText.

        Performs entity recognition by matching text against known entity names,
        synonyms, and abbreviations using the Aho-Corasick algorithm.
        Uses case-sensitive matching for genes and case-insensitive for diseases/drugs.
        """
        extracted = []

        # Extract diseases and drugs (case-insensitive)
        keywords_found = self.keyword_processor.extract_keywords(text, span_info=True)
        for clean_name, start, end in keywords_found:
            entity_id, entity_type = clean_name.split("|")
            extracted.append(
                ExtractedEntity(
                    mention_text=text[start:end],
                    canonical_id=entity_id,
                    entity_type=entity_type,
                    start_char=start,
                    end_char=end,
                    chunk_id=chunk_id,
                    confidence=1.0,
                    extraction_method="flashtext",
                )
            )

        # Extract genes (case-sensitive)
        gene_keywords = self.gene_processor.extract_keywords(text, span_info=True)
        for clean_name, start, end in gene_keywords:
            entity_id, entity_type = clean_name.split("|")
            extracted.append(
                ExtractedEntity(
                    mention_text=text[start:end],
                    canonical_id=entity_id,
                    entity_type=entity_type,
                    start_char=start,
                    end_char=end,
                    chunk_id=chunk_id,
                    confidence=1.0,
                    extraction_method="flashtext_case_sensitive",
                )
            )

        return extracted


class BioBERTExtractor(BaseEntityExtractor):
    """Context-aware entity extraction using BioBERT.

    BioBERT is BERT pre-trained on biomedical literature, enabling contextual NER.

    Pros: Context-aware, handles ambiguous terms, state-of-art accuracy
    Cons: Slower (requires model inference), needs GPU for speed, larger memory footprint
    """

    def __init__(self, entity_collection: EntityCollection, cache: EmbeddingCache):
        super().__init__(entity_collection, cache)
        self._load_biobert()
        self._build_entity_index()

    def _load_biobert(self):
        """Load pre-trained BioBERT model"""
        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification
            import torch
        except ImportError:
            raise ImportError(
                "Install transformers and torch: pip install transformers torch"
            )

        # BioBERT fine-tuned on BC5CDR (diseases and chemicals/drugs)
        model_name = "dmis-lab/biobert-base-cased-v1.2"

        logger.info(f"Loading BioBERT model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        # BioBERT BC5CDR label mapping
        # 0: O (outside), 1: B-Chemical, 2: I-Chemical, 3: B-Disease, 4: I-Disease
        self.label_map = {
            1: "drug",  # B-Chemical
            2: "drug",  # I-Chemical
            3: "disease",  # B-Disease
            4: "disease",  # I-Disease
        }

    def _build_entity_index(self):
        """Build index for canonical entity linking"""
        self.entity_index = {}  # lowercase text -> (entity_id, entity_type)

        for entity_type, collection in [
            ("disease", self.entities.diseases),
            ("gene", self.entities.genes),
            ("drug", self.entities.drugs),
        ]:
            for entity in collection.values():
                # Index by lowercase name
                key = entity.name.lower()
                self.entity_index[key] = (entity.entity_id, entity_type)

                # Index synonyms
                for synonym in entity.synonyms:
                    key = synonym.lower()
                    self.entity_index[key] = (entity.entity_id, entity_type)

    def extract_entities(self, text: str, chunk_id: str) -> List[ExtractedEntity]:
        """Extract entities using BioBERT context-aware NER.

        BioBERT predicts entity spans, we then link them to canonical IDs.
        """
        import torch

        extracted = []

        # Truncate very long texts to avoid memory issues
        if len(text) > 2000:
            logger.warning(
                f"Text chunk too long ({len(text)} chars), truncating to 2000"
            )
            text = text[:2000]

        # Tokenize
        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
                return_offsets_mapping=True,
            )
        except Exception as e:
            logger.error(f"Tokenization error: {e}")
            return extracted

        # Get offset mapping to reconstruct original text spans
        offset_mapping = inputs.pop("offset_mapping")[0]
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Predict
        try:
            with torch.no_grad():
                outputs = self.model(**inputs)
            predictions = torch.argmax(outputs.logits, dim=2)[0]
        except Exception as e:
            logger.error(f"Model inference error: {e}")
            return extracted

        # Extract entity spans
        input_ids = inputs["input_ids"][0]
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids)

        current_entity = None
        current_start = None

        for token_idx, (token, pred_label) in enumerate(zip(tokens, predictions)):
            label = int(pred_label.item())

            # Get character span from offset mapping
            start_char, end_char = offset_mapping[token_idx]

            if label == 0:  # O (outside)
                if current_entity:
                    # Save the entity
                    entity_text = text[current_start:end_char]
                    extracted.append(
                        self._link_entity(
                            entity_text,
                            current_entity["type"],
                            current_start,
                            end_char,
                            chunk_id,
                        )
                    )
                    current_entity = None

            elif label in self.label_map:
                entity_type = self.label_map[label]

                # Start new entity on B- tags
                if label % 2 == 1:  # B- tags (odd numbers)
                    if current_entity:
                        entity_text = text[current_start:start_char]
                        extracted.append(
                            self._link_entity(
                                entity_text,
                                current_entity["type"],
                                current_start,
                                start_char,
                                chunk_id,
                            )
                        )
                    current_entity = {"type": entity_type}
                    current_start = start_char

                # Continue I- tag if same type
                elif current_entity and current_entity["type"] == entity_type:
                    pass  # Continue current entity
                else:
                    # Type mismatch, start new
                    if current_entity:
                        entity_text = text[current_start:start_char]
                        extracted.append(
                            self._link_entity(
                                entity_text,
                                current_entity["type"],
                                current_start,
                                start_char,
                                chunk_id,
                            )
                        )
                    current_entity = {"type": entity_type}
                    current_start = start_char

        # Save final entity
        if current_entity:
            entity_text = text[current_start : len(text)]
            extracted.append(
                self._link_entity(
                    entity_text,
                    current_entity["type"],
                    current_start,
                    len(text),
                    chunk_id,
                )
            )

        return [e for e in extracted if e is not None]  # Filter out None results

    def _link_entity(
        self,
        mention_text: str,
        entity_type: str,
        start_char: int,
        end_char: int,
        chunk_id: str,
    ) -> Optional[ExtractedEntity]:
        """Link extracted mention to canonical entity ID"""
        mention_lower = mention_text.lower().strip()

        # Try exact match first
        if mention_lower in self.entity_index:
            entity_id, canonical_type = self.entity_index[mention_lower]
            return ExtractedEntity(
                mention_text=mention_text,
                canonical_id=entity_id,
                entity_type=canonical_type,
                start_char=start_char,
                end_char=end_char,
                chunk_id=chunk_id,
                confidence=0.95,
                extraction_method="biobert",
            )

        # TODO: Add fuzzy matching for partial matches
        # For now, skip unmatched entities
        return None


class HybridExtractor(BaseEntityExtractor):
    """Hybrid approach: BioBERT for genes, FlashText for diseases/drugs.

    Best of both worlds:
    - BioBERT for gene NER (context-aware, understands "HR" as hazard ratio not gene symbol)
    - FlashText for diseases/drugs (fast, already working well and reliable)
    """

    def __init__(self, entity_collection: EntityCollection, cache: EmbeddingCache):
        super().__init__(entity_collection, cache)

        logger.info(
            "Initializing hybrid extractor (BioBERT for genes + FlashText for diseases/drugs)"
        )

        # Always initialize FlashText for diseases/drugs
        self.flashtext = FlashTextExtractor(entity_collection, cache)

        # Try to initialize BioBERT for genes, fallback to FlashText if it fails
        self.use_biobert = False
        try:
            self.biobert = BioBERTExtractor(entity_collection, cache)
            self.use_biobert = True
            logger.info("BioBERT loaded successfully for gene extraction")
        except Exception as e:
            logger.warning(
                f"BioBERT initialization failed: {e}, will use FlashText for genes as fallback"
            )

    def extract_entities(self, text: str, chunk_id: str) -> List[ExtractedEntity]:
        """Extract entities using hybrid approach.

        Strategy:
        1. Use FlashText for diseases and drugs (fast, reliable)
        2. Use BioBERT for genes (context-aware, avoids false positives)
        3. If BioBERT unavailable, fall back to FlashText for genes
        """
        extracted = []

        # Step 1: Extract diseases and drugs using FlashText
        flashtext_results = self.flashtext.extract_entities(text, chunk_id)
        disease_drug_results = [
            e for e in flashtext_results if e.entity_type in ("disease", "drug")
        ]
        extracted.extend(disease_drug_results)

        # Step 2: Extract genes using BioBERT (context-aware)
        if self.use_biobert:
            try:
                biobert_results = self.biobert.extract_entities(text, chunk_id)
                gene_results = [e for e in biobert_results if e.entity_type == "gene"]
                extracted.extend(gene_results)
            except Exception as e:
                logger.warning(
                    f"BioBERT gene extraction failed: {e}, falling back to FlashText"
                )
                gene_results = [e for e in flashtext_results if e.entity_type == "gene"]
                extracted.extend(gene_results)
        else:
            # BioBERT not available, use FlashText for genes
            gene_results = [e for e in flashtext_results if e.entity_type == "gene"]
            extracted.extend(gene_results)

        return extracted


class RelationshipExtractor:
    """Extracts relationships between biomedical entities from text."""

    def extract_relationships(
        self, entities: List[ExtractedEntity], text: str, chunk_id: str
    ) -> List[Relationship]:
        """Extract relationships between entities based on co-occurrence in sentences."""
        import re

        relationships = []

        # Split into sentences
        sentences = re.split(r"[.!?]+", text)

        current_pos = 0
        for sent in sentences:
            if not sent.strip():
                continue

            try:
                sent_start = text.index(sent, current_pos)
            except ValueError:
                continue

            sent_end = sent_start + len(sent)
            current_pos = sent_end

            # Find entities in this sentence
            sent_entities = [
                e for e in entities if sent_start <= e.start_char < sent_end
            ]

            # Create co-occurrence relationships
            for i, e1 in enumerate(sent_entities):
                for e2 in sent_entities[i + 1 :]:
                    # Only create meaningful relationships
                    if (
                        (e1.entity_type == "drug" and e2.entity_type == "disease")
                        or (e1.entity_type == "disease" and e2.entity_type == "drug")
                        or (e1.entity_type == "gene" and e2.entity_type == "disease")
                        or (e1.entity_type == "disease" and e2.entity_type == "gene")
                    ):
                        relationships.append(
                            Relationship(
                                subject_id=e1.canonical_id,
                                predicate="ASSOCIATED_WITH",
                                object_id=e2.canonical_id,
                                evidence_text=sent.strip(),
                                chunk_id=chunk_id,
                                confidence=0.5,
                                extraction_method="cooccurrence",
                            )
                        )

        return relationships


def aggregate_entity_mentions(entities: List[ExtractedEntity]) -> List[EntityMention]:
    """Aggregate extracted entities into entity mentions."""
    from collections import defaultdict

    entity_groups = defaultdict(
        lambda: {"mentions": [], "chunk_ids": set(), "count": 0}
    )

    for entity in entities:
        key = (entity.canonical_id, entity.entity_type)
        entity_groups[key]["mentions"].append(entity.mention_text)
        entity_groups[key]["chunk_ids"].add(entity.chunk_id)
        entity_groups[key]["count"] += 1

    result = []
    for (entity_id, entity_type), data in entity_groups.items():
        result.append(
            EntityMention(
                entity_id=entity_id,
                canonical_name=data["mentions"][0],
                entity_type=entity_type,
                mention_count=data["count"],
                mentions=list(set(data["mentions"])),
                chunk_ids=list(data["chunk_ids"]),
            )
        )

    return result
