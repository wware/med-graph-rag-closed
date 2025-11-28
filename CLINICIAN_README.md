# Medical Knowledge Graph: Your Research Partner

## What This Does for You

Imagine having a research assistant who has read every relevant paper on PubMed and can instantly answer questions like:

- **"What treatments work for BRCA1-mutated breast cancer?"** — Not just a list, but with evidence strength, response rates, and the actual papers to review
- **"What are the side effects of combining Drug A with Drug B?"** — Including rare interactions buried in case reports
- **"Show me contradicting evidence about Drug X for Disease Y"** — Because medicine evolves, and knowing where experts disagree matters

This system does exactly that. It reads medical research papers, understands the relationships between diseases, genes, drugs, and treatments, and lets you query that knowledge in plain English.

## Why This Matters

### The Problem Every Clinician Faces

Medical knowledge doubles every 73 days. No human can keep up. Even specialists struggle to stay current in their narrow fields. When you're seeing patients, you need answers *now*—not after spending hours searching PubMed and reading dozens of papers.

### What Makes This Different

Traditional search gives you papers. You still have to:
1. Read them all
2. Figure out which findings matter
3. Reconcile contradictions
4. Remember which paper said what

**This system does that work for you.** It reads the papers, extracts the medical facts, connects them together, and tracks which papers support each claim. It even flags when different studies disagree.

## Real Clinical Use Cases

### Case 1: Precision Oncology

**Your patient:** 42-year-old woman, newly diagnosed breast cancer, genetic testing shows BRCA1 mutation

**Your question:** "What drugs treat BRCA1-mutated breast cancer?"

**What you get:**
```
Drug: Olaparib
- Response rate: 59%
- Indication: BRCA-mutated breast cancer
- Evidence strength: High (85% confidence)
- Based on: 8 clinical trials
- Source papers: [links to PMC articles]

Drug: Talazoparib
- Response rate: 63%
- Indication: Advanced BRCA1/2-mutated breast cancer
- Evidence strength: High (82% confidence)
- Based on: 5 clinical trials
- Source papers: [links to PMC articles]
```

You can immediately see which PARP inhibitors have the best evidence, compare their efficacy, and access the original trials—all in under 10 seconds.

### Case 2: Avoiding Dangerous Drug Interactions

**Your patient:** 68-year-old on warfarin, needs antibiotic for UTI

**Your question:** "What antibiotics interact with warfarin?"

**What you get:**
```
Drug: Trimethoprim-Sulfamethoxazole
- Interaction type: Antagonistic (increases warfarin effect)
- Severity: Major
- Clinical significance: Significant bleeding risk, requires INR monitoring
- Frequency: Common (affects 30-50% of patients)
- Source papers: [links to studies and case reports]

Drug: Ciprofloxacin
- Interaction type: Antagonistic (increases warfarin effect)
- Severity: Moderate
- Clinical significance: May increase bleeding risk
- Recommendation: Monitor INR if co-prescribed
- Source papers: [links to evidence]

Drug: Nitrofurantoin
- Interaction type: Minimal
- Severity: Minor
- Clinical significance: Safe to co-prescribe
- Source papers: [links to safety data]
```

Instead of hoping you remember every interaction or checking multiple databases, you get a comprehensive view with evidence strength.

### Case 3: Understanding Contradictory Evidence

**Your question:** "What's the evidence for aspirin in primary prevention of cardiovascular disease?"

**What you get:**
```
Relationship: Aspirin → Prevents Cardiovascular Disease

SUPPORTING EVIDENCE (6 studies):
- ASPREE trial (2018): No benefit in healthy elderly (>70 years)
  * Sample: 19,114 patients
  * Finding: No reduction in cardiovascular events

- ARRIVE trial (2018): No benefit in moderate-risk patients
  * Sample: 12,546 patients
  * Finding: No significant reduction in cardiovascular events

CONTRADICTING EVIDENCE (4 earlier studies):
- Physicians' Health Study (1989): Reduced MI risk
  * Sample: 22,071 physicians
  * Finding: 44% reduction in first MI
  * Note: All male population, younger than recent trials

CURRENT CONSENSUS:
- Confidence: Medium (mixed evidence)
- Interpretation: Benefit unclear in low-moderate risk;
  newer trials suggest less benefit than previously thought
- Recommendation: Consider bleeding risk vs. benefit on individual basis
```

You see the evolution of medical thinking, understand why guidelines have changed, and can make informed decisions with your patients.

## How It Works (The Simple Version)

Think of this system as three things working together:

### 1. **The Reader**
The system downloads medical papers from PubMed Central and reads them—not just skimming for keywords, but actually understanding what they say about diseases, drugs, genes, and treatments.

### 2. **The Brain**
It extracts the important facts: "This drug treats this disease," "This gene increases risk for this condition," "These two drugs interact badly." It stores these facts in a knowledge graph (imagine a giant web where dots are medical concepts and lines show how they relate).

### 3. **The Search Engine**
When you ask a question in plain English, it understands what you're asking and searches both:
- For papers semantically similar to your question (finds relevant research even if it uses different words)
- For specific relationships in the knowledge graph (finds exact connections: Drug A → treats → Disease B)

Then it combines both results, ranks them by evidence strength, and gives you a clear answer with sources.

## What Kind of Questions Can You Ask?

The system handles questions that require connecting multiple pieces of information:

**Direct Treatment Questions:**
- "What drugs treat metastatic melanoma?"
- "What are the treatment options for triple-negative breast cancer?"

**Risk and Genetics:**
- "What diseases are associated with Lynch syndrome?"
- "What's the cancer risk with PALB2 mutations?"

**Drug Safety:**
- "What are the cardiac side effects of anthracyclines?"
- "What drugs are contraindicated in pregnancy?"

**Mechanism and Biology:**
- "What pathways does EGFR participate in?"
- "What proteins does the TP53 gene encode?"

**Complex Multi-Hop Questions:**
- "What drugs target proteins in the DNA repair pathway?"
- "What biomarkers predict response to immunotherapy in lung cancer?"

**Evidence Quality:**
- "Show me high-confidence treatments for rheumatoid arthritis"
- "What's the evidence quality for colchicine in COVID-19?"

## An Example Query (For the Curious)

You don't need to know this to use the system—you just type questions in English. But if you're curious about what happens under the hood, here's one example:

**Your question:** "What drugs treat BRCA1-mutated breast cancer?"

**The system translates this to:**
```
Find all:
  - Drugs (variable: drug)
  - Connected to Diseases named "Breast Cancer" (variable: disease)
  - Through a TREATS relationship (variable: treats)
  - Where the Disease is also connected to Gene "BRCA1"
  - Through an INCREASES_RISK relationship

Return:
  - drug.name
  - treats.efficacy
  - treats.response_rate
  - treats.source_papers

Order by:
  - treats.confidence (highest first)
```

The system then searches its knowledge graph, finds all the connections, and returns results ranked by evidence strength.

## What Makes the Answers Trustworthy?

### Every Fact is Sourced
Unlike AI chatbots that sometimes "hallucinate" facts, every relationship in this system links back to actual research papers. When it says "Drug X treats Disease Y," it shows you the papers that support that claim.

### Evidence Strength Scoring
Not all papers are equal. The system considers:
- **Study type:** Randomized controlled trials weighted higher than case reports
- **Sample size:** Larger studies get more weight
- **Number of supporting papers:** More replication = higher confidence
- **Journal quality:** Higher-impact journals weighted slightly more
- **Contradictions:** If some papers disagree, confidence score drops

### Contradiction Detection
The system doesn't hide conflicting evidence. If Paper A says "Drug X works" but Paper B says "Drug X doesn't work," you see both. This is crucial because medicine evolves—what we thought was true in 2010 might be contradicted by better studies in 2023.

### Temporal Tracking
Medical knowledge changes. The system tracks *when* each finding was published, so you can see:
- How understanding evolved over time
- Whether newer studies contradict older ones
- What the current consensus is

## What It Doesn't Do

**It's not a replacement for clinical judgment.** This is a research tool that helps you find and synthesize evidence faster. You still need to:
- Evaluate whether findings apply to your specific patient
- Consider individual patient factors and preferences
- Use your clinical experience and expertise
- Stay within your scope of practice

**It's not WebMD.** This isn't designed for patients (though a patient-friendly version could be built). It assumes medical knowledge and uses clinical terminology.

**It's not comprehensive (yet).** The system only knows about papers it has ingested. Right now, that's a subset of PubMed Central. It doesn't include:
- Papers still behind paywalls
- Very recent research (there's a processing lag)
- Clinical trial databases (though this could be added)
- Textbook knowledge not in research papers

## The Technology (Very High Level)

For those who want to understand what's happening behind the scenes:

**Data Source:** Research papers from PubMed Central (millions of articles available as structured XML files)

**Entity Extraction:** The system identifies medical concepts in papers:
- Diseases (mapped to standard IDs like UMLS codes)
- Genes (mapped to HGNC gene symbols)
- Drugs (mapped to RxNorm medication codes)
- Proteins, symptoms, procedures, biomarkers, etc.

**Relationship Detection:** It finds connections: "Drug X treats Disease Y," "Gene A increases risk of Disease B," "Drug X interacts with Drug Y"

**Storage:**
- **Vector Database (OpenSearch):** Stores mathematical representations of text meaning, enabling semantic search
- **Knowledge Graph (Neptune):** Stores entities and their relationships, enabling connection-based queries

**Query Interface:**
- Type questions in plain English
- AI (Claude 3.5) converts your question into a structured query
- System searches both the vector database and knowledge graph
- Results are synthesized, ranked by confidence, and returned with source citations

**Standards-Based:** Uses medical standards like UMLS (Unified Medical Language System), MeSH (Medical Subject Headings), HGNC (gene nomenclature), and RxNorm (medication names) to ensure consistency.

## Getting Started

### For Individual Clinicians

The easiest way to use this is through the web interface (when available):
1. Go to the web portal
2. Type your medical question in plain English
3. Review results with confidence scores and source papers
4. Click through to original papers for full context

### For Healthcare Organizations

This system can be deployed within your institution to:
- Stay within your security and compliance requirements (HIPAA, etc.)
- Integrate with your EHR system
- Customize for your specialty or patient population
- Add your institution's proprietary research or guidelines

Contact your IT department about a pilot deployment.

### For Researchers

If you're doing systematic reviews, meta-analyses, or just trying to map out a research area, this tool can dramatically accelerate your work. Instead of manually searching and screening hundreds of papers, you can:
- Find all papers mentioning specific drug-disease combinations
- Map out what's known about a particular pathway or mechanism
- Identify gaps in the literature (relationships with low evidence)
- Find contradictions that warrant further study

## Privacy and Data Security

**What data does this system access?**
- Only published medical research papers (already public on PubMed Central)
- No patient data
- No EHR data
- No private health information

**What happens to your queries?**
- Queries are processed to return results
- Depending on deployment, queries may be logged for system improvement
- No PHI (Protected Health Information) should ever be entered into queries

**Can it be used for clinical documentation?**
Not in its current form. This is a research and decision-support tool, not a documentation system. Always document clinical decisions in your official EHR.

## Evidence Quality: What the Confidence Scores Mean

When the system shows a relationship like "Drug X treats Disease Y," it includes a confidence score (0.0 to 1.0). Here's how to interpret it:

**High Confidence (0.8 - 1.0):**
- Multiple high-quality studies (RCTs, large cohorts)
- Consistent findings across studies
- Few or no contradictions
- Large sample sizes
- *Interpretation:* Strong evidence, widely accepted

**Medium Confidence (0.5 - 0.79):**
- Several studies, but mixed quality
- Some contradictions or limitations
- Moderate sample sizes
- May be emerging evidence
- *Interpretation:* Reasonable evidence, but not definitive

**Low Confidence (0.3 - 0.49):**
- Limited studies
- Small samples or case reports
- Significant contradictions
- Preliminary findings
- *Interpretation:* Weak evidence, needs more research

**Very Low Confidence (0.0 - 0.29):**
- Single small study or case report
- Major contradictions
- Very limited data
- *Interpretation:* Insufficient evidence for clinical decisions

## Future Directions

This is an evolving system. Planned enhancements include:

**More Data Sources:**
- ClinicalTrials.gov integration (ongoing trials and results)
- FDA drug labels and safety alerts
- Clinical practice guidelines
- Pharmacovigilance databases

**Better Entity Recognition:**
- Advanced medical NER (Named Entity Recognition) models
- AWS Comprehend Medical integration
- Better recognition of rare diseases and novel therapies

**Clinical Decision Support:**
- Integration with EHR systems
- Real-time alerts for drug interactions
- Personalized treatment recommendations based on patient genetics

**Visualization:**
- Interactive knowledge graph visualization
- Timeline views showing how evidence evolved
- Relationship strength maps

## Questions?

**"How current is the information?"**
The system is updated as new papers are added to PubMed Central. There's typically a lag of a few weeks to months depending on ingestion schedule.

**"What if I find an error?"**
The system is only as good as the papers it reads. If source papers have errors, or if the extraction process makes a mistake, errors can propagate. Always verify critical findings by reviewing source papers.

**"Can I trust this for patient care decisions?"**
Use it as you would any clinical decision support tool: as one input to your decision-making, not the only input. Always consider individual patient factors, your clinical judgment, and current practice guidelines.

**"How is this different from PubMed search?"**
PubMed finds papers that mention your keywords. This system finds papers that answer your specific question, extracts the relevant facts, synthesizes across multiple papers, shows evidence strength, and highlights contradictions.

**"What about cost?"**
Deployment costs vary based on scale. For small research groups, monthly costs can be under $100. For enterprise deployments serving thousands of clinicians, costs scale up but are still typically much less than traditional clinical decision support systems.

## About This Project

This system was built to bridge the gap between the explosion of medical research and clinicians' ability to stay current. It represents a new approach to medical knowledge management: not just indexing papers, but truly understanding and connecting the medical facts within them.

The goal is to give every clinician the equivalent of a research team working 24/7 to keep them up to date—because patients deserve doctors who have the best available evidence at their fingertips.

---

**Built with:** AWS Bedrock (Claude AI), Amazon OpenSearch (vector search), Amazon Neptune (knowledge graph), PubMed Central (research papers)

**Standards:** UMLS, MeSH, HGNC, RxNorm, ICD-10, CPT

**For more information:** See [README.md](README.md) for technical details, or contact your health informatics team about a pilot deployment.
