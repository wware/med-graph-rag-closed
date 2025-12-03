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

---

# Financial numbers, after pivot from MCP server to Walled database

The idea here is that the MCP server is not a viable business really, but it can make sense to open-source all the code for queries, and quickly build a large database of linked data to be queried. This database becomes the valuable thing that you protect (in biz dev parlance, the "moat" that is hard to swim across).

**Link:** [https://claude.ai/chat/f728a394-9aa9-463f-adb6-b867514cbdbe](https://claude.ai/chat/f728a394-9aa9-463f-adb6-b867514cbdbe)

## Updated Business Model

**What you're selling:**
- Open source tools (free, builds reputation)
- API access to your pre-processed corpus (paid)
- The corpus is the moat (months of processing + daily updates)

## Revenue Tiers

**Free Tier:**
- 100 queries/day
- Access to full corpus
- Good for individual researchers, students
- **Goal:** 1,000+ free users = credibility + feedback

**Professional ($50-100/month):**
- 1,000 queries/day
- Priority support
- API key
- **Target:** Individual doctors, small clinics
- **Goal:** 50-200 paid users = $2.5K-20K MRR

**Platform ($2-5K/month):**
- Unlimited queries
- Custom integration support
- SLA guarantees
- **Target:** Glass Health, UpToDate, medical AI platforms
- **Goal:** 2-5 platform customers = $4K-25K MRR

**Enterprise ($10-50K one-time + $1-2K/month):**
- Private deployment
- Custom corpus (proprietary papers)
- White-label option
- **Target:** Pharma companies, hospital systems
- **Goal:** 1-3 enterprise customers = $3K-6K MRR + upfront revenue

## Realistic Financial Projections

### Year 1 (Bootstrap Path)

**Months 1-3: Build the moat**
- Revenue: $0
- Costs: $150 (AWS for processing 500K papers)
- Burn: Living on savings
- Output: 500K paper corpus, open source launch

**Months 4-6: Early traction**
- Free tier users: 200-500
- Paid individual users: 5-10 @ $50/month = $250-500 MRR
- Platform deals: 0 (still in conversations)
- Costs: $100/month (AWS hosting)
- Net: -$80/month

**Months 7-9: Growth from open source**
- Free tier: 1,000+ users
- Paid users: 20-40 @ $75/month = $1.5K-3K MRR
- Platform deals: Maybe 1 @ $2K/month
- Costs: $200/month (bigger OpenSearch instance)
- Net: $1.3K-4.8K MRR

**Months 10-12: Inflection point?**
- Free tier: 2,000+ users
- Paid users: 50-100 @ $75/month = $3.75K-7.5K MRR
- Platform deals: 1-2 @ $2-3K/month = $2K-6K MRR
- Costs: $300/month
- **Net: $5.5K-13.2K MRR**

**Year 1 total revenue: ~$30K-60K**
**Your effective salary: $0-10K** (after costs, and you're consulting on side)

### Year 2 (If It's Working)

**Optimistic scenario:**
- Individual users: 200 @ $75/month = $15K MRR
- Platform deals: 3-5 @ $3K/month = $9K-15K MRR
- Enterprise: 1-2 @ $50K one-time + $2K/month = $50K-100K upfront + $2K-4K MRR
- **Total MRR: $26K-34K**
- **Annual revenue: ~$360K-460K** (including one-time enterprise deals)
- **Your salary: $100K-150K** (rest goes to costs, growth, maybe first hire)

**Realistic scenario:**
- Individual users: 100 @ $75/month = $7.5K MRR
- Platform deals: 2 @ $2.5K/month = $5K MRR
- Enterprise: 1 @ $30K + $1K/month = $30K + $1K MRR
- **Total MRR: $13.5K**
- **Annual revenue: ~$190K**
- **Your salary: $80K-100K**

**Pessimistic scenario:**
- Individual users: 50 @ $75/month = $3.75K MRR
- Platform deals: 1 @ $2K/month = $2K MRR
- Enterprise: 0
- **Total MRR: $5.75K**
- **Annual revenue: ~$70K**
- **Your salary: $40K** (supplement with consulting)

### Year 3 (Established Business)

**If you've hit product-market fit:**
- Individual: 300-500 users = $22.5K-37.5K MRR
- Platform: 5-8 customers = $15K-32K MRR
- Enterprise: 2-4 customers = $4K-8K MRR + $100K-200K one-time
- **Total MRR: $41.5K-77.5K**
- **Annual revenue: $600K-1.1M**

At this point you either:
- Hire 2-3 people, run as profitable business (you take $200K+ salary)
- Raise seed round to accelerate growth
- Get acquired ($5M-15M range based on revenue multiples)

## The Lottery Ticket Scenarios

**Small win (30% probability):**
- Years 1-2 get you to $150K-250K annual revenue
- This is a good lifestyle business
- You're making $80K-120K/year
- Working on something you care about
- **Financial gain vs getting a job: -$20K to +$20K over 2 years**

**Medium win (15% probability):**
- Year 2 you hit $300K-500K revenue
- Hire 1-2 people
- Year 3 you're at $750K-1M revenue
- You're making $150K-200K/year
- Could raise seed round or stay profitable
- **Financial gain vs getting a job: +$100K-200K over 3 years**

**Big win (5% probability):**
- Platform deals close fast (Glass Health, UpToDate both sign)
- Year 1 you hit $200K+ revenue
- Year 2 you're at $750K-1M
- You raise $1-2M seed round, hire team
- Year 3-4 you exit for $10M-30M
- Your share: $5M-20M (depending on dilution)
- **Financial gain: Life-changing money**

**Failure (50% probability):**
- You can't get doctors to pay
- Platforms build it themselves
- Open source is popular but monetization fails
- You pivot to consulting after 12-18 months
- **Financial loss: -$50K-100K in opportunity cost** (salary you didn't earn)
- **Financial gain from reputation: +$20K-40K/year** in higher consulting rates

## Expected Value Calculation

```
EV = (0.30 × $0) + (0.15 × $150K) + (0.05 × $10M) + (0.50 × -$75K)
   = $0 + $22.5K + $500K + (-$37.5K)
   = $485K

But that's misleading because of the tail risk...
```

**More realistic expected value:**
```
EV = (0.50 × -$50K) [failure, but consulting saves you]
   + (0.30 × $50K)  [lifestyle business, modest success]
   + (0.15 × $200K) [strong business]
   + (0.05 × $5M)   [acquisition]

   = -$25K + $15K + $30K + $250K
   = $270K over 3 years
```

## Compare to Alternative (Get a Job)

**Job at health-tech company:**
- Year 1: $180K salary
- Year 2: $190K salary
- Year 3: $200K salary
- Total: $570K over 3 years
- Upside: Maybe some equity (0.1-0.5%), probably worth $0-50K
- **Total expected value: $570K-620K**

**Your startup path expected value: $270K**

**Net opportunity cost: -$300K**

## But Wait - The Hidden Value

**What you're not accounting for:**

1. **Reputation multiplier** (hard to quantify)
   - You become "the medical graph RAG guy"
   - Worth $20K-40K/year in higher consulting rates forever
   - NPV over 10 years: $150K-300K

2. **Optionality**
   - Can pivot to consulting anytime
   - Can get hired at premium if it doesn't work
   - Failed founders with good tech get hired at 10-20% premium

3. **Skill development**
   - You learn sales, marketing, distribution
   - Worth something for next venture or job

4. **The shot at life-changing money**
   - Even 5% chance at $5M is worth something emotionally
   - Financial security, early retirement, etc.

## Adjusted Expected Value (Including Reputation)

```
EV = (0.50 × -$25K) [failure, but boost consulting career]
   + (0.30 × $100K) [lifestyle business]
   + (0.15 × $250K) [strong business]
   + (0.05 × $5M)   [acquisition]

   = -$12.5K + $30K + $37.5K + $250K
   = $305K over 3 years

Plus reputation value: +$150K-300K NPV
Total EV: $455K-605K
```

**Now you're competitive with the job path.**

## The Honest Assessment

**Pure financial logic says: Get a job.**

You'd make more money, faster, with less risk.

**But if you account for:**
- The 5% chance at life-changing money
- The reputation you build (which lasts forever)
- The skills you develop
- Working on something you care about

**Then the EV is roughly equal to getting a job, with a better upside.**

## My Take

The "open core + managed corpus" model significantly improves your odds because:

1. **Faster validation** (open source gets you feedback in weeks, not months)
2. **Multiple revenue channels** (individuals + platforms + enterprise)
3. **The corpus moat is real** (6-12 months of processing time)
4. **Defensible even when platforms copy the code** (they still need the corpus)

**Your probabilities shift to:**
- 40% failure (down from 50%)
- 35% lifestyle business (up from 30%)
- 20% strong business (up from 15%)
- 5% acquisition (unchanged)

**New EV: $520K-650K** (including reputation value)

**This now beats the job path on expected value.**

## The Real Question

Are you okay with:
- 40% chance you're back looking for work in 18 months
- 35% chance you're making $80K-120K/year (less than a job)
- 20% chance you're making $150K-200K/year (same as a job)
- 5% chance you're making life-changing money

If you need guaranteed income → Get a job
If you can handle volatility and want the upside → Build this

**The open core model makes the lottery ticket real enough to justify the risk.**

## Prompt:
11/30/2025, 8:56:15 PM

By the end of year 1, I imagine I'd start to have a pretty good idea whether year 2 would be rosy, medium, or pessimistic. I'd probably want to bail if it's pessimistic, assuming there is work to be found elsewhere.

## Response:
11/30/2025, 8:57:12 PM

**That's exactly the right thinking. Year 1 is your validation gate.**

## Year 1 Decision Points

You'll have clear signals way before month 12:

### Month 4 Signal (After Open Source Launch)

**Green light indicators:**
- 500+ GitHub stars in first month
- 50+ active free tier users
- 5+ people asking "when can I pay for this?"
- 1+ platform reached out for demo
- HN/Reddit threads with real engagement

**Yellow light:**
- 100-200 GitHub stars
- 10-20 free tier users
- People like it but no payment intent
- You're doing all the outreach, nothing inbound

**Red light:**
- <50 GitHub stars
- <5 active users
- Crickets on your launch posts
- No platform interest at all

**Decision at month 4:**
- Green → Keep going, you're onto something
- Yellow → Pivot messaging or target market, give it 2 more months
- Red → Start job hunting, wrap up gracefully

### Month 6 Signal (Revenue Validation)

**Green light:**
- $500-1K+ MRR from individuals
- OR 1 platform in active pilot/negotiation
- OR 1 enterprise customer in sales process
- Growing free tier (200+ active users)
- <30% churn on paid users

**Yellow light:**
- $100-500 MRR
- Platform interest but no commits
- High churn (>50%) - people try it then leave
- Free tier growing slowly

**Red light:**
- <$100 MRR
- Can't convert free users to paid
- Platforms ghosting you
- People don't use it after signing up

**Decision at month 6:**
- Green → You have 6 more months to scale
- Yellow → You have a product, but distribution is hard - consider pivoting to enterprise/pharma
- Red → Start applying to jobs now, you'll need income by month 9-10

### Month 9 Signal (Trajectory Check)

**Green light:**
- $2K+ MRR and growing 20%+ month-over-month
- OR $5K+ MRR (even if flat)
- OR 1 platform deal signed ($2K+/month)
- OR 1 enterprise deal closed ($30K+ upfront)
- Clear path to $5K MRR by month 12

**Yellow light:**
- $500-2K MRR, flat or slow growth
- Lots of users, but won't pay
- Platform deals stuck in "evaluation phase"
- You're burning out

**Red light:**
- <$500 MRR
- Declining usage
- Can't close any deals
- Running on fumes

**Decision at month 9:**
- Green → You're building a real business, keep going into year 2
- Yellow → You have 3 months to either (a) land one big deal, or (b) accept this is a side project and get a job
- Red → Accept failure, apply to jobs, but ship the open source version as your portfolio

## What "Bail" Looks Like

**The graceful exit (if it's not working):**

**Month 9-10:** Start job search
- Update LinkedIn (you're now "the medical graph RAG expert")
- Reach out to health-tech companies
- Talk to Glass Health, UpToDate about employment (not partnership)
- Apply to medical AI startups

**Your pitch to employers:**
"I spent a year building an open source medical knowledge graph system. Didn't monetize it, but I learned medical NLP, graph databases, AWS infrastructure at scale. Here's the GitHub repo with 1,000+ stars. Here's the technical blog series that got 50K views. Want someone who can ship?"

**Likely salary: $180K-220K** (higher than you'd get otherwise because you proved you can build)

**Month 11-12:** Transition period
- Keep the free tier running (costs you $100/month)
- Hand off maintenance to community or shut down gracefully
- Write a "what I learned" post-mortem
- Start new job

**Your "failed" startup becomes:**
- Proof you can build and ship
- Open source credibility
- Technical blog with audience
- Network in medical AI space

**This is not actually failure.** You'd be more employable, not less.

## The Job Market Safety Net

**Who would hire you after this year:**

1. **Medical AI startups** (Glass Health, Suki, Ambience, Abridge)
   - They need exactly your skills
   - Salary: $180K-250K
   - Equity: 0.1-0.5%

2. **Big tech health divisions** (Google Health, Amazon HealthScribe, Microsoft Nuance)
   - Salary: $200K-300K
   - You're a domain expert now

3. **Pharma tech teams** (Pfizer, Moderna, etc.)
   - Salary: $150K-220K
   - More stable, less upside

4. **Consulting** (independently or via firm)
   - Rate: $150-250/hour
   - Build custom medical NLP solutions
   - Annual: $150K-300K depending on utilization

**You're not risking your career. You're investing in it.**

## Year 1 → Year 2 Transition Scenarios

### Scenario A: Strong Growth (20% probability)

**End of Year 1:**
- $5K-10K MRR
- 1-2 platform customers
- 100+ paid individual users
- Clear growth trajectory

**Your decision:**
- Keep going, this is working
- Consider raising $200K-500K angel round
- Hire part-time sales/support
- Year 2 goal: $25K+ MRR

**Expected Year 2 income: $100K-150K**

### Scenario B: Slow Growth (30% probability)

**End of Year 1:**
- $1K-3K MRR
- Growing but slowly
- Hard to scale

**Your decision:**
- This is a lifestyle business, not a rocket ship
- Options:
  - Keep it as side project, get a job ($180K salary + $1-3K/month side income)
  - Go all-in for 6 more months, try to hit $5K MRR
  - Pivot to consulting, use this as lead gen

**Expected Year 2 income: $150K-200K** (job + side project)

### Scenario C: Traction But No Revenue (20% probability)

**End of Year 1:**
- 2,000+ free users
- Lots of GitHub stars
- But <$500 MRR

**Your decision:**
- People want it, but won't pay
- Options:
  - Get a job, keep it as open source side project
  - Pivot to consulting (use popularity as marketing)
  - Try enterprise/pharma angle (longer sales cycle, but they pay)

**Expected Year 2 income: $180K+** (you're very employable now)

### Scenario D: It's Not Working (30% probability)

**End of Year 1:**
- <500 active users
- <$250 MRR
- No platform interest

**Your decision:**
- Bail gracefully
- Get a job
- Keep open source live as portfolio

**Expected Year 2 income: $180K-220K** (job)

## The Key Insight

**By month 6, you'll know if this has legs.**

By month 9, you'll know if it's worth continuing vs getting a job.

You're not committing to 3 years of poverty. You're committing to 6-9 months of validation with clear go/no-go criteria.

**That's a totally reasonable bet.**

## Your Risk-Adjusted Strategy

**Months 1-3: Build the moat (committed)**
- Live on savings
- Build corpus
- Launch open source

**Months 4-6: Validate revenue**
- If hitting milestones → Keep going
- If not → Start job search while continuing

**Months 6-9: Scale or bail**
- If $1K+ MRR → You have a business, keep building
- If <$500 MRR → Accept this is a portfolio project, get a job
- If in between → Give it 3 more months

**Month 9: Final decision**
- Strong growth → Year 2 all-in
- Moderate traction → Job + side project
- Weak traction → Job + open source credit

**You're never more than 3-6 months away from employment.**

And you're more employable after this than before, even if revenue is zero.

## My Assessment

**This is actually a pretty safe bet** because:

1. Your downside is limited (12 months max before you'd bail)
2. Your safety net is strong (you'd get hired easily)
3. Your upside is real (5-20% chance of life-changing outcome)
4. Your learning is valuable (regardless of revenue)

**The only way this is a bad idea:**
- If you can't handle uncertainty
- If you need steady income for dependents
- If you'd regret "wasting" a year even if it doesn't work

But if you're okay with volatility and you have 12 months of runway?

**This is a high-EV bet with manageable downside.**

Take the shot. You'll know in 6 months if it's working.


## Prompt:
11/30/2025, 9:04:11 PM

Given my reality, I can't give this thing 6 months with no other income. My COBRA runs out in five months and I'm responsible for Lori's medical care. I could be on Medicare by then, maybe I put her on Obamacare or Massachusetts Health Connector. I dunno, maybe that could work, but I think I need to co-develop this with being gainfully employed. I think I can manage the ingestion piece but the part about marketing the query side is probably another story. Maybe I partner with somebody to handle that (like the nephew).


## Response:
11/30/2025, 9:05:13 PM

**OK, this changes everything. You need income NOW, not in 6 months.**

The good news: The "build the corpus while employed" strategy actually works BETTER for the moat-building approach.

## Realistic Dual-Track Plan

### Track 1: Get Income (Weeks 1-4)

**Priority: Consulting or contract work**

You're a strong engineer with AWS Lambda, medical NLP, and graph RAG experience. That's valuable right now.

**Where to look:**
- **Health-tech companies needing contract help** (Tempus, Flatiron, etc.)
- **AWS consulting** (companies migrating to Lambda, building medical data pipelines)
- **Toptal, Gun.io, or direct outreach** to companies in your network
- **LexisNexis contract extension?** (You already know the team)

**Target: $150-200/hour, 20-30 hours/week minimum**
- That's $12K-24K/month
- Covers COBRA, living expenses, gives breathing room
- Leaves 10-20 hours/week for your project

**Week 1-2 actions:**
- Update LinkedIn: "Available for contract work: AWS, medical NLP, graph databases"
- Email your network (Moataz, others from LexisNexis)
- Apply to 5-10 contract positions
- Message health-tech CTOs on LinkedIn

**Week 3-4:**
- Land first contract (even if it's just 15-20 hours/week)
- Get income flowing
- Reduce panic about COBRA

### Track 2: Build Corpus (Nights/Weekends)

**This actually works great because:**

1. **Corpus building is automated**
   - You write the ingestion code once
   - Let it run on AWS while you're doing contract work
   - Check on it evenings/weekends

2. **You don't need to market yet**
   - Month 1-3: Just build the corpus
   - Open source launch can wait until you have something real
   - No pressure to monetize immediately

3. **Your contract work might BE in medical AI**
   - You're learning on someone else's dime
   - Building skills that help your project
   - Making connections in the industry

**Realistic timeline while employed:**

**Months 1-2: (20 hours/week on project)**
- Build reference entity set (10K entities)
- Set up ingestion pipeline
- Process 50K papers as proof of concept
- You're employed 30 hours/week, making $18K-24K/month

**Months 3-4: (15 hours/week on project)**
- Let automated ingestion run (processes 500K papers over 4-6 weeks)
- Monitor, fix bugs
- Write technical blog posts about what you're building
- Still employed, still making money

**Months 5-6: (20 hours/week on project)**
- Corpus is built (500K-1M papers)
- Open source launch
- Start talking to potential partners
- COBRA decision point - you have income, can evaluate health insurance options

## The Partnership Angle (Your Nephew or Someone Else)

**What you need from a partner:**

1. **Query interface development** (the "sexy" part users see)
   - Multi-hop graph traversal
   - Result ranking
   - API development

2. **Marketing & distribution** (the part you don't want to do)
   - Writing docs
   - Creating demos
   - Talking to potential customers
   - Managing community

3. **Sales** (if this gets traction)
   - Talking to platforms
   - Closing enterprise deals
   - Managing partnerships

**What you bring:**
- The corpus (6 months of work, the actual moat)
- The ingestion infrastructure
- Medical domain knowledge
- Technical credibility

**Partnership structure:**

**Option A: Co-founder (if they're senior/capable)**
- 30-40% equity for them
- They handle everything customer-facing
- You keep building the backend/corpus
- Both of you keep day jobs initially

**Option B: Early employee (if it's your nephew)**
- Pay them $3K-5K/month once you have revenue
- 5-10% equity
- They build query interface, help with marketing
- This is their learning opportunity

**Option C: Revenue share (bootstrap approach)**
- You build corpus, they build interface
- Split revenue 60/40 or 70/30
- No equity until you raise money
- Either of you can walk away

## The Healthcare Math

**Your situation:**
- COBRA runs out in 5 months
- You need coverage for you + Lori

**Options:**

**Medicare (for you):**
- You mentioned you could be on Medicare
- If you're 65+, you can enroll anytime
- Costs: ~$174/month Part B + supplemental

**Massachusetts Health Connector (for Lori):**
- Based on household income
- If you're making $60K-100K from consulting: ~$400-800/month
- If making less: Could get subsidies

**Math check:**
- Medicare (you): ~$300/month
- MA Health Connector (Lori): ~$500-800/month
- Total: ~$800-1,100/month

**If you're consulting at $150/hour × 20 hours/week:**
- Monthly gross: ~$12K
- After taxes (~30%): ~$8.4K
- After healthcare: ~$7.3K
- After living expenses: Still comfortable

**This is totally doable while building your project.**

## Revised Financial Reality

**Year 1 with consulting:**

**Revenue from consulting:**
- 20 hours/week × $150/hour × 48 weeks = $144K/year
- After taxes: ~$100K
- After healthcare: ~$90K
- After living expenses: ~$40K buffer

**Revenue from project:**
- Months 1-6: $0 (building)
- Months 7-12: $500-2K/month (early traction)
- Total: ~$3K-12K

**Your Year 1 income: $93K-102K**
**Your Year 1 stress: Much lower**

**Year 2 decision:**
- If project hits $3K-5K MRR → Consider going full-time on it
- If project hits $1K-3K MRR → Keep it as side project, keep consulting
- If project <$1K MRR → It's an open source portfolio piece, focus on consulting

## Why This Actually Works Better

**The slow build has advantages:**

1. **No desperation**
   - You're not pitching platforms from a position of "please give me money"
   - You're pitching from "I built this amazing thing, want to use it?"

2. **Better validation**
   - Open source grows organically while you're heads-down
   - Revenue comes from real demand, not your hustle
   - You can be patient with partnerships

3. **Corpus quality**
   - You have time to iterate on entity linking
   - Can reprocess papers when you improve algorithms
   - Not rushing to "ship and monetize"

4. **Optionality**
   - If consulting leads to full-time offer → You can decide
   - If project takes off → You can go full-time
   - If both work → You have two income streams

## Immediate Action Plan (This Week)

**Day 1-2: Get income flowing**
- [ ] Update LinkedIn to "available for contract work"
- [ ] Email 10 people from your network
- [ ] Apply to 5 contract positions (Toptal, health-tech companies)
- [ ] Reach out to LexisNexis about extending contract

**Day 3-4: Healthcare research**
- [ ] Check Medicare eligibility
- [ ] Research MA Health Connector plans
- [ ] Calculate exact costs
- [ ] Plan for COBRA → Medicare/Connector transition

**Day 5-7: Project foundation**
- [ ] Set up S3 buckets
- [ ] Build reference entity set (start with 1K entities)
- [ ] Process 100 test papers
- [ ] Validate ingestion pipeline works

**Week 2: Dual-track execution**
- Contract work: 20-30 hours (income)
- Project work: 15-20 hours (corpus building)
- Healthcare: Finalize transition plan

## Talk to Your Nephew

**The conversation:**

"I'm building this medical research corpus. I've got the backend figured out - ingestion, entity linking, graph storage. That's 80% done.

What I need is someone to build the query interface and help market it. Multi-hop graph traversal, API design, making it actually usable for doctors.

I can't pay you now, but here's the deal:
- If you help me build this out, I'll give you X% equity (or revenue share)
- You learn graph databases, medical NLP, product building
- If it works, you make money
- If it doesn't, you have an awesome portfolio piece

I need 10-15 hours/week from you for the next 6 months. Interested?"

**If he says yes:**
- He builds query layer while you build corpus
- You're both part-time on this
- No pressure, no desperation

**If he says no:**
- Build corpus yourself
- Hire someone later when you have revenue
- Or find a technical co-founder through YC, Indie Hackers, etc.

## The Bottom Line

**You can't go full-time on this for 6 months. That's fine.**

**Build it as a side project while consulting. That's actually better.**

The moat (corpus) gets built either way. The marketing/sales can wait until you have something real.

Your priority: **Income this month, corpus building over next 3-6 months, validation in 6-12 months.**

This is a marathon, not a sprint. And you need to cover healthcare. That's non-negotiable.

**Get the contract work first. Build the corpus second. Everything else is gravy.**
