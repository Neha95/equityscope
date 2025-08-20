
📌 Objective
To build a structured Summary Engine that delivers insight-driven yet actionable output for a retail investor analyzing a stock. The engine supports two usage tiers:
* Simple Mode: No LLM inference. Works using quantitative rules, heuristics, and pre-written logic.
* Agentic Mode: LLM-enabled single-agent system generating debate, synthesis, and natural language insights across multiple perspectives.
🚫 Plugin toggles or per-plugin settings will NOT be implemented at this stage to reduce complexity.

🧱 Feature Structure
🔺 Summary Box (Top of Screen)
* Always shown
* Gives an executive-level overview of all stock analysis across 3 lenses:
    * Valuation Insights
    * Market Signals
    * Business & Macro Fundamentals
Contains:
1. Fair Value Band (e.g., ₹212–₹240)
2. Investment Label (e.g., "Cautiously Bullish")
3. Key Factors Influencing the Label
4. Optional: What Changed (since last visit)
5. Data health warnings if any fallbacks or missing data

🔹 Simple Mode (No LLM)
🧮 Method:
Rule-based & formula-driven summaries + templated insight sentences
✅ Summary Box Output (Example):
📊 Valuation: DCF estimates fair value at ₹230. Current price is 12% below → Undervalued.
📉 Market: RSI is 27 → Oversold.
⚠️ Fundamentals: Promoter stake dropped 3% → Potential red flag.
🧠 Label: Cautiously Bullish
🔧 Rules & Triggers
Valuation Rules:
* DCF price > current price by 10–25% → "Appears moderately undervalued"
* DCF price within 5% → "Near fair value"
* DCF price < current price by >10% → "Possibly overvalued"
* If DCF not available: fallback to PE/multiple-based fair value
Technical Rules:
* RSI < 30 → "Oversold territory"
* RSI > 70 → "Overbought territory"
* MACD crossover (up) → "Momentum shift likely"
* Low volume + price rise → "Weak rally signal"
* If indicator unavailable: flag as "insufficient data"
Business Fundamentals:
* Promoter holding drop >2% QoQ → "Promoter selling — caution"
* Pledged shares >10% → "High pledge risk"
* FCF negative 3+ quarters → "Cash flow pressure"
* PE > sector avg by >30% → "Expensive vs peers"
Peer Comparison:
* Always compare to 3–5 peers from same industry (default = 5, fallback = 3 if data missing)
* Time window: Last 12 months + TTM (Trailing Twelve Months)
Earnings Rules:
* Revenue CAGR 3Y >15% + EPS CAGR 3Y >12% → "Strong growth track record"
* Negative PAT or declining EBITDA margins → "Weak earnings quality"
Sentiment Summary (limited):
* Derived from news scoring APIs or up/down trends in analyst recommendations
* E.g., >5 recent downgrades → "Analyst sentiment turning bearish"
🗂️ Summary Box Format
[Label: Cautiously Bullish]
Fair Value Range: ₹212–₹240
Key Drivers:
- Undervalued vs DCF
- RSI in oversold zone
- Promoter selling last quarter
Data Quality: Technical data partially unavailable (MACD)

🔸 Agentic Mode (LLM-enabled)
🔍 Method:
A single Financial Analyst Agent receives structured inputs and runs a composite reasoning process (valuation, market, fundamentals, sentiment, macro). Internal reasoning steps are executed within the agent using system prompts.
🧠 Summary Box Output (Example):
Financial Analyst Agent:
This stock appears moderately undervalued, with DCF and peer multiples supporting a ₹230–₹250 band. Technicals show oversold signals but volume is low. Recent promoter selling and low FCF may suggest caution.
🧠 Agent Prompt Template (Single Agent):
“Given the following structured data for stock X and its 5 peers — including valuation models, technical indicators, financial metrics, macro trends, and sentiment signals — generate a structured investment thesis:
1. Fair Value Range & Valuation Summary
2. Market Signals & Momentum Indicators
3. Business Fundamentals & Earnings Drivers
4. Macro Risks or Tailwinds
5. Final Label + Rationale (3 bullets)”
🗃️ Internal Prompt Decomposition:
* Internally breaks down analysis into valuation, technical, and fundamental segments
* Uses internal prompt chaining but within the same agent instance
* Uses retrieval context for sector adaptation (see below)

🧭 Sector-Specific Logic
🔁 Dual Contextualization:
We define separate logic for Simple and Agentic modes across key sectors.
🎯 Prioritized Sectors (Phase 1):
* BFSI (Banks, NBFCs)
* FMCG
* IT & Services
* Pharma
* Energy & Commodities
* Real Estate
🧮 Simple Mode Sector Logic:
Each sector overrides base logic with:
* Custom valuation model:
    * Excess Return Model for BFSI
    * DCF + EV/EBITDA for Pharma
    * NAV-based for Real Estate
* Trigger thresholds tailored to sector norms:
    * GNPA > 5% for Banks = red flag
    * Inventory turnover < 0.5x in Real Estate = monetization risk
    * R&D < 5% of revenue in Pharma = concern on innovation
* Sector-specific phrases:
    * "NIM compression observed" (BFSI)
    * "Regulatory bottleneck in approvals" (Pharma)
    * "Low absorption rate in Tier 2 cities" (Real Estate)
🧠 Agentic Mode Sector Adaptation:
* Prompt includes: sector name, company type, applicable KPIs, and macro dependencies
* Agent uses this to prioritize relevant fields and weighting in reasoning
📄 Sample Sector Context Snippets:
* Pharma: "Company has 8 ANDAs pending, R&D spend at 4.2%, 2 recent USFDA observations. Revenue split: 52% US, 33% domestic."
* Real Estate: "Inventory velocity at 0.4x, D/E at 1.7x, 70% bookings from Tier 2 projects."

⚠️ Fallbacks & Graceful Degradation
All fallbacks are made visible to user with clear indicators:
Scenario	Fallback	User Message
Peer data missing	Use 3 peers or sector average	"Using reduced peer set (3 stocks)" or "Fallback to sector avg"
Missing technical indicator	Hide section	"Market signals unavailable — insufficient data"
DCF data unavailable	Use PE/multiple valuation	"Fair value based on peer PE multiple"
Sentiment data missing	Hide sentiment line	"Sentiment data unavailable"
API/connection failure	Cache last 48h data	"Data may be outdated (cached)"
Agentic mode partial failure	Return partial output	"1 or more data blocks unavailable — partial insight shown"
📊 Data Specs
Dimension	Spec
Peer Comparison	3–5 peers (auto-selected from same NSE/BSE sector)
Time Horizon	3 months (technical), 12 months (valuation), 3Y CAGR (fundamentals)
	
📌 Design & Technical Principles
* Graceful degradation: Every failure path must trigger fallback logic and inform the user.
* Sector intelligence: All logic paths (simple and agentic) must adapt dynamically to sector archetype.
* Reusable prompt structure: Internal prompts decomposed into predictable sections to improve LLM reliability.
* LLM fallback control: Agent is instructed to suppress sections if data is missing — avoids hallucinations.


✅ Acceptance Criteria
* Summary Box appears consistently across both modes
* Simple mode delivers factual insights using deterministic rules
* Agentic mode synthesizes a cohesive multi-lens thesis using one Financial Analyst Agent
* Summary Box shows fair value range, investment label, rationale, and fallback warnings
* Sector logic applies correctly per mode
* Sentiment and macro blocks show up only when available
* System fails gracefully when data or agent is unavailable

