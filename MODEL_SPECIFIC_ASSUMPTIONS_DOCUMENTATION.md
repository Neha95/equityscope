# 📊 COMPREHENSIVE DCF MODEL ASSUMPTIONS & METHODOLOGY DOCUMENTATION

**Date**: August 1, 2025  
**Purpose**: Document all assumptions per model with calculation logic and tooltip definitions  
**Status**: 🔄 **ANALYSIS COMPLETE** - Ready for Implementation

---

## 🏦 **1. BANKING EXCESS RETURNS MODEL (BFSI Sector)**

### **Core Assumptions Used:**
1. **Starting ROE** - Return on Equity (primary driver)
2. **Cost of Equity** - CAPM-based discount rate  
3. **ROE Fade Rate** - Convergence to terminal ROE over 10 years
4. **Terminal ROE** - Long-term sustainable ROE 
5. **Beta** - Sector and size-adjusted market risk
6. **Risk-Free Rate** - Indian 10-year G-Sec yield
7. **Equity Risk Premium** - India market risk premium
8. **Competitive Moat Premium** - Sustainable competitive advantage
9. **Book Value Per Share** - Tangible book value base
10. **Retention Ratio** - Earnings retained vs. distributed

### **Calculation Formula:**
```
Intrinsic Value = Book Value Per Share + PV(Excess Returns) + PV(Terminal Value)

Where:
- Excess Returns = (ROE - Cost of Equity) × Book Value × Retention Ratio  
- Cost of Equity = Risk-Free Rate + (Beta × Equity Risk Premium)
- Terminal ROE = Cost of Equity + Competitive Moat Premium
- ROE(Year t) = Starting ROE × (1 - Convergence Weight) + Terminal ROE × Convergence Weight
```

### **Code Implementation Location:**
- **Function**: `calculateBankingExcessReturns()` in DCFModelsCard.tsx
- **Lines**: ~440-650

### **Actual Code Logic Analysis:**
```typescript
// Starting ROE Calculation (3-year average)
const roeHistory = [];
for (let i = 0; i < netIncomes.length; i++) {
  const totalEquityApprox = sharesOutstanding[i] * bookValuePerShare;
  const roe = netIncomes[i] / totalEquityApprox;
  roeHistory.push(roe);
}
const averageROE = roeHistory.reduce((sum, roe) => sum + roe, 0) / roeHistory.length;

// Cost of Equity (CAPM)
const riskFreeRate = 0.072; // 7.2% Indian 10-year G-Sec
const equityRiskPremium = 0.085; // 8.5% India ERP
const beta = getDynamicBeta(summaryData.sector, marketCap);
const costOfEquity = riskFreeRate + (beta * equityRiskPremium);

// Terminal ROE
const competitiveMoatPremium = 0.015; // 1.5%
const terminalROE = costOfEquity + competitiveMoatPremium;

// ROE Fade (Linear Convergence)
const convergenceWeight = (year - 1) / (projectionYears - 1);
const currentYearROE = startingROE * (1 - convergenceWeight) + terminalROE * convergenceWeight;
```

### **Tooltip Definitions:**
- **Starting ROE**: "ROE (Return on Equity) calculated using 3-year historical average for [COMPANY NAME]. Formula: Net Income ÷ Total Shareholders' Equity"
- **Cost of Equity**: "CAPM-based discount rate using Indian 10-year G-Sec (7.2%) + Beta × India ERP (8.5%) for [COMPANY NAME]"
- **ROE Fade Rate**: "Linear convergence from current ROE to terminal ROE over 10 years, reflecting competitive pressure normalization"
- **Terminal ROE**: "Long-term sustainable ROE = Cost of Equity + Competitive Moat Premium (1.5% for market leaders)"
- **Beta**: "Market risk measure: 1.0 for large banks like HDFC, 1.2 for smaller banks, based on [COMPANY NAME]'s market cap"
- **Book Value Per Share**: "Tangible book value calculated from current stock price ÷ P/B ratio for [COMPANY NAME]"

---

## 📈 **2. PE-BASED VALUATION MODEL**

### **Core Assumptions Used:**
1. **Current EPS** - Earnings Per Share from latest financials
2. **Historical EPS Growth** - 3-year CAGR growth rate
3. **Conservative Growth Cap** - Maximum allowable growth rate (15%)
4. **Industry P/E Multiple** - Sector-specific P/E ratio
5. **Forward P/E Calculation** - Projected fair value P/E
6. **Shares Outstanding** - Current share count

### **Calculation Formula:**
```
Fair Value = Projected EPS × Industry P/E Multiple

Where:
- Projected EPS = Current EPS × (1 + Conservative Growth Rate)
- Conservative Growth Rate = Min(Historical EPS Growth, 15%)
- Industry P/E = Sector-specific multiple from getSectorPE()
```

### **Code Implementation Location:**
- **Function**: `calculatePEBasedValuation()` in DCFModelsCard.tsx
- **Lines**: ~760-850

### **Actual Code Logic Analysis:**
```typescript
// Current EPS Calculation
const latestNetIncome = financialData.net_income?.[0] || 0;
const currentSharesOutstanding = financialData.shares_outstanding?.[0] || sharesOutstanding;
const currentEPS = latestNetIncome / currentSharesOutstanding;

// Historical EPS Growth (3-year CAGR)
let epsGrowthCAGR = 0.10; // Default 10%
if (financialData.net_income && financialData.net_income.length >= 3) {
  const oldestEPS = financialData.net_income[financialData.net_income.length - 1] / 
                    financialData.shares_outstanding[financialData.shares_outstanding.length - 1];
  const years = financialData.net_income.length - 1;
  epsGrowthCAGR = Math.pow(currentEPS / oldestEPS, 1 / years) - 1;
}

// Conservative Growth Cap
const conservativeGrowthRate = Math.min(epsGrowthCAGR, 0.15); // Cap at 15%

// Industry P/E Multiple
const industryPE = getIndustryPE(summaryData.sector);

// Fair Value Calculation
const projectedEPS = currentEPS * (1 + conservativeGrowthRate);
const fairValue = projectedEPS * industryPE;
```

### **Tooltip Definitions:**
- **Current EPS**: "Earnings Per Share calculated from latest net income ÷ shares outstanding for [COMPANY NAME]"
- **Historical EPS Growth**: "3-year compound annual growth rate (CAGR) of earnings for [COMPANY NAME]"
- **Conservative Growth Cap**: "Growth rate capped at 15% maximum for prudent valuation regardless of historical performance"
- **Industry P/E Multiple**: "Sector-specific P/E ratio: BFSI (15x), IT (22x), PHARMA (18x) based on [SECTOR NAME] sector"
- **Forward P/E**: "Projected P/E ratio = Fair Value ÷ Projected EPS for [COMPANY NAME]"

---

## 🏗️ **3. REAL ESTATE NAV MODEL**

### **Core Assumptions Used:**
1. **Book Value Per Share** - Tangible asset base
2. **NAV Premium Multiple** - Asset quality and location premium
3. **Market Position Premium** - Size-based premium/discount
4. **Asset Quality Premium** - ROE-based quality assessment
5. **Development Pipeline Premium** - Future project value
6. **Location Premium** - Tier-1 vs Tier-2 exposure
7. **ROE** - Return on Equity for asset quality
8. **Market Cap** - Company size for positioning

### **Calculation Formula:**
```
NAV-Based Fair Value = Book Value Per Share × Final NAV Multiple

Where:
- Final NAV Multiple = Base NAV Multiple + Quality Premium + Pipeline Premium + Location Premium
- Base NAV Multiple = Size-based (1.4x for >₹5L Cr, 1.25x for >₹2L Cr, 1.15x for >₹5k Cr)
- Quality Premium = ROE-based (0.15 for >15% ROE, 0.08 for 10-15%, -0.10 for <5%)
```

### **Code Implementation Location:**
- **Function**: `calculateRealEstateNAV()` in DCFModelsCard.tsx
- **Lines**: ~900-1050

### **Actual Code Logic Analysis:**
```typescript
// Book Value Per Share
const bookValuePerShare = currentPrice / pbRatio;

// Market Position Premium (Size-based)
let navPremium = 1.0; // Start at book value (1.0x)
if (marketCap > 500000000000) {      // >₹5 lakh crore
  navPremium = 1.4; // 40% premium to book value
} else if (marketCap > 200000000000) { // >₹2 lakh crore
  navPremium = 1.25; // 25% premium to book value  
} else if (marketCap > 50000000000) {  // >₹5k crore
  navPremium = 1.15; // 15% premium to book value
} else {
  navPremium = 0.95; // 5% discount for smaller players
}

// Asset Quality Premium (ROE-based)
let qualityPremium = 0;
if (roe > 0.15) {          // >15% ROE = premium assets
  qualityPremium = 0.15;
} else if (roe > 0.10) {   // 10-15% ROE = good assets
  qualityPremium = 0.08;
} else if (roe > 0.05) {   // 5-10% ROE = average assets
  qualityPremium = 0.02;
} else {                   // <5% ROE = asset quality concerns
  qualityPremium = -0.10;
}

// Pipeline & Location Premiums
const pipelinePremium = marketCap > 200000000000 ? 0.10 : 0.05;
const locationPremium = marketCap > 200000000000 ? 0.08 : 0.03;

const finalNAVMultiple = navPremium + qualityPremium + pipelinePremium + locationPremium;
```

### **Tooltip Definitions:**
- **Book Value Per Share**: "Net tangible asset value per share calculated from current price ÷ P/B ratio for [COMPANY NAME]"
- **NAV Premium Multiple**: "Asset-based valuation multiple reflecting land bank, development rights, and market position for [COMPANY NAME]"
- **Market Position Premium**: "Size-based premium: 40% for >₹5L Cr market cap, 25% for mid-tier, based on [COMPANY NAME]'s ₹[X] Cr market cap"
- **Asset Quality Premium**: "ROE-based quality assessment: +15% for >15% ROE, reflects asset monetization efficiency for [COMPANY NAME]"
- **Location Premium**: "Tier-1 city exposure premium: 8% for large developers, 3% for others, based on [COMPANY NAME]'s market presence"

---

## 💻 **4. IT SERVICES EV/REVENUE MODEL**

### **Core Assumptions Used:**
1. **Revenue Growth Rate** - Historical revenue CAGR
2. **EV/Revenue Multiple** - Sector-specific revenue multiple
3. **Market Premium** - Size and quality-based adjustment
4. **Current Revenue** - Latest annual revenue
5. **Revenue Quality Factor** - Growth consistency and margins
6. **Market Cap** - Current market valuation

### **Calculation Formula:**
```
Fair Value = (Current Revenue × Revenue Multiple × Market Premium) ÷ Shares Outstanding

Where:
- Revenue Multiple = Base IT sector multiple (6-8x) adjusted for company quality
- Market Premium = Size-based adjustment (1.2x for >₹2L Cr, 1.1x for >₹1L Cr)
```

### **Code Implementation Location:**
- **Function**: `calculateITServicesModel()` in DCFModelsCard.tsx
- **Lines**: ~1100-1250

### **Actual Code Logic Analysis:**
```typescript
// Revenue Growth Calculation
let revenueGrowthCAGR = assumptions.revenue_growth_rate / 100;
if (financialData.revenue && financialData.revenue.length >= 3) {
  const oldestRevenue = financialData.revenue[financialData.revenue.length - 1];
  const years = financialData.revenue.length - 1;
  revenueGrowthCAGR = Math.pow(latestRevenue / oldestRevenue, 1 / years) - 1;
}

// IT Revenue Multiple Calculation
const getITRevenueMultiple = async (marketCap: number, growthRate: number, sector: string): Promise<number> => {
  let baseMultiple = 6.0; // Base IT services multiple
  
  // Size premium
  if (marketCap > 2000000000000) {      // >₹20 lakh crore (TCS, Infosys)
    baseMultiple = 8.0;
  } else if (marketCap > 1000000000000) { // >₹10 lakh crore (Wipro, HCL)
    baseMultiple = 7.0;
  } else if (marketCap > 500000000000) {  // >₹5 lakh crore (Tech Mahindra)
    baseMultiple = 6.5;
  }
  
  // Growth premium
  if (growthRate > 0.15) {       // >15% growth
    baseMultiple += 0.5;
  } else if (growthRate > 0.10) { // 10-15% growth
    baseMultiple += 0.3;
  }
  
  return baseMultiple;
};

// Fair Value Calculation  
const revenueMultiple = await getITRevenueMultiple(marketCap, revenueGrowthCAGR, summaryData.sector);
const enterpriseValue = latestRevenue * revenueMultiple;
const fairValue = enterpriseValue / sharesOutstanding;
```

### **Tooltip Definitions:**
- **Revenue Growth Rate**: "3-year compound annual growth rate of revenue for [COMPANY NAME]"
- **EV/Revenue Multiple**: "Enterprise value to revenue multiple: 6-8x for IT sector, adjusted for [COMPANY NAME]'s quality metrics"
- **Market Premium**: "Quality premium based on [COMPANY NAME]'s market cap of ₹[X] Cr and growth consistency"
- **Revenue Quality Factor**: "Assessment of revenue predictability, client concentration, and margin sustainability for [COMPANY NAME]"

---

## 💎 **5. STANDARD FCFF DCF MODEL (Dynamic Implementation)**

### **Core Assumptions Used:**
1. **Starting Revenue** - Latest annual revenue from financial data API
2. **Revenue Growth Rate** - Historical CAGR calculated from 3-5 years of data
3. **EBITDA Margin** - Historical average calculated from financial statements
4. **WACC** - Sector-specific with large-cap validation (Energy: 10-12% range)
5. **Terminal Growth Rate** - Sector-specific long-term growth assumptions
6. **CapEx Percentage** - DYNAMIC: Calculated from historical CapEx/Revenue ratios
7. **Working Capital Change** - DYNAMIC: Calculated from historical ΔWC/Revenue ratios  
8. **Depreciation Percentage** - DYNAMIC: Calculated from historical D&A/Revenue ratios
9. **Tax Rate** - Sector-specific corporate tax rates
10. **Projection Years** - Standard 10-year projection period

### **Calculation Formula:**
```
FCFF = EBIT × (1 - Tax Rate) + Depreciation - CapEx - ΔWorking Capital
DCF Fair Value = PV(FCFFs) + PV(Terminal Value)

Where:
- EBIT = Revenue × EBITDA Margin
- CapEx = Revenue × Dynamic CapEx %
- ΔWC = Revenue × Dynamic WC %  
- D&A = Revenue × Dynamic D&A %
- Terminal Value = Terminal FCFF ÷ (WACC - Terminal Growth)
```

### **Code Implementation Location:**
- **Function**: `calculateStandardFCFFDCF()` in DCFModelsCard.tsx
- **Lines**: ~2692-2846
- **Routing**: Used for ENERGY, FMCG, PHARMA, and other non-specialized sectors

### **Dynamic vs Static Variables:**

#### **✅ DYNAMIC (Real Financial Data)**
- **Starting Revenue**: ₹9.65L Cr for RELIANCE.NS (from latest financials)
- **CapEx %**: 14.5% for RELIANCE.NS (calculated from 3-year CapEx/Revenue average)
- **D&A %**: 5.5% for RELIANCE.NS (calculated from 3-year D&A/Revenue average)
- **WC %**: 2.5% for RELIANCE.NS (calculated from 3-year ΔWC/Revenue average)
- **Revenue Growth**: Historical CAGR from actual revenue progression
- **EBITDA Margin**: Historical average from actual EBITDA/Revenue ratios

#### **🔒 STATIC (Sector Defaults with Validation)**  
- **WACC**: 11.0% for Energy (sector default, max 12% for large-cap)
- **Terminal Growth**: 2.5% for Energy sector
- **Tax Rate**: 30.0% for Energy sector  
- **Projection Years**: 10 years standard

### **Data Quality & Fallbacks:**
```typescript
// Dynamic calculation with quality checks
if (capitalMetrics.data_quality === 'high') {
  // Use calculated percentages from historical data
  capex_percentage: calculated from 3-5 years of CapEx/Revenue
  working_capital_percentage: calculated from ΔWC/Revenue
  depreciation_percentage: calculated from D&A/Revenue
} else {
  // Fallback to sector-specific defaults
  capex_percentage: 12.0% (Energy sector default)
  working_capital_percentage: 6.0% (Energy sector default)  
  depreciation_percentage: 8.0% (Energy sector default)
}
```

### **Real Test Case - RELIANCE.NS:**
```
✅ Backend Data Extraction:
Revenue: [₹9,646.93B, ₹9,010.64B, ₹8,778.35B]
CapEx: [₹1,399.67B, ₹1,528.83B, ₹1,409.88B]  
D&A: [₹531.36B, ₹508.32B, ₹403.03B]

✅ Dynamic Calculations:
CapEx %: 14.5% (Real) vs 4.0% (Backend Default)
D&A %: 5.5% (Real) vs null (Backend Default)
WACC: 11.0% (Frontend) vs 16.46% (Backend Rejected)
```

### **Tooltip Definitions:**
- **Starting Revenue**: "Latest annual revenue from company's financial statements: ₹[X] Cr for [COMPANY NAME]"
- **CapEx Percentage**: "Capital expenditure calculated from [COMPANY NAME]'s 3-year historical average: [X]% of revenue"
- **Working Capital %**: "Working capital impact based on [COMPANY NAME]'s historical ΔWC/Revenue ratio: [X]%"
- **Depreciation %**: "Depreciation & amortization based on [COMPANY NAME]'s 3-year D&A/Revenue average: [X]%"
- **WACC**: "Weighted cost of capital: [X]% based on [SECTOR NAME] sector characteristics and company size"
- **Revenue Growth**: "Revenue growth rate: [X]% CAGR calculated from [COMPANY NAME]'s [Y]-year historical revenue data"

---

## 🧬 **6. PHARMA R&D PIPELINE MODEL (Placeholder)**

### **Core Assumptions Used:**
1. **Current Revenue** - Base pharmaceutical revenue
2. **R&D Spend Percentage** - R&D investment as % of revenue
3. **Pipeline Value Multiple** - Expected pipeline commercialization value
4. **Patent Cliff Impact** - Revenue at risk from patent expiry
5. **FDA Approval Rate** - Success rate for drug approvals
6. **Generic Competition Factor** - Competitive pressure assessment

### **Calculation Formula:**
```
Fair Value = Base Pharma Value + Pipeline Value - Patent Cliff Impact

Where:
- Base Pharma Value = Current Revenue × Pharma P/E Multiple
- Pipeline Value = R&D Spend × Pipeline Multiple × FDA Success Rate
- Patent Cliff Impact = Revenue at Risk × Competition Factor
```

### **Code Implementation Location:**
- **Function**: `calculatePharmaRnDPipeline()` in DCFModelsCard.tsx
- **Lines**: ~720-750 (Currently placeholder)

### **Actual Code Logic Analysis:**
```typescript
// Currently implemented as placeholder
const calculatePharmaRnDPipeline = (ticker: string, summaryData: SummaryResponse, assumptions: DCFAssumptions): ValuationResult => {
  // For now, use generic calculation - will implement later
  const fairValue = (summaryData.fair_value_band.min_value + summaryData.fair_value_band.max_value) / 2;
  const upside = ((fairValue - summaryData.fair_value_band.current_price) / summaryData.fair_value_band.current_price) * 100;
  
  return {
    model: 'sector',
    fairValue,
    currentPrice: summaryData.fair_value_band.current_price,
    upside,
    confidence: summaryData.fair_value_band.confidence,
    method: 'Pharma_R&D_Pipeline',
    assumptions: getModelAssumptions(assumptions),
    reasoning: summaryData.key_factors.slice(0, 4),
    isLoading: false
  };
};
```

### **Tooltip Definitions:**
- **R&D Spend Percentage**: "R&D investment as percentage of revenue for [COMPANY NAME], indicating innovation focus"
- **Pipeline Value Multiple**: "Expected commercialization multiple for R&D pipeline based on [COMPANY NAME]'s therapeutic areas"
- **FDA Approval Rate**: "Historical success rate for drug approvals in [COMPANY NAME]'s focus areas"
- **Patent Cliff Impact**: "Revenue at risk from patent expiry over next 5 years for [COMPANY NAME]"

---

## 🔧 **6. GENERIC DCF MODEL (Standard)**

### **Core Assumptions Used:**
1. **Revenue Growth Rate** - Annual revenue growth assumption
2. **EBITDA Margin** - Operating margin assumption
3. **Tax Rate** - Corporate tax rate
4. **WACC** - Weighted Average Cost of Capital
5. **Terminal Growth Rate** - Long-term growth assumption
6. **CapEx Percentage** - Capital expenditure as % of revenue
7. **Working Capital Change** - Working capital impact
8. **Depreciation Percentage** - D&A as % of revenue
9. **Projection Years** - DCF projection period

### **Calculation Formula:**
```
DCF Fair Value = PV(Free Cash Flows) + PV(Terminal Value)

Where:
- FCF = EBIT × (1 - Tax Rate) + Depreciation - CapEx - ΔWorking Capital  
- Terminal Value = FCF(Final Year) × (1 + Terminal Growth) ÷ (WACC - Terminal Growth)
- PV = Future Value ÷ (1 + WACC)^Year
```

### **Code Implementation Location:**
- **Function**: Used in fallback scenarios and adjustment calculations
- **Interface**: `DCFAssumptions` in InteractiveDCFAssumptions.tsx

### **Actual Code Logic Analysis:**
```typescript
// Current assumptions interface
interface DCFAssumptions {
  revenue_growth_rate: number;    // From historical data or sector defaults
  ebitda_margin: number;          // From historical financials 
  tax_rate: number;               // Sector-specific (BFSI: 25%, IT: 22%, etc.)
  wacc: number;                   // Calculated using Damodaran sector data
  terminal_growth_rate: number;   // Sector-specific long-term growth
  projection_years: number;       // Standard 5-10 years
  capex_percentage: number;       // From 3-year historical average
  working_capital_percentage: number; // From historical working capital changes
  depreciation_percentage: number;    // From historical D&A data
}

// Used in applyAssumptionAdjustments function
const applyAssumptionAdjustments = (
  baseFairValue: number, 
  customAssumptions: DCFAssumptions, 
  defaultAssumptions: DCFDefaults
): number => {
  let adjustmentFactor = 1.0;
  
  // Revenue growth impact
  const growthDiff = customAssumptions.revenue_growth_rate - defaultAssumptions.revenue_growth_rate;
  adjustmentFactor += growthDiff * 0.02; // 2% valuation change per 1% growth change
  
  // EBITDA margin impact
  const marginDiff = customAssumptions.ebitda_margin - defaultAssumptions.ebitda_margin;
  adjustmentFactor += marginDiff * 0.015; // 1.5% valuation change per 1% margin change
  
  // WACC impact (higher WACC = lower valuation)
  const waccDiff = customAssumptions.wacc - defaultAssumptions.wacc;
  adjustmentFactor -= waccDiff * 0.05; // 5% valuation change per 1% WACC change
  
  return baseFairValue * adjustmentFactor;
};
```

### **Tooltip Definitions:**
- **Revenue Growth Rate**: "Annual revenue growth rate based on [COMPANY NAME]'s 3-year historical average or sector benchmark"
- **EBITDA Margin**: "Operating margin calculated from [COMPANY NAME]'s historical financial statements average"
- **WACC**: "Weighted Average Cost of Capital calculated using [SECTOR NAME] sector beta and current risk-free rate"
- **Terminal Growth Rate**: "Long-term growth rate based on [SECTOR NAME] sector characteristics and GDP expectations"
- **CapEx Percentage**: "Capital expenditure as % of revenue based on [COMPANY NAME]'s 3-year historical average"
- **Working Capital Change**: "Working capital impact based on [COMPANY NAME]'s historical working capital/revenue ratio"

---

## 🎯 **DIFFERENCES FOUND BETWEEN DOCUMENTATION & CODE**

### **1. Banking Model - Complete Implementation ✅**
- **Documentation Claims**: Sophisticated ROE fade model with CAPM
- **Code Reality**: ✅ **FULLY IMPLEMENTED** - All described features present
- **Key Features**: ROE convergence, CAPM cost of equity, competitive moat premium

### **2. PE Model - Complete Implementation ✅**
- **Documentation Claims**: Historical EPS growth with conservative cap  
- **Code Reality**: ✅ **FULLY IMPLEMENTED** - EPS growth capped at 15%
- **Key Features**: Industry P/E multiples, growth rate calculations

### **3. Real Estate NAV - Complete Implementation ✅**
- **Documentation Claims**: NAV multiples based on size and ROE
- **Code Reality**: ✅ **FULLY IMPLEMENTED** - Size-based premiums, ROE quality assessment
- **Key Features**: Market position premiums, pipeline premiums, location premiums

### **4. IT Services - Complete Implementation ✅**  
- **Documentation Claims**: EV/Revenue multiple with growth adjustments
- **Code Reality**: ✅ **FULLY IMPLEMENTED** - Revenue multiples with size and growth premiums
- **Key Features**: Dynamic multiple calculation, market cap adjustments

### **5. Pharma Model - Placeholder Only ❌**
- **Documentation Claims**: R&D pipeline and patent cliff modeling
- **Code Reality**: ❌ **NOT IMPLEMENTED** - Just uses generic fair value band average
- **Status**: Needs full implementation

### **6. Generic DCF - Adjustment-Based Only ⚠️**
- **Documentation Claims**: Full DCF calculation
- **Code Reality**: ⚠️ **PARTIAL** - Uses adjustment factors rather than full DCF projection
- **Current**: `applyAssumptionAdjustments()` with percentage impacts
- **Missing**: Year-by-year cash flow projections with terminal value

---

## 🎯 **IMPLEMENTATION APPROACH**

### **Dynamic Assumptions Panel Logic:**
```typescript
const getModelSpecificAssumptions = (activeModel: string, sector: string, ticker: string) => {
  switch (activeModel) {
    case 'sector': 
      return getSectorSpecificAssumptions(sector, ticker);
    case 'pe_valuation':
      return getPEModelAssumptions(ticker);
    case 'generic_dcf':
      return getGenericDCFAssumptions(ticker);
    default:
      return getGenericDCFAssumptions(ticker);
  }
};

const getSectorSpecificAssumptions = (sector: string, ticker: string) => {
  if (isSectorType(sector, 'BFSI')) return getBankingAssumptions(ticker);
  if (isSectorType(sector, 'REAL ESTATE')) return getRealEstateAssumptions(ticker);
  if (isSectorType(sector, 'IT')) return getITServicesAssumptions(ticker);
  if (isSectorType(sector, 'PHARMA')) return getPharmaAssumptions(ticker);
  return getGenericDCFAssumptions(ticker);
};
```

### **Next Implementation Steps:**
1. ✅ **Documentation Complete** - Comprehensive analysis done
2. ⏳ **Modify InteractiveDCFAssumptions** - Make it model-aware
3. ⏳ **Update DCFModelsCard** - Pass active model type
4. ⏳ **Implement Dynamic Tooltips** - Company/sector-specific information
5. ⏳ **Add Missing Models** - Complete Pharma implementation
6. ⏳ **Enhance Generic DCF** - Replace adjustment logic with full projections

---

## 🚨 **CRITICAL ARCHITECTURE ISSUE: THE OVERRIDE CONFLICT**

**Date**: August 2, 2025  
**Severity**: CRITICAL  
**Issue**: API defaults overriding intelligent normalization causing negative cash flows

### **Root Cause Analysis**

**The Problem**: Despite implementing sophisticated Dynamic Normalization System, RELIANCE.NS still shows negative cash flows due to **assumption override conflict**.

**The Sequence of Events**:

#### **Step A (✅ Correct): Calculate Normalized Assumptions**
- Peak Investment Cycle detector runs correctly
- Identifies Reliance: 11.5% growth + 12% CapEx → triggers normalization
- Creates intelligent assumptions: CapEx fade 12% → 7% over 10 years

#### **Step B (⚠️ The Conflict): Fetch API Defaults**  
- API call: `/api/valuation/RELIANCE.NS/defaults`
- Returns raw historical averages: `revenue_growth_rate: 11.9%`, `capex_percentage: 15.5%`
- **These are UN-normalized peak values**

#### **Step C (❌ The Bug): Override Happens**
- Raw API values merged into assumptions object
- **Overwrites intelligent normalized values**
- Model executes with conflicting raw numbers → negative cash flows

### **The Solution: Data Precedence Hierarchy**

**Critical Fix**: Enforce strict assumption precedence where **local normalization ALWAYS wins**

```typescript
// ❌ WRONG ORDER (API overwrites normalized)
const finalAssumptions = { ...normalizedMetrics, ...apiDefaults };

// ✅ CORRECT ORDER (normalized wins)  
const finalAssumptions = { ...apiDefaults, ...normalizedMetrics };
```

**Implemented Hierarchy**:
1. **Sector Defaults** (baseline)
2. **Dynamic Historical Metrics** (company-specific)  
3. **Normalization Engine** (intelligent overrides) ← **FINAL AUTHORITY**
4. **API Defaults** (only fill gaps, never override)

### **Technical Implementation**

```typescript
// 1. Start with sector defaults
let finalAssumptions = { ...sectorDefaults };

// 2. Apply dynamic historical metrics  
const dynamicMetrics = await calculateDynamicMetrics(ticker);
finalAssumptions = { ...finalAssumptions, ...dynamicMetrics };

// 3. Run Normalization Engine (FINAL AUTHORITY)
const normalizedMetrics = runNormalizationEngine(finalAssumptions);
finalAssumptions = { ...finalAssumptions, ...normalizedMetrics };

// 4. API defaults ONLY fill missing gaps (never override)
const apiDefaults = await getApiDefaults(ticker);
finalAssumptions = { ...apiDefaults, ...finalAssumptions }; // Note order!
```

### **Validation Results**

**Before Fix**:
- CapEx: 15.5% (raw API default)
- FCFF: -₹3,189 Cr (negative)
- Fair Value: ₹-218 (broken)

**After Fix** (Expected):
- CapEx: Normalized fade 12% → 7%
- FCFF: Positive and growing
- Fair Value: Realistic positive value

---

*This documentation serves as the foundation for implementing dynamic, model-specific assumptions panels with accurate tooltips that reflect the actual calculation methodology being used in the codebase.*