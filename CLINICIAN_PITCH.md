# Deep Literature Reasoning for Complex Cases

## You Already Use AI Assistants

Maybe you use **UpToDate** for clinical summaries. **Claude or ChatGPT** for quick questions. **PubMed** for literature searches.

These tools excel at **straightforward questions**. But when you're stuck on a complex diagnostic puzzle—symptoms that don't fit textbooks, multi-system presentations, rare conditions—you still end up:

- Reading dozens of papers manually
- Trying to connect evidence scattered across different studies
- Hoping you didn't miss a critical connection

**This tool fills that gap.**

## What It Does Differently

This is an MCP server that adds **deep literature reasoning** to AI assistants you already use:

**Multi-hop reasoning across papers**
- Connect Gene X → Protein Y → Pathway Z → Drug target across 4 different studies
- Follow evidence chains that no single paper describes

**Automatic contradiction detection**
- "Paper A (2023, n=500) shows benefit BUT Paper B (2024, n=1200) found no effect"
- Don't discover conflicts after you've made a recommendation

**Diagnostic chain following**
- Trace symptom → rare condition → cited treatment studies
- The kind of detective work that cracked your toughest cases

**Paragraph-level provenance**
- "PMC123456, Results section, paragraph 4" (not just "according to this paper")
- Verify claims before you trust them

## A Real Example

**Clinical scenario:** 28-year-old woman with progressive muscle weakness + cardiomyopathy + mild cognitive impairment + elevated lactate + severe post-exercise fatigue.

Standard workup negative. Each finding has dozens of causes.

**Your question to your AI assistant:**
*"What conditions cause muscle weakness + cardiomyopathy + cognitive decline + elevated lactate + exercise intolerance?"*

**Your AI assistant (using this MCP server) returns in 8 seconds:**

```
Primary Diagnosis: Mitochondrial Disease (MELAS, CPEO, Kearns-Sayre)
Confidence: High (0.83)

Key Evidence:
- All symptoms explained by mitochondrial dysfunction
- Elevated lactate is hallmark finding (85% of cases)
- Exercise intolerance due to impaired oxidative phosphorylation
- Age and symptom pattern consistent with late-onset presentation

Evidence from 12 studies:
- Hirano et al. (2019, n=286): "Mitochondrial diseases: Clinical features..."
  PMC6234567, Results section, paragraph 3
- Gorman et al. (2016, n=1,504): "Mitochondrial diseases in adults..."
  PMC5678901, Discussion section, paragraph 7

Contradictory evidence flagged:
- None significant (consensus diagnosis)

Recommended workup:
- Lactate/pyruvate ratio
- Muscle biopsy with electron microscopy
- Mitochondrial DNA sequencing
- Consider: cardiac MRI, neuropsychological testing
```

This is the case that could take **hours of searching** PubMed and reading papers. The MCP server does it **instantly**, with **sources you can verify**.

## How It Works with Your Existing Tools

**Install once:**
```bash
uvx pubmed-graph-rag
```

**Works everywhere:**
- Claude Desktop
- Any MCP-compatible AI assistant
- Future medical AI platforms

**Seamless:**
- You ask questions the same way you always do
- Your AI assistant calls this MCP server automatically when needed
- Results appear inline with provenance and contradictions

## What Makes It Trustworthy

**Every fact is sourced:** Unlike AI that hallucinates, every claim links to actual papers, sections, and paragraphs.

**Evidence strength scores:**
- Study quality (RCTs > case reports)
- Sample sizes
- Number of supporting papers
- Contradictions flagged (if papers disagree, you see both)

**Tracks evidence evolution:** See how understanding changed from 2010 → 2024 trials.

## What It Doesn't Replace

- **UpToDate** for standard clinical summaries → Still use it
- **Your clinical judgment** for patient-specific decisions → Always needed
- **PubMed** for comprehensive literature searches → Complement, don't replace
- **Your EHR** for documentation → This is decision support only

## Who This Helps

**Primary care:** Complex multi-system presentations that don't fit patterns

**Specialists:** Rare conditions within your specialty that you see once every few years

**Academic medicine:** Literature synthesis for grand rounds, teaching, research

**Precision oncology:** Connecting genetic findings to treatment options across trials

## Why This Matters Now

Someone close to me spent **18 months getting diagnosed** with an autoimmune condition. Her doctors knew something was wrong, but symptoms didn't fit textbooks. Each specialist searched different databases, read different papers. The connections were there in literature—scattered across studies no single doctor had time to read.

**This system does that detective work in seconds.**

Medical knowledge doubles every 73 days. No human can keep up. But your AI assistant can—if it has the right tools.

## Getting Started

**Individual clinicians:**
```bash
# Install the MCP server
uvx pubmed-graph-rag

# Add to Claude Desktop config
# (One-time setup, automatic after that)
```

**Healthcare organizations:**
Deploy within your institution:
- HIPAA compliant
- Integrate with EHR systems
- Customize for your specialty
- Add institutional guidelines

Contact IT about a pilot.

## Use Cases Beyond Diagnosis

**Precision oncology:** *"What drugs target the PI3K pathway in treatment-resistant DLBCL?"*

**Drug safety:** *"What medications are contraindicated in long QT syndrome?"* (Including rare interactions from case reports)

**Research synthesis:** *"Show me contradicting evidence about biologics in Crohn's disease"* (Maps field evolution)

**Genetic counseling:** *"What's the penetrance of Lynch syndrome mutations by age?"*

## Try It

Install the MCP server and try real cases. If it doesn't save you time or catch something you would have missed, uninstall it. No commitment.

**Built to give every clinician the equivalent of a research team working 24/7—because patients deserve doctors with the best evidence at their fingertips.**

---

**Questions?** See [CLINICIAN_README.md](CLINICIAN_README.md) for detailed documentation.

**Technical details?** See [README.md](README.md) or [TECH_CHAT.md](TECH_CHAT.md).
