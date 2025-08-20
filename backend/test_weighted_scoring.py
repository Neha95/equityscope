#!/usr/bin/env python3
"""
Test script for v3 Weighted Scoring Framework
Tests the integration of sector-specific DCF models with weighted component scoring
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import Dict

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.v3_summary_service import V3SummaryService
from app.services.weighted_scoring_service import WeightedScoringService
from app.models.summary import InvestmentLabel

class WeightedScoringTester:
    """Test the v3 weighted scoring system with realistic data"""
    
    def __init__(self):
        self.v3_service = V3SummaryService()
        self.scoring_service = WeightedScoringService()
        
        # Test data for different scenarios
        self.test_cases = {
            "strong_buy": {
                "ticker": "STRONG_BUY_TEST",
                "company_data": {
                    "name": "Strong Buy Test Company",
                    "current_price": 100,
                    "info": {
                        "trailingPE": 12,
                        "returnOnEquity": 0.22,
                        "profitMargins": 0.18,
                        "revenueGrowth": 0.25,
                        "debtToEquity": 0.3,
                        "currentRatio": 2.1
                    }
                },
                "sector": "IT",
                "expected_label": InvestmentLabel.STRONGLY_BULLISH
            },
            "neutral": {
                "ticker": "NEUTRAL_TEST",
                "company_data": {
                    "name": "Neutral Test Company", 
                    "current_price": 200,
                    "info": {
                        "trailingPE": 18,
                        "returnOnEquity": 0.12,
                        "profitMargins": 0.08,
                        "revenueGrowth": 0.05,
                        "debtToEquity": 0.8,
                        "currentRatio": 1.3
                    }
                },
                "sector": "FMCG",
                "expected_label": InvestmentLabel.NEUTRAL
            },
            "strong_sell": {
                "ticker": "STRONG_SELL_TEST",
                "company_data": {
                    "name": "Strong Sell Test Company",
                    "current_price": 50,
                    "info": {
                        "trailingPE": 35,
                        "returnOnEquity": 0.02,
                        "profitMargins": -0.05,
                        "revenueGrowth": -0.15,
                        "debtToEquity": 2.5,
                        "currentRatio": 0.8
                    }
                },
                "sector": "ENERGY",
                "expected_label": InvestmentLabel.STRONGLY_BEARISH
            },
            "banking_test": {
                "ticker": "BANK_TEST",
                "company_data": {
                    "name": "Banking Test Company",
                    "current_price": 150,
                    "info": {
                        "trailingPE": 8,
                        "returnOnEquity": 0.15,
                        "returnOnAssets": 0.015,
                        "bookValue": 140,
                        "profitMargins": 0.12
                    }
                },
                "sector": "BFSI",
                "expected_label": InvestmentLabel.CAUTIOUSLY_BULLISH
            }
        }
    
    async def run_all_tests(self):
        """Run comprehensive weighted scoring tests"""
        print("🚀 Starting v3 Weighted Scoring Framework Tests")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, test_data in self.test_cases.items():
            print(f"\n📊 Testing: {test_name.upper().replace('_', ' ')}")
            print("-" * 40)
            
            try:
                # Test weighted scoring service directly
                result = await self._test_scoring_service(test_data)
                total_tests += 1
                
                if self._validate_scoring_result(result, test_data):
                    passed_tests += 1
                    print("✅ Test PASSED")
                else:
                    print("❌ Test FAILED")
                
                # Test full v3 summary service integration
                summary_result = await self._test_v3_integration(test_data)
                total_tests += 1
                
                if self._validate_summary_result(summary_result, test_data):
                    passed_tests += 1
                    print("✅ Integration Test PASSED")
                else:
                    print("❌ Integration Test FAILED")
                
            except Exception as e:
                print(f"❌ Test ERROR: {e}")
                total_tests += 2  # Both tests failed
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📈 Test Results: {passed_tests}/{total_tests} tests passed")
        print(f"🎯 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Weighted scoring system is working correctly.")
        else:
            print("⚠️  Some tests failed. Review the implementation.")
    
    async def _test_scoring_service(self, test_data: Dict):
        """Test weighted scoring service directly"""
        print(f"Testing weighted scoring for {test_data['ticker']}")
        
        # Create mock peer and technical data
        peer_data = self._create_mock_peer_data(test_data['sector'])
        technical_data = self._create_mock_technical_data(test_data['ticker'])
        
        result = await self.scoring_service.calculate_weighted_score(
            ticker=test_data['ticker'],
            company_data=test_data['company_data'],
            sector=test_data['sector'],
            peer_data=peer_data,
            technical_data=technical_data
        )
        
        # Print detailed results
        print(f"  Total Score: {result.total_score:.1f}")
        print(f"  Investment Label: {result.investment_label}")
        print(f"  Component Breakdown:")
        print(f"    DCF: {result.dcf_score:.1f} (Raw: {result.component_scores['DCF'].raw_score:.1f})")
        print(f"    Financial: {result.financial_score:.1f} (Raw: {result.component_scores['Financial'].raw_score:.1f})")
        print(f"    Technical: {result.technical_score:.1f} (Raw: {result.component_scores['Technical'].raw_score:.1f})")
        print(f"    Peer: {result.peer_score:.1f} (Raw: {result.component_scores['Peer'].raw_score:.1f})")
        print(f"  Confidence: {result.confidence:.2f}")
        
        # Print key reasoning
        for component_name, component in result.component_scores.items():
            if component.reasoning:
                print(f"  {component_name} Reasoning: {component.reasoning[0]}")
        
        return result
    
    async def _test_v3_integration(self, test_data: Dict):
        """Test full v3 summary service integration"""
        print(f"Testing v3 integration for {test_data['ticker']}")
        
        # Mock the data fetching methods for testing
        original_fetch_company = self.v3_service._fetch_company_data
        original_classify_sector = self.v3_service._classify_sector
        
        async def mock_fetch_company(ticker):
            return test_data['company_data']
        
        def mock_classify_sector(ticker):
            return test_data['sector']
        
        # Replace methods temporarily
        self.v3_service._fetch_company_data = mock_fetch_company
        self.v3_service._classify_sector = mock_classify_sector
        
        try:
            result = await self.v3_service.generate_simple_summary(test_data['ticker'])
            
            print(f"  Summary Generated Successfully")
            print(f"  Investment Label: {result.investment_label}")
            print(f"  Fair Value Band: ₹{result.fair_value_band.min_value:.0f} - ₹{result.fair_value_band.max_value:.0f}")
            print(f"  Current Price: ₹{result.fair_value_band.current_price:.0f}")
            print(f"  Key Factors: {len(result.key_factors)} factors identified")
            
            if result.weighted_score is not None:
                print(f"  Weighted Score: {result.weighted_score:.1f}")
            
            return result
            
        finally:
            # Restore original methods
            self.v3_service._fetch_company_data = original_fetch_company
            self.v3_service._classify_sector = original_classify_sector
    
    def _validate_scoring_result(self, result, test_data: Dict) -> bool:
        """Validate that scoring result meets expectations"""
        expected_label = test_data['expected_label']
        actual_label = result.investment_label
        
        # Check if label matches expected
        label_match = actual_label == expected_label
        
        # Check score consistency with label
        score_consistent = self._is_score_consistent_with_label(result.total_score, actual_label)
        
        # Check that all components are present
        required_components = ["DCF", "Financial", "Technical", "Peer"]
        components_present = all(comp in result.component_scores for comp in required_components)
        
        # Check confidence is reasonable
        confidence_ok = 0.2 <= result.confidence <= 1.0
        
        if not label_match:
            print(f"    ⚠️  Label mismatch: Expected {expected_label}, got {actual_label}")
        if not score_consistent:
            print(f"    ⚠️  Score inconsistent: Score {result.total_score:.1f} doesn't match label {actual_label}")
        if not components_present:
            print(f"    ⚠️  Missing components: {set(required_components) - set(result.component_scores.keys())}")
        if not confidence_ok:
            print(f"    ⚠️  Confidence out of range: {result.confidence:.2f}")
        
        return label_match and score_consistent and components_present and confidence_ok
    
    def _validate_summary_result(self, result, test_data: Dict) -> bool:
        """Validate that summary result is properly integrated"""
        # Check basic fields
        has_basic_fields = all([
            result.ticker == test_data['ticker'],
            result.investment_label,
            result.fair_value_band,
            result.key_factors
        ])
        
        # Check weighted scoring integration
        has_weighted_score = result.weighted_score is not None
        has_component_scores = result.component_scores is not None
        
        # Check insights are populated
        has_insights = all([
            result.valuation_insights,
            result.market_signals,
            result.business_fundamentals
        ])
        
        if not has_basic_fields:
            print("    ⚠️  Missing basic summary fields")
        if not has_weighted_score:
            print("    ⚠️  Missing weighted score in summary")
        if not has_component_scores:
            print("    ⚠️  Missing component scores in summary")
        if not has_insights:
            print("    ⚠️  Missing insights in summary")
        
        return has_basic_fields and has_weighted_score and has_component_scores and has_insights
    
    def _is_score_consistent_with_label(self, score: float, label: InvestmentLabel) -> bool:
        """Check if total score is consistent with investment label"""
        if label == InvestmentLabel.STRONGLY_BULLISH:
            return score >= 60
        elif label == InvestmentLabel.CAUTIOUSLY_BULLISH:
            return 20 <= score < 60
        elif label == InvestmentLabel.NEUTRAL:
            return -20 <= score < 20
        elif label == InvestmentLabel.CAUTIOUSLY_BEARISH:
            return -60 <= score < -20
        elif label == InvestmentLabel.STRONGLY_BEARISH:
            return score < -60
        return False
    
    def _create_mock_peer_data(self, sector: str) -> Dict:
        """Create realistic mock peer data for testing"""
        if sector == "BFSI":
            peers = [
                {"ticker": "PEER1", "pe_ratio": 10, "revenue_growth": 0.08, "profit_margin": 0.15, "roe": 0.14},
                {"ticker": "PEER2", "pe_ratio": 12, "revenue_growth": 0.12, "profit_margin": 0.18, "roe": 0.16},
                {"ticker": "PEER3", "pe_ratio": 9, "revenue_growth": 0.06, "profit_margin": 0.12, "roe": 0.13}
            ]
        elif sector == "IT":
            peers = [
                {"ticker": "PEER1", "pe_ratio": 20, "revenue_growth": 0.15, "profit_margin": 0.20, "roe": 0.18},
                {"ticker": "PEER2", "pe_ratio": 25, "revenue_growth": 0.18, "profit_margin": 0.22, "roe": 0.20},
                {"ticker": "PEER3", "pe_ratio": 18, "revenue_growth": 0.12, "profit_margin": 0.18, "roe": 0.16}
            ]
        else:
            # Generic peer data
            peers = [
                {"ticker": "PEER1", "pe_ratio": 15, "revenue_growth": 0.08, "profit_margin": 0.10, "roe": 0.12},
                {"ticker": "PEER2", "pe_ratio": 18, "revenue_growth": 0.10, "profit_margin": 0.12, "roe": 0.14},
                {"ticker": "PEER3", "pe_ratio": 16, "revenue_growth": 0.06, "profit_margin": 0.08, "roe": 0.10}
            ]
        
        return {"peers": peers, "sector": sector}
    
    def _create_mock_technical_data(self, ticker: str) -> Dict:
        """Create mock technical data for testing"""
        if "STRONG_BUY" in ticker:
            return {
                "rsi": 25,  # Oversold
                "macd_signal": "bullish_crossover",
                "volume_trend": "high_bullish",
                "price_momentum": 15,  # Strong positive momentum
                "support_resistance": "above_strong_support"
            }
        elif "STRONG_SELL" in ticker:
            return {
                "rsi": 80,  # Overbought
                "macd_signal": "bearish_crossover",
                "volume_trend": "high_bearish",
                "price_momentum": -20,  # Strong negative momentum
                "support_resistance": "below_support"
            }
        else:
            return {
                "rsi": 50,  # Neutral
                "macd_signal": "neutral",
                "volume_trend": "neutral",
                "price_momentum": 2,  # Slight positive
                "support_resistance": "neutral"
            }

async def main():
    """Run the weighted scoring tests"""
    tester = WeightedScoringTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())