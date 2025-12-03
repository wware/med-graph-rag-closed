"""
Stage 3: Convert scispaCy extractions to typed Pydantic entities
"""

import spacy
from scispacy.linking import EntityLinker
import time
from src.schema.entity import Disease, Drug, EntityCollection, Symptom

# Load reference entities first
print("Loading reference entities...")
collection = EntityCollection.load("reference_entities.jsonl")
print(f"✓ Loaded {collection.entity_count} reference entities")
print(f"  - Diseases: {len(collection.diseases)}")
print(f"  - Genes: {len(collection.genes)}")
print(f"  - Drugs: {len(collection.drugs)}")
print()

# Load models (this is the slow part)
print("Loading models...")
start = time.time()
nlp = spacy.load("en_ner_bc5cdr_md")
nlp.add_pipe(
    "scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"}
)
print(f"Loaded in {time.time() - start:.1f}s\n")

# Your test abstracts
abstracts = """BRCA1 mutations increase the risk of breast cancer. 
Patients with BRCA1 185delAG showed 5-fold increased risk.

BRCA1 mutations increase the risk of breast cancer. Patients with BRCA1 185delAG
frameshift mutation showed 5-fold increased lifetime risk compared to general
population. Penetrance was estimated at 72% by age 80.

Olaparib, a PARP inhibitor, demonstrated significant efficacy in
BRCA-mutated ovarian cancer. The phase III trial showed median progression-free
survival of 19.1 months versus 5.5 months with placebo (HR 0.30, p<0.0001).
Response rate was 59% in the olaparib group.

Type 2 diabetes mellitus is associated with increased cardiovascular disease risk.
Meta-analysis of 37 prospective studies found diabetic patients had 2-fold increased
risk of coronary heart disease and 2.3-fold increased stroke risk after adjusting
for conventional risk factors.

Pembrolizumab, an anti-PD-1 antibody, showed durable responses in non-small
cell lung cancer patients with high PD-L1 expression. Overall survival at 5 years
was 31.9% versus 16.3% with chemotherapy. Common adverse events included fatigue,
rash, and immune-mediated toxicities.

The TP53 gene encodes the p53 tumor suppressor protein. TP53 mutations occur in
approximately 50% of human cancers and result in loss of cell cycle checkpoint
control and apoptosis. The R175H missense mutation is one of the most common
hotspot mutations.

Metformin reduces hepatic glucose production through AMPK-dependent inhibition
of gluconeogenesis. It also improves insulin sensitivity in peripheral tissues.
Unlike sulfonylureas, metformin does not cause hypoglycemia and is associated
with modest weight loss.

Warfarin and aspirin interact to increase bleeding risk. Concurrent use results
in 2.4-fold increased risk of major hemorrhage. INR monitoring should be
intensified when aspirin is added to warfarin therapy. The interaction is
pharmacodynamic rather than pharmacokinetic.

EGFR tyrosine kinase inhibitors such as erlotinib are effective in non-small cell
lung cancer with EGFR exon 19 deletions or L858R mutations. However, acquired
resistance typically develops through T790M mutation in EGFR exon 20.
Third-generation inhibitors like osimertinib overcome T790M-mediated resistance.

Statin therapy reduces LDL cholesterol and cardiovascular events. The CTT
meta-analysis showed each 1 mmol/L reduction in LDL-C resulted in 21% relative
risk reduction for major vascular events. Benefits were consistent across patient
subgroups regardless of baseline LDL levels.

HLA-B*5701 screening prevents abacavir hypersensitivity reactions in HIV patients.
Presence of this allele increases hypersensitivity risk from 4% to 48%. Current
guidelines recommend HLA-B*5701 testing before abacavir initiation. The
pharmacogenetic association has 100% negative predictive value.
""".strip().split(
    "\n\n"
)

# Track what's new vs merged
new_entities = 0
merged_entities = 0

# Common symptoms that get mislabeled as diseases
SYMPTOM_TERMS = {
    "fatigue",
    "rash",
    "nausea",
    "vomiting",
    "headache",
    "dizziness",
    "weight loss",
    "weight gain",
    "pain",
    "fever",
    "cough",
    "bleeding",
    "toxicities",
    "diarrhea",
    "constipation",
    "insomnia",
}

# Process abstracts
for i, abstract in enumerate(abstracts, 1):
    doc = nlp(abstract)

    print(f"=== Abstract {i} ===")

    for ent in doc.ents:
        # Skip if no UMLS linking
        if not ent._.kb_ents:
            print(f"⚠ Skipped '{ent.text}' (no UMLS link)")
            continue

        umls_id, confidence = ent._.kb_ents[0]

        if ent.label_ == "DISEASE":
            entity_text_lower = ent.text.lower()

            # Check if this is actually a symptom
            if any(symptom in entity_text_lower for symptom in SYMPTOM_TERMS):
                existing = collection.symptoms.get(umls_id)

                if existing:
                    if ent.text not in existing.synonyms:
                        existing.synonyms.append(ent.text)
                        merged_entities += 1
                        print(
                            f"✓ Updated symptom {existing.name} with synonym '{ent.text}'"
                        )
                else:
                    symptom = Symptom(
                        entity_id=umls_id,
                        name=ent.text,
                        synonyms=[ent.text],
                        source="extracted",
                    )
                    collection.symptoms[symptom.entity_id] = symptom
                    new_entities += 1
                    print(
                        f"✓ Added symptom: {symptom.name} ({umls_id}, conf={confidence:.2f})"
                    )
                continue

            # Check if we already have this disease
            existing = collection.get_by_umls(umls_id)

            if existing:
                # Merge synonym
                if ent.text not in existing.synonyms:
                    existing.synonyms.append(ent.text)
                    merged_entities += 1
                    print(f"✓ Updated {existing.name} with synonym '{ent.text}'")
            else:
                # Create new disease
                disease = Disease(
                    entity_id=umls_id,
                    name=ent.text,  # Use mention as name for now
                    synonyms=[ent.text],
                    umls_id=umls_id,
                    source="extracted",
                )
                collection.add_disease(disease)
                new_entities += 1
                print(
                    f"✓ Added disease: {disease.name} ({umls_id}, conf={confidence:.2f})"
                )

        elif ent.label_ == "CHEMICAL":
            # Check if it's already stored as a disease/symptom
            disease_match = collection.get_by_umls(umls_id)
            if disease_match:
                if ent.text not in disease_match.synonyms:
                    disease_match.synonyms.append(ent.text)
                    merged_entities += 1
                print(f"✓ Merged '{ent.text}' into disease {disease_match.name}")
                continue

            # Check existing drugs
            existing = collection.get_by_id(umls_id)

            if existing:
                # Merge synonym
                if ent.text not in existing.synonyms:
                    existing.synonyms.append(ent.text)
                    merged_entities += 1
                    print(f"✓ Updated {existing.name} with synonym '{ent.text}'")
            else:
                # Create new drug (treating all chemicals as drugs for now)
                drug = Drug(
                    entity_id=umls_id,
                    name=ent.text,
                    synonyms=[ent.text],
                    rxnorm_id=umls_id,  # UMLS often includes RxNorm
                    source="extracted",
                )
                collection.add_drug(drug)
                new_entities += 1
                print(f"✓ Added drug: {drug.name} ({umls_id}, conf={confidence:.2f})")

    print()

# Summary
print(f"=== Summary ===")
print(f"Total entities: {collection.entity_count}")
print(f"  - Diseases: {len(collection.diseases)}")
print(f"  - Drugs: {len(collection.drugs)}")
print(f"  - Symptoms: {len(collection.symptoms)}")  # Add this!
print(f"\nNew entities added: {new_entities}")
print(f"Existing entities updated: {merged_entities}")
print()

# Show symptoms too
print("=== Symptoms ===")
for symptom in collection.symptoms.values():
    print(f"{symptom.name} ({symptom.entity_id})")
    if len(symptom.synonyms) > 1:
        print(f"  Synonyms: {', '.join(symptom.synonyms)}")
print()

# Show what we have
print("=== Diseases ===")
for disease in collection.diseases.values():
    print(f"{disease.name} ({disease.entity_id})")
    if len(disease.synonyms) > 1:
        print(f"  Synonyms: {', '.join(disease.synonyms)}")
print()

print("=== Drugs ===")
for drug in collection.drugs.values():
    print(f"{drug.name} ({drug.entity_id})")
    if len(drug.synonyms) > 1:
        print(f"  Synonyms: {', '.join(drug.synonyms)}")
print()

# Save to JSONL
output_path = "entities.jsonl"
collection.save(output_path)
print(f"✓ Saved to {output_path}")

# Test reload
loaded = EntityCollection.load(output_path)
print(f"✓ Reloaded: {loaded.entity_count} entities")
