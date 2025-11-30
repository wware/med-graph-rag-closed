# Medical Literature Reasoning: Complete Guide for Clinicians

> **Want the quick pitch?** See [CLINICIAN_PITCH.md](CLINICIAN_PITCH.md) for a concise overview.
>
> This document provides comprehensive information about how the tool works, what it does and doesn't do, and how it fits with your existing workflow.

## How This Fits Your Existing Workflow

You already use clinical AI tools. This one fills a specific gap.

### Tools You Probably Already Use

**UpToDate** - Clinical summaries for standard presentations
- Excellent for "What's the first-line treatment for X?"
- Curated, expert-reviewed content
- **Limitation:** Doesn't handle complex multi-system cases that don't fit textbooks

**PubMed** - Literature database
- Comprehensive, free, up-to-date
- **Limitation:** Returns papers, you still read and synthesize manually

**Claude, ChatGPT, Glass Health** - AI assistants
- Quick questions, differential diagnosis support
- **Limitation:** Can hallucinate, don't connect evidence across papers systematically

**This MCP Server** - Deep literature reasoning
- Multi-hop connections across papers
- Automatic contradiction detection
- Diagnostic chain following
- Paragraph-level provenance

### How They Work Together

```
Complex diagnostic question
    ↓
Your AI assistant (Claude, etc.)
    ↓
Calls this MCP server for deep literature reasoning
    ↓
Returns answer with multi-hop connections + contradictions flagged
    ↓
You verify with source papers (PubMed links provided)
    ↓
Check UpToDate for standard treatment guidelines
    ↓
Make clinical decision with all evidence
```

**You don't change how you work.** You ask questions the same way. The MCP server just makes your AI assistant smarter about medical literature.

## What This Does

### The Core Capabilities

**1. Multi-hop reasoning across papers**

Standard search: "Find papers mentioning BRCA1 and breast cancer" → 10,000 results

This tool: "What's the treatment pathway for BRCA1-mutated breast cancer?" → Connects:
- BRCA1 mutation → DNA repair deficiency
- DNA repair deficiency → PARP inhibitor sensitivity
- PARP inhibitors → Specific drugs (olaparib, talazoparib)
- Clinical trials → Response rates and evidence strength

All with citations to specific papers, sections, and paragraphs.

**2. Automatic contradiction detection**

Ask: "What's the evidence for aspirin in primary prevention?"

Get:
```
SUPPORTING (older studies):
- Physicians' Health Study (1989): 44% reduction in MI
  BUT: All-male population, younger than current recommendations

CONTRADICTING (recent trials):
- ASPREE (2018, n=19,114): No benefit in elderly (>70 years)
- ARRIVE (2018, n=12,546): No benefit in moderate-risk patients

CONSENSUS: Benefit unclear in low-moderate risk populations.
Recent evidence suggests less benefit than previously thought.
```

You see **both sides** with evidence quality, so you can explain to patients why guidelines changed.

**3. Diagnostic chain following**

Complex case: "Patient with elevated ALP, normal AST/ALT, fatigue, photosensitive rash, joint pain, positive ANA"

The system traces:
```
Isolated elevated ALP
    ↓
Primary biliary cholangitis (PBC) OR bone disorders
    ↓
PBC + photosensitive rash + joint pain + ANA
    ↓
Overlap syndrome: PBC + Systemic lupus erythematosus
    ↓
Cited treatment studies for overlap syndrome
```

With evidence strength at each step and contradictions flagged.

**4. Paragraph-level provenance**

Every claim links to: **"PMC1234567, Results section, paragraph 3"**

Not just "according to this study" but **exactly where** so you can verify before trusting.

## Real Clinical Examples

### Example 1: Precision Oncology

**Patient:** 42F, newly diagnosed breast cancer, BRCA1 mutation

**Question:** *"What drugs treat BRCA1-mutated breast cancer?"*

**Results:**
```
Olaparib (PARP inhibitor)
- Response rate: 59%
- Evidence: 8 RCTs, high confidence (0.85)
- FDA approved for BRCA-mutated breast cancer
- Source: OlympiAD trial (Robson et al., NEJM 2017)
  PMC5678234, Results, paragraph 2

Talazoparib (PARP inhibitor)
- Response rate: 63%
- Evidence: 5 RCTs, high confidence (0.82)
- FDA approved for advanced BRCA1/2-mutated breast cancer
- Source: EMBRACA trial (Litton et al., Lancet Oncol 2018)
  PMC6123456, Results, paragraph 4

Platinum-based chemotherapy
- Response rate: 53%
- Evidence: 12 studies, medium confidence (0.68)
- Higher toxicity than PARP inhibitors
- Often used after PARP inhibitor progression
```

**Time to result:** 6 seconds

**What you'd do manually:** Search PubMed for "BRCA1 breast cancer treatment" → 3,487 papers → Read abstracts → Find trials → Compare results → 45+ minutes

### Example 2: Avoiding Dangerous Interactions

**Patient:** 68M on warfarin, needs antibiotic for UTI

**Question:** *"What antibiotics interact with warfarin?"*

**Results:**
```
HIGH RISK - Avoid:
Trimethoprim-Sulfamethoxazole
- Increases warfarin effect significantly
- Bleeding risk: 30-50% of patients
- Mechanism: CYP2C9 inhibition
- Source: 8 case series + 3 cohort studies
  PMC8765432, Discussion, paragraph 5

MODERATE RISK - Monitor INR:
Ciprofloxacin
- May increase warfarin effect
- Bleeding risk: 10-15% of patients
- Recommendation: Check INR 3-5 days after starting
- Source: 5 case series + 2 RCTs

LOW RISK - Safe alternative:
Nitrofurantoin
- Minimal interaction
- Safe to co-prescribe
- Source: 3 large cohort studies showing no significant interaction
```

Better than hoping you remember every interaction or checking multiple databases.

### Example 3: Understanding Evidence Evolution

**Question:** *"Has the evidence for hormone replacement therapy in menopause changed over time?"*

**Results:**
```
1980s-1990s CONSENSUS:
- Observational studies showed cardiovascular benefit
- Widely recommended for heart disease prevention
- Confidence: Medium (observational data only)

2002 PIVOT - Women's Health Initiative:
- First large RCT (n=16,608)
- INCREASED cardiovascular risk in some groups
- Changed practice overnight
- Source: WHI trial (JAMA 2002)

2010s-PRESENT NUANCED VIEW:
- Timing hypothesis: benefit if started at menopause
- Risk if started >10 years post-menopause
- Individualized risk-benefit assessment
- Confidence: High (multiple RCTs now available)

Current consensus: Not for cardiovascular prevention,
but may be appropriate for menopausal symptoms in
younger women without contraindications.
```

You see **why** guidelines changed and can explain evolution to patients.

## What Makes This Trustworthy

### Every Fact Has a Source

Unlike AI chatbots that sometimes hallucinate, every relationship links to actual papers:

- **Which paper:** PMC ID and DOI
- **Which section:** Results, Methods, Discussion
- **Which paragraph:** Exact location for verification

### Evidence Strength Scoring

Not all evidence is equal. The system considers:

**Study design:**
- Randomized controlled trials: High weight
- Cohort studies: Medium weight
- Case-control studies: Lower weight
- Case reports: Lowest weight

**Sample size:**
- Larger studies weighted higher
- n=10,000 > n=100

**Replication:**
- Multiple studies showing same result → Higher confidence
- Single study → Lower confidence

**Contradictions:**
- If papers disagree, confidence drops
- You see both sides

**Recency:**
- Recent large RCTs can override older observational data
- System tracks how evidence evolved

### Confidence Score Interpretation

**High (0.8-1.0):** Strong evidence, widely accepted, multiple high-quality studies

**Medium (0.5-0.79):** Reasonable evidence but some limitations or contradictions

**Low (0.3-0.49):** Weak evidence, preliminary findings, needs more research

**Very Low (0.0-0.29):** Insufficient evidence, single case reports, major contradictions

## What It Doesn't Do

### Not a Replacement for Clinical Judgment

This is a **research and decision support tool**. You still need to:
- Evaluate if findings apply to your specific patient
- Consider individual patient factors (age, comorbidities, preferences)
- Use your clinical expertise
- Stay within your scope of practice

### Not Comprehensive (Yet)

The system only knows about papers it has ingested:
- Subset of PubMed Central (growing daily)
- Doesn't include papers behind paywalls
- Processing lag (a few weeks for very recent papers)
- Doesn't include clinical trial databases (could be added)

### Not a Documentation System

This is for **research and decision support**, not clinical documentation.

- Don't enter PHI (Protected Health Information) in queries
- Document clinical decisions in your official EHR
- Use this to inform decisions, not as the official record

### Not WebMD

This assumes medical knowledge and uses clinical terminology. It's designed for clinicians and researchers, not patients (though a patient-friendly version could be built).

## How to Use It

### Installation (One-Time Setup)

```bash
# Install the MCP server
uvx pubmed-graph-rag

# Add to your Claude Desktop config
# File location: ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "pubmed-graph-rag": {
      "command": "uvx",
      "args": ["pubmed-graph-rag"]
    }
  }
}
```

**That's it.** Your AI assistant can now call the MCP server automatically.

### Asking Questions

**Natural language:** Just ask questions like you would a colleague

**Good questions:**
- "What drugs treat metastatic melanoma with BRAF mutations?"
- "What are the cardiac side effects of anthracyclines?"
- "Show me contradicting evidence about colchicine in COVID-19"
- "What conditions cause elevated ALP with normal AST/ALT?"

**Too vague:**
- "Tell me about cancer" (too broad)
- "What's the best treatment?" (need context: best for what?)

**Complex multi-hop questions work well:**
- "What drugs target proteins in the DNA repair pathway affected by BRCA mutations?"
- "What biomarkers predict response to immunotherapy in non-small cell lung cancer?"

### Interpreting Results

**Check confidence scores:** High confidence = strong evidence, Low = preliminary

**Verify sources:** Click through to papers for critical decisions

**Look for contradictions:** If flagged, understand both sides before recommending

**Consider recency:** Recent large trials may override older observational data

### When to Use This vs. Other Tools

**Use UpToDate when:**
- Standard presentation of common condition
- Need quick first-line treatment guideline
- Want expert-curated summary

**Use PubMed when:**
- Need comprehensive literature search
- Writing a paper or systematic review
- Want to see ALL studies on a topic

**Use this MCP server when:**
- Complex multi-system presentation
- Need to connect evidence across papers
- Want contradictions flagged automatically
- Rare condition you see occasionally
- Precision medicine question (genetics → treatment)

## For Healthcare Organizations

### Institutional Deployment

The MCP server can be deployed within your organization:

**Security & Compliance:**
- HIPAA compliant deployment options
- On-premise or secure cloud
- No PHI leaves your environment
- Audit logging for queries

**Integration:**
- EHR integration possible
- Single sign-on (SSO)
- Institutional authentication

**Customization:**
- Add your institutional research
- Include institutional guidelines
- Customize for your specialty
- Priority support

**Contact your IT department** about a pilot deployment.

## Privacy & Data Security

**What data does this access?**
- Only published medical research papers (public on PubMed Central)
- No patient data
- No EHR data
- No PHI

**What happens to your queries?**
- Queries processed to return results
- May be logged for system improvement (depending on deployment)
- **Never enter PHI in queries** (patient names, MRNs, specific dates, etc.)

**Can queries be traced to you?**
- Depends on deployment
- Institutional deployments may log for compliance
- Individual use: queries associated with your account

## Future Development

**More data sources (planned):**
- ClinicalTrials.gov (ongoing trials and results)
- FDA drug labels and safety alerts
- Clinical practice guidelines (AHA, ACC, ASCO, etc.)
- Pharmacovigilance databases

**Better entity recognition (in progress):**
- Advanced medical NER models
- Better rare disease recognition
- Novel therapy identification

**Clinical decision support (future):**
- Real-time EHR integration
- Drug interaction alerts
- Personalized recommendations based on genetics

**Visualization (planned):**
- Interactive knowledge graph views
- Timeline showing evidence evolution
- Relationship strength maps

## Questions & Answers

**Q: How current is the information?**
A: Updated as new papers added to PubMed Central. Typical lag: few weeks to months depending on ingestion schedule.

**Q: What if I find an error?**
A: The system is only as good as source papers. If papers have errors, or extraction makes mistakes, errors can propagate. Always verify critical findings by reviewing sources.

**Q: Can I trust this for patient care decisions?**
A: Use it like any clinical decision support tool: one input to decision-making, not the only input. Consider individual patient factors, your judgment, and current guidelines.

**Q: How is this different from asking Claude/ChatGPT directly?**
A: This MCP server adds systematic literature reasoning that Claude alone doesn't have. Claude can hallucinate; this tool links every claim to actual papers with paragraph-level citations.

**Q: What about cost?**
A: For individual clinicians: Free during beta, then ~$50-100/month subscription. For institutions: Contact for enterprise pricing (typically much less than traditional clinical decision support systems).

**Q: Can I use this for research/publications?**
A: Yes! Many researchers use it for literature synthesis, systematic reviews, and identifying research gaps. Always verify sources before citing in publications.

## About This Project

This system was built to solve a real problem: a family member spent 18 months getting diagnosed because connections between symptoms existed in literature but were scattered across papers no single doctor had time to read.

The goal is to give every clinician the equivalent of a research team working 24/7—because patients deserve doctors with the best available evidence at their fingertips.

---

## Technical Appendix (Optional)

**For those who want technical details:**

**Data source:** PubMed Central research papers (JATS XML format)

**Processing pipeline:**
1. Entity extraction: Diseases, genes, drugs, proteins (medical NLP)
2. Relationship detection: "Drug X treats Disease Y"
3. Standardization: Maps to UMLS, MeSH, HGNC, RxNorm

**Storage:**
- Vector database (Amazon OpenSearch): Semantic search
- Knowledge graph (Amazon Neptune): Structured relationships
- AI orchestration (Claude via AWS Bedrock): Query understanding

**Why this architecture:**
- Vector search finds relevant papers even with different terminology
- Graph queries find exact entity relationships with evidence
- Combining both gives comprehensive, precise results

**For implementation details:** See [README.md](README.md) or [TECH_CHAT.md](TECH_CHAT.md)
