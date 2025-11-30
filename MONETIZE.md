# Business Strategy & Monetization

## Executive Summary

Medical AI assistants are here and doctors use them daily. UpToDate has 3M+ clinician users. Glass Health (YC W21) is growing fast. Over 10 basic PubMed search tools exist as MCP servers.

**The gap:** None of them do multi-hop reasoning across papers, surface contradictory evidence automatically, or trace diagnostic chains through literature.

**Our strategy:** Build the best medical literature reasoning engine as MCP server infrastructure. Sell to platforms (Glass Health, UpToDate) as backend, while also enabling direct-to-doctor subscriptions.

**The market timing:** MCP protocol just launched in 2024. We're first-mover on medical graph RAG as MCP infrastructure.

## The Value Proposition

We solve a real clinical problem: connecting evidence scattered across multiple papers for complex diagnoses.

**What existing tools do:**
- Find individual papers by keyword
- Return abstracts and citations
- Provide clinical summaries from curated databases

**What they can't do (our differentiators):**
1. **Multi-hop reasoning** - Connect Gene X → Protein Y → Pathway Z → Drug target across 4 different studies
2. **Automatic contradiction detection** - "Paper A (n=500, 2023) shows benefit BUT Paper B (n=1200, 2024) found no effect"
3. **Diagnostic chain following** - Trace symptom → rare condition → cited treatment studies
4. **Paragraph-level provenance** - "PMC123456, Results section, paragraph 4" (not just "according to this paper")

**The customer pain:** A doctor spent hours doing diagnostic detective work to get an accurate diagnosis. Our tool makes that systematic and fast, not luck-dependent.

## Revenue Models

We have three paths to revenue, optimized for different customer segments:

### Option A: B2B Platform Infrastructure ($5K-50K/month per partner)

**Target customers:** Glass Health, UpToDate, OpenEvidence, Medwise, iatroX

**Value proposition:** "We're Stripe for medical literature reasoning - you integrate once, we handle the hard backend"

**Pricing models:**
- **Per-query:** $0.10-0.50 per query (volume discounts)
- **Flat monthly:** $5K-20K for unlimited queries
- **Revenue share:** 20-30% of their subscription revenue attributed to our features

**Sales strategy:**
- Demo to Glass Health first (YC company, likely most agile)
- Show: "Your users ask X, we return multi-hop answer with contradictions flagged"
- Pitch: "Don't build this yourself - it took us 6 months and $50K"

**Why platforms will buy:**
- Differentiation vs competitors (they all have similar keyword search)
- Faster than building in-house
- We handle PubMed ingestion, updates, infrastructure
- Integration is just MCP protocol (standard, minimal dev work)

**Deal size estimates:**
- Glass Health: $10-20K/month (early adopter, smaller user base)
- UpToDate: $50K+/month (enterprise, millions of users)
- 3-5 platform deals = $100-200K/month ARR

### Option B: Direct-to-Doctor MCP Marketplace ($50-100/month per doctor)

**Target customers:** Individual physicians and small practices

**Distribution:** MCP marketplace (when it exists), Claude desktop app store, direct sales

**Value proposition:** "Works with any AI assistant you already use (Claude, future tools)"

**Installation:** One command (`uvx pubmed-graph-rag`), works immediately

**Pricing tiers:**
- **Free:** 10 queries/month (freemium funnel)
- **Professional:** $50/month, 500 queries/month
- **Practice:** $200/month, unlimited queries, 5 users

**Why doctors will pay:**
- Already paying for UpToDate ($500-1000/year)
- Our tool augments (not replaces) existing subscriptions
- Solves real pain: complex diagnostic cases
- No switching costs (integrates with their existing AI assistant)

**Challenge:** Direct doctor sales are slow (not their budget, institutional purchasing)

**Deal size estimates:**
- Year 1: 100 doctors @ $50/month = $5K/month ($60K ARR)
- Year 2: 1,000 doctors @ $50/month = $50K/month ($600K ARR)
- Year 3: 10,000 doctors @ $50/month = $500K/month ($6M ARR)

### Option C: Hybrid Model (Recommended)

**Layer the revenue streams:**

1. **Free tier** - 10 queries/month for individual doctors
   - Builds user base and word-of-mouth
   - Demonstrates value before asking for payment
   - Freemium conversion funnel

2. **Platform deals** - $5K-50K/month each
   - Primary revenue driver in Year 1-2
   - Faster sales cycle than enterprise
   - Validates product-market fit

3. **Direct subscriptions** - $50-100/month per doctor
   - Supplements platform revenue
   - Direct customer relationships and feedback
   - Higher margins than platform revenue share

4. **Enterprise** - Custom pricing for hospital systems
   - Year 2-3 opportunity
   - On-premise deployment option
   - $100K+ annual contracts

**Why hybrid works:**
- Multiple revenue streams reduce risk
- Platform deals fund growth while direct builds user base
- Enterprise opportunities emerge after platform validation

## Market Opportunity

**Total Addressable Market (TAM):**
- 1M+ physicians in US
- 3M+ physicians globally using clinical decision support
- UpToDate alone: $1B+ revenue (Wolters Kluwer doesn't break out separately)

**Serviceable Addressable Market (SAM):**
- Physicians handling complex diagnostic cases: ~300K in US
- Researchers using medical literature: ~200K globally
- Price point: $50-100/month individual, $5K-50K/month platforms

**Serviceable Obtainable Market (SOM - Year 3):**
- Platform deals: 5 platforms @ $20K/month avg = $1.2M ARR
- Direct subscriptions: 10,000 doctors @ $50/month = $6M ARR
- **Total SOM: $7.2M ARR by Year 3**

## Competitive Positioning

### vs. Basic PubMed MCP Servers (10+ exist)
- **They have:** Keyword search, abstract retrieval
- **We have:** Multi-hop reasoning, contradiction detection, diagnostic chains
- **Our advantage:** Only medical graph RAG MCP server

### vs. Clinical Platforms (Glass Health, UpToDate, OpenEvidence)
- **They have:** Large user bases, established brands, clinical summaries
- **We have:** Deep literature reasoning they can buy as infrastructure
- **Our strategy:** Partner, don't compete - we're their backend

### vs. Building In-House
- **Their challenge:** 6+ months development, ongoing maintenance
- **Our advantage:** Ready now, we handle updates and infrastructure
- **Our pitch:** "Buy vs build - integrate in 1 week vs build in 6 months"

### vs. Traditional PubMed Search
- **They have:** Free, comprehensive, doctors already use it
- **We have:** Automated reasoning, contradiction detection, saved time
- **Our positioning:** Augment, not replace - we make PubMed smarter

## Go-to-Market Strategy

### Phase 1: Platform Partnership (Months 1-6)
**Goal:** Land first 2-3 platform deals

**Tactics:**
1. **Demo video** - 3 minutes showing complex query → multi-hop answer
2. **Reach Glass Health** - YC connection, show to founders directly
3. **UpToDate pilot** - Harder to reach but biggest potential
4. **OpenEvidence** - Newer player, may be most receptive

**Success metric:** 2 platform deals signed by Month 6

### Phase 2: Direct Beta (Months 3-9)
**Goal:** 100 doctor users providing feedback

**Tactics:**
1. **Post in medical AI communities** - Twitter, Reddit, Slack groups
2. **Free beta** - No payment required, gather testimonials
3. **Partner's doctor** - Start with your PCP who understands the problem
4. **Iterate based on feedback** - Which queries matter most?

**Success metric:** 100 active users, 10 strong testimonials

### Phase 3: Scale (Months 9-18)
**Goal:** $500K ARR

**Tactics:**
1. **Platform expansion** - 3-5 deals at $10-30K/month each
2. **Paid subscriptions** - Convert beta users, acquire new
3. **Content marketing** - Case studies, blog posts, medical conferences
4. **Enterprise pilots** - 1-2 hospital system trials

**Success metric:** $500K ARR, path to $1M visible

## Financial Projections (3-Year)

### Revenue Forecast

**Year 1:**
- Platform deals: 2 @ $10K/month avg = $240K
- Direct subscriptions: 100 @ $50/month = $60K
- **Total Y1: $300K**

**Year 2:**
- Platform deals: 5 @ $20K/month avg = $1.2M
- Direct subscriptions: 1,000 @ $50/month = $600K
- Enterprise: 1 @ $100K/year = $100K
- **Total Y2: $1.9M**

**Year 3:**
- Platform deals: 8 @ $25K/month avg = $2.4M
- Direct subscriptions: 5,000 @ $50/month = $3M
- Enterprise: 3 @ $150K/year avg = $450K
- **Total Y3: $5.85M**

### Cost Structure

**Fixed costs (annual):**
- Founders: $0 (sweat equity) → $300K (Y2+)
- Engineering: $200K (1 hire Y1) → $600K (3 hires Y2) → $1M (5 hires Y3)
- Sales/BD: $150K (1 hire Y2) → $450K (3 hires Y3)
- AWS infrastructure: $50K → $150K → $300K

**Variable costs:**
- AWS Bedrock API: ~10% of revenue
- Support: ~5% of revenue

**Y1 expenses:** ~$300K (need funding or profitable side projects)
**Y2 expenses:** ~$1.2M
**Y3 expenses:** ~$2M

### Path to Profitability

- **Y1:** Need $300K funding or founders working for equity
- **Y2:** Revenue $1.9M, Expenses $1.2M = $700K profit
- **Y3:** Revenue $5.85M, Expenses $2M = $3.85M profit

**Break-even:** Month 18 (assumes Y1 funding secured)

## Investment Ask

### For Investors

**Raising:** $500K seed round

**Use of funds:**
- 12 months runway for 2 founders
- 1 senior engineer hire
- AWS infrastructure costs
- Platform demo development and sales

**Milestones by end of runway:**
- 3-5 platform partnership deals
- 1,000+ doctor users
- $500K ARR
- Path to Series A ($2M at $1.5M ARR)

**Exit opportunities:**
- Acquisition by UpToDate/Wolters Kluwer ($20-50M)
- Acquisition by Glass Health or similar ($10-30M)
- Standalone growth to $10M+ ARR, Series B+

### For Co-Founder

**Looking for:** Business/Sales co-founder

**Ideal background:**
- Healthcare sales experience (selling to hospitals, physicians, or medical software)
- Technical enough to understand the product
- Network in medical AI or clinical decision support space
- Comfortable with early-stage risk and equity compensation

**Equity:** 20-40% (negotiable based on experience and contribution)

**Responsibilities:**
- Platform partnership sales (Glass Health, UpToDate, etc.)
- Direct customer acquisition strategy
- Fundraising (if needed)
- Business operations and finance

## Why This Works

**Technical moat:** Multi-hop graph RAG over medical literature is genuinely hard. 6 months of work already done.

**Market timing:** MCP protocol just launched. First-mover advantage as medical graph RAG infrastructure.

**Real problem:** Doctors do this detective work manually today. We're making it systematic.

**Multiple paths to revenue:** Platform deals (fast), direct subscriptions (scalable), enterprise (high-value).

**Capital efficient:** Can build to $1M ARR with <$500K funding. Backend mostly built.

**Clear exits:** Strategic acquirers exist and are actively buying in this space.

## Next Steps

**For investors:** Review deck, schedule demo call, meet founding team

**For co-founder candidates:** Review technical repo, discuss equity split, align on vision

**For platform partners:** See demo, discuss integration timeline, pilot terms

**For early users:** Join beta, provide feedback, get free access

---

**Contact:** [Your contact information]

**Links:**
- GitHub: https://github.com/wware/med-graph-rag
- Demo video: [To be created]
- Technical docs: See TECH_CHAT.md and README.md
