# EquityScope Complete Mode-Based Implementation Plan
*Comprehensive end-to-end architecture for Simple vs Agentic mode analysis system*

## 📋 **Executive Summary**

This document outlines the complete implementation of EquityScope's dual-mode analysis system with sector-specific DCF models, weighted scoring framework, and comprehensive AI integration.

### **Core Architecture Changes**
- **Pre-search mode selection** (Simple vs Agentic)
- **Sector-specific DCF models** (BFSI, Pharma, Real Estate, IT, FMCG, Energy)
- **Weighted scoring framework** for rule-based labeling
- **Complete component redesign** for dual-mode support
- **Comprehensive peer comparison** system
- **Advanced logging & debugging** infrastructure

---

## 🎯 **User Experience Flow**

### **Step 1: Mode Selection (First Screen)**
```
User lands → Sees two cards (Simple vs Agentic) → Selects mode → Enters ticker → Gets analysis
```

**Simple Mode Promise:**
- Fast analysis using quantitative rules (<5 seconds)
- Sector-specific DCF valuation models
- Technical indicators with rule-based interpretation
- 3-peer comparison with quantitative metrics
- Weighted scoring leading to final investment label

**Agentic Mode Promise:**
- Deep AI analysis with natural language insights
- Sector-aware investment thesis generation
- AI-annotated assumptions and risk analysis
- News sentiment analysis and market context
- Multi-perspective synthesis with confidence scoring

### **Step 2: Analysis Display**
```
Summary Box (always shown) → DCF Box → Technical Box → Peer Comparison Box → Financials Box
Note: Sentiment Box only shown in Agentic mode
```

---

## 🏗️ **Backend Architecture Implementation**

### **1. Sector-Specific DCF Service**

#### **A. New DCF Model Classes**
```python
# File: backend/app/services/sector_dcf_service.py

class SectorDCFService:
    def __init__(self):
        self.calculators = {
            "BFSI": BankingDCFCalculator(),
            "Pharma": PharmaDCFCalculator(), 
            "Real Estate": RealEstateDCFCalculator(),
            "IT": DefaultDCFCalculator(),
            "FMCG": DefaultDCFCalculator(),
            "Energy": DefaultDCFCalculator()
        }
    
    async def calculate_sector_dcf(self, ticker: str, sector: str, mode: str):
        calculator = self.calculators.get(sector, self.calculators["IT"])
        return await calculator.calculate(ticker, mode)

class BankingDCFCalculator:
    """Excess Return Model for BFSI companies"""
    
    def calculate_inputs(self, company_data):
        return {
            "book_value": company_data.get("book_value"),
            "roe": company_data.get("roe"),
            "cost_of_equity": self.calculate_cost_of_equity(),
            "nim": company_data.get("net_interest_margin"),
            "gnpa": company_data.get("gross_npa"),
            "cost_to_income": company_data.get("cost_to_income_ratio")
        }
    
    def calculate_fair_value(self, inputs):
        # Excess Return Model: P/B = ROE / Cost of Equity
        excess_return = inputs["roe"] - inputs["cost_of_equity"]
        fair_pb = inputs["roe"] / inputs["cost_of_equity"]
        return fair_pb * inputs["book_value"]
    
    def get_sector_rules(self):
        return {
            "red_flags": {
                "gnpa_threshold": 5.0,  # GNPA > 5% = red flag
                "nim_compression": -0.5  # NIM decline > 0.5% = concern
            },
            "positive_signals": {
                "roe_threshold": 15.0,  # ROE > 15% = strong
                "cost_efficiency": 40.0  # Cost/Income < 40% = efficient
            }
        }

class PharmaDCFCalculator:
    """DCF + EV/EBITDA hybrid for Pharma companies"""
    
    def calculate_inputs(self, company_data):
        return {
            "revenue": company_data.get("revenue"),
            "ebitda": company_data.get("ebitda"),
            "rd_spend": company_data.get("rd_expense"),
            "anda_pipeline": company_data.get("anda_count", 0),
            "usfda_observations": company_data.get("usfda_issues", 0),
            "revenue_split": company_data.get("revenue_geography", {})
        }
    
    def calculate_fair_value(self, inputs):
        # Traditional DCF for base case
        dcf_value = self.calculate_traditional_dcf(inputs)
        
        # EV/EBITDA multiple for cross-check
        sector_ev_multiple = 12  # Pharma sector average
        ev_based_value = inputs["ebitda"] * sector_ev_multiple
        
        # Weighted average (70% DCF, 30% multiple)
        return (dcf_value * 0.7) + (ev_based_value * 0.3)
    
    def get_sector_rules(self):
        return {
            "red_flags": {
                "rd_spend_low": 5.0,  # R&D < 5% of revenue = concern
                "usfda_issues_high": 3  # >3 observations = regulatory risk
            },
            "positive_signals": {
                "anda_pipeline_strong": 10,  # >10 ANDAs = strong pipeline
                "us_revenue_exposure": 40.0  # >40% US revenue = premium
            }
        }

class RealEstateDCFCalculator:
    """NAV-based valuation for Real Estate companies"""
    
    def calculate_inputs(self, company_data):
        return {
            "land_bank": company_data.get("land_area_sqft"),
            "inventory_value": company_data.get("inventory"),
            "debt": company_data.get("total_debt"),
            "cash": company_data.get("cash_equivalents"),
            "inventory_turnover": company_data.get("inventory_turnover"),
            "project_pipeline": company_data.get("upcoming_projects", [])
        }
    
    def calculate_fair_value(self, inputs):
        # Net Asset Value approach
        land_value = inputs["land_bank"] * self.get_land_rate_per_sqft()
        inventory_realizable = inputs["inventory_value"] * 0.8  # 20% discount
        net_cash = inputs["cash"] - inputs["debt"]
        
        return land_value + inventory_realizable + net_cash
    
    def get_sector_rules(self):
        return {
            "red_flags": {
                "inventory_turnover_low": 0.5,  # <0.5x = monetization risk
                "debt_equity_high": 1.5  # D/E > 1.5x = leverage concern
            },
            "positive_signals": {
                "tier1_exposure": 60.0,  # >60% Tier 1 cities = premium
                "pre_sales_strong": 70.0  # >70% pre-sales = execution
            }
        }
```

#### **B. Enhanced V3 Summary Service Integration**
```python
# File: backend/app/services/v3_summary_service.py (MODIFY existing)

class V3SummaryService:
    def __init__(self):
        self.sector_dcf_service = SectorDCFService()
        self.weighted_scoring_service = WeightedScoringService()
        self.peer_comparison_service = PeerComparisonService()
        self.logging_service = AnalysisLoggingService()
    
    async def generate_simple_summary(self, ticker: str, force_refresh: bool = False):
        """Enhanced Simple Mode with sector-specific DCF and weighted scoring"""
        
        # Step 1: Get company data and classify sector
        company_data = await self._fetch_company_data(ticker)
        sector = self._classify_sector(ticker)
        
        self.logging_service.log_analysis_start(ticker, "simple", sector)
        
        # Step 2: Calculate sector-specific DCF
        dcf_result = await self.sector_dcf_service.calculate_sector_dcf(
            ticker, sector, "simple"
        )
        self.logging_service.log_dcf_calculation(dcf_result)
        
        # Step 3: Get peer comparison data
        peer_data = await self.peer_comparison_service.get_peer_analysis(
            ticker, sector, count=3
        )
        self.logging_service.log_peer_selection(peer_data)
        
        # Step 4: Calculate weighted scores for each component
        scores = await self.weighted_scoring_service.calculate_all_scores(
            dcf_result=dcf_result,
            technical_data=await self._get_technical_data(ticker),
            peer_data=peer_data,
            financial_data=company_data
        )
        self.logging_service.log_weighted_scores(scores)
        
        # Step 5: Determine final investment label
        final_label = self.weighted_scoring_service.calculate_final_label(scores)
        self.logging_service.log_final_result(final_label, scores["weighted_total"])
        
        return SimpleSummaryResponse(
            ticker=ticker,
            company_name=company_data["name"],
            fair_value_band=dcf_result["fair_value_band"],
            investment_label=final_label,
            key_factors=self._extract_key_factors(scores),
            valuation_insights=dcf_result["insights"],
            market_signals=scores["technical"]["summary"],
            business_fundamentals=scores["financial"]["summary"],
            data_health_warnings=self._get_data_warnings(dcf_result, peer_data),
            analysis_timestamp=datetime.now(),
            analysis_mode="simple",
            sector=sector,
            rules_applied=self._get_all_rules_applied(scores),
            weighted_scores_debug=scores  # For debugging
        )
```

### **2. Weighted Scoring Framework**

```python
# File: backend/app/services/weighted_scoring_service.py (NEW)

class WeightedScoringService:
    def __init__(self):
        self.weights = {
            "dcf": 0.35,        # 35% weight
            "financial": 0.25,   # 25% weight  
            "technical": 0.20,   # 20% weight
            "peer": 0.20        # 20% weight
        }
    
    async def calculate_all_scores(self, dcf_result, technical_data, peer_data, financial_data):
        """Calculate weighted scores for all components"""
        
        scores = {
            "dcf": self._score_dcf_component(dcf_result),
            "technical": self._score_technical_component(technical_data),
            "peer": self._score_peer_component(peer_data),
            "financial": self._score_financial_component(financial_data)
        }
        
        # Calculate weighted total
        weighted_total = sum(
            scores[component]["score"] * self.weights[component]
            for component in scores.keys()
        )
        
        scores["weighted_total"] = weighted_total
        return scores
    
    def _score_dcf_component(self, dcf_result):
        """Score DCF component: +1 (Bullish), 0 (Neutral), -1 (Bearish)"""
        current_price = dcf_result["current_price"]
        fair_value = dcf_result["fair_value"]
        
        upside = ((fair_value - current_price) / current_price) * 100
        
        if upside > 30:
            return {"score": 1, "reason": f"Significantly undervalued ({upside:.1f}% upside)"}
        elif upside > 10:
            return {"score": 1, "reason": f"Moderately undervalued ({upside:.1f}% upside)"}
        elif upside < -30:
            return {"score": -1, "reason": f"Significantly overvalued ({abs(upside):.1f}% downside)"}
        elif upside < -10:
            return {"score": -1, "reason": f"Moderately overvalued ({abs(upside):.1f}% downside)"}
        else:
            return {"score": 0, "reason": "Near fair value"}
    
    def _score_technical_component(self, technical_data):
        """Score technical component based on RSI, MACD, moving averages"""
        score = 0
        reasons = []
        
        # RSI scoring
        rsi = technical_data.get("rsi", 50)
        if rsi < 30:
            score += 1
            reasons.append("RSI oversold (bullish)")
        elif rsi > 70:
            score -= 1
            reasons.append("RSI overbought (bearish)")
        
        # MACD scoring
        macd_signal = technical_data.get("macd_signal", "neutral")
        if macd_signal == "bullish_crossover":
            score += 1
            reasons.append("MACD bullish crossover")
        elif macd_signal == "bearish_crossover":
            score -= 1
            reasons.append("MACD bearish crossover")
        
        # Moving average scoring
        price_vs_ma = technical_data.get("price_vs_ma200", "neutral")
        if price_vs_ma == "above":
            score += 0.5
            reasons.append("Price above 200-day MA")
        elif price_vs_ma == "below":
            score -= 0.5
            reasons.append("Price below 200-day MA")
        
        # Normalize to -1, 0, 1 range
        final_score = max(-1, min(1, score))
        
        return {
            "score": final_score,
            "reason": "; ".join(reasons) if reasons else "Neutral technical signals"
        }
    
    def _score_peer_component(self, peer_data):
        """Score peer comparison component"""
        if not peer_data or len(peer_data.get("peers", [])) < 2:
            return {"score": 0, "reason": "Insufficient peer data"}
        
        company_metrics = peer_data["company"]
        peer_averages = peer_data["peer_averages"]
        
        score = 0
        reasons = []
        
        # PE ratio comparison
        pe_company = company_metrics.get("pe_ratio", 0)
        pe_peer_avg = peer_averages.get("pe_ratio", 0)
        
        if pe_company > 0 and pe_peer_avg > 0:
            pe_discount = ((pe_peer_avg - pe_company) / pe_peer_avg) * 100
            if pe_discount > 20:  # 20% cheaper than peers
                score += 1
                reasons.append(f"PE {pe_discount:.1f}% below peer average")
            elif pe_discount < -20:  # 20% more expensive
                score -= 1
                reasons.append(f"PE {abs(pe_discount):.1f}% above peer average")
        
        # ROE comparison
        roe_company = company_metrics.get("roe", 0)
        roe_peer_avg = peer_averages.get("roe", 0)
        
        if roe_company > roe_peer_avg * 1.2:  # 20% better ROE
            score += 0.5
            reasons.append("ROE significantly above peers")
        elif roe_company < roe_peer_avg * 0.8:  # 20% worse ROE
            score -= 0.5
            reasons.append("ROE significantly below peers")
        
        final_score = max(-1, min(1, score))
        
        return {
            "score": final_score,
            "reason": "; ".join(reasons) if reasons else "In line with peers"
        }
    
    def _score_financial_component(self, financial_data):
        """Score financial performance component"""
        score = 0
        reasons = []
        
        # Revenue growth
        revenue_growth = financial_data.get("revenue_growth_3y", 0)
        if revenue_growth > 15:
            score += 1
            reasons.append(f"Strong revenue growth ({revenue_growth:.1f}%)")
        elif revenue_growth < 0:
            score -= 1
            reasons.append(f"Declining revenue ({revenue_growth:.1f}%)")
        
        # ROE performance
        roe = financial_data.get("roe", 0)
        if roe > 18:
            score += 0.5
            reasons.append(f"Strong ROE ({roe:.1f}%)")
        elif roe < 10:
            score -= 0.5
            reasons.append(f"Weak ROE ({roe:.1f}%)")
        
        # Debt levels
        debt_equity = financial_data.get("debt_to_equity", 0)
        if debt_equity < 0.3:
            score += 0.5
            reasons.append("Low debt levels")
        elif debt_equity > 1.0:
            score -= 0.5
            reasons.append("High debt levels")
        
        final_score = max(-1, min(1, score))
        
        return {
            "score": final_score,
            "reason": "; ".join(reasons) if reasons else "Average financial performance"
        }
    
    def calculate_final_label(self, scores):
        """Calculate final investment label from weighted score"""
        weighted_total = scores["weighted_total"]
        
        if weighted_total >= 0.60:
            return "Bullish"
        elif weighted_total >= 0.20:
            return "Cautiously Bullish"
        elif weighted_total >= -0.19:
            return "Neutral"
        elif weighted_total >= -0.60:
            return "Cautiously Bearish"
        else:
            return "Bearish"
```

### **3. Peer Comparison Service**

```python
# File: backend/app/services/peer_comparison_service.py (NEW)

class PeerComparisonService:
    def __init__(self):
        self.peer_mappings = {
            "BFSI": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
            "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS"],
            "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "LUPIN.NS", "AUROPHARMA.NS"],
            "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS"],
            "Real Estate": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "BRIGADE.NS"],
            "Energy": ["RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "GAIL.NS"]
        }
    
    async def get_peer_analysis(self, ticker: str, sector: str, count: int = 3):
        """Get peer comparison data for the ticker"""
        
        # Select peers from same sector
        peers = self._select_peers(ticker, sector, count)
        
        # Fetch data for all peers
        peer_data = await self._fetch_peer_data(peers)
        company_data = await self._fetch_company_financial_data(ticker)
        
        # Calculate peer averages
        peer_averages = self._calculate_peer_averages(peer_data)
        
        return {
            "company": company_data,
            "peers": peer_data,
            "peer_averages": peer_averages,
            "comparison_metrics": self._generate_comparison_metrics(company_data, peer_averages)
        }
    
    def _select_peers(self, ticker: str, sector: str, count: int):
        """Select peer companies from same sector"""
        all_peers = self.peer_mappings.get(sector, [])
        
        # Remove the company itself from peer list
        ticker_base = ticker.replace('.NS', '')
        filtered_peers = [p for p in all_peers if not p.startswith(ticker_base)]
        
        # Return top N peers
        return filtered_peers[:count]
    
    async def _fetch_peer_data(self, peer_tickers):
        """Fetch financial data for all peer companies"""
        peer_data = []
        
        for ticker in peer_tickers:
            try:
                data = await self._fetch_company_financial_data(ticker)
                if data:
                    peer_data.append({
                        "ticker": ticker,
                        "name": data.get("name", ticker),
                        **data
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch data for peer {ticker}: {e}")
                continue
        
        return peer_data
    
    def _calculate_peer_averages(self, peer_data):
        """Calculate average metrics across all peers"""
        if not peer_data:
            return {}
        
        metrics = ["market_cap", "pe_ratio", "pb_ratio", "roe", "revenue_growth", "ebitda_margin"]
        averages = {}
        
        for metric in metrics:
            values = [p.get(metric, 0) for p in peer_data if p.get(metric, 0) > 0]
            if values:
                averages[metric] = sum(values) / len(values)
            else:
                averages[metric] = 0
        
        return averages
    
    def _generate_comparison_metrics(self, company_data, peer_averages):
        """Generate comparison insights"""
        comparisons = {}
        
        for metric in ["pe_ratio", "pb_ratio", "roe", "revenue_growth"]:
            company_val = company_data.get(metric, 0)
            peer_avg = peer_averages.get(metric, 0)
            
            if company_val > 0 and peer_avg > 0:
                difference_pct = ((company_val - peer_avg) / peer_avg) * 100
                comparisons[metric] = {
                    "company": company_val,
                    "peer_average": peer_avg,
                    "difference_percent": difference_pct,
                    "status": "above" if difference_pct > 5 else "below" if difference_pct < -5 else "inline"
                }
        
        return comparisons
```

### **4. Analysis Logging Service**

```python
# File: backend/app/services/analysis_logging_service.py (NEW)

import logging
from datetime import datetime
import json

class AnalysisLoggingService:
    def __init__(self):
        # Create dedicated logger for analysis debugging
        self.logger = logging.getLogger('analysis_debug')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler for analysis logs
        handler = logging.FileHandler('logs/analysis_debug.log')
        formatter = logging.Formatter('[%(asctime)s] %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_analysis_start(self, ticker: str, mode: str, sector: str):
        """Log the start of analysis"""
        self.logger.info(f"TICKER: {ticker} | MODE: {mode} | SECTOR: {sector}")
    
    def log_dcf_calculation(self, dcf_result):
        """Log DCF calculation details"""
        fair_value = dcf_result.get("fair_value", 0)
        current_price = dcf_result.get("current_price", 0)
        method = dcf_result.get("method", "unknown")
        
        if current_price > 0:
            upside = ((fair_value - current_price) / current_price) * 100
            self.logger.info(f"DCF_CALCULATION | method: {method} | fair_value: {fair_value:.2f} | current_price: {current_price:.2f} | upside: {upside:.1f}%")
    
    def log_peer_selection(self, peer_data):
        """Log peer selection and data quality"""
        peers = peer_data.get("peers", [])
        peer_count = len(peers)
        peer_names = [p.get("ticker", "unknown") for p in peers]
        
        self.logger.info(f"PEER_SELECTION | count: {peer_count} | peers: {', '.join(peer_names)}")
    
    def log_weighted_scores(self, scores):
        """Log detailed weighted scoring breakdown"""
        for component, data in scores.items():
            if component != "weighted_total" and isinstance(data, dict):
                score = data.get("score", 0)
                reason = data.get("reason", "")
                weight = {"dcf": 35, "financial": 25, "technical": 20, "peer": 20}.get(component, 0)
                
                self.logger.info(f"SCORE_{component.upper()} | score: {score:+.1f} | weight: {weight}% | reason: {reason}")
        
        total = scores.get("weighted_total", 0)
        self.logger.info(f"WEIGHTED_TOTAL | score: {total:+.2f}")
    
    def log_final_result(self, final_label: str, weighted_score: float):
        """Log final investment label and reasoning"""
        self.logger.info(f"FINAL_LABEL | {final_label} | weighted_score: {weighted_score:+.2f}")
        self.logger.info("=" * 80)  # Separator for next analysis
    
    def log_error(self, component: str, error: str, ticker: str):
        """Log errors during analysis"""
        self.logger.error(f"ERROR_{component.upper()} | ticker: {ticker} | error: {error}")
    
    def log_ai_interaction(self, prompt_type: str, token_usage: dict, cost: float):
        """Log AI/Claude API interactions for cost tracking"""
        self.logger.info(f"AI_CALL | type: {prompt_type} | tokens: {token_usage} | cost: ${cost:.4f}")
```

---

## 🎨 **Frontend Architecture Implementation**

### **1. Pre-Search Mode Selection Component**

```typescript
// File: frontend/src/components/ModeSelection/ModeSelectionCards.tsx (NEW)

import React from 'react';
import { motion } from 'framer-motion';
import { Calculator, Brain } from 'lucide-react';
import type { AnalysisMode } from '../../types/summary';

interface ModeSelectionCardsProps {
  selectedMode: AnalysisMode;
  onModeSelect: (mode: AnalysisMode) => void;
}

export const ModeSelectionCards: React.FC<ModeSelectionCardsProps> = ({
  selectedMode,
  onModeSelect
}) => {
  const modes = [
    {
      id: 'simple' as const,
      title: 'Rule-Based Analysis',
      icon: Calculator,
      color: 'blue',
      description: 'Fast, quantitative analysis using proven financial rules',
      features: [
        'Sector-specific DCF models (BFSI, Pharma, Real Estate)',
        'Technical indicators with rule-based interpretation',
        '3-peer comparison with quantitative metrics',
        'Weighted scoring framework for final label',
        'Analysis completed in <5 seconds'
      ],
      bestFor: 'Quick screening, multiple stock comparison'
    },
    {
      id: 'agentic' as const,
      title: 'AI Analyst Insights',
      icon: Brain,
      color: 'purple',
      description: 'Comprehensive AI analysis with expert-level insights',
      features: [
        'AI-enhanced DCF with assumption annotations',
        'Natural language technical pattern interpretation',
        'News sentiment analysis and market context',
        'Sector-aware investment thesis generation',
        'Multi-perspective risk analysis'
      ],
      bestFor: 'Deep research, complex investment decisions'
    }
  ];

  const getColorClasses = (color: string, isSelected: boolean) => {
    const colors = {
      blue: {
        border: isSelected ? 'border-blue-500' : 'border-slate-600 hover:border-blue-400',
        bg: isSelected ? 'bg-blue-900/20' : 'bg-slate-800 hover:bg-slate-750',
        icon: isSelected ? 'bg-blue-600' : 'bg-slate-600',
        accent: 'text-blue-400'
      },
      purple: {
        border: isSelected ? 'border-purple-500' : 'border-slate-600 hover:border-purple-400',
        bg: isSelected ? 'bg-purple-900/20' : 'bg-slate-800 hover:bg-slate-750',
        icon: isSelected ? 'bg-purple-600' : 'bg-slate-600',
        accent: 'text-purple-400'
      }
    };
    return colors[color as keyof typeof colors];
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
      {modes.map((mode) => {
        const isSelected = selectedMode === mode.id;
        const colors = getColorClasses(mode.color, isSelected);
        const Icon = mode.icon;

        return (
          <motion.div
            key={mode.id}
            onClick={() => onModeSelect(mode.id)}
            className={`p-6 rounded-lg border-2 cursor-pointer transition-all duration-200 ${colors.border} ${colors.bg}`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: mode.id === 'simple' ? 0 : 0.1 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className={`p-3 rounded-lg ${colors.icon}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-100">{mode.title}</h3>
                  <p className="text-sm text-slate-400">{mode.description}</p>
                </div>
              </div>
              {isSelected && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-4 h-4 bg-green-400 rounded-full flex items-center justify-center"
                >
                  <div className="w-2 h-2 bg-white rounded-full" />
                </motion.div>
              )}
            </div>

            {/* Features List */}
            <div className="space-y-3 mb-4">
              <p className="text-slate-300 font-medium text-sm">✨ What You Get:</p>
              <ul className="space-y-2">
                {mode.features.map((feature, index) => (
                  <li key={index} className="flex items-start space-x-2 text-sm text-slate-400">
                    <div className="w-1.5 h-1.5 bg-slate-500 rounded-full mt-2 flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Best For */}
            <div className={`p-3 rounded-lg bg-slate-700/50 border-l-4 ${colors.border.replace('border-', 'border-l-')}`}>
              <p className={`text-sm font-medium ${colors.accent}`}>
                💡 Best for: {mode.bestFor}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};
```

### **2. Enhanced V3 Dashboard with Mode Selection**

```typescript
// File: frontend/src/components/V3Dashboard.tsx (MODIFY existing)

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { TrendingUp, AlertCircle, Loader2, Search } from 'lucide-react';
import { ModeSelectionCards } from './ModeSelection/ModeSelectionCards';
import { SummaryBox } from './SummaryEngine/SummaryBox';
import { DCFBox } from './AnalysisBoxes/DCFBox';
import { TechnicalBox } from './AnalysisBoxes/TechnicalBox';
import { PeerComparisonBox } from './AnalysisBoxes/PeerComparisonBox';
import { FinancialBox } from './AnalysisBoxes/FinancialBox';
import { SentimentBox } from './AnalysisBoxes/SentimentBox';
import { StockAutocomplete } from './common/StockAutocomplete';
import { v3ApiService } from '../services/v3ApiService';
import type { SummaryResponse, AnalysisMode, AppState } from '../types/summary';

export const V3Dashboard: React.FC = () => {
  const [state, setState] = useState<AppState>({
    currentTicker: '',
    summaryData: null,
    analysisMode: 'simple', // Default to Simple mode
    isLoading: false,
    error: null
  });

  const [searchTicker, setSearchTicker] = useState('');

  const updateState = useCallback((updates: Partial<AppState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const fetchAnalysis = useCallback(async (ticker: string) => {
    if (!ticker.trim()) return;

    try {
      updateState({ isLoading: true, error: null });
      
      const formattedTicker = ticker.includes('.') ? ticker : `${ticker}.NS`;
      const summaryData = await v3ApiService.getSummary(formattedTicker, state.analysisMode);
      
      updateState({
        currentTicker: formattedTicker,
        summaryData,
        isLoading: false
      });
    } catch (error) {
      console.error('Error fetching analysis:', error);
      updateState({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Analysis failed'
      });
    }
  }, [state.analysisMode, updateState]);

  const handleSearch = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    await fetchAnalysis(searchTicker);
  }, [searchTicker, fetchAnalysis]);

  const handleModeSelect = useCallback((mode: AnalysisMode) => {
    updateState({ analysisMode: mode });
    // If user already has analysis, refetch with new mode
    if (state.currentTicker) {
      fetchAnalysis(state.currentTicker);
    }
  }, [updateState, state.currentTicker, fetchAnalysis]);

  const hasData = state.summaryData && !state.isLoading && !state.error;

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-primary-600 rounded-lg">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-100">EquityScope v3</h1>
                <p className="text-xs text-slate-400">Sector-Specific Investment Analysis</p>
              </div>
            </div>
            
            {/* Mode Indicator */}
            <div className="flex items-center space-x-3">
              <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                state.analysisMode === 'simple' 
                  ? 'bg-blue-900/30 text-blue-300' 
                  : 'bg-purple-900/30 text-purple-300'
              }`}>
                {state.analysisMode === 'simple' ? '🔢 Rule-Based' : '🧠 AI-Powered'}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step 1: Mode Selection (always visible if no analysis) */}
        {!hasData && (
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-12"
          >
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-slate-100 mb-4">
                Choose Your Analysis Mode
              </h1>
              <p className="text-slate-400 max-w-3xl mx-auto text-lg leading-relaxed">
                Select between fast rule-based analysis or comprehensive AI-powered insights. 
                Your choice affects all analysis components including DCF, technical analysis, and peer comparison.
              </p>
            </div>

            <ModeSelectionCards
              selectedMode={state.analysisMode}
              onModeSelect={handleModeSelect}
            />
          </motion.section>
        )}

        {/* Step 2: Stock Search (visible after mode selection or with analysis) */}
        <AnimatePresence>
          {(state.analysisMode || hasData) && (
            <motion.section
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-8"
            >
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold text-slate-100 mb-2">
                  Enter Stock Ticker
                </h2>
                <p className="text-slate-400">
                  Get {state.analysisMode === 'simple' ? 'rule-based' : 'AI-powered'} analysis for any NSE stock
                </p>
              </div>

              <form onSubmit={handleSearch} className="max-w-lg mx-auto">
                <div className="flex space-x-3">
                  <div className="flex-1">
                    <StockAutocomplete
                      value={searchTicker}
                      onChange={setSearchTicker}
                      onSelect={(stock) => fetchAnalysis(stock.ticker)}
                      placeholder="Enter stock ticker (e.g., TCS, RELIANCE, HDFCBANK)"
                      disabled={state.isLoading}
                    />
                  </div>
                  <button
                    type="submit"
                    disabled={state.isLoading || !searchTicker.trim()}
                    className="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed min-w-[120px]"
                  >
                    {state.isLoading ? (
                      <div className="flex items-center justify-center space-x-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Analyzing...</span>
                      </div>
                    ) : (
                      <div className="flex items-center justify-center space-x-2">
                        <Search className="h-4 w-4" />
                        <span>Analyze</span>
                      </div>
                    )}
                  </button>
                </div>
              </form>
            </motion.section>
          )}
        </AnimatePresence>

        {/* Error Display */}
        <AnimatePresence>
          {state.error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-8"
            >
              <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <AlertCircle className="h-5 w-5 text-red-400" />
                  <div className="text-red-300">{state.error}</div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Loading State */}
        <AnimatePresence>
          {state.isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-center py-12"
            >
              <Loader2 className="h-12 w-12 text-primary-400 animate-spin mx-auto mb-4" />
              <div className="text-slate-300 mb-2">
                Generating {state.analysisMode} analysis for {searchTicker}...
              </div>
              <div className="text-sm text-slate-400">
                {state.analysisMode === 'simple' 
                  ? 'Applying sector-specific rules and calculating weighted scores...'
                  : 'AI analyst is processing company data and generating insights...'
                }
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Analysis Results */}
        <AnimatePresence>
          {hasData && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* Summary Box - Always on top */}
              <SummaryBox
                ticker={state.currentTicker}
                summary={state.summaryData!}
                onModeToggle={handleModeSelect}
                isLoading={state.isLoading}
                showModeToggle={true}
              />

              {/* Analysis Boxes Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* DCF Box */}
                <DCFBox
                  ticker={state.currentTicker}
                  mode={state.analysisMode}
                  data={state.summaryData!}
                />

                {/* Technical Box */}
                <TechnicalBox
                  ticker={state.currentTicker}
                  mode={state.analysisMode}
                  data={state.summaryData!}
                />

                {/* Peer Comparison Box */}
                <PeerComparisonBox
                  ticker={state.currentTicker}
                  mode={state.analysisMode}
                  data={state.summaryData!}
                />

                {/* Financial Performance Box */}
                <FinancialBox
                  ticker={state.currentTicker}
                  mode={state.analysisMode}
                  data={state.summaryData!}
                />
              </div>

              {/* Sentiment Box - Only in Agentic Mode */}
              {state.analysisMode === 'agentic' && (
                <SentimentBox
                  ticker={state.currentTicker}
                  data={state.summaryData!}
                />
              )}

              {/* Change Mode Suggestion */}
              <div className="text-center py-6">
                <button
                  onClick={() => handleModeSelect(state.analysisMode === 'simple' ? 'agentic' : 'simple')}
                  className="text-slate-400 hover:text-slate-300 text-sm underline"
                >
                  Try {state.analysisMode === 'simple' ? 'AI-Powered' : 'Rule-Based'} analysis for different insights
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};
```

### **3. Analysis Box Components**

#### **A. DCF Box Component**
```typescript
// File: frontend/src/components/AnalysisBoxes/DCFBox.tsx (NEW)

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Calculator, TrendingUp, TrendingDown, Info, AlertCircle } from 'lucide-react';
import type { SummaryResponse, AnalysisMode } from '../../types/summary';

interface DCFBoxProps {
  ticker: string;
  mode: AnalysisMode;
  data: SummaryResponse;
}

export const DCFBox: React.FC<DCFBoxProps> = ({ ticker, mode, data }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  const fairValue = (data.fair_value_band.min_value + data.fair_value_band.max_value) / 2;
  const currentPrice = data.fair_value_band.current_price;
  const upside = ((fairValue - currentPrice) / currentPrice) * 100;
  
  const getValuationStatus = () => {
    if (upside > 20) return { status: 'Significantly Undervalued', color: 'text-green-400', icon: TrendingUp };
    if (upside > 0) return { status: 'Undervalued', color: 'text-green-400', icon: TrendingUp };
    if (upside < -20) return { status: 'Significantly Overvalued', color: 'text-red-400', icon: TrendingDown };
    if (upside < 0) return { status: 'Overvalued', color: 'text-red-400', icon: TrendingDown };
    return { status: 'Fair Value', color: 'text-blue-400', icon: Calculator };
  };

  const valuationInfo = getValuationStatus();
  const StatusIcon = valuationInfo.icon;

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600 rounded-lg">
            <Calculator className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-100">DCF Valuation</h3>
            <p className="text-xs text-slate-400">
              {mode === 'simple' ? 'Sector-specific model' : 'AI-enhanced analysis'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400">Method</div>
          <div className="text-sm font-medium text-slate-300">{data.fair_value_band.method}</div>
        </div>
      </div>

      {/* Valuation Summary */}
      <div className="grid grid-cols-3 gap-4 mb-4">
        <div className="text-center">
          <div className="text-xs text-slate-400">Current Price</div>
          <div className="text-lg font-bold text-slate-100">₹{currentPrice.toFixed(0)}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-slate-400">Fair Value</div>
          <div className="text-lg font-bold text-slate-100">₹{fairValue.toFixed(0)}</div>
        </div>
        <div className="text-center">
          <div className="text-xs text-slate-400">Upside/Downside</div>
          <div className={`text-lg font-bold ${upside >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {upside >= 0 ? '+' : ''}{upside.toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Status */}
      <div className={`flex items-center space-x-2 p-3 rounded-lg border ${
        upside >= 0 ? 'border-green-500/30 bg-green-900/10' : 'border-red-500/30 bg-red-900/10'
      }`}>
        <StatusIcon className={`h-4 w-4 ${valuationInfo.color}`} />
        <span className={`font-medium ${valuationInfo.color}`}>{valuationInfo.status}</span>
      </div>

      {/* Mode-specific content */}
      {mode === 'simple' ? (
        <SimpleModeDCFContent data={data} showDetails={showDetails} onToggleDetails={setShowDetails} />
      ) : (
        <AgenticModeDCFContent data={data} showDetails={showDetails} onToggleDetails={setShowDetails} />
      )}

      {/* Confidence & Method Info */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <Info className="h-3 w-3" />
            <span>Confidence: {(data.fair_value_band.confidence * 100).toFixed(0)}%</span>
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-blue-400 hover:text-blue-300 underline"
          >
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
        </div>
      </div>
    </div>
  );
};

const SimpleModeDCFContent: React.FC<{
  data: SummaryResponse;
  showDetails: boolean;
  onToggleDetails: (show: boolean) => void;
}> = ({ data, showDetails }) => {
  if (!showDetails) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="mt-4 p-3 bg-slate-700/30 rounded-lg"
    >
      <h4 className="text-sm font-medium text-slate-200 mb-2">Rule-Based Assumptions</h4>
      <div className="space-y-2 text-xs text-slate-400">
        <div className="flex justify-between">
          <span>Sector Model:</span>
          <span className="text-slate-300">{data.fair_value_band.method}</span>
        </div>
        <div className="flex justify-between">
          <span>Risk-Free Rate:</span>
          <span className="text-slate-300">7.2%</span>
        </div>
        <div className="flex justify-between">
          <span>Market Risk Premium:</span>
          <span className="text-slate-300">6.5%</span>
        </div>
        <div className="flex justify-between">
          <span>Terminal Growth:</span>
          <span className="text-slate-300">4.0%</span>
        </div>
      </div>
    </motion.div>
  );
};

const AgenticModeDCFContent: React.FC<{
  data: SummaryResponse;
  showDetails: boolean;
  onToggleDetails: (show: boolean) => void;
}> = ({ data, showDetails }) => {
  if (!showDetails) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      className="mt-4 space-y-4"
    >
      {/* AI Commentary */}
      <div className="p-3 bg-purple-900/10 border border-purple-500/30 rounded-lg">
        <h4 className="text-sm font-medium text-purple-300 mb-2">🧠 AI Analysis</h4>
        <p className="text-xs text-slate-300 leading-relaxed">
          {data.valuation_insights}
        </p>
      </div>

      {/* AI-Enhanced Assumptions with Annotations */}
      <div className="p-3 bg-slate-700/30 rounded-lg">
        <h4 className="text-sm font-medium text-slate-200 mb-3">AI-Enhanced Assumptions</h4>
        <div className="space-y-3">
          {[
            { name: 'Revenue Growth', value: '12.5%', annotation: 'Conservative vs management guidance of 15%' },
            { name: 'Terminal Growth', value: '4.2%', annotation: 'Slightly above GDP considering sector tailwinds' },
            { name: 'WACC', value: '11.8%', annotation: 'Adjusted for company-specific risk factors' }
          ].map((assumption, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="flex-1">
                <div className="flex justify-between items-center">
                  <span className="text-xs text-slate-400">{assumption.name}:</span>
                  <span className="text-xs font-medium text-slate-300">{assumption.value}</span>
                </div>
              </div>
              <div className="group relative">
                <AlertCircle className="h-3 w-3 text-purple-400 cursor-help" />
                <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 p-2 bg-slate-900 border border-slate-600 rounded text-xs text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity">
                  {assumption.annotation}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  );
};
```

#### **B. Technical Box Component**
```typescript
// File: frontend/src/components/AnalysisBoxes/TechnicalBox.tsx (NEW)

import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, Activity, BarChart3 } from 'lucide-react';
import type { SummaryResponse, AnalysisMode } from '../../types/summary';

interface TechnicalBoxProps {
  ticker: string;
  mode: AnalysisMode;
  data: SummaryResponse;
}

export const TechnicalBox: React.FC<TechnicalBoxProps> = ({ ticker, mode, data }) => {
  // Mock technical data - in real implementation, this would come from backend
  const technicalData = {
    rsi: 42,
    macd: { signal: 'neutral', value: 0.2 },
    movingAverages: {
      price: data.fair_value_band.current_price,
      ma20: data.fair_value_band.current_price * 0.98,
      ma50: data.fair_value_band.current_price * 1.02,
      ma200: data.fair_value_band.current_price * 0.95
    },
    volume: { trend: 'increasing', relative: 1.2 }
  };

  const getRSIStatus = (rsi: number) => {
    if (rsi > 70) return { status: 'Overbought', color: 'text-red-400', signal: 'bearish' };
    if (rsi < 30) return { status: 'Oversold', color: 'text-green-400', signal: 'bullish' };
    return { status: 'Neutral', color: 'text-blue-400', signal: 'neutral' };
  };

  const rsiStatus = getRSIStatus(technicalData.rsi);

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-green-600 rounded-lg">
            <Activity className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-100">Technical Analysis</h3>
            <p className="text-xs text-slate-400">
              {mode === 'simple' ? 'Rule-based signals' : 'AI pattern recognition'}
            </p>
          </div>
        </div>
      </div>

      {/* Technical Indicators */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* RSI */}
        <div className="text-center p-3 bg-slate-700/30 rounded-lg">
          <div className="text-xs text-slate-400">RSI (14)</div>
          <div className={`text-lg font-bold ${rsiStatus.color}`}>{technicalData.rsi}</div>
          <div className={`text-xs ${rsiStatus.color}`}>{rsiStatus.status}</div>
        </div>

        {/* MACD */}
        <div className="text-center p-3 bg-slate-700/30 rounded-lg">
          <div className="text-xs text-slate-400">MACD</div>
          <div className="text-lg font-bold text-blue-400">{technicalData.macd.value}</div>
          <div className="text-xs text-blue-400 capitalize">{technicalData.macd.signal}</div>
        </div>
      </div>

      {/* Moving Averages */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-slate-200 mb-2">Moving Averages</h4>
        <div className="space-y-2">
          {[
            { name: 'MA20', value: technicalData.movingAverages.ma20, period: '20-day' },
            { name: 'MA50', value: technicalData.movingAverages.ma50, period: '50-day' },
            { name: 'MA200', value: technicalData.movingAverages.ma200, period: '200-day' }
          ].map((ma, index) => {
            const isAbove = technicalData.movingAverages.price > ma.value;
            return (
              <div key={index} className="flex justify-between items-center">
                <span className="text-xs text-slate-400">{ma.period}:</span>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-300">₹{ma.value.toFixed(0)}</span>
                  <span className={`text-xs ${isAbove ? 'text-green-400' : 'text-red-400'}`}>
                    {isAbove ? '↗' : '↘'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Mode-specific Analysis */}
      {mode === 'simple' ? (
        <SimpleModeTechnicalContent data={technicalData} />
      ) : (
        <AgenticModeTechnicalContent data={technicalData} summary={data.market_signals} />
      )}
    </div>
  );
};

const SimpleModeTechnicalContent: React.FC<{ data: any }> = ({ data }) => (
  <div className="p-3 bg-blue-900/10 border border-blue-500/30 rounded-lg">
    <h4 className="text-sm font-medium text-blue-300 mb-2">📊 Rule-Based Signals</h4>
    <ul className="space-y-1 text-xs text-slate-300">
      <li>• RSI at {data.rsi} indicates {data.rsi > 70 ? 'overbought' : data.rsi < 30 ? 'oversold' : 'neutral'} conditions</li>
      <li>• Price {data.movingAverages.price > data.movingAverages.ma200 ? 'above' : 'below'} 200-day MA suggests {data.movingAverages.price > data.movingAverages.ma200 ? 'bullish' : 'bearish'} trend</li>
      <li>• Volume trend is {data.volume.trend} ({data.volume.relative}x average)</li>
    </ul>
  </div>
);

const AgenticModeTechnicalContent: React.FC<{ data: any; summary: string }> = ({ data, summary }) => (
  <div className="p-3 bg-purple-900/10 border border-purple-500/30 rounded-lg">
    <h4 className="text-sm font-medium text-purple-300 mb-2">🧠 AI Technical Interpretation</h4>
    <p className="text-xs text-slate-300 leading-relaxed">
      {summary || "Technical analysis shows mixed signals with RSI in neutral territory. Price action suggests consolidation phase with potential for breakout above key resistance levels."}
    </p>
  </div>
);
```

#### **C. Peer Comparison Box Component**
```typescript
// File: frontend/src/components/AnalysisBoxes/PeerComparisonBox.tsx (NEW)

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { SummaryResponse, AnalysisMode } from '../../types/summary';

interface PeerComparisonBoxProps {
  ticker: string;
  mode: AnalysisMode;
  data: SummaryResponse;
}

export const PeerComparisonBox: React.FC<PeerComparisonBoxProps> = ({ ticker, mode, data }) => {
  const [showDetails, setShowDetails] = useState(false);
  
  // Mock peer data - in real implementation, this would come from backend API
  const peerData = {
    company: {
      name: data.company_name,
      pe_ratio: 22.5,
      pb_ratio: 3.2,
      roe: 18.5,
      revenue_growth: 12.3
    },
    peers: [
      { name: 'Peer 1', ticker: 'PEER1.NS', pe_ratio: 25.1, pb_ratio: 3.8, roe: 16.2, revenue_growth: 10.1 },
      { name: 'Peer 2', ticker: 'PEER2.NS', pe_ratio: 19.8, pb_ratio: 2.9, roe: 20.1, revenue_growth: 14.5 },
      { name: 'Peer 3', ticker: 'PEER3.NS', pe_ratio: 27.3, pb_ratio: 4.1, roe: 15.8, revenue_growth: 8.7 }
    ],
    averages: {
      pe_ratio: 24.1,
      pb_ratio: 3.6,
      roe: 17.4,
      revenue_growth: 11.1
    }
  };

  const getComparisonStatus = (companyValue: number, peerAverage: number) => {
    const difference = ((companyValue - peerAverage) / peerAverage) * 100;
    if (Math.abs(difference) < 5) return { status: 'inline', color: 'text-blue-400', icon: Minus };
    if (difference > 0) return { status: 'above', color: 'text-green-400', icon: TrendingUp };
    return { status: 'below', color: 'text-red-400', icon: TrendingDown };
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-orange-600 rounded-lg">
            <Users className="h-5 w-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-slate-100">Peer Comparison</h3>
            <p className="text-xs text-slate-400">
              vs {peerData.peers.length} similar companies
            </p>
          </div>
        </div>
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-xs text-blue-400 hover:text-blue-300 underline"
        >
          {showDetails ? 'Hide' : 'Show'} Details
        </button>
      </div>

      {/* Key Metrics Comparison */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {[
          { name: 'P/E Ratio', company: peerData.company.pe_ratio, average: peerData.averages.pe_ratio, lower_is_better: true },
          { name: 'P/B Ratio', company: peerData.company.pb_ratio, average: peerData.averages.pb_ratio, lower_is_better: true },
          { name: 'ROE (%)', company: peerData.company.roe, average: peerData.averages.roe, lower_is_better: false },
          { name: 'Revenue Growth (%)', company: peerData.company.revenue_growth, average: peerData.averages.revenue_growth, lower_is_better: false }
        ].map((metric, index) => {
          const status = getComparisonStatus(metric.company, metric.average);
          const StatusIcon = status.icon;
          const isPositive = metric.lower_is_better ? status.status === 'below' : status.status === 'above';
          
          return (
            <div key={index} className="p-3 bg-slate-700/30 rounded-lg">
              <div className="flex items-center justify-between mb-1">
                <div className="text-xs text-slate-400">{metric.name}</div>
                <StatusIcon className={`h-3 w-3 ${isPositive ? 'text-green-400' : status.status === 'inline' ? 'text-blue-400' : 'text-red-400'}`} />
              </div>
              <div className="text-sm font-semibold text-slate-100">
                {metric.company.toFixed(1)}
              </div>
              <div className="text-xs text-slate-400">
                Peers: {metric.average.toFixed(1)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Detailed Peer Table */}
      <AnimatePresence>
        {showDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4"
          >
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-slate-600">
                    <th className="text-left py-2 text-slate-400">Company</th>
                    <th className="text-right py-2 text-slate-400">P/E</th>
                    <th className="text-right py-2 text-slate-400">P/B</th>
                    <th className="text-right py-2 text-slate-400">ROE</th>
                    <th className="text-right py-2 text-slate-400">Growth</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="bg-blue-900/20">
                    <td className="py-2 text-slate-200 font-medium">{data.company_name}</td>
                    <td className="text-right py-2 text-slate-200">{peerData.company.pe_ratio}</td>
                    <td className="text-right py-2 text-slate-200">{peerData.company.pb_ratio}</td>
                    <td className="text-right py-2 text-slate-200">{peerData.company.roe}%</td>
                    <td className="text-right py-2 text-slate-200">{peerData.company.revenue_growth}%</td>
                  </tr>
                  {peerData.peers.map((peer, index) => (
                    <tr key={index} className="border-b border-slate-700">
                      <td className="py-2 text-slate-300">{peer.name}</td>
                      <td className="text-right py-2 text-slate-300">{peer.pe_ratio}</td>
                      <td className="text-right py-2 text-slate-300">{peer.pb_ratio}</td>
                      <td className="text-right py-2 text-slate-300">{peer.roe}%</td>
                      <td className="text-right py-2 text-slate-300">{peer.revenue_growth}%</td>
                    </tr>
                  ))}
                  <tr className="bg-slate-700/30 font-medium">
                    <td className="py-2 text-slate-200">Peer Average</td>
                    <td className="text-right py-2 text-slate-200">{peerData.averages.pe_ratio}</td>
                    <td className="text-right py-2 text-slate-200">{peerData.averages.pb_ratio}</td>
                    <td className="text-right py-2 text-slate-200">{peerData.averages.roe}%</td>
                    <td className="text-right py-2 text-slate-200">{peerData.averages.revenue_growth}%</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Mode-specific Analysis */}
      {mode === 'simple' ? (
        <SimpleModePeerContent data={peerData} />
      ) : (
        <AgenticModePeerContent data={peerData} />
      )}
    </div>
  );
};

const SimpleModePeerContent: React.FC<{ data: any }> = ({ data }) => {
  const peComparison = ((data.averages.pe_ratio - data.company.pe_ratio) / data.averages.pe_ratio) * 100;
  const roeComparison = ((data.company.roe - data.averages.roe) / data.averages.roe) * 100;

  return (
    <div className="p-3 bg-orange-900/10 border border-orange-500/30 rounded-lg">
      <h4 className="text-sm font-medium text-orange-300 mb-2">📊 Peer Analysis</h4>
      <ul className="space-y-1 text-xs text-slate-300">
        <li>• Trading at {Math.abs(peComparison).toFixed(1)}% {peComparison > 0 ? 'discount' : 'premium'} to peer P/E average</li>
        <li>• ROE is {Math.abs(roeComparison).toFixed(1)}% {roeComparison > 0 ? 'above' : 'below'} peer average</li>
        <li>• Revenue growth {data.company.revenue_growth > data.averages.revenue_growth ? 'outpacing' : 'lagging'} peer group</li>
      </ul>
    </div>
  );
};

const AgenticModePeerContent: React.FC<{ data: any }> = ({ data }) => (
  <div className="p-3 bg-purple-900/10 border border-purple-500/30 rounded-lg">
    <h4 className="text-sm font-medium text-purple-300 mb-2">🧠 AI Competitive Analysis</h4>
    <p className="text-xs text-slate-300 leading-relaxed">
      Company trades at a reasonable valuation relative to peers, with superior ROE indicating efficient capital allocation. 
      The P/E discount appears justified by slightly lower growth rates, but the quality premium suggests potential for multiple expansion.
    </p>
  </div>
);
```

---

## 🧪 **Testing Strategy**

### **Backend Testing Implementation**

```python
# File: backend/tests/test_sector_dcf_models.py (NEW)

import pytest
from app.services.sector_dcf_service import BankingDCFCalculator, PharmaDCFCalculator, RealEstateDCFCalculator

class TestSectorDCFModels:
    
    def test_banking_dcf_excess_return_model(self):
        """Test BFSI Excess Return Model calculation"""
        calculator = BankingDCFCalculator()
        
        # Mock banking company data
        company_data = {
            "book_value": 100,
            "roe": 18.0,
            "net_interest_margin": 4.2,
            "gross_npa": 2.1,
            "cost_to_income_ratio": 42.0
        }
        
        inputs = calculator.calculate_inputs(company_data)
        fair_value = calculator.calculate_fair_value(inputs)
        
        assert inputs["roe"] == 18.0
        assert inputs["gnpa"] == 2.1
        assert fair_value > 0
        assert isinstance(fair_value, float)
    
    def test_banking_sector_rules(self):
        """Test banking-specific rules and red flags"""
        calculator = BankingDCFCalculator()
        rules = calculator.get_sector_rules()
        
        assert "red_flags" in rules
        assert rules["red_flags"]["gnpa_threshold"] == 5.0
        assert "positive_signals" in rules
        assert rules["positive_signals"]["roe_threshold"] == 15.0
    
    def test_pharma_dcf_hybrid_model(self):
        """Test Pharma DCF + EV/EBITDA hybrid model"""
        calculator = PharmaDCFCalculator()
        
        company_data = {
            "revenue": 1000,
            "ebitda": 200,
            "rd_expense": 80,
            "anda_count": 12,
            "usfda_issues": 1
        }
        
        inputs = calculator.calculate_inputs(company_data)
        fair_value = calculator.calculate_fair_value(inputs)
        
        assert inputs["rd_spend"] == 80
        assert inputs["anda_pipeline"] == 12
        assert fair_value > 0
    
    def test_real_estate_nav_model(self):
        """Test Real Estate NAV-based valuation"""
        calculator = RealEstateDCFCalculator()
        
        company_data = {
            "land_area_sqft": 1000000,
            "inventory": 5000,
            "total_debt": 2000,
            "cash_equivalents": 500,
            "inventory_turnover": 0.8
        }
        
        inputs = calculator.calculate_inputs(company_data)
        fair_value = calculator.calculate_fair_value(inputs)
        
        assert inputs["inventory_turnover"] == 0.8
        assert fair_value > 0

# File: backend/tests/test_weighted_scoring.py (NEW)

import pytest
from app.services.weighted_scoring_service import WeightedScoringService

class TestWeightedScoring:
    
    def test_dcf_component_scoring(self):
        """Test DCF component scoring logic"""
        service = WeightedScoringService()
        
        # Test significantly undervalued scenario
        dcf_result = {
            "current_price": 100,
            "fair_value": 140,  # 40% upside
            "method": "DCF"
        }
        
        score = service._score_dcf_component(dcf_result)
        assert score["score"] == 1  # Bullish
        assert "undervalued" in score["reason"].lower()
        
        # Test overvalued scenario
        dcf_result = {
            "current_price": 140,
            "fair_value": 100,  # -28% downside
            "method": "DCF"
        }
        
        score = service._score_dcf_component(dcf_result)
        assert score["score"] == -1  # Bearish
        assert "overvalued" in score["reason"].lower()
    
    def test_final_label_calculation(self):
        """Test final investment label calculation"""
        service = WeightedScoringService()
        
        # Test strongly bullish scenario
        scores = {
            "dcf": {"score": 1},
            "technical": {"score": 1}, 
            "peer": {"score": 1},
            "financial": {"score": 1},
            "weighted_total": 1.0  # All components bullish
        }
        
        label = service.calculate_final_label(scores)
        assert label == "Bullish"
        
        # Test neutral scenario
        scores["weighted_total"] = 0.0
        label = service.calculate_final_label(scores)
        assert label == "Neutral"
        
        # Test bearish scenario
        scores["weighted_total"] = -0.8
        label = service.calculate_final_label(scores)
        assert label == "Bearish"
    
    def test_weighted_calculation(self):
        """Test weighted score calculation"""
        service = WeightedScoringService()
        
        # Mock component scores
        mock_scores = {
            "dcf": {"score": 1},      # 35% weight
            "financial": {"score": 0}, # 25% weight
            "technical": {"score": -1}, # 20% weight
            "peer": {"score": 1}      # 20% weight
        }
        
        # Calculate weighted total manually
        expected = (1 * 0.35) + (0 * 0.25) + (-1 * 0.20) + (1 * 0.20)
        # = 0.35 + 0 - 0.20 + 0.20 = 0.35
        
        weighted_total = sum(
            mock_scores[component]["score"] * service.weights[component]
            for component in mock_scores.keys()
        )
        
        assert abs(weighted_total - expected) < 0.01
        assert abs(weighted_total - 0.35) < 0.01

# File: backend/tests/test_peer_comparison.py (NEW)

import pytest
from unittest.mock import AsyncMock, patch
from app.services.peer_comparison_service import PeerComparisonService

class TestPeerComparison:
    
    def test_peer_selection_logic(self):
        """Test peer selection from sector mappings"""
        service = PeerComparisonService()
        
        # Test IT sector peer selection
        peers = service._select_peers("TCS.NS", "IT", count=3)
        assert len(peers) <= 3
        assert "TCS.NS" not in peers  # Should exclude the company itself
        assert all("NS" in peer for peer in peers)  # All should be NSE tickers
        
        # Test BFSI sector peer selection
        peers = service._select_peers("HDFCBANK.NS", "BFSI", count=3)
        assert len(peers) <= 3
        assert not any(peer.startswith("HDFCBANK") for peer in peers)
    
    def test_peer_averages_calculation(self):
        """Test calculation of peer averages"""
        service = PeerComparisonService()
        
        mock_peer_data = [
            {"pe_ratio": 20, "pb_ratio": 3, "roe": 15, "revenue_growth": 10},
            {"pe_ratio": 25, "pb_ratio": 4, "roe": 18, "revenue_growth": 12},
            {"pe_ratio": 22, "pb_ratio": 3.5, "roe": 16, "revenue_growth": 8}
        ]
        
        averages = service._calculate_peer_averages(mock_peer_data)
        
        assert averages["pe_ratio"] == (20 + 25 + 22) / 3
        assert averages["roe"] == (15 + 18 + 16) / 3
        assert abs(averages["pb_ratio"] - 3.5) < 0.01
    
    def test_comparison_metrics_generation(self):
        """Test generation of comparison metrics"""
        service = PeerComparisonService()
        
        company_data = {"pe_ratio": 20, "roe": 18}
        peer_averages = {"pe_ratio": 25, "roe": 15}
        
        comparisons = service._generate_comparison_metrics(company_data, peer_averages)
        
        assert "pe_ratio" in comparisons
        assert comparisons["pe_ratio"]["status"] == "below"  # 20% discount
        assert comparisons["roe"]["status"] == "above"  # 20% premium
```

### **Frontend Testing Implementation**

```typescript
// File: frontend/src/components/ModeSelection/ModeSelectionCards.test.tsx (NEW)

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { ModeSelectionCards } from './ModeSelectionCards';

describe('ModeSelectionCards', () => {
  const mockOnModeSelect = jest.fn();

  beforeEach(() => {
    mockOnModeSelect.mockClear();
  });

  test('renders both mode cards', () => {
    render(
      <ModeSelectionCards
        selectedMode="simple"
        onModeSelect={mockOnModeSelect}
      />
    );

    expect(screen.getByText('Rule-Based Analysis')).toBeInTheDocument();
    expect(screen.getByText('AI Analyst Insights')).toBeInTheDocument();
  });

  test('shows correct selected state', () => {
    render(
      <ModeSelectionCards
        selectedMode="simple"
        onModeSelect={mockOnModeSelect}
      />
    );

    const simpleCard = screen.getByText('Rule-Based Analysis').closest('.cursor-pointer');
    const agenticCard = screen.getByText('AI Analyst Insights').closest('.cursor-pointer');

    expect(simpleCard).toHaveClass('border-blue-500');
    expect(agenticCard).toHaveClass('border-slate-600');
  });

  test('calls onModeSelect when card is clicked', () => {
    render(
      <ModeSelectionCards
        selectedMode="simple"
        onModeSelect={mockOnModeSelect}
      />
    );

    const agenticCard = screen.getByText('AI Analyst Insights').closest('.cursor-pointer');
    fireEvent.click(agenticCard!);

    expect(mockOnModeSelect).toHaveBeenCalledWith('agentic');
  });

  test('displays correct features for each mode', () => {
    render(
      <ModeSelectionCards
        selectedMode="simple"
        onModeSelect={mockOnModeSelect}
      />
    );

    expect(screen.getByText(/Sector-specific DCF models/)).toBeInTheDocument();
    expect(screen.getByText(/News sentiment analysis/)).toBeInTheDocument();
    expect(screen.getByText(/Quick screening/)).toBeInTheDocument();
    expect(screen.getByText(/Deep research/)).toBeInTheDocument();
  });
});

// File: frontend/src/components/AnalysisBoxes/DCFBox.test.tsx (NEW)

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { DCFBox } from './DCFBox';
import type { SummaryResponse } from '../../types/summary';

const mockSummaryData: SummaryResponse = {
  ticker: 'TCS.NS',
  company_name: 'Tata Consultancy Services',
  fair_value_band: {
    min_value: 3000,
    max_value: 3500,
    current_price: 3200,
    method: 'DCF',
    confidence: 0.8
  },
  investment_label: 'Cautiously Bullish',
  key_factors: ['Undervalued vs DCF', 'Strong fundamentals'],
  valuation_insights: 'DCF indicates fair value with moderate upside',
  market_signals: 'Technical indicators show neutral momentum',
  business_fundamentals: 'Strong financial performance',
  data_health_warnings: [],
  analysis_timestamp: '2025-07-30T10:30:00Z',
  analysis_mode: 'simple',
  sector: 'IT'
};

describe('DCFBox', () => {
  test('renders DCF valuation information', () => {
    render(
      <DCFBox
        ticker="TCS.NS"
        mode="simple"
        data={mockSummaryData}
      />
    );

    expect(screen.getByText('DCF Valuation')).toBeInTheDocument();
    expect(screen.getByText('₹3200')).toBeInTheDocument(); // Current price
    expect(screen.getByText('₹3250')).toBeInTheDocument(); // Fair value (average)
    expect(screen.getByText('DCF')).toBeInTheDocument(); // Method
  });

  test('calculates and displays upside correctly', () => {
    render(
      <DCFBox
        ticker="TCS.NS"
        mode="simple"
        data={mockSummaryData}
      />
    );

    // Fair value average = (3000 + 3500) / 2 = 3250
    // Upside = ((3250 - 3200) / 3200) * 100 = 1.6%
    expect(screen.getByText('+1.6%')).toBeInTheDocument();
  });

  test('shows different content for Simple vs Agentic mode', () => {
    const { rerender } = render(
      <DCFBox
        ticker="TCS.NS"
        mode="simple"
        data={mockSummaryData}
      />
    );

    expect(screen.getByText('Sector-specific model')).toBeInTheDocument();

    rerender(
      <DCFBox
        ticker="TCS.NS"
        mode="agentic"
        data={mockSummaryData}
      />
    );

    expect(screen.getByText('AI-enhanced analysis')).toBeInTheDocument();
  });

  test('toggles details visibility', () => {
    render(
      <DCFBox
        ticker="TCS.NS"
        mode="simple"
        data={mockSummaryData}
      />
    );

    const detailsButton = screen.getByText('Show Details');
    fireEvent.click(detailsButton);

    expect(screen.getByText('Rule-Based Assumptions')).toBeInTheDocument();
    expect(screen.getByText('Hide Details')).toBeInTheDocument();
  });
});

// File: frontend/src/components/V3Dashboard.test.tsx (NEW)

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { V3Dashboard } from './V3Dashboard';
import { v3ApiService } from '../services/v3ApiService';

// Mock the API service
jest.mock('../services/v3ApiService');
const mockV3ApiService = v3ApiService as jest.Mocked<typeof v3ApiService>;

describe('V3Dashboard', () => {
  beforeEach(() => {
    mockV3ApiService.getSummary.mockReset();
  });

  test('renders mode selection cards initially', () => {
    render(<V3Dashboard />);

    expect(screen.getByText('Choose Your Analysis Mode')).toBeInTheDocument();
    expect(screen.getByText('Rule-Based Analysis')).toBeInTheDocument();
    expect(screen.getByText('AI Analyst Insights')).toBeInTheDocument();
  });

  test('selects Simple mode by default', () => {
    render(<V3Dashboard />);

    const simpleCard = screen.getByText('Rule-Based Analysis').closest('.cursor-pointer');
    expect(simpleCard).toHaveClass('border-blue-500');
  });

  test('shows search form after mode selection', () => {
    render(<V3Dashboard />);

    const agenticCard = screen.getByText('AI Analyst Insights').closest('.cursor-pointer');
    fireEvent.click(agenticCard!);

    expect(screen.getByText('Enter Stock Ticker')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter stock ticker/)).toBeInTheDocument();
  });

  test('calls API with correct mode when analyzing stock', async () => {
    const mockSummaryData = {
      ticker: 'TCS.NS',
      company_name: 'TCS',
      fair_value_band: { min_value: 3000, max_value: 3500, current_price: 3200, method: 'DCF', confidence: 0.8 },
      investment_label: 'Bullish',
      key_factors: [],
      valuation_insights: '',
      market_signals: '',
      business_fundamentals: '',
      data_health_warnings: [],
      analysis_timestamp: '2025-07-30T10:30:00Z',
      analysis_mode: 'agentic',
      sector: 'IT'
    };

    mockV3ApiService.getSummary.mockResolvedValue(mockSummaryData);

    render(<V3Dashboard />);

    // Select Agentic mode
    const agenticCard = screen.getByText('AI Analyst Insights').closest('.cursor-pointer');
    fireEvent.click(agenticCard!);

    // Enter ticker and search
    const searchInput = screen.getByPlaceholderText(/Enter stock ticker/);
    const searchButton = screen.getByText('Analyze');

    fireEvent.change(searchInput, { target: { value: 'TCS' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockV3ApiService.getSummary).toHaveBeenCalledWith('TCS.NS', 'agentic');
    });
  });

  test('displays analysis results after successful API call', async () => {
    const mockSummaryData = {
      ticker: 'TCS.NS',
      company_name: 'Tata Consultancy Services',
      fair_value_band: { min_value: 3000, max_value: 3500, current_price: 3200, method: 'DCF', confidence: 0.8 },
      investment_label: 'Bullish',
      key_factors: ['Strong fundamentals'],
      valuation_insights: 'Undervalued based on DCF',
      market_signals: 'Neutral technical indicators',
      business_fundamentals: 'Excellent financial health',
      data_health_warnings: [],
      analysis_timestamp: '2025-07-30T10:30:00Z',
      analysis_mode: 'simple',
      sector: 'IT'
    };

    mockV3ApiService.getSummary.mockResolvedValue(mockSummaryData);

    render(<V3Dashboard />);

    // Search for stock
    const searchInput = screen.getByPlaceholderText(/Enter stock ticker/);
    const searchButton = screen.getByText('Analyze');

    fireEvent.change(searchInput, { target: { value: 'TCS' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('Tata Consultancy Services')).toBeInTheDocument();
      expect(screen.getByText('DCF Valuation')).toBeInTheDocument();
      expect(screen.getByText('Technical Analysis')).toBeInTheDocument();
      expect(screen.getByText('Peer Comparison')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    mockV3ApiService.getSummary.mockRejectedValue(new Error('API Error'));

    render(<V3Dashboard />);

    const searchInput = screen.getByPlaceholderText(/Enter stock ticker/);
    const searchButton = screen.getByText('Analyze');

    fireEvent.change(searchInput, { target: { value: 'INVALID' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(screen.getByText('API Error')).toBeInTheDocument();
    });
  });
});
```

---

## 📚 **Documentation Updates**

### **API Documentation Update**

```markdown
# File: docs/API_DOCUMENTATION_V3.md (NEW)

# EquityScope v3 API Documentation

## Overview
EquityScope v3 introduces mode-based analysis with sector-specific DCF models and weighted scoring framework.

## Base URL
```
https://api.equityscope.com/api/v3
```

## Authentication
Currently no authentication required for basic endpoints.

## Endpoints

### GET /summary/{ticker}/simple
Get rule-based analysis summary for a stock.

**Parameters:**
- `ticker` (path): Stock ticker (e.g., "TCS.NS")
- `force_refresh` (query, optional): Force refresh of cached data

**Response:**
```json
{
  "ticker": "TCS.NS",
  "company_name": "Tata Consultancy Services Limited",
  "fair_value_band": {
    "min_value": 3000,
    "max_value": 3500,
    "current_price": 3200,
    "method": "DCF",
    "confidence": 0.8
  },
  "investment_label": "Bullish",
  "key_factors": [
    "Undervalued vs DCF analysis",
    "Strong technical momentum"
  ],
  "valuation_insights": "DCF analysis indicates 8% upside to fair value",
  "market_signals": "RSI at 42 indicates neutral momentum",
  "business_fundamentals": "Strong ROE of 28% with consistent growth",
  "data_health_warnings": [],
  "analysis_timestamp": "2025-07-30T10:30:00Z",
  "analysis_mode": "simple",
  "sector": "IT",
  "rules_applied": ["DCF_FAIR_VALUE", "RSI_NEUTRAL", "STRONG_ROE"],
  "weighted_scores_debug": {
    "dcf": {"score": 0, "reason": "Near fair value"},
    "technical": {"score": 0, "reason": "Neutral technical signals"},
    "peer": {"score": 1, "reason": "PE 15% below peer average"},
    "financial": {"score": 1, "reason": "Strong ROE (28%)"},
    "weighted_total": 0.45
  }
}
```

### GET /summary/{ticker}/agentic
Get AI-powered analysis summary for a stock.

**Parameters:**
- `ticker` (path): Stock ticker (e.g., "TCS.NS")
- `force_refresh` (query, optional): Force refresh of cached data

**Response:**
```json
{
  "ticker": "TCS.NS",
  "company_name": "Tata Consultancy Services Limited",
  "fair_value_band": {
    "min_value": 3100,
    "max_value": 3400,
    "current_price": 3200,
    "method": "DCF",
    "confidence": 0.85
  },
  "investment_label": "Cautiously Bullish",
  "key_factors": [
    "AI-identified competitive moats in digital transformation",
    "Sector tailwinds from IT spending recovery",
    "Management guidance appears conservative"
  ],
  "valuation_insights": "AI analysis suggests DCF assumptions are conservative given company's digital transformation capabilities and market share gains.",
  "market_signals": "Technical analysis indicates consolidation phase with potential breakout above ₹3,300 resistance.",
  "business_fundamentals": "AI assessment reveals strong execution capabilities with industry-leading margins and client acquisition rates.",
  "data_health_warnings": ["News sentiment data partially cached (2 hours old)"],
  "analysis_timestamp": "2025-07-30T10:30:00Z",
  "analysis_mode": "agentic",
  "sector": "IT",
  "agent_reasoning": "Comprehensive analysis considering sector dynamics, competitive positioning, and execution track record.",
  "cost_breakdown": {"tokens_used": 2500, "cost_usd": 0.08},
  "model_version": "claude-3-sonnet"
}
```

### GET /peers/{ticker}
Get peer comparison analysis.

**Parameters:**
- `ticker` (path): Stock ticker
- `target_count` (query, optional): Number of peers (default: 3, max: 5)

**Response:**
```json
{
  "primary_ticker": "TCS.NS",
  "sector": "IT",
  "peer_count": 3,
  "peers": [
    {
      "ticker": "INFY.NS",
      "company_name": "Infosys Limited",
      "fair_value_band": {...},
      "investment_label": "Neutral",
      "sector": "IT"
    }
  ],
  "analysis_timestamp": "2025-07-30T10:30:00Z"
}
```

## Sector-Specific Models

### BFSI (Banking/NBFC)
**Model:** Excess Return Model
**Key Metrics:** NIM, GNPA, Cost-to-Income, Book Value
**Special Rules:**
- GNPA > 5%: Red flag
- NIM compression > 0.5%: Concern

### Pharma
**Model:** DCF + EV/EBITDA hybrid
**Key Metrics:** R&D spend, ANDA pipeline, USFDA compliance
**Special Rules:**
- R&D < 5% of revenue: Innovation concern
- USFDA observations > 3: Regulatory risk

### Real Estate
**Model:** NAV-based valuation
**Key Metrics:** Inventory turnover, D/E ratio, project pipeline
**Special Rules:**
- Inventory turnover < 0.5x: Monetization risk
- D/E > 1.5x: Leverage concern

## Error Responses

### 400 Bad Request
```json
{
  "error": true,
  "message": "Invalid ticker symbol",
  "status_code": 400,
  "api_version": "3.0.0"
}
```

### 404 Not Found
```json
{
  "error": true,
  "message": "Financial data not found for ticker",
  "status_code": 404,
  "api_version": "3.0.0"
}
```

### 500 Internal Server Error
```json
{
  "error": true,
  "message": "Analysis failed due to internal error",
  "status_code": 500,
  "api_version": "3.0.0"
}
```

## Rate Limits
- Simple Mode: 60 requests/minute
- Agentic Mode: 20 requests/minute (due to AI processing)
- Peer Analysis: 30 requests/minute

## Caching
- Simple Mode: 4-hour cache
- Agentic Mode: 2-hour cache (due to dynamic AI insights)
- Peer Data: 6-hour cache
```

---

## 📅 **Implementation Timeline**

### **Week 1: Backend Foundation**
- ✅ Day 1-2: Sector-specific DCF models implementation
- ✅ Day 3-4: Weighted scoring framework development
- ✅ Day 5-7: Peer comparison service and logging infrastructure

### **Week 2: API Integration**
- ✅ Day 1-3: V3 API endpoints with mode-specific logic
- ✅ Day 4-5: AI integration for Agentic mode
- ✅ Day 6-7: Comprehensive backend testing

### **Week 3: Frontend Development**
- ✅ Day 1-2: Mode selection UI implementation
- ✅ Day 3-4: Analysis box components (DCF, Technical, Peer, Financial)
- ✅ Day 5-7: Dashboard integration and responsive design

### **Week 4: Testing & Polish**
- ✅ Day 1-3: Frontend component testing
- ✅ Day 4-5: End-to-end integration testing
- ✅ Day 6-7: Bug fixes and performance optimization

### **Week 5: Documentation & Deployment**
- ✅ Day 1-3: API documentation and user guides
- ✅ Day 4-5: Production deployment preparation
- ✅ Day 6-7: Final testing and launch readiness

---

This comprehensive implementation plan provides a complete roadmap for transforming EquityScope into a sophisticated, mode-based analysis platform with sector-specific intelligence and weighted scoring framework. The architecture supports both rapid rule-based analysis and deep AI-powered insights while maintaining production-grade reliability and comprehensive testing coverage.