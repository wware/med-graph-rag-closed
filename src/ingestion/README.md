# Ingestion Pipeline

This directory contains the core logic for processing medical papers, generating embeddings, and indexing them into the knowledge graph.

## Work flow

At a high level

1. Preliminary entity collection
   - Data should be pristine at this point
   - See the `regen-jsonl.sh` script
2. Parse JATS XML files (standard format for PMC papers)
   - Use the highest quality biomedical model practically available for this
   - First pass: NER (named entity recognition)
     - Identify any novel entities, add to the entity collection
   - Second pass: entity linking, subgraph creation
     - Extract relationships, generate triples/properties
   - Result is a nested JSON object `ParsedPaper`
3. Generate vector embeddings for text chunks, add them to subgraph
4. Store JSON subgraph in another S3 folder

The entity collection contains canonical IDs for entities shared by all subgraphs. These must stay consistent across the entire corpus. These allow different papers to provide different information about the same entities (diseases, drugs, genes, symptoms, treatments, etc).

At query time, it may or may not make sense to join all the subgraphs into a single big graph in some graph database. This might be done on an ephemeral basis or it might be persistent, that will depend on cost, performance, and other considerations. It's unlikely (but not impossible) that queries across multiple papers will be performant working directly from JSON subgraph files.

### Parsing papers

Papers have [a standard structure](https://guides.mclibrary.duke.edu/scientificwriting/sections) telling what sections to include, in what order (abstract, introduction, methods, results, discussion). This structure must be preserved in the JSON subgraph, probably by creating a subgraph per section.

When a researcher wants to confirm a conclusion reached by the system, it must be possible to identify the section, and the paragraph within the section, substantiating or supporting the conclusion. This location info must also be part of the parsed structure.

### NER

Here is some preliminary code for extracting entities from parsed papers. This assumes you've already fetched abstracts as text strings. This an abstract-only example for early development when you want to run experiments quickly. In production entities might be fetched from the entire paper.

```python
from src.schema.entity import Disease, Drug, EntityCollection, Symptom

collection = EntityCollection.load("reference_entities.jsonl")
nlp = spacy.load("en_ner_bc5cdr_md")
nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})
SYMPTOM_TERMS = {"fatigue", "rash", "nausea", "vomiting", "headache", ...}
for i, abstract in enumerate(abstracts, 1):
    doc = nlp(abstract)
    for ent in doc.ents:
        if not ent._.kb_ents:
            continue  # no UMLS link
        umls_id, confidence = ent._.kb_ents[0]
        if ent.label_ == "DISEASE":
            entity_text_lower = ent.text.lower()
            existing = collection.get_by_umls(umls_id)
            if any(symptom in entity_text_lower for symptom in SYMPTOM_TERMS):
                if existing:
                    if ent.text not in existing.synonyms:
                        existing.synonyms.append(ent.text)
                else:
                    symptom = Symptom(
                        entity_id=umls_id,
                        name=ent.text,
                        synonyms=[ent.text],
                        source="extracted"
                    )
                    collection.symptoms[symptom.entity_id] = symptom
            elif existing:
                if ent.text not in existing.synonyms:
                    existing.synonyms.append(ent.text)
            else:
                disease = Disease(
                    entity_id=umls_id,
                    name=ent.text,  # Use mention as name for now
                    synonyms=[ent.text],
                    umls_id=umls_id,
                    source="extracted"
                )
                collection.add_disease(disease)
        elif ent.label_ == "CHEMICAL":
            disease_match = collection.get_by_umls(umls_id)
            if disease_match:
                if ent.text not in disease_match.synonyms:
                    disease_match.synonyms.append(ent.text)
                continue
            existing = collection.get_by_id(umls_id)
            if existing:
                if ent.text not in existing.synonyms:
                    existing.synonyms.append(ent.text)
            else:
                drug = Drug(
                    entity_id=umls_id,
                    name=ent.text,
                    synonyms=[ent.text],
                    rxnorm_id=umls_id,  # UMLS often includes RxNorm
                    source="extracted"
                )
                collection.add_drug(drug)
```

## Deeper thinking

I will need a couple of folders in s3, first for raw papers in JATS-XML format (possibly other formats later). The second is for JSON objects, one per paper, containing the subgraph for that paper, various metadata, and embeddings for the paper. There is a RDS PostgreSQL database of entities shared by all these JSON objects. Graphs express relationships among entities. See knowledge graph schema. Papers are pulled into the first folder from pubmed or elsewhere by a lambda, and another lambda generates embeddings, does NER, and builds the relationship graph.

Where I say "Lambda", I do not exclude the possibility of using other cloud services if more appropriate, such as EKS or Fargate.

For embedding models, I am thinking **scispaCy** ([1](https://allenai.github.io/scispacy/)) is looking good for NER and entity linking, and possibly **BioLORD-2023** ([2](https://huggingface.co/FremyCompany/BioLORD-2023)) for embeddings. Possible alternative to scispaCy would be **AWS Comprehend Medical** ([1](https://docs.aws.amazon.com/comprehend-medical/latest/dev/comprehendmedical-welcome.html), [2](https://docs.aws.amazon.com/comprehend-medical/latest/dev/comprehendmedical-howitworks.html), [3](https://docs.aws.amazon.com/comprehend-medical/latest/api/Welcome.html)).

When complete, the system should handle complex multi hop queries across different entity types using a query language of nested JSON expressions via HTTP POST calls. Assume the user is medically sophisticated but not a LLM expert. The query language should be LLM-friendly:

* Declarative and intuitive - reads like the question
* Forgiving - small variations still work
* Self-documenting - field names match natural language
* Compositional - complex queries built from simple patterns

At the present time we are not working on querying, we are working on ingestion. I mention queries only to avoid making early design choices that bite us when it's time to work on querying.

For ambiguous mentions (e.g., "p53" could be gene or protein), the disambiguation strategy is to send an email via AWS SNS to a human and mark the paper as needing later human review. The raw source is retained in S3 and a JSON file is generated containing both possible interpretations. The email should help the human locate both so they can manually edit the JSON file appropriately. As volume increases, batch the ambiguous cases into a weekly digest with a simple web UI for resolution, rather than individual emails. That scales better and helps to see patterns (maybe "p53" is almost always used as a gene symbol in the corpus).

As far as preliminary scale of the project, assume 1K to 10K papers, later handle 100K to 1M papers per month.

Do not generate any code yet, we are still discussing and doing preliminary research.


## Relationship Extraction Options

### 1. Rule-Based (Dependency Parsing)

Use spaCy's dependency parser to find syntactic patterns connecting entities.

**How it works:** Define patterns like "DRUG treats DISEASE" where "treats" is a verb connecting the two entities. You write rules matching dependency tree structures.

**Pros:** Fast, interpretable, no training data needed, deterministic
**Cons:** Brittle to phrasing variations, requires manual rule writing, misses implicit relationships
**Best for:** High-precision extraction of common, well-structured relationships

**Example patterns:**
- "X inhibits Y" → INHIBITS relationship
- "patients treated with X for Y" → TREATS relationship
- "X is associated with increased risk of Y" → INCREASES_RISK relationship

---

### 2. Pre-trained Biomedical RE Models

Models already trained on biomedical relationship datasets.

**Options:**
- **PubMedBERT + RE head** - fine-tuned on datasets like ChemProt, DDI, GAD
- **BioBERT-RE** - specifically for biomedical relation extraction
- **SciREX** - scientific information extraction including relations
- **REBEL** - seq2seq model that extracts triplets directly

**Pros:** Works out of the box, captures learned patterns from large corpora
**Cons:** Limited to relationship types in training data, may not match your schema exactly
**Best for:** Standard relationships (drug-disease, gene-disease, drug-drug interactions)

---

### 3. Fine-tuned Model on Your Schema

Train or fine-tune a model on your specific relationship types.

**How it works:** Annotate a few hundred examples of your target relationships, fine-tune PubMedBERT or similar with a classification head.

- **Pros:** Matches your exact schema, can handle domain-specific relationship types
- **Cons:** Requires labeled training data, ongoing maintenance as schema evolves
- **Best for:** When pre-trained models don't cover your relationship types well

---

### 4. LLM-Based (Claude/GPT-4)

Send text chunks to an LLM with your schema and ask it to extract relationships.

**How it works:** Prompt with entity pairs and surrounding context, ask for structured JSON output with relationship type and confidence.

- **Pros:** Handles complex/implicit relationships, adapts to any schema via prompt, captures nuance, can explain reasoning
- **Cons:** Slower, more expensive, non-deterministic, potential hallucination
- **Best for:** Complex relationships, low-frequency relationship types, high-value papers

Hybrid approach:** Use LLM for difficult cases or to generate training data for a fine-tuned model.

---

### 5. Distant Supervision

Automatically generate training data from existing knowledge bases.

**How it works:** If UMLS says "Olaparib treats Breast Cancer" and a sentence contains both entities, assume that sentence expresses a TREATS relationship. Train a classifier on these automatically-labeled examples.

- **Pros:** No manual annotation, scales to large training sets
- **Cons:** Noisy labels (sentence might not actually express the relationship), requires existing KB
- **Best for:** Bootstrapping when you have good reference KBs but no labeled sentences

---

### 6. OpenIE (Open Information Extraction)

Extract all relationship triplets without predefined schema.

**Tools:** Stanford OpenIE, AllenNLP OpenIE, OPIEC

**How it works:** Extract (subject, predicate, object) triplets from any sentence, then map predicates to your schema.

- **Pros:** Discovers unexpected relationships, no predefined schema needed
- **Cons:** Noisy, requires post-processing to map to your ontology, many irrelevant triplets
- **Best for:** Exploratory analysis, discovering new relationship types

---

### 7. Graph Neural Networks

Use the document structure itself as a graph for relationship prediction.

**How it works:** Build a graph where entities are nodes, use GNN to predict edges based on co-occurrence patterns, sentence structure, and entity embeddings.

- **Pros:** Captures document-level context, can find relationships across sentences
- **Cons:** Complex to implement, requires significant training data
- **Best for:** Document-level relationship extraction, when entities are far apart in text

---

## My Recommendation for Your Project

**Tiered approach:**

| Tier | Method | Use Case |
|------|--------|----------|
| **Tier 1** | Rule-based | High-confidence common patterns (treats, causes, inhibits) |
| **Tier 2** | Pre-trained BioBERT-RE | Standard biomedical relationships not caught by rules |
| **Tier 3** | Claude API | Ambiguous cases, complex multi-hop relationships, validation |

This gives you speed and cost efficiency for the bulk of extractions while preserving quality for difficult cases. The rule-based tier also gives you interpretable provenance for your `evidence_text` field.

You could also use Claude in a bootstrapping phase - extract relationships from a few hundred papers with Claude, review the output, then use that as training data for a fine-tuned model that handles the bulk processing more cheaply.


## Biomedical NER and Embedding Model Alternatives

<details>
<summary>Research</summary>

````plaintext
Web Search: biomedical NER models 2024 PubMedBERT BioBERT comparison
````

> **BioBERT vs. PubMedBERT. Model Comparison | by Eleventh Hour Enthusiast | Medium** [medium.com](https://medium.com/@EleventhHourEnthusiast/model-comparison-biobert-vs-pubmedbert-8c2d78178d10)
>
> **BioBERT: a pre-trained biomedical language representation model for biomedical text mining - PMC** [nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7703786/)
>
> **A comparative study of pre-trained language models for named entity recognition in clinical trial eligibility criteria from multiple corpora | BMC Medical Informatics and Decision Making | Full Text** [biomedcentral.com](https://bmcmedinformdecismak.biomedcentral.com/articles/10.1186/s12911-022-01967-7)
>
> **GitHub - dmis-lab/biobert: Bioinformatics'2020: BioBERT: a pre-trained biomedical language representation model for biomedical text mining** [github.com](https://github.com/dmis-lab/biobert)
>
> **Do LLMs Surpass Encoders for Biomedical NER?** [arxiv.org](https://arxiv.org/html/2504.00664v1)
>
> **A comparative study of pre-trained language models for named entity recognition in clinical trial eligibility criteria from multiple corpora - PubMed** [nih.gov](https://pubmed.ncbi.nlm.nih.gov/36068551/)
>
> **How Do Your Biomedical Named Entity Recognition Models Generalize to Novel Entities? - PMC** [nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC9014470/)
>
> **GitHub - naver/biobert-pretrained: BioBERT: a pre-trained biomedical language representation model for biomedical text mining** [github.com](https://github.com/naver/biobert-pretrained)
>
> **How Do Your Biomedical Named Entity Recognition ...** [arxiv.org](https://arxiv.org/pdf/2101.00160)
>
> **From Zero to Hero: Harnessing Transformers for Biomedical Named Entity Recognition in Zero- and Few-shot Contexts** [arxiv.org](https://arxiv.org/html/2305.04928v5)
>
````plaintext
Web Search: scispacy biomedical NER entity linking UMLS
````

> **GitHub - allenai/scispacy: A full spaCy pipeline and models for scientific/biomedical documents.** [github.com](https://github.com/allenai/scispacy)
>
> **scispacy | SpaCy models for biomedical text processing** [github.io](https://allenai.github.io/scispacy/)
>
> **Improving broad-coverage medical entity linking with semantic type prediction and large-scale datasets - PMC** [nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC8952339/)
>
> **MedLinker: Medical Entity Linking with Neural Representations and Dictionary Matching - PMC** [nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7148021/)
>
> **Biomedical Nested NER with Large Language Model and UMLS Heuristics** [arxiv.org](https://arxiv.org/html/2407.05480v1)
>
> **(PDF) scispaCy for Bio-medical Named Entity Recognition(NER)** [researchgate.net](https://www.researchgate.net/publication/335543849_scispaCy_for_Bio-medical_Named_Entity_RecognitionNER)
>
> **ScispaCy: Fast and Robust Models for Biomedical Natural ...** [aclanthology.org](https://aclanthology.org/W19-5034.pdf)
>
> **How to use scispaCy for Biomedical Named Entity Recognition, Abbreviation Resolution and link UMLS | by Wuraola Oyewusi | Medium** [medium.com](https://medium.com/@oyewusiwuraola/how-to-use-scispacy-for-biomedical-named-entity-recognition-abbreviation-resolution-and-link-umls-87d3f7c08db2)
>
> **Building a Biomedical Entity Linker with LLMs | Towards Data Science** [towardsdatascience.com](https://towardsdatascience.com/building-a-biomedical-entity-linker-with-llms-d385cb85c15a/)
>
> **CORD-19 SciSpaCy Entity Dataset - Elsevier BV** [digitalcommonsdata.com](https://elsevier.digitalcommonsdata.com/datasets/gk9njn3pth/1)
>
````plaintext
Web Search: biomedical sentence embeddings 2024 SapBERT BioLinkBERT comparison
````

> **kamalkraj/BioSimCSE-BioLinkBERT-BASE · Hugging Face** [huggingface.co](https://huggingface.co/kamalkraj/BioSimCSE-BioLinkBERT-BASE)
>
> **BioSimCSE: BioMedical Sentence Embeddings using Contrastive learning - ACL Anthology** [aclanthology.org](https://aclanthology.org/2022.louhi-1.10/)
>
> **The t-SNE of sentence representation of BioLinkBERT before training... | Download Scientific Diagram** [researchgate.net](https://www.researchgate.net/figure/The-t-SNE-of-sentence-representation-of-BioLinkBERT-before-training-with-SimCSE_fig1_372921673)
>
> **BALI: Enhancing Biomedical Language Representations through Knowledge Graph and Language Model Alignment** [arxiv.org](https://arxiv.org/html/2509.07588)
>
> **(PDF) BioSimCSE: BioMedical Sentence Embeddings using Contrastive learning** [researchgate.net](https://www.researchgate.net/publication/372921673_BioSimCSE_BioMedical_Sentence_Embeddings_using_Contrastive_learning)
>
> **Unsupervised SapBERT-based bi-encoders for medical concept annotation of clinical narratives with SNOMED CT - PMC** [nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11531008/)
>
> **Puer at SemEval-2024 Task 2: A BioLinkBERT Approach to Biomedical Natural Language Inference - ACL Anthology** [aclanthology.org](https://aclanthology.org/2024.semeval-1.12/)
>
> **Evaluating sentence representations for biomedical text: Methods and experimental results - PubMed** [nih.gov](https://pubmed.ncbi.nlm.nih.gov/32147441/)
>
> **GitHub - cambridgeltl/sapbert: [NAACL'21 & ACL'21] SapBERT: Self-alignment pretraining for BERT & XL-BEL: Cross-Lingual Biomedical Entity Linking.** [github.com](https://github.com/cambridgeltl/sapbert)
>
> **cambridgeltl/SapBERT-from-PubMedBERT-fulltext · Hugging Face** [huggingface.co](https://huggingface.co/cambridgeltl/SapBERT-from-PubMedBERT-fulltext)
>
````plaintext
Web Search: GLINER biomedical NER zero-shot 2024
````

> **GLiNER-biomed: A Suite of Efficient Models for Open Biomedical Named Entity Recognition** [arxiv.org](https://arxiv.org/html/2504.00676v1)
>
> **GitHub - urchade/GLiNER: Generalist and Lightweight Model for Named Entity Recognition (Extract any entity types from texts) @ NAACL 2024** [github.com](https://github.com/urchade/GLiNER)
>
> **GLiNER: Generalist Model for Named Entity Recognition using Bidirectional Transformer | Request PDF** [researchgate.net](https://www.researchgate.net/publication/382634629_GLiNER_Generalist_Model_for_Named_Entity_Recognition_using_Bidirectional_Transformer)
>
> **(PDF) GLiNER-biomed: A Suite of Efficient Models for Open Biomedical Named Entity Recognition** [researchgate.net](https://www.researchgate.net/publication/390404555_GLiNER-biomed_A_Suite_of_Efficient_Models_for_Open_Biomedical_Named_Entity_Recognition)
>
> **GLiNER: Generalist Model for Named Entity Recognition ...** [aclanthology.org](https://aclanthology.org/2024.naacl-long.300.pdf)
>
> **GLiNER: Generalist Model for Named Entity Recognition Using Bidirectional Transformer | by Zilliz | Medium** [medium.com](https://medium.com/@zilliz_learn/gliner-generalist-model-for-named-entity-recognition-using-bidirectional-transformer-ed65165a4877)
>
> **Benchmarking zero-shot biomedical relation triplet ...** [aclanthology.org](https://aclanthology.org/2025.bionlp-1.9.pdf)
>
> **GLiNER: A Zero-Shot NER that outperforms ChatGPT and traditional NER models | by Netra Prasad Neupane | Medium** [medium.com](https://netraneupane.medium.com/gliner-zero-shot-ner-outperforming-chatgpt-and-traditional-ner-models-1f4aae0f9eef)
>
> **KoGNER: A Novel Framework for Knowledge Graph Distillation on Biomedical Named Entity Recognition** [arxiv.org](https://arxiv.org/html/2503.15737)
>
> **OPENBIONER: Lightweight Open-Domain Biomedical ...** [aclanthology.org](https://aclanthology.org/2025.findings-naacl.47.pdf)
>
````plaintext
Web Search: HunFlair2 memory requirements model size GPU
````

> **How to quickly determine memory requirements for model - Beginners - Hugging Face Forums** [huggingface.co](https://discuss.huggingface.co/t/how-to-quickly-determine-memory-requirements-for-model/43426)
>
> **Model memory estimator** [huggingface.co](https://huggingface.co/docs/accelerate/main/en/usage_guides/model_size_estimator)
>
> **GPU** [huggingface.co](https://huggingface.co/docs/transformers/perf_train_gpu_one)
>
> **nlp - What size language model can you train on a GPU with x GB of memory? - Data Science Stack Exchange** [stackexchange.com](https://datascience.stackexchange.com/questions/117444/what-size-language-model-can-you-train-on-a-gpu-with-x-gb-of-memory)
>
> **microsoft/phi-2 · [AUTOMATED] Model Memory Requirements** [huggingface.co](https://huggingface.co/microsoft/phi-2/discussions/42)
>
> **LLaMA 7B GPU Memory Requirement - 🤗Transformers - Hugging Face Forums** [huggingface.co](https://discuss.huggingface.co/t/llama-7b-gpu-memory-requirement/34323)
>
> **Unbelievable! Run 70B LLM Inference on a Single 4GB GPU with This NEW Technique** [huggingface.co](https://huggingface.co/blog/lyogavin/airllm)
>
> **AI Model Size Calculator - Estimate GPU Memory Requirements 2025** [gpuvec.com](https://gpuvec.com/tools/model-size-calculator)
>
> **Efficient Training on a Single GPU** [huggingface.co](https://huggingface.co/docs/transformers/v4.20.1/en/perf_train_gpu_one)
>
> **Model Memory Utility - a Hugging Face Space by hf-accelerate** [huggingface.co](https://huggingface.co/spaces/hf-accelerate/model-memory-usage)
>
````plaintext
Web Search: "HunFlair2" flair NER model size parameters
````

> **HunFlair2 Tutorial 3: Training NER models — Flair Documentation** [github.io](https://flairnlp.github.io/flair/master/tutorial/tutorial-hunflair2/training-ner-models.html)
>
> **README.md · hunflair/hunflair2-ner at main** [huggingface.co](https://huggingface.co/hunflair/hunflair2-ner/blob/main/README.md)
>
> **hunflair/hunflair2-ner · Hugging Face** [huggingface.co](https://huggingface.co/hunflair/hunflair2-ner)
>
> **Releases · flairNLP/flair** [github.com](https://github.com/flairNLP/flair/releases)
>
> **flair/resources/docs/HUNFLAIR.md at master · flairNLP/flair** [github.com](https://github.com/flairNLP/flair/blob/master/resources/docs/HUNFLAIR.md)
>
> **flair/resources/docs/HUNFLAIR2.md at master · flairNLP/flair** [github.com](https://github.com/flairNLP/flair/blob/master/resources/docs/HUNFLAIR2.md)
>
> **flair/flair/models/sequence_tagger_model.py at master · flairNLP/flair** [github.com](https://github.com/flairNLP/flair/blob/master/flair/models/sequence_tagger_model.py)
>
> **HunFlair2 - Overview — Flair Documentation** [github.io](https://flairnlp.github.io/flair/master/tutorial/tutorial-hunflair2/overview.html)
>
> **regel-corpus/hunflair2-regel-enhancer · Hugging Face** [huggingface.co](https://huggingface.co/regel-corpus/hunflair2-regel-enhancer)
>
> **flair/resources/docs/HUNFLAIR2_TUTORIAL_2_LINKING.md at master · flairNLP/flair** [github.com](https://github.com/flairNLP/flair/blob/master/resources/docs/HUNFLAIR2_TUTORIAL_2_LINKING.md)
>
````plaintext
Web Search: BioLORD embedding model size memory comparison PubMedBERT
````

> **[2210.11892] BioLORD: Learning Ontological Representations from Definitions for Biomedical Concepts and their Textual Descriptions** [arxiv.org](https://ar5iv.labs.arxiv.org/html/2210.11892)
>
> **Lessons Learned on Information Retrieval in Electronic Health Records: A Comparison of Embedding Models and Pooling Strategies** [arxiv.org](https://arxiv.org/html/2409.15163v1)
>
> **GitHub - ncbi-nlp/BioSentVec: BioWordVec & BioSentVec: pre-trained embeddings for biomedical words and sentences** [github.com](https://github.com/ncbi-nlp/BioSentVec)
>
> **Top embedding models on the MTEB leaderboard | Modal Blog** [modal.com](https://modal.com/blog/mteb-leaderboard-article)
>
> **Bioformer: an efficient transformer language model for biomedical text mining - PMC** [nih.gov](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10029052/)
>
> **Bioformer: an efficient transformer language model for biomedical text mining** [arxiv.org](https://arxiv.org/pdf/2302.01588)
>
> **BioBERT vs. PubMedBERT. Model Comparison | by Eleventh Hour Enthusiast | Medium** [medium.com](https://medium.com/@EleventhHourEnthusiast/model-comparison-biobert-vs-pubmedbert-8c2d78178d10)
>
> **BioLORD: Contrastive learning for biomedical concepts | by Heloisa Oss Boll | Medium** [medium.com](https://hossboll.medium.com/biolord-contrastive-learning-for-biomedical-concepts-32c453f7a830)
>
> **NeuML/pubmedbert-base-embeddings · Hugging Face** [huggingface.co](https://huggingface.co/NeuML/pubmedbert-base-embeddings)
>
> **Generalist embedding models are better at short-context clinical semantic search than specialized embedding models** [arxiv.org](https://arxiv.org/html/2401.01943v2)
>
Let me get a bit more information on model sizes and Lambda compatibility:

````plaintext
Web Search: AWS Lambda container image ML model inference size limits 10GB
````

> **amazon web services - How to increase the maximum size of the AWS lambda deployment package (RequestEntityTooLargeException)? - Stack Overflow** [stackoverflow.com](https://stackoverflow.com/questions/54632009/how-to-increase-the-maximum-size-of-the-aws-lambda-deployment-package-requesten)
>
> **SageMaker Inference Recommender: Image size is greater than supported size 10GB | AWS re:Post** [repost.aws](https://repost.aws/questions/QULY7aP9zDSV6AkjehrFPjeQ/sagemaker-inference-recommender-image-size-is-greater-than-supported-size-10gb)
>
> **ML Inference using Lambda's 10 GB Ephemeral Storage** [bitesizedserverless.com](https://bitesizedserverless.com/bite/ml-inference-in-lambda/)
>
> **AWS Lambda Now Supports Up to 10 GB Ephemeral Storage | Amazon Web Services** [amazon.com](https://aws.amazon.com/blogs/aws/aws-lambda-now-supports-up-to-10-gb-ephemeral-storage/)
>
> **Deploy multiple machine learning models for inference on AWS Lambda and Amazon EFS | Artificial Intelligence** [amazon.com](https://aws.amazon.com/blogs/machine-learning/deploy-multiple-machine-learning-models-for-inference-on-aws-lambda-and-amazon-efs/)
>
> **Using container images to run TensorFlow models in AWS Lambda | Artificial Intelligence** [amazon.com](https://aws.amazon.com/blogs/machine-learning/using-container-images-to-run-tensorflow-models-in-aws-lambda/)
>
> **Using container images to run PyTorch models in AWS Lambda | Artificial Intelligence** [amazon.com](https://aws.amazon.com/blogs/machine-learning/using-container-images-to-run-pytorch-models-in-aws-lambda/)
>
> **Troubleshoot issues with SageMaker Serverless Inference endpoints | AWS re:Post** [repost.aws](https://repost.aws/knowledge-center/sagemaker-serverless-inference-errors)
>
> **Lambda Package Exceeds 60MB: Solutions for Large Dependencies? | AWS re:Post** [repost.aws](https://repost.aws/questions/QUoXSNWrkdSf61jVqG7IwBxg/lambda-package-exceeds-60mb-solutions-for-large-dependencies)
>
> **Deploy a machine learning inference data capture solution on AWS Lambda | Artificial Intelligence** [amazon.com](https://aws.amazon.com/blogs/machine-learning/deploy-a-machine-learning-inference-data-capture-solution-on-aws-lambda/)
>
I now have enough information to provide a comprehensive comparison. Let me synthesize this into a clear alternatives proposal.

</details>
<br/>

| Model | Type | Size (approx) | Lambda-Friendly? | Entity Linking | Notes |
|-------|------|---------------|------------------|----------------|-------|
| **HunFlair2** | Flair + BioLinkBERT | ~500MB-1GB | ⚠️ Tight fit | ✅ Built-in | Best biomedical NER accuracy, includes entity normalization |
| **scispaCy** | spaCy pipeline | ~100-400MB | ✅ Yes | ✅ UMLS/MeSH/RxNorm | Mature, well-documented, fast, includes abbreviation detection |
| **GLiNER-biomed** | Transformer encoder | ~500MB-1.3GB | ⚠️ Marginal | ❌ Needs separate | Zero-shot, flexible entity types, very new (April 2025) |
| **PubMedBERT + fine-tuning** | BERT-base | ~440MB | ✅ Yes | ❌ Needs separate | Requires training on NER datasets |
| **BioBERT** | BERT-base | ~440MB | ✅ Yes | ❌ Needs separate | Older but well-tested |
| **Bioformer16L** | Compact BERT | ~170MB | ✅ Yes | ❌ Needs separate | 60% smaller than PubMedBERT, 2-3x faster, deployed at PubTator |

### My Analysis

**For Lambda deployment (10GB container limit, 10GB memory max):**

1. **scispaCy** is the pragmatic choice for your use case:
   - Small footprint (~100-400MB depending on model variant)
   - Built-in entity linking to UMLS (~3M concepts), MeSH (~30k entities), and RxNorm (~100k concepts)
   - Abbreviation detection and resolution built-in
   - Mature library with good documentation
   - Scispacy remains a robust tool for biomedical entity extraction and linking, outperforming LLM-based methods in experiments. It also requires less computational power, running on CPU without needing a GPU.

2. **GLiNER-biomed** is interesting for future consideration:
   - Uses natural language descriptions to infer arbitrary entity types, enabling zero-shot recognition
   - Achieves 5.96% improvement in F1-score over the strongest baseline on biomedical NER benchmarks
   - But it's very new (April 2025) and lacks built-in entity linking

3. **HunFlair2** if you need maximum accuracy:
   - Outperforms other biomedical entity extraction tools on corpora not used for training
   - Includes entity normalization to standard ontologies
   - But heavier weight and requires Flair framework

---

## Embedding Model Alternatives

| Model | Base | Dim | Size | Use Case |
|-------|------|-----|------|----------|
| **BioLORD-2023** | STAMB2 | 768 | ~440MB | Concept similarity, entity linking, sentence similarity |
| **SapBERT** | PubMedBERT | 768 | ~440MB | Entity linking (SOTA on medical entity linking) |
| **BioSimCSE-BioLinkBERT** | BioLinkBERT | 768 | ~440MB | Sentence similarity (biomedical STS SOTA) |
| **PubMedBERT-base-embeddings** | PubMedBERT | 768 | ~440MB | General biomedical sentence embeddings |
| **Bioformer8L/16L** | Custom | 512/384 | ~170MB | Compact, fast, production-ready |

### My Analysis

**For your use case (abstract embeddings + entity embeddings):**

1. **SapBERT** for entity linking/disambiguation:
   - SapBERT offers an elegant one-model-for-all solution to the problem of medical entity linking, achieving a new state-of-the-art (SOTA) on six MEL benchmarking datasets
   - Trained with UMLS 2020AA, using PubMedBERT as the base model
   - Excellent for matching extracted mentions to your RDS entity database

2. **BioLORD-2023** for sentence/abstract similarity:
   - State-of-the-art performance for both biomedical concept similarity and clinical sentence similarity, using one set of weights
   - Able to embed both clinical sentences and biomedical concepts in the same latent space
   - Good choice for abstract-level embeddings

3. **PubMedBERT-base-embeddings** as a simpler alternative:
   - A PubMedBERT-base model fine-tuned using sentence-transformers that maps sentences & paragraphs to a 768 dimensional dense vector space
   - Lighter integration, works directly with sentence-transformers

---

## Practical Recommendation for Your Architecture

Given Lambda constraints (10GB container, 10GB memory, 15min timeout) and your goals:

### Option A: scispaCy + SapBERT (Conservative)
```
NER + Entity Linking: scispaCy (en_core_sci_lg or en_ner_bc5cdr_md)
                      + UmlsEntityLinker
Entity Embeddings:    SapBERT for matching to RDS
Abstract Embeddings:  PubMedBERT-base-embeddings or BioLORD-2023
```
- Total model size: ~1-1.5GB
- Fits comfortably in Lambda
- Mature, well-documented

### Option B: GLiNER-biomed + SapBERT (Flexible, newer)
```
NER:                  GLiNER-biomed (zero-shot, flexible entity types)
Entity Linking:       SapBERT + your RDS synonyms table
Abstract Embeddings:  BioLORD-2023
```
- Total model size: ~1.5-2GB
- More flexibility for entity types
- Less mature entity linking pipeline

### Option C: HunFlair2 (Maximum accuracy, tighter fit)
```
NER + Entity Linking: HunFlair2 (includes disease/gene/chemical/species linkers)
Abstract Embeddings:  BioLinkBERT or BioLORD-2023
```
- Total model size: ~1.5-2GB
- Best accuracy
- Heavier cold starts

---

## Key Questions for Your Decision

1. **Cold start tolerance** - How often will this Lambda be invoked? If infrequent, larger models = longer cold starts (20-40 seconds for HunFlair2)

2. **Entity type flexibility** - Do you need to add new entity types later without retraining? If yes, GLiNER-biomed is attractive

3. **Entity linking strategy** - scispaCy's char-3gram linker is fast but coarse; SapBERT embedding similarity is more accurate but requires vector search infrastructure

4. **GPU availability** - All these run on CPU, but if you later move to ECS/Fargate with GPU, options expand


## Take a look at BlueBERT

[BlueBERT](https://github.com/ncbi-nlp/bluebert) is from NCBI (National Center for Biotechnology Information) - the same people who run PubMed, so they know the domain well.

Potential limitations: BlueBERT's ChemProt training involves the relationship types in ChemProt (inhibitor, substrate, agonist, antagonist, activator) which map well to the schema, but they're chemical-protein specific. The schema has broader relationship types like TREATS, INCREASES_RISK, ASSOCIATED_WITH, not covered by ChemProt. Hopefully the MIMIC training data will help with this, and there is mention of other training data sources (ShARe/CLEFE, DDI, i2b2 2010).

### What It Is

BlueBERT is pre-trained on:

- **PubMed abstracts** (~4 billion words)
- **MIMIC-III clinical notes** (optional variant) - real clinical records from Beth Israel Deaconess

Available in four variants:

| Model | Size | Training Data |
|-------|------|---------------|
| BlueBERT-Base-PubMed | 768-dim, 12 layers | PubMed only |
| BlueBERT-Base-PubMed+MIMIC | 768-dim, 12 layers | PubMed + clinical notes |
| BlueBERT-Large-PubMed | 1024-dim, 24 layers | PubMed only |
| BlueBERT-Large-PubMed+MIMIC | 1024-dim, 24 layers | PubMed + clinical notes |

### Directly Relevant to Your Project

BlueBERT has **built-in fine-tuning scripts** for exactly the tasks you need:

1. **NER** (`run_bluebert_ner.py`)
   - BC5CDR: Chemical and disease recognition
   - ShARe/CLEFE: Clinical entity extraction

2. **Relation Extraction** (`run_bluebert.py`)
   - **ChemProt**: Chemical-protein interactions (your Drug-Protein relationships)
   - **DDI**: Drug-drug interactions (your INTERACTS_WITH relationship)
   - **i2b2 2010**: Clinical relation extraction

3. **Sentence Similarity** (`run_bluebert_sts.py`)
   - Could help with deduplication or finding similar papers

### BlueBERT vs Other Options

| Model | Training Data | Strengths | Weaknesses |
|-------|--------------|-----------|------------|
| **BlueBERT** | PubMed + MIMIC-III | Clinical notes included, NCBI pedigree, built-in RE tasks | Older (2019), TensorFlow 1.x codebase |
| **PubMedBERT** | PubMed only | From-scratch biomedical vocab, newer | No clinical notes |
| **BioLORD-2023** | Ontology-aligned | Best for entity similarity/linking | Not designed for RE |
| **BioBERT** | PubMed + PMC | Larger corpus (full papers) | General bio, not clinical |

### My Revised Recommendation

For your use case, I'd consider:

**Embeddings:**

- **BioLORD-2023** for entity embeddings (ontology alignment is valuable for your UMLS/HGNC linking)
- **BlueBERT or PubMedBERT** for paper/abstract embeddings

**Relation Extraction:**

- **BlueBERT fine-tuned on ChemProt + DDI** as your Tier 2 model - this gives you drug-protein and drug-drug interactions out of the box
- The ChemProt task specifically extracts relationships like: inhibitor, substrate, agonist, antagonist, activator - which map well to your schema

**NER:**

- Stick with **scispaCy** for NER (more modern, better maintained, handles entity linking)
- Or use BlueBERT's NER for chemical/disease recognition as a second opinion

### Practical Considerations

**Downsides of BlueBERT:**

- TensorFlow 1.x codebase (the repo code, not the HuggingFace weights)
- Last updated 2020
- Would need to wrap in modern PyTorch/HuggingFace for easier Lambda deployment

**Upsides:**

- HuggingFace weights available - you can load with `transformers` library and ignore the old TF code
- Pre-defined tasks match your relationship types well
- NCBI backing means the training was done carefully

### Quick Test You Could Run

```python
from transformers import AutoTokenizer, AutoModel

# Load BlueBERT from HuggingFace
tokenizer = AutoTokenizer.from_pretrained("bionlp/bluebert_pubmed_uncased_L-12_H-768_A-12")
model = AutoModel.from_pretrained("bionlp/bluebert_pubmed_uncased_L-12_H-768_A-12")

# Test on biomedical text
text = "Olaparib inhibits PARP1 in BRCA-mutated breast cancer cells."
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

# Get [CLS] embedding for sentence
sentence_embedding = outputs.last_hidden_state[:, 0, :]
```








# Overall Architecture

The tiered approach for relationship extraction makes sense — rule-based for high-confidence patterns, pre-trained models for standard biomedical relationships, and Claude for ambiguous or complex cases. The cost/speed tradeoffs are realistic for Lambda deployment.

## Model Selection Observations

Your analysis of the NER/embedding landscape is thorough. A few thoughts:

**scispaCy as the pragmatic choice** — I agree. The built-in UMLS/MeSH/RxNorm entity linking is a significant advantage over models that require you to build that pipeline yourself. The ~100-400MB footprint leaves plenty of room in a Lambda container for other components.

**BioLORD-2023 for embeddings** — Good choice for your use case. The ability to embed both concepts and sentences in the same latent space is valuable when you're matching extracted mentions against your RDS entity database.

**BlueBERT for relation extraction** — The ChemProt and DDI fine-tuning is directly relevant, but as you noted, those relationship types (inhibitor, substrate, agonist) are narrower than your schema's TREATS, INCREASES_RISK, ASSOCIATED_WITH. You might need to treat BlueBERT as a specialized Tier 2 component for drug-protein and drug-drug relationships specifically, with a separate model or Claude handling the broader relationship types.

## Schema Questions

**1. Temporal representation placeholder** — This is genuinely hard. One approach: rather than validity windows on edges, you could version the entire subgraph per paper. Each paper's JSON in S3 represents a snapshot of knowledge at publication time, and the aggregate graph reflects current consensus. Contradictions then emerge naturally from comparing paper subgraphs rather than requiring explicit temporal tracking.

**2. Confidence scoring formula** — The formula caps base_score at 0.8 with 10+ papers, which seems conservative. Is that intentional to leave room for study quality and other factors to push it higher? Also, the contradiction_penalty treats all contradictions equally — a single case report contradicting five RCTs would have disproportionate impact.

## Ambiguity Handling

The "p53" disambiguation strategy (SNS email → human review → weekly digest as volume increases) is practical. One addition to consider: when you store both interpretations in the JSON, you could also store a preliminary "best guess" based on context (e.g., if the paper discusses transcription, lean toward gene; if it discusses protein folding, lean toward protein). The human reviewer then confirms or corrects rather than deciding from scratch.

## Questions for You

1. **Entity collection storage** — The JSONL format with `{"type": "disease", "data": {...}}` is simple, but how do you handle cross-references? If a Drug references a Gene via `gene_id`, and you're loading incrementally, do you validate references at load time or defer to query time?

2. **Cold start strategy** — With 1K-10K papers initially, are you planning to pre-load all entities into RDS, or will the entity collection grow organically as papers are processed? If the latter, how do you handle the first paper that mentions a gene not yet in your collection?

3. **Relationship extraction scope** — Are you extracting relationships only from abstracts, or from full text? Full text gives you more signal but also more noise and significantly more tokens to process.

What aspects would you like to dig into further?



## Prompt:
12/3/2025, 12:56:54 PM

I'm not married to BlueBERT. I liked it because the PubMed people built it, but I know it's old and as you say, it misses some of the relationships I'm looking for. Please propose an alternative.

Can you suggest a better way to handle the Mutation/Gene/Variant question?

When generating Python code, please avoid dataclasses and use Pydantic models instead.



## Response:
12/3/2025, 12:57:53 PM

## Relationship Extraction Alternative to BlueBERT

Given your schema needs (TREATS, INCREASES_RISK, ASSOCIATED_WITH, INTERACTS_WITH, etc.), here are the stronger options:

### Option 1: PubMedBERT + Multi-task Fine-tuning

Start with `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext` and fine-tune on multiple RE datasets simultaneously:

- **ChemProt** — drug-protein interactions
- **DDI** — drug-drug interactions
- **GAD** — gene-disease associations (maps to INCREASES_RISK, ASSOCIATED_WITH)
- **EU-ADR** — drug-adverse event relations (maps to SIDE_EFFECT)

This gives you broader coverage than BlueBERT's single-task models while using a more modern base. The multi-task approach also tends to generalize better to unseen relationship types.

### Option 2: BioRE-based Models

**REBEL-biomedical** (`Babelscape/rebel-large`) is a seq2seq model that extracts triplets directly as text. It was trained on a broad relation ontology and can be prompted with your specific relationship types. The advantage is you don't need a separate classification head per relationship type — it generates `(subject, predicate, object)` tuples directly.

Example output format:
```
"Olaparib inhibits PARP1" → (Olaparib, INHIBITS, PARP1)
"BRCA1 mutations increase breast cancer risk" → (BRCA1 mutations, INCREASES_RISK, breast cancer)
```

### Option 3: Tiered Hybrid (My Recommendation)

Given your Lambda constraints and the breadth of relationships you need:

| Tier | Method | Relationships | Notes |
|------|--------|---------------|-------|
| **Tier 1** | Rule-based (spaCy dependency patterns) | TREATS, CAUSES, INHIBITS | High precision, fast, interpretable |
| **Tier 2** | PubMedBERT fine-tuned on GAD + ChemProt + DDI | INCREASES_RISK, INTERACTS_WITH, ASSOCIATED_WITH | Covers ~70% of cases |
| **Tier 3** | Claude API | Complex/implicit relationships, validation, ambiguous cases | Handles CONTRAINDICATED_FOR, multi-hop, nuanced relationships |

For Tier 2, I'd use `pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb` as a starting point — it's already fine-tuned for biomedical NLI which transfers well to relation classification. Then fine-tune further on the combined RE datasets.

### Bootstrap Strategy

Use Claude to generate training data for your specific relationship types:

1. Run Claude on 200-500 papers with your schema definition
2. Have Claude extract relationships with explanations
3. Human review a sample for quality
4. Fine-tune PubMedBERT on this Claude-generated + human-validated dataset
5. Use the fine-tuned model for bulk processing, Claude for edge cases

This gets you a model tailored to your exact schema without requiring months of manual annotation.


## Relationship Extraction Alternative to BlueBERT

Given your schema needs (TREATS, INCREASES_RISK, ASSOCIATED_WITH, INTERACTS_WITH, etc.), here are stronger options:

### Option 1: PubMedBERT + Multi-task Fine-tuning

Start with `microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext` and fine-tune on multiple RE datasets simultaneously:

- **ChemProt** — drug-protein interactions
- **DDI** — drug-drug interactions
- **GAD** — gene-disease associations (maps to INCREASES_RISK, ASSOCIATED_WITH)
- **EU-ADR** — drug-adverse event relations (maps to SIDE_EFFECT)

This provides broader coverage than BlueBERT while using a more modern base. Multi-task learning also generalizes better to unseen relationship types.

### Option 2: REBEL for Flexible Extraction

**REBEL** (`Babelscape/rebel-large`) is a seq2seq model that extracts triplets directly as text. It generates `(subject, predicate, object)` tuples without requiring separate classification heads for each relationship type.

Example:
```
"Olaparib inhibits PARP1" → (Olaparib, INHIBITS, PARP1)
"BRCA1 mutations increase breast cancer risk" → (BRCA1 mutations, INCREASES_RISK, breast cancer)
```

### Option 3: Tiered Hybrid (Recommended)

| Tier | Method | Relationships | Notes |
|------|--------|---------------|-------|
| **Tier 1** | Rule-based (spaCy dependency patterns) | TREATS, CAUSES, INHIBITS | High precision, fast, interpretable |
| **Tier 2** | PubMedBERT fine-tuned on GAD + ChemProt + DDI | INCREASES_RISK, INTERACTS_WITH, ASSOCIATED_WITH | Covers ~70% of cases |
| **Tier 3** | Claude API | Complex/implicit relationships, validation | Handles CONTRAINDICATED_FOR, multi-hop reasoning |

For Tier 2, start with `pritamdeka/PubMedBERT-mnli-snli-scinli-scitail-mednli-stsb` — it's already fine-tuned for biomedical NLI which transfers well to relation classification.

### Bootstrap Strategy

Use Claude to generate training data:

1. Run Claude on 200-500 papers with your schema definition
2. Extract relationships with explanations
3. Human review a sample for quality
4. Fine-tune PubMedBERT on this Claude-generated + validated dataset
5. Use fine-tuned model for bulk processing, Claude for edge cases

This creates a model tailored to your exact schema without months of manual annotation.

## Mutation/Gene/Variant Modeling

Your current approach has `Variant` as both a property on `Gene` nodes and as a separate relationship qualifier. I'd suggest simplifying to **one pattern**:

### Recommended: Variant as First-Class Entity

Make `Variant` a proper node type with bidirectional relationships:

```
Variant Node:
- variant_id: dbSNP ID (e.g., rs80357906) or HGVS notation
- gene_id: Reference to parent gene (HGNC ID)
- hgvs_c: Coding notation (e.g., c.68_69delAG)
- hgvs_p: Protein notation (e.g., p.Glu23ValfsTer17)
- variant_type: (snp, deletion, insertion, frameshift, etc.)
- consequence: (missense, nonsense, loss_of_function, etc.)
- clinvar_significance: ClinVar classification
- allele_frequency: Population frequency (if relevant)
- embedding_biolord: 768-dim embedding
- source: ("clinvar", "dbsnp", "extracted")
- created_at: Timestamp
```

**Relationships:**

```
Gene -[VARIANT_OF]-> Variant
  Properties:
  - transcript_affected: Which transcript
  - functional_impact: Description

Variant -[INCREASES_RISK]-> Disease
  Properties:
  - risk_ratio: 5.0
  - penetrance: 0.72
  - source_papers: [PMC IDs]
  - confidence: 0.92

Variant -[MODIFIES_RESPONSE]-> Drug
  Properties:
  - effect: (increased_efficacy, resistance, toxicity)
  - evidence: Description
  - source_papers: [PMC IDs]
```

**Why this is better:**

1. **Variants get their own identity** — Important for pharmacogenomics where specific variants affect drug response
2. **Cleaner queries** — `MATCH (v:Variant)-[:INCREASES_RISK]->(d:Disease)` instead of filtering on edge properties
3. **Reusability** — Same variant can appear in multiple relationships without duplication
4. **Embeddings** — Each variant gets its own embedding for semantic search
5. **Provenance** — Track where variant information came from (ClinVar vs. extracted)

**Example graph:**

```
(:Gene {hgnc_id: "HGNC:1100", symbol: "BRCA1"})
  -[:VARIANT_OF]->
(:Variant {variant_id: "rs80357906", hgvs_c: "c.68_69delAG", consequence: "frameshift"})
  -[:INCREASES_RISK {risk_ratio: 5.0, penetrance: 0.72, confidence: 0.92}]->
(:Disease {umls_id: "C0006142", name: "Breast Cancer"})

(:Variant {variant_id: "rs80357906"})
  -[:MODIFIES_RESPONSE {effect: "increased_efficacy", confidence: 0.88}]->
(:Drug {rxnorm_id: "1187832", name: "Olaparib"})
```

This enables queries like:
- "Which BRCA1 variants increase breast cancer risk?"
- "Which variants affect Olaparib response?"
- "What's the clinical significance of rs80357906?"

## Questions to think about

1. **Entity collection storage** — With the JSONL format `{"type": "disease", "data": {...}}`, how do you handle cross-references? If a Drug references a Gene via `gene_id` and you're loading incrementally, do you validate references at load time or defer to query time? ANSWER: The gene DB only ever grows, never shrinks, so a gene_id need never be reassigned and as a reference it will always remain valid.

2. **Cold start strategy** — With 1K-10K papers initially, are you pre-loading all entities from UMLS/HGNC/RxNorm into RDS, or will the entity collection grow organically as papers are processed? ANSWER: I'll start with a small set of entities from trusted sources, and let the collection grow organically as papers are processed.

3. **Relationship extraction scope** — Are you extracting from abstracts only or full text? Full text gives more signal but also more noise and processing cost. ANSWER: I'll start with abstracts only, and move to full text at a later date.

4. **Temporal representation** — Your placeholder section raises a good question. Rather than validity windows on edges, have you considered versioning the entire subgraph per paper? Each paper's JSON represents a snapshot at publication time, and the aggregate graph reflects current consensus. Contradictions emerge naturally from comparing paper subgraphs.
