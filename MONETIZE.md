# Business Strategy & Go-to-Market

## Why I'm Building This

Someone close to me spent **18 months getting diagnosed** with an autoimmune condition. Her doctors knew something was wrong, but her symptoms didn't fit textbook presentations. Each specialist searched different databases, read different papers. The connections were there in the literature—scattered across dozens of studies no single doctor had time to read.

I'm a **30-year software engineer** who just lost my job. I have **12 weeks of savings** to validate this idea before I need income again. That constraint is forcing real validation, not endless planning.

**I'm building this whether investors fund it or not.** With capital, I move faster. Without it, I bootstrap with consulting income and slower iteration.

## What's Actually Built (Not Just Planned)

**Working now:**
- JATS XML parser for PubMed Central (processes structured medical papers)
- OpenSearch integration with vector + keyword search
- AWS Bedrock embeddings (Titan V2)
- Entity extraction pipeline
- Python client library
- Docker development environment
- Local testing on 100+ papers

**Not built yet:**
- MCP server wrapper (~200 lines, 1-2 weeks)
- Multi-hop graph traversal (algorithms designed, not implemented)
- Contradiction detection (proof of concept only)
- Production deployment

**My 12-week constraint:** Validate one revenue channel or admit this doesn't work and get a job.

## What I Need to Learn (Customer Discovery Gaps)

**Honest assessment - I haven't validated product-market fit yet:**

✅ **What I know:**
- Technical feasibility: The backend works on test data
- Personal pain point: I watched this problem nearly kill someone
- Ecosystem gap: 10+ basic PubMed MCP servers exist, none do graph RAG

❌ **What I don't know (critical gaps):**
- Will doctors actually pay $50-100/month for this?
- Would Glass Health pay $5K/month or just build it themselves?
- Is pharma research a better wedge than clinical use?
- What's the real sales cycle for platform partnerships?

**Customer conversations so far:** Zero. This is the first thing I need to fix.

**My validation plan (next 4 weeks):**
1. Talk to 20 physicians (starting with my partner's doctor who solved the case)
2. Reach out to Glass Health founders via YC network
3. Contact 5 pharma companies doing systematic reviews
4. Ask: "Would you pay for this? What's missing? What would make it a must-have?"

## Three Possible Revenue Channels (Picking ONE)

I'm not "layering all three" - that's a recipe for failure. I need to pick the channel with shortest validation cycle.

### Option A: Platform Partnerships (Glass Health, UpToDate)

**The pitch:** "We're infrastructure. You integrate once via MCP, we handle the hard backend."

**Why they might buy:**
- Differentiation vs competitors (they all have similar keyword search)
- Faster than building in-house (we have 6 months head start)
- We handle PubMed ingestion, updates, infrastructure

**Why they might NOT buy:**
- Glass Health is 3 years old, well-funded, can build this themselves
- UpToDate has 30 years of moat, why do they need us?
- Technical integration risk (even "just MCP" needs trust)

**Sales cycle estimate:** 6-9 months (demos, pilots, legal, integration)

**Validation test (4 weeks):** Get Glass Health to take a demo call. If they say "interesting but not now," this channel is dead.

### Option B: Direct to Doctors (MCP Marketplace)

**The pitch:** "Install once, works with any AI assistant you use."

**Why they might buy:**
- Already paying for UpToDate ($500-1000/year)
- Solves real pain (complex diagnostic cases)
- No switching costs

**Why they might NOT buy:**
- Doctors don't control budgets (institutions do)
- "Another subscription" fatigue
- Most cases aren't complex enough to justify cost

**Validation test (4 weeks):** Get 10 doctors to try beta free. See if they'd pay $50/month after 30 days.

### Option C: Pharma Research Teams (Contract Revenue)

**The pitch:** "We automate systematic literature reviews that cost you $50K+ per drug."

**Why they might buy:**
- Clear ROI (manual systematic reviews are expensive)
- Budget exists (R&D departments spend millions)
- Fewer customers needed ($100K contracts vs $50/month subscriptions)

**Why they might NOT buy:**
- They already have solutions (Elsevier, Ovid)
- Regulatory requirements for data provenance
- Long sales cycles (12-18 months)

**Validation test (8 weeks):** Talk to research teams at 5 pharma companies. Ask what they currently pay for systematic reviews.

## My Pick: Option B (Direct to Doctors) - Here's Why

**Shortest validation cycle:**
- Can test in 4 weeks with 10 beta users
- If it doesn't work, pivot to pharma or platforms
- No long sales cycles blocking feedback

**Leverages what I have:**
- Working backend
- MCP wrapper is 1-2 weeks of work
- Can ship beta in 3 weeks

**Clear fail-fast criteria:**
- If 0 out of 10 doctors would pay → Kill it or pivot
- If 5+ out of 10 would pay → Double down
- If 2-4 out of 10 would pay → Refine positioning

**My 12-week plan:**
- Weeks 1-2: Build MCP server wrapper
- Weeks 3-4: Get 10 beta doctors (starting with my partner's doctor)
- Weeks 5-8: Iterate based on feedback
- Weeks 9-12: Either (a) converting beta to paid, or (b) pivoting to platform/pharma

## Technical Moat: Why Can't Others Just Build This?

**Honest answer:** They can. This isn't a 10-year moat.

**But we have 6-12 month head start because:**

1. **JATS XML parsing is harder than it looks**
   - PubMed Central has inconsistent XML schemas
   - Entity extraction from medical text is brittle
   - We've debugged this for 100+ papers already

2. **Graph RAG + medical NLP combination**
   - Most teams do one or the other, not both
   - Getting OpenSearch + graph traversal + entity linking to work together took 3 months
   - Medical terminology normalization (UMLS, MeSH, RxNorm) is tedious

3. **First-mover in MCP ecosystem**
   - MCP just launched (2024)
   - We're first medical graph RAG MCP server
   - Network effects if we get early adopters

**What happens when Glass Health builds this?** They will, eventually. Our advantage is we're focused on this ONE problem. They're building a full clinical platform. We can be better at deep literature reasoning because it's all we do.

**Defensibility comes from:**
- Corpus size (more papers ingested = better results)
- User feedback loops (what queries work/fail)
- Platform partnerships (if we integrate with Glass Health, they're less likely to compete)

**This is a feature, not a company - unless** we execute flawlessly on ONE channel and build distribution faster than platforms can copy us.

## Realistic Validation Milestones (Not Hockey Stick Projections)

### Months 1-3: Can We Get 10 Paying Customers?

**Goal:** Validate doctors will pay

**Spend:** $0 (living on savings, AWS free tier for testing)

**Milestones:**
- Ship MCP server wrapper (week 2)
- 10 beta doctors using it (week 4)
- 5+ say they'd pay $50/month (week 8)
- Convert 5 to paid pilot (week 12)

**Success criteria:** $250/month MRR by week 12
**Failure criteria:** <2 doctors willing to pay

**If success:** Raise $150K to hire sales-focused co-founder, scale to 100 doctors
**If failure:** Pivot to pharma contracts or get a job

### Months 4-6: Can We Scale to $2K MRR?

**Assuming Month 3 success (5 paying doctors):**

**Goal:** 40 paying doctors @ $50/month = $2K MRR

**Spend:** $5K (AWS costs for production deployment)

**Milestones:**
- Deploy to production AWS (month 4)
- Launch on MCP marketplace when available (month 5)
- Content marketing (case studies from beta doctors)
- Referrals from existing users

**Success criteria:** $2K MRR + <20% monthly churn
**Failure criteria:** High churn (>30%) or no organic growth

### Months 7-12: Can We Get to $10K MRR?

**Assuming Month 6 success ($2K MRR):**

**Goal:** 200 paying doctors @ $50/month = $10K MRR

**At this point, consider:**
- Raising seed round ($300-500K) to hire
- Platform partnership (use traction to negotiate)
- Institutional sales (sell to hospital systems)

**But only if organic growth + low churn prove product-market fit**

## What I'm Actually Asking For

### From Investors (If Interested)

**NOT asking for $500K seed round yet.** I haven't validated anything.

**Asking for angel round: $50-100K**

**Use of funds:**
- 6 months runway for me (covers savings gap)
- AWS production costs ($5-10K)
- If validation works, hire part-time BD/sales help

**Milestones by end of runway:**
- 50+ paying doctors at $50/month = $2.5K MRR
- <20% monthly churn
- Clear path to $10K MRR

**What you get:**
- If it works: First money in, conversion to seed round at better terms
- If it doesn't: Honest "this didn't work" admission by month 6

### From Co-Founder Candidates

**NOT leading with equity split.** That's backwards.

**What I've built:**
- 6 months of technical work (JATS parser, OpenSearch, embeddings)
- Working backend that processes medical papers
- Proof of concept on 100+ papers

**What I need:**
- Someone who can talk to doctors and close deals
- Healthcare sales experience (selling to physicians or hospital systems)
- Comfortable with "validate fast or fail fast" approach

**The conversation:**
1. Show you the working demo
2. Discuss customer discovery plan (20 doctors in 4 weeks)
3. If you believe in it, we talk equity (20-40% range based on contribution)
4. If you don't, no hard feelings - I'd rather find out now

**12-week constraint is a feature:** We'll know if this works quickly. No years of "maybe."

## Why This Might Actually Work

**Not because of TAM or projections.** Those are made-up numbers.

**Because:**

1. **Real problem:** I watched someone nearly die because doctors couldn't connect evidence
2. **Working code:** I have 6 months of technical infrastructure built
3. **Forced validation:** 12-week constraint means no hiding from reality
4. **Ecosystem timing:** MCP just launched, we're first medical graph RAG server
5. **Realistic moat:** Not 10 years, but 6-12 months if we execute fast

## Why This Might Fail

**Honest risks:**

1. **Doctors won't pay:** Institutions control budgets, individual adoption is hard
2. **Platforms build it themselves:** Glass Health has resources to copy this
3. **Sales cycle too long:** Even "just an MCP server" needs trust and integration
4. **Churn is high:** Solves problem for 5% of cases, not worth $50/month
5. **I can't sell:** I'm an engineer, not a salesperson - need co-founder fast

## Next Steps

**This week:**
1. Ship MCP server wrapper (in progress)
2. Set up 10 customer discovery calls (starting with my partner's doctor)
3. Create demo video (3 minutes showing complex query → multi-hop answer)

**Week 2:**
1. Talk to 20 physicians
2. Ask: "Would you pay $50/month for this? Why or why not?"
3. Document every objection and feature request

**Week 4:**
1. Pivot if feedback is bad
2. Double down if feedback is good
3. Raise angel round or find co-founder if validation works

**I'm building this regardless.** The question is whether it's venture-backable or a consulting side project.

---

**Contact:** [Your contact information]

**What I'd love from you:**

- **Investors:** Advice on customer discovery, even if not investing yet
- **Co-founders:** Coffee to see the demo and discuss validation plan
- **Doctors:** 20 minutes to tell me why this would/wouldn't help you
- **Platform founders:** Honest feedback on whether you'd integrate vs build

**Links:**
- GitHub: https://github.com/wware/med-graph-rag
- Technical docs: README.md, TECH_CHAT.md
- Clinician pitch: CLINICIAN_PITCH.md
