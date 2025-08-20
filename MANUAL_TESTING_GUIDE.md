# EquityScope v2.0 Manual Testing Guide

**Purpose**: Validate user-facing functionality that automated tests cannot cover  
**Updated**: July 29, 2025 - 10-Year DCF System + Educational Features Complete  
**Next Update**: After Mobile UX Implementation  

---

## 🎯 **Testing Philosophy**

**Automated Tests**: Cover technical correctness, edge cases, performance  
**Manual Tests**: Validate user experience, business logic, integration quality  

**Coverage Split**:
- **Automated**: 85% - API responses, data validation, error handling, performance
- **Manual**: 15% - User workflows, business insights quality, UX edge cases

---

## 📋 **Phase 1: Optimized AI Architecture - Manual Testing Scenarios**

### **Scenario 1: Cost Optimization Validation**
**Objective**: Confirm 50% cost reduction is achieved in practice

**Test Steps**:
1. Run analysis on **TCS.NS** using v1 (if available) 
2. Run same analysis on **TCS.NS** using v2 API: `POST /api/v2/analyze`
3. Compare response metadata cost fields
4. Test with 5 different stocks: TCS, RELIANCE, HDFC, INFY, WIPRO

**Expected Results**:
```json
{
  "metadata": {
    "cost_optimization": {
      "estimated_cost_usd": 0.30,      // Should be ≤ $0.30
      "cost_reduction_vs_v1": "50%",   // Should show reduction
      "estimated_tokens": 10000        // Should be ≤ 10K
    }
  }
}
```

**Success Criteria**:
- [ ] Cost per analysis ≤ $0.30 for all test stocks
- [ ] Token usage ≤ 10,000 for all analyses  
- [ ] Analysis quality comparable to v1 (subjective assessment)

---

### **Scenario 2: Performance Improvement Validation**
**Objective**: Confirm <30 second response time target

**Test Steps**:
1. Use v2 streaming endpoint: `POST /api/v2/analyze/stream`
2. Time full analysis for each stock: TCS, RELIANCE, HDFC, SBI, INFY
3. Test during different times (morning/evening) for network variation
4. Test with different assumption sets (quick vs detailed)

**Expected Results**:
- Analysis completes in <30 seconds consistently
- Progress updates are meaningful and frequent
- No hanging or timeout issues

**Success Criteria**:
- [ ] All analyses complete within 30 seconds
- [ ] Progress updates show every 2-3 seconds
- [ ] No analyses fail due to timeouts
- [ ] Response time consistent across different stocks

---

### **Scenario 3: Analysis Quality Validation**
**Objective**: Ensure AI insights are valuable and company-specific

**Test Companies & What to Validate**:

**TCS.NS (Technology)**:
- [ ] Investment thesis mentions IT services leadership
- [ ] Key strengths include client relationships/digital capabilities
- [ ] Risks mention currency impact and competition
- [ ] DCF assumptions are reasonable for tech company (8-12% growth)
- [ ] AI insights are specific to TCS, not generic tech analysis

**RELIANCE.NS (Conglomerate)**:
- [ ] Analysis acknowledges multi-business complexity
- [ ] Mentions retail/telecom growth stories  
- [ ] DCF assumptions account for diverse business mix
- [ ] Risk assessment includes energy transition concerns
- [ ] Valuation context compares to relevant peers

**HDFCBANK.NS (Banking)**:
- [ ] Analysis correctly identifies as banking sector
- [ ] Risk assessment mentions NIM pressure, asset quality
- [ ] Financial health score reflects banking metrics
- [ ] Note: Should work but may suggest DDM model (Phase 2 feature)

**Success Criteria**:
- [ ] Each analysis contains company-specific insights (not templates)
- [ ] Investment thesis makes sense for the business model
- [ ] Risk factors are relevant to company/industry
- [ ] Financial assumptions are reasonable vs peer companies

---

### **Scenario 4: Error Handling & Edge Cases**
**Objective**: Validate graceful degradation and user-friendly errors

**Test Cases**:

**Invalid Ticker**:
- Input: `INVALIDSTOCK` 
- Expected: Clear error message with suggestions
- Test: `POST /api/v2/analyze {"ticker": "INVALIDSTOCK"}`

**Network Issues** (simulate by disconnecting):
- Expected: Timeout handling with retry suggestions
- User guidance should suggest checking connection

**Partial Data Scenarios**:
- Test stocks with limited financial data
- Expected: Analysis continues with available data + disclaimers

**API Key Issues** (if applicable):
- Expected: Clear error about AI service unavailability
- Fallback to basic DCF without AI insights

**Success Criteria**:
- [ ] No cryptic error messages or stack traces
- [ ] All errors include actionable user guidance
- [ ] System degrades gracefully (partial features vs complete failure)
- [ ] Recovery suggestions are helpful and specific

---

### **Scenario 5: User Guidance Quality**
**Objective**: Validate "What This Means" sections are helpful

**For Each Test Stock**:
1. Review `enhanced_insights.investment_summary` 
2. Check `user_guidance.what_this_means`
3. Evaluate `user_guidance.next_steps`

**Quality Checks**:
- [ ] Investment summary is clear to non-experts
- [ ] "What this means" explains financial jargon
- [ ] Next steps are actionable and specific
- [ ] Action guidance matches the analysis (buy/hold/sell)
- [ ] Educational content helps users understand DCF concepts

**Success Criteria**:
- [ ] A beginner investor can understand the key takeaways
- [ ] Recommendations are clear (not ambiguous)
- [ ] Risk warnings are prominent where appropriate

---

### **Scenario 6: API Integration & Streaming**
**Objective**: Validate streaming progress and final results

**Test Steps**:
1. Use streaming endpoint with browser/Postman
2. Monitor Server-Sent Events during analysis
3. Verify progress updates are meaningful
4. Confirm final result matches regular endpoint

**Progress Updates to Validate**:
```
data: {"step": "ingestion", "progress": 10, "message": "Gathering TCS.NS financial data..."}
data: {"step": "analysis", "progress": 40, "message": "Running Analysis Engine..."}
data: {"step": "validation", "progress": 80, "message": "Running DCF Validator..."}
data: {"step": "complete", "progress": 100, "message": "Analysis complete!"}
```

**Success Criteria**:
- [ ] Progress updates are regular (not stuck at any stage)
- [ ] Messages are descriptive and match actual processing
- [ ] Final result structure matches non-streaming endpoint
- [ ] Stream closes properly after completion

---

## 📋 **Phase 2: Multi-Model DCF - Manual Testing Scenarios**

### **Scenario 7: Banking Company DDM Model Auto-Selection**
**Objective**: Validate DDM model is automatically selected for banking companies

**Test Steps**:
1. Test model recommendation endpoint: `POST /api/v2/model-recommendation`
2. Test with banking companies: HDFCBANK, SBIN, ICICIBANK, KOTAKBANK, AXISBANK
3. Run full analysis: `POST /api/v2/analyze` and verify integrated multi-model results

**Expected Results**:
```json
{
  "model_recommendation": {
    "recommended_model": {
      "model": "DDM",
      "rationale": "Private Sector Bank companies typically use DDM model",
      "confidence_score": 0.9
    },
    "default_assumptions": {
      "dividend_growth_rate": 6.0,
      "roe": 18.0,
      "payout_ratio": 0.4,
      "cost_of_equity": 11.0
    }
  }
}
```

**Success Criteria**:
- [ ] All banking companies recommend DDM model with confidence >0.8
- [ ] DDM assumptions include dividend_growth_rate, roe, payout_ratio
- [ ] Rationale mentions banking/financial services characteristics
- [ ] Alternative models include DCF and Asset for comparison

---

### **Scenario 8: Technology Company DCF Model Selection**
**Objective**: Validate DCF model is selected for technology companies

**Test Companies**: TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS, TECHM.NS

**Test Steps**:
1. Get model recommendations for each tech company
2. Verify DCF model selection and rationale
3. Check assumption reasonableness for tech sector

**Expected Results**:
- Model: DCF with confidence >0.7
- Assumptions include revenue_growth_rate, ebitda_margin, wacc
- Revenue growth: 8-15% range for tech companies
- EBITDA margin: 15-25% range for IT services

**Success Criteria**:
- [ ] All tech companies recommend DCF model
- [ ] Growth assumptions are reasonable for sector
- [ ] Rationale mentions cash flow predictability

---

### **Scenario 9: Asset-Heavy Company Model Selection**
**Objective**: Validate Asset-based model for infrastructure/utilities

**Test Companies**: NTPC.NS, POWERGRID.NS, L&T.NS (infrastructure)

**Test Steps**:
1. Test companies with substantial fixed assets
2. Verify Asset-based model recommendation
3. Check asset-specific assumptions

**Expected Results**:
- Model: Asset with confidence >0.7
- Assumptions include book_value_growth, roe, asset_turnover
- Rationale mentions tangible asset base

**Success Criteria**:
- [ ] Asset-heavy companies recommend Asset model
- [ ] Assumptions focus on book value and asset utilization
- [ ] Model rationale explains asset-based approach

---

### **Scenario 10: Multi-Model Valuation Comparison**
**Objective**: Validate multi-model calculations provide different perspectives

**Test Steps**:
1. Use multi-model endpoint: `POST /api/v2/multi-model-valuation`
2. Test with companies that could use multiple models (e.g., RELIANCE)
3. Verify valuation range and consensus calculation

**Expected Results**:
```json
{
  "primary_model": "DCF",
  "valuations": {
    "DCF": {"intrinsic_value": 2850.0, "upside_downside": 5.2},
    "DDM": {"intrinsic_value": 2700.0, "upside_downside": -0.3},
    "Asset": {"intrinsic_value": 2920.0, "upside_downside": 7.8}
  },
  "valuation_summary": {
    "valuation_range": {"min": 2700.0, "max": 2920.0, "average": 2823.3},
    "consensus": {"recommendation": "Buy", "confidence": "medium"}
  }
}
```

**Success Criteria**:
- [ ] Multiple models calculate different intrinsic values
- [ ] Valuation range shows min, max, average correctly
- [ ] Consensus recommendation makes sense vs current price
- [ ] Model agreement confidence reflects variance

---

### **Scenario 11: Model Override and User Preference**
**Objective**: Validate users can override recommended model

**Test Steps**:
1. Get recommendation for HDFCBANK (should be DDM)
2. Override with DCF: `POST /api/v2/multi-model-valuation?user_model_preference=DCF`
3. Verify primary model switches to DCF but recommendation shows DDM

**Expected Results**:
- Primary model becomes DCF (user preference)
- Recommendation still shows DDM as recommended
- Both models calculate different valuations

**Success Criteria**:
- [ ] User preference overrides primary model selection  
- [ ] Original recommendation is preserved for context
- [ ] Multiple models are calculated regardless of preference

---

### **Scenario 12: Industry Edge Cases**
**Objective**: Test classification edge cases and unknown sectors

**Test Cases**:

**Conglomerate (RELIANCE.NS)**:
- Mixed business (Oil & Gas + Retail + Telecom)
- Should default to DCF with medium confidence
- Multiple models should show significant variance

**Unknown/New Sectors**:
- Test with companies in emerging sectors
- Should default to DCF with lower confidence
- Error handling should be graceful

**Success Criteria**:
- [ ] Complex conglomerates get reasonable model recommendations
- [ ] Unknown sectors default to DCF with <0.7 confidence  
- [ ] No classification errors or exceptions

---

### **Scenario 13: Enhanced User Guidance Integration**
**Objective**: Validate multi-model insights enhance user guidance

**Test Steps**:
1. Run full analysis with multi-model integration
2. Check `user_guidance.what_this_means.model_selection`
3. Verify educational content includes model explanation

**Expected Results**:
```json
{
  "user_guidance": {
    "what_this_means": {
      "model_selection": "We recommend the DDM model with high confidence. Private Sector Bank companies typically use DDM model",
      "key_takeaways": [
        "Key strength: Market leadership in retail banking",
        "Main concern: NIM pressure from rate competition", 
        "Multi-model consensus: Buy"
      ]
    },
    "educational_content": {
      "model_education": {
        "what_it_is": "DDM values companies based on expected future dividend payments",
        "key_assumptions": "Dividend growth rate, payout ratio, and cost of equity",
        "best_for": "Financial services companies that focus on returning capital to shareholders"
      }
    }
  }
}
```

**Success Criteria**:
- [ ] Model selection is clearly explained to users
- [ ] Key takeaways include multi-model insights
- [ ] Educational content matches selected model
- [ ] "What This Means" sections are user-friendly

---

### **Scenario 14: Performance and Cost Validation**
**Objective**: Ensure multi-model integration doesn't break performance targets

**Test Steps**:
1. Time full analysis with multi-model integration
2. Monitor token usage and cost estimates
3. Compare vs Phase 1 performance

**Performance Targets**:
- Response time: Still <30 seconds (despite additional model calculations)
- Cost: Still ≤$0.30 per analysis (multi-model logic is deterministic)
- Token usage: ≤10K tokens (AI agents unchanged)

**Success Criteria**:
- [ ] Response time remains <30 seconds for all test companies
- [ ] Cost estimates remain ≤$0.30 per analysis
- [ ] Multi-model logic adds <5 seconds to analysis time
- [ ] No performance regression vs Phase 1

---

## 🧪 **Phase 2 Testing Commands**

### **Quick API Test Commands**:
```bash
# Model recommendation only
curl -X POST "http://localhost:8000/api/v2/model-recommendation?ticker=HDFCBANK" 

# Multi-model valuation
curl -X POST "http://localhost:8000/api/v2/multi-model-valuation?ticker=TCS"

# Multi-model with user preference
curl -X POST "http://localhost:8000/api/v2/multi-model-valuation?ticker=HDFCBANK&user_model_preference=DCF"

# Get supported models info
curl -X GET "http://localhost:8000/api/v2/supported-models"

# Full analysis with multi-model integration
curl -X POST "http://localhost:8000/api/v2/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "HDFCBANK"}'
```

### **Test Data for Phase 2**:
```bash
# Banking companies (should recommend DDM)
BANKING_STOCKS=("HDFCBANK.NS" "SBIN.NS" "ICICIBANK.NS" "KOTAKBANK.NS" "AXISBANK.NS")

# Tech companies (should recommend DCF)  
TECH_STOCKS=("TCS.NS" "INFY.NS" "WIPRO.NS" "HCLTECH.NS" "TECHM.NS")

# Infrastructure/Asset-heavy (should recommend Asset model)
ASSET_HEAVY=("NTPC.NS" "POWERGRID.NS" "COALINDIA.NS")

# Conglomerates (complex classification)
COMPLEX_COMPANIES=("RELIANCE.NS" "ITC.NS" "ADANIPORTS.NS")
```

---

## 📋 **Intelligent Caching - Manual Testing Scenarios**

### **Scenario 15: Cache Performance Validation**
**Objective**: Validate caching system improves performance and reduces costs

**Test Steps**:
1. Clear all cache: `DELETE /api/v2/cache/clear`
2. Run first analysis on TCS.NS: `POST /api/v2/analyze {"ticker": "TCS.NS"}`
3. Note response time and cache statistics
4. Run same analysis again immediately
5. Compare response times and check cache hit statistics

**Expected Results**:
```json
{
  "metadata": {
    "cache_performance": {
      "hit_rate_percentage": 75.0,
      "total_cost_saved_usd": 0.20,
      "cache_enabled": true
    }
  }
}
```

**Success Criteria**:
- [ ] Second analysis is significantly faster (>50% improvement)
- [ ] Cache hit rate increases with repeated analyses
- [ ] Cost savings accumulate over multiple requests
- [ ] Cache statistics show proper hit/miss tracking

---

### **Scenario 16: Cache TTL Strategy Validation**
**Objective**: Verify different cache types expire at appropriate intervals

**Test Components to Validate**:

**Financial Data (24hr TTL)**:
- Run analysis on RELIANCE.NS
- Verify financial data cached for 24 hours
- Should remain cached across multiple sessions

**News Articles (6hr TTL)**:
- Check news caching with: `GET /api/v2/cache/stats`
- News should update every 6 hours
- Different max_articles parameters create separate cache entries

**AI Insights (6hr TTL)**:
- AI analysis results cached for 6 hours
- Significant performance improvement on cache hits
- Different news contexts create separate cache entries

**Success Criteria**:
- [ ] Financial data stays cached for full 24 hours
- [ ] News articles refresh every 6 hours
- [ ] AI insights provide 6-hour performance boost
- [ ] Model recommendations cached for 24 hours

---

### **Scenario 17: Cache Statistics and Monitoring**
**Objective**: Validate cache monitoring and statistics accuracy

**Test Steps**:
1. Get baseline cache stats: `GET /api/v2/cache/stats`
2. Run analyses on 5 different stocks: TCS, RELIANCE, HDFCBANK, INFY, WIPRO
3. Run same analyses again (should hit cache)
4. Check updated cache statistics
5. Verify cost savings calculations

**Expected Results**:
```json
{
  "cache_statistics": {
    "total_requests": 10,
    "cache_hits": 5,
    "cache_misses": 5,
    "hit_rate_percentage": 50.0,
    "total_cost_saved_usd": 1.00
  },
  "cache_storage": {
    "cache_files": 15,
    "storage_size_mb": 2.5
  }
}
```

**Success Criteria**:
- [ ] Hit rate calculation is accurate
- [ ] Cost savings match expected values ($0.20 per cached analysis)
- [ ] Storage statistics reflect actual cache usage
- [ ] TTL configuration shows correct values (24hr, 6hr, 6hr)

---

### **Scenario 18: Cache Warming for Popular Stocks**
**Objective**: Test cache warming functionality for improved user experience

**Test Steps**:
1. Clear all cache
2. Warm cache for popular stocks: `POST /api/v2/cache/warm`
3. Verify cache warming background task starts
4. Test analyses on warmed stocks show immediate cache hits
5. Compare with non-warmed stocks

**Expected Results**:
```json
{
  "cache_warming": "started",
  "stocks_to_warm": ["TCS.NS", "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "WIPRO.NS"],
  "estimated_duration_minutes": 10,
  "background_processing": true
}
```

**Success Criteria**:
- [ ] Cache warming completes successfully
- [ ] Popular stocks show immediate cache hits
- [ ] First-time user experience improved for common stocks
- [ ] Background processing doesn't block API responses

---

## 📋 **Cache Testing Commands**

### **Cache Management API Tests**:
```bash
# Get cache statistics
curl -X GET "http://localhost:8000/api/v2/cache/stats"

# Warm cache for popular stocks  
curl -X POST "http://localhost:8000/api/v2/cache/warm"

# Clear specific cache entry
curl -X DELETE "http://localhost:8000/api/v2/cache/clear?cache_type=financial_data&ticker=TCS.NS"

# Clear expired entries only
curl -X DELETE "http://localhost:8000/api/v2/cache/clear"
```

### **Cache Performance Testing**:
```bash
# Test cache performance for multiple analyses
for ticker in TCS.NS RELIANCE.NS HDFCBANK.NS INFY.NS WIPRO.NS; do
  echo "First analysis of $ticker (should miss cache):"
  time curl -X POST "http://localhost:8000/api/v2/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"ticker\": \"$ticker\"}"
  
  echo "Second analysis of $ticker (should hit cache):"
  time curl -X POST "http://localhost:8000/api/v2/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"ticker\": \"$ticker\"}"
done
```

---

## 📋 **10-Year Multi-Stage DCF System - Manual Testing Scenarios**

### **Scenario 19: 10-Year DCF Mode Selection Validation**
**Objective**: Verify Simple vs Agentic mode recommendations work correctly

**Test Steps**:
1. Test mode recommendation endpoint: `POST /api/v2/mode-recommendation`
2. Test with different company types:
   - **Stable Companies**: TCS.NS, HDFCBANK.NS (should recommend Simple)
   - **Transforming Companies**: RELIANCE.NS, ADANIPORTS.NS (should recommend Agentic)
   - **Growth Companies**: INFY.NS, WIPRO.NS (may recommend either based on data)

**Expected Results**:
```json
{
  "mode_recommendation": {
    "recommended_mode": "simple",
    "confidence_score": 0.85,
    "reasoning": "Historical performance data is consistent and predictable",
    "mode_explanation": "Simple Mode uses 5-year historical data with GDP blending",
    "alternative_available": true
  }
}
```

**Success Criteria**:
- [ ] Mature, stable companies recommend Simple mode with high confidence (>0.8)
- [ ] Transforming/volatile companies recommend Agentic mode 
- [ ] Mode explanations are clear and company-specific
- [ ] Confidence scores reflect data quality and business predictability

---

### **Scenario 20: Multi-Stage Growth Engine Validation**
**Objective**: Verify 10-year growth stages are calculated correctly

**Test Companies**: TCS.NS, RELIANCE.NS, HDFCBANK.NS

**Test Steps**:
1. Run full DCF analysis: `POST /api/v2/multi-stage-dcf`
2. Verify growth stage breakdown in response
3. Check GDP blending progression over 10 years
4. Validate growth waterfall visualization data

**Expected Results for TCS.NS (Simple Mode)**:
```json
{
  "growth_stages": [
    {
      "years": "1-2",
      "growth_rate": 11.75,
      "method": "historical_cagr",
      "gdp_weight": 0.2,
      "confidence": "high"
    },
    {
      "years": "3-5", 
      "growth_rate": 7.0,
      "method": "industry_fade",
      "gdp_weight": 0.5,
      "confidence": "high"
    },
    {
      "years": "6-8",
      "growth_rate": 3.4,
      "method": "competitive_convergence", 
      "gdp_weight": 0.75,
      "confidence": "medium"
    },
    {
      "years": "9-10",
      "growth_rate": 3.0,
      "method": "gdp_convergence",
      "gdp_weight": 1.0, 
      "confidence": "high"
    }
  ]
}
```

**Success Criteria**:
- [ ] All companies show 4 distinct growth stages (1-2, 3-5, 6-8, 9-10)
- [ ] GDP weight increases progressively from early to late stages
- [ ] Growth rates decline logically from near-term to long-term
- [ ] Methods match stage characteristics (historical → fade → convergence)
- [ ] Terminal growth rate converges to GDP (3.0%) in final stage

---

### **Scenario 21: 10-Year Projection Quality Validation**
**Objective**: Ensure 10-year projections are reasonable and internally consistent

**Test Steps**:
1. Analyze projection arrays for mathematical consistency
2. Verify present value calculations using WACC
3. Check terminal value calculation methodology
4. Validate revenue, FCF, and PV progressions

**Mathematical Checks**:
```javascript
// Verify present value calculation
for (let projection of projections) {
  const expectedPV = projection.free_cash_flow / Math.pow(1 + wacc/100, projection.year);
  assert(Math.abs(projection.present_value - expectedPV) < 1000); // Within ₹1K
}

// Verify revenue growth consistency
for (let i = 1; i < projections.length; i++) {
  const actualGrowth = (projections[i].revenue / projections[i-1].revenue - 1) * 100;
  assert(Math.abs(actualGrowth - projections[i].revenue_growth_rate) < 0.1); // Within 0.1%
}
```

**Success Criteria**:
- [ ] Present value calculations mathematically correct
- [ ] Revenue growth rates match actual year-over-year changes
- [ ] Free cash flow progression is logical (generally increasing)
- [ ] Terminal value represents reasonable % of total enterprise value (40-70%)
- [ ] No negative cash flows in outer years (red flag for assumptions)

---

### **Scenario 22: Progressive Disclosure Educational System**
**Objective**: Validate educational content adapts to user experience level

**Test Steps**:
1. Test with different user levels: `POST /api/v2/multi-stage-dcf?user_level=beginner`
2. Verify educational tooltips show appropriate content
3. Check progressive disclosure panel content organization
4. Test educational content search and filtering

**Content Validation by User Level**:

**Beginner Level**:
- Educational content uses simple language
- Avoids technical jargon (WACC, NOPAT, etc.)
- Focuses on "what this means for investors"
- Includes investment disclaimers

**Intermediate Level**:
- Includes methodology explanations
- Shows calculation details when requested
- Balances technical accuracy with accessibility
- Provides context for assumptions

**Advanced Level**:
- Full technical detail available
- Mathematical formulas shown
- Sensitivity analysis included
- Academic/professional level explanations

**Success Criteria**:
- [ ] Content complexity matches user experience level
- [ ] Technical terms are defined appropriately for each level
- [ ] Educational flow progresses logically (basic → advanced concepts)
- [ ] All experience levels find content valuable (subjective assessment)

---

### **Scenario 23: Demo Mode Interactive Experience**
**Objective**: Validate guided demo walkthroughs function correctly

**Test Steps**:
1. Access demo mode: Click "Try Demo" button in dashboard
2. Test all three demo companies: TCS.NS, RELIANCE.NS, HDFCBANK.NS
3. Verify 5-step guided walkthrough for each demo
4. Test interactive controls (play/pause, next/previous, close)

**Demo Flow Validation**:

**TCS.NS Demo (Beginner)**:
- [ ] Step 1: Introduction shows company overview with highlights
- [ ] Step 2: Company analysis displays SWOT and market position
- [ ] Step 3: Mode selection explains why Simple mode is recommended
- [ ] Step 4: DCF results show 10-year projection visualization
- [ ] Step 5: Key insights provide plain-English investment summary

**RELIANCE.NS Demo (Advanced)**:
- [ ] Shows Agentic mode complexity and transformation analysis
- [ ] Explains multi-business valuation challenges
- [ ] Demonstrates AI-enhanced projections vs historical data
- [ ] Advanced concepts like digital transformation impact

**HDFCBANK.NS Demo (Intermediate)**:
- [ ] Banking-specific DCF considerations explained
- [ ] Credit cycle and regulatory environment discussed
- [ ] Asset quality metrics integrated into analysis
- [ ] Sector-specific investment considerations

**Interactive Controls**:
- [ ] Auto-advance timing works correctly (10-30 seconds per step)
- [ ] Play/pause controls function properly
- [ ] Navigation (next/previous) works in all states
- [ ] Progress bar accurately reflects completion
- [ ] Close functionality returns to main dashboard

**Success Criteria**:
- [ ] All demo companies load without errors
- [ ] Educational narrative flows logically
- [ ] Interactive controls are responsive and intuitive
- [ ] Demo content matches the specified difficulty levels
- [ ] Users can complete demos without technical issues

---

### **Scenario 24: "What This Means" Interpretation Sections**
**Objective**: Validate investment interpretation and decision guidance

**Test Steps**:
1. Run DCF analysis for companies with different valuation outcomes
2. Verify interpretation insights match analysis results
3. Test investment decision framework logic
4. Check assumption sensitivity explanations

**Test Cases by Valuation Outcome**:

**Significant Upside (>15% undervalued)**:
- [ ] Interpretation correctly identifies "Significant Upside Potential"
- [ ] Investment decision framework suggests "Strong Buy Consideration"
- [ ] Risk factors appropriately balance bullish interpretation
- [ ] Action items are specific and actionable

**Moderate Upside (5-15% undervalued)**:
- [ ] Interpretation shows "Moderate Upside Opportunity"
- [ ] Decision framework suggests "Buy Consideration"
- [ ] Limited margin of safety mentioned in risks

**Fair Value (±5%)**:
- [ ] Interpretation indicates "Fair Value Trading Range"
- [ ] Decision framework suggests "Hold/Neutral"
- [ ] Focus shifts to dividend yield and alternatives

**Overvalued (<-5%)**:
- [ ] Interpretation warns of "Overvaluation Risk"
- [ ] Decision framework suggests "Avoid/Sell Consideration"
- [ ] Clear warnings about downside risk

**Intelligence Validation**:
```json
{
  "interpretation_insights": [
    {
      "type": "bullish|bearish|neutral|warning",
      "title": "Clear, descriptive title",
      "description": "Plain-English explanation",
      "confidence": "high|medium|low",
      "reasoning": "Supporting logic"
    }
  ],
  "investment_decision": {
    "recommendation": "Strong Buy|Buy|Hold|Avoid",
    "rationale": "Why this recommendation makes sense",
    "actions": ["Specific action 1", "Specific action 2"],
    "risks": ["Key risk 1", "Key risk 2"]
  }
}
```

**Success Criteria**:
- [ ] Interpretations match mathematical analysis results
- [ ] Investment recommendations are logically consistent
- [ ] Risk warnings appear for highly uncertain scenarios
- [ ] Action items are specific and implementable
- [ ] Language is accessible to target user experience level

---

### **Scenario 25: Growth Waterfall Visualization**
**Objective**: Verify interactive growth stage visualization works correctly

**Test Steps**:
1. Load DCF analysis with growth waterfall enabled
2. Test interactive hover states on each growth stage
3. Verify educational tooltips for each stage
4. Check visual progression from high to low growth

**Visual Elements to Validate**:
- [ ] Growth stages display as connected waterfall bars
- [ ] Colors progress logically (green → yellow → orange → blue)
- [ ] Hover states show detailed stage information
- [ ] Educational tooltips explain methodology for each stage
- [ ] Animation timing feels smooth and purposeful

**Tooltip Content Validation**:
```json
{
  "stage_1_2": {
    "tooltip": "Years 1-2: Historical CAGR methodology",
    "explanation": "Based on company's 5-year performance record",
    "confidence": "High - verified historical data"
  },
  "stage_3_5": {
    "tooltip": "Years 3-5: Industry fade approach", 
    "explanation": "Growth normalizes as competition increases",
    "confidence": "High - industry pattern recognition"
  }
}
```

**Success Criteria**:
- [ ] Waterfall visualization loads without errors
- [ ] Interactive elements respond to user input
- [ ] Educational content matches growth stage methodology
- [ ] Visual design enhances understanding of concept
- [ ] Responsive design works on different screen sizes

---

### **Scenario 26: Enhanced DCF Educational Content**
**Objective**: Validate comprehensive educational content system

**Test Steps**:
1. Access DCF educational panel from analysis results
2. Navigate through all educational content categories
3. Test search functionality within educational content
4. Verify content relevance and accuracy

**Educational Content Categories**:

**DCF Basics**:
- [ ] "What is DCF?" explanation clear for beginners
- [ ] Present value concept explained with examples
- [ ] Terminal value methodology described
- [ ] Assumptions and limitations covered

**Multi-Stage Growth**:
- [ ] Why 10 years vs traditional 5-year models
- [ ] Growth stage methodology explained
- [ ] GDP blending rationale provided
- [ ] Historical validation process described

**Mode Selection**:
- [ ] Simple vs Agentic mode differences explained
- [ ] When to use each mode guidance provided
- [ ] Mode recommendation logic transparent
- [ ] Confidence scoring interpretation included

**Advanced Concepts**:
- [ ] WACC calculation methodology
- [ ] Terminal value sensitivity analysis
- [ ] Monte Carlo simulation concepts (if implemented)
- [ ] Scenario analysis frameworks

**Success Criteria**:
- [ ] All educational content loads correctly
- [ ] Content search returns relevant results
- [ ] Educational flow supports progressive learning
- [ ] Content accuracy verified by financial professionals
- [ ] User feedback indicates educational value

---

## 📋 **10-Year DCF Testing Commands**

### **Mode Recommendation Testing**:
```bash
# Test mode recommendations for different company types
curl -X POST "http://localhost:8000/api/v2/mode-recommendation" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TCS.NS"}'

curl -X POST "http://localhost:8000/api/v2/mode-recommendation" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "RELIANCE.NS"}'
```

### **10-Year DCF Analysis**:
```bash
# Simple mode analysis
curl -X POST "http://localhost:8000/api/v2/multi-stage-dcf" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TCS.NS",
    "mode": "simple", 
    "user_level": "intermediate"
  }'

# Agentic mode analysis
curl -X POST "http://localhost:8000/api/v2/multi-stage-dcf" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "RELIANCE.NS",
    "mode": "agentic",
    "user_level": "advanced"
  }'
```

### **Demo Mode API Testing**:
```bash
# Get demo data
curl -X GET "http://localhost:8000/api/v2/demo-analyses/TCS.NS"
curl -X GET "http://localhost:8000/api/v2/demo-analyses/RELIANCE.NS" 
curl -X GET "http://localhost:8000/api/v2/demo-analyses/HDFCBANK.NS"

# List available demos
curl -X GET "http://localhost:8000/api/v2/demo-analyses"
```

### **Educational Content Testing**:
```bash
# Get educational content by category
curl -X GET "http://localhost:8000/api/v2/educational-content?category=dcf_basics&user_level=beginner"

# Search educational content
curl -X GET "http://localhost:8000/api/v2/educational-content/search?query=terminal%20value"
```

---

## 📋 **Test Data for 10-Year DCF System**

### **Companies by Complexity Level**:
```bash
# Beginner-friendly (stable, predictable)
STABLE_COMPANIES=("TCS.NS" "HDFCBANK.NS" "ITC.NS" "NESTLEIND.NS")

# Intermediate (moderate complexity)
MODERATE_COMPANIES=("INFY.NS" "WIPRO.NS" "ICICIBANK.NS" "MARUTI.NS")

# Advanced (complex, transforming)  
COMPLEX_COMPANIES=("RELIANCE.NS" "ADANIPORTS.NS" "BHARTIARTL.NS")

# Banking (sector-specific considerations)
BANKING_COMPANIES=("HDFCBANK.NS" "SBIN.NS" "ICICIBANK.NS" "KOTAKBANK.NS")
```

### **Expected Growth Stage Patterns**:
```bash
# Stable IT Services (TCS pattern)
STABLE_IT_PATTERN="12% → 8% → 4% → 3%"

# Transforming Conglomerate (Reliance pattern) 
TRANSFORMATION_PATTERN="15% → 9% → 4% → 3%"

# Banking (Credit cycle dependent)
BANKING_PATTERN="18% → 12% → 6% → 3%"
```

---

## 📋 **Phase 3: Mobile UX - Manual Testing Scenarios**
*(Will be added after Phase 3 implementation)*

### **Scenario 27: Mobile Touch Interface**
*(Placeholder - will be detailed after implementation)*

**Test Devices**: iPhone, Android, iPad  
**Objective**: Validate touch-friendly DCF controls

---

## 🧪 **Testing Environment Setup**

### **Prerequisites**:
- Access to v2 API endpoints (localhost:8000 or deployed)
- API testing tool (Postman, curl, or browser)
- Claude API key configured
- Stable internet connection

### **Test Data Preparation**:
```bash
# Test ticker symbols
TECH_STOCKS=("TCS.NS" "INFY.NS" "WIPRO.NS" "HCLTECH.NS")
BANK_STOCKS=("HDFCBANK.NS" "SBIN.NS" "ICICIBANK.NS")
DIVERSE_STOCKS=("RELIANCE.NS" "ITC.NS" "MARUTI.NS")

# Sample DCF assumptions for testing
CONSERVATIVE_ASSUMPTIONS={
  "revenue_growth_rate": 6.0,
  "ebitda_margin": 15.0,
  "tax_rate": 25.0,
  "wacc": 12.0,
  "terminal_growth_rate": 3.0
}

AGGRESSIVE_ASSUMPTIONS={
  "revenue_growth_rate": 15.0,
  "ebitda_margin": 22.0,
  "tax_rate": 25.0,
  "wacc": 10.0,
  "terminal_growth_rate": 4.0
}
```

### **Quick API Test Commands**:
```bash
# Health check
curl -X GET "http://localhost:8000/api/v2/health"

# Basic analysis
curl -X POST "http://localhost:8000/api/v2/analyze" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TCS"}'

# Analysis with assumptions
curl -X POST "http://localhost:8000/api/v2/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "TCS",
    "user_assumptions": {
      "revenue_growth_rate": 10.0,
      "ebitda_margin": 18.0,
      "tax_rate": 25.0,
      "wacc": 11.5,
      "terminal_growth_rate": 3.5
    }
  }'

# Cost metrics
curl -X GET "http://localhost:8000/api/v2/cost-metrics"
```

---

## 📊 **Manual Testing Results Template**

### **Test Execution Record**:
```
Date: ___________
Tester: ___________
Environment: Local/Staging/Production
Version: v2.0-optimized

SCENARIO 1: Cost Optimization ✅/❌
- TCS.NS Cost: $_____  (Target: ≤$0.30)
- RELIANCE.NS Cost: $_____
- Average Response Time: _____s (Target: ≤30s)
- Issues Found: ________________

SCENARIO 2: Performance ✅/❌
- All analyses <30s: ✅/❌
- Streaming works: ✅/❌
- Issues Found: ________________

[Continue for all scenarios...]

OVERALL ASSESSMENT:
- Ready for user testing: ✅/❌
- Blockers found: ________________
- Recommendations: ________________
```

---

## 🚨 **Issues to Watch For**

### **Common Issues from v1.0**:
1. **Banking company DCF failures** - Should be resolved with better error handling
2. **Price inconsistencies** - Monitor metadata consistency
3. **Timeout failures** - Watch for hanging requests
4. **Mobile usability** - Touch controls difficult to use

### **v2.0 Specific Risks**:
1. **Cost monitoring accuracy** - Verify token counting is correct
2. **Analysis quality degradation** - Ensure 2-agent system maintains insights
3. **Performance regression** - Under load, response times may increase
4. **Streaming reliability** - SSE connections can be fragile

### **10-Year DCF System Risks**:
1. **Growth stage logic errors** - Verify 4 stages always calculated correctly
2. **GDP blending issues** - Check progressive weight increases (0.2 → 1.0)
3. **Terminal value calculation errors** - Monitor for unreasonable terminal values
4. **Mode recommendation inconsistency** - Same company should get same mode recommendation
5. **Educational content loading failures** - Large content database may have performance issues
6. **Demo mode state management** - Interactive controls may desync with content

### **Red Flags**:
- Analysis cost >$0.40 (target is $0.30)
- Response time >45s (worse than v1.0)
- Generic insights not specific to company
- Errors without actionable guidance
- Inconsistent results across runs

### **10-Year DCF Red Flags**:
- Growth stages don't sum to 4 total stages
- Terminal growth rate >4% or <2% (should be ~3%)
- Terminal value >80% of enterprise value (too dependent on assumptions)
- Mode recommendations flip-flop for same company
- Educational tooltips show loading errors or empty content
- Demo mode crashes or becomes unresponsive
- "What This Means" sections don't match mathematical results

---

## 📝 **Testing Documentation Requirements**

### **After Each Testing Session**:
1. **Update results** in this document
2. **Log issues** in appropriate GitHub issues or tracking system
3. **Update success criteria** based on learnings
4. **Add new edge cases** discovered during testing

### **Before Each Phase**:
1. **Review and update** scenarios for new functionality
2. **Add performance baselines** for comparison
3. **Update test data** with relevant examples
4. **Prepare comparison metrics** vs previous version

---

**Next Update Scheduled**: After Mobile UX implementation  
**Current Status**: 10-Year DCF System + Educational Features scenarios ready for manual validation  
**Focus Areas**: 10-year multi-stage DCF, demo mode, interpretation sections, educational content, mobile UX preparation

## 📊 **Testing Coverage Summary**

### **✅ COMPREHENSIVE TESTING COVERAGE FOR**:
- **Phase 1**: 2-Agent AI Architecture (Scenarios 1-6)
- **Phase 2**: Multi-Model DCF Integration (Scenarios 7-14) 
- **Intelligent Caching**: Performance & TTL Strategy (Scenarios 15-18)
- **10-Year DCF System**: Mode Selection & Growth Engine (Scenarios 19-21)
- **Educational Features**: Progressive Disclosure & Demo Mode (Scenarios 22-23)
- **Investment Interpretation**: "What This Means" Sections (Scenarios 24-26)

### **📊 TESTING STATISTICS**:
- **Total Test Scenarios**: 26 comprehensive scenarios
- **API Endpoints Covered**: 15+ endpoints with sample commands
- **Company Test Data**: 20+ ticker symbols across sectors
- **User Experience Levels**: Beginner, Intermediate, Advanced testing
- **Platform Coverage**: Web interface, API, mobile preparation

### **🎯 NEXT PRIORITIES**:
1. **Mobile UX Testing** (Scenario 27+) - Touch interfaces and responsive design
2. **Performance Load Testing** - Multi-user concurrent analysis testing
3. **Integration Testing** - End-to-end user journey validation
4. **Accessibility Testing** - Screen reader and keyboard navigation support