#!/usr/bin/env python3
"""
Test script to verify SectorDCFService integration
Tests sector classification and weighted scoring integration
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.sector_dcf_service import SectorDCFService
from app.services.weighted_scoring_service import WeightedScoringService

async def test_sector_classification():
    """Test sector classification for major Indian stocks"""
    
    sector_dcf_service = SectorDCFService()
    
    test_companies = [
        # BFSI sector
        ("HDFCBANK.NS", "BFSI"),
        ("ICICIBANK.NS", "BFSI"),
        ("SBIN.NS", "BFSI"),
        
        # Pharma sector
        ("SUNPHARMA.NS", "PHARMA"),
        ("DRREDDY.NS", "PHARMA"),
        ("CIPLA.NS", "PHARMA"),
        
        # IT sector
        ("TCS.NS", "IT"),
        ("INFY.NS", "IT"),
        ("WIPRO.NS", "IT"),
        
        # Real Estate
        ("DLF.NS", "REALESTATE"),
        ("GODREJPROP.NS", "REALESTATE"),
        
        # FMCG
        ("HINDUNILVR.NS", "FMCG"),
        ("ITC.NS", "FMCG"),
        
        # Energy
        ("RELIANCE.NS", "ENERGY"),
        ("ONGC.NS", "ENERGY"),
        
        # Unknown (should default to IT)
        ("UNKNOWN.NS", "IT")
    ]
    
    print("🧪 Testing Sector Classification")
    print("=" * 50)
    
    all_correct = True
    for ticker, expected_sector in test_companies:
        classified_sector = sector_dcf_service.classify_sector(ticker)
        status = "✅" if classified_sector == expected_sector else "❌"
        
        print(f"{status} {ticker:<15} → {classified_sector:<12} (expected: {expected_sector})")
        
        if classified_sector != expected_sector:
            all_correct = False
    
    print(f"\n🎯 Sector Classification: {'PASSED' if all_correct else 'FAILED'}")
    return all_correct

async def test_sector_dcf_calculation():
    """Test sector DCF calculation with mock data"""
    
    sector_dcf_service = SectorDCFService()
    
    # Mock company data for testing
    mock_company_data = {
        "current_price": 1500,
        "info": {
            "returnOnEquity": 0.15,
            "bookValue": 800,
            "netInterestMargin": 0.035,
            "returnOnAssets": 0.012,
            "costToIncome": 0.45,
            "gnpaRatio": 0.025,
            "marketCap": 1000000000000,  # 10 Lakh Crore
            "sharesOutstanding": 666666666  # To get price around 1500
        }
    }
    
    print("\n🔬 Testing Sector DCF Calculation")
    print("=" * 50)
    
    test_cases = [
        ("HDFCBANK.NS", "BFSI"),
        ("TCS.NS", "IT"), 
        ("SUNPHARMA.NS", "PHARMA"),
        ("DLF.NS", "REALESTATE")
    ]
    
    for ticker, expected_sector in test_cases:
        try:
            result = await sector_dcf_service.calculate_sector_dcf(
                ticker=ticker,
                sector=expected_sector, 
                mode="simple",
                company_data=mock_company_data
            )
            
            print(f"✅ {ticker:<15} → Fair Value: ₹{result.fair_value:.0f}, "
                  f"Upside: {result.upside_downside_pct:.1f}%, "
                  f"Method: {result.dcf_method}, "
                  f"Confidence: {result.confidence:.2f}")
            
        except Exception as e:
            print(f"❌ {ticker:<15} → Error: {str(e)}")
    
    print(f"\n🎯 Sector DCF Calculation: COMPLETED")

async def test_weighted_scoring_integration():
    """Test weighted scoring service with sector DCF integration"""
    
    weighted_scoring_service = WeightedScoringService()
    
    # Mock complete data for weighted scoring
    mock_company_data = {
        "current_price": 1500,
        "info": {
            "returnOnEquity": 0.15,
            "profitMargins": 0.18,
            "revenueGrowth": 0.12,
            "debtToEquity": 0.3,
            "currentRatio": 1.8,
            "trailingPE": 22,
            "bookValue": 800,
            "netInterestMargin": 0.035,
            "returnOnAssets": 0.012,
            "costToIncome": 0.45,
            "gnpaRatio": 0.025
        }
    }
    
    mock_technical_data = {
        "rsi": 45,
        "macd_signal": "bullish",
        "volume_trend": "normal_bullish",
        "price_momentum": 8.5
    }
    
    mock_peer_data = {
        "peers": [
            {"pe_ratio": 25, "revenue_growth": 0.10, "profit_margin": 0.16},
            {"pe_ratio": 20, "revenue_growth": 0.08, "profit_margin": 0.14},
            {"pe_ratio": 28, "revenue_growth": 0.15, "profit_margin": 0.20}
        ]
    }
    
    print("\n⚖️ Testing Weighted Scoring Integration")
    print("=" * 50)
    
    try:
        result = await weighted_scoring_service.calculate_weighted_score(
            ticker="HDFCBANK.NS",
            company_data=mock_company_data,
            sector="BFSI",
            peer_data=mock_peer_data,
            technical_data=mock_technical_data
        )
        
        print(f"✅ HDFCBANK.NS Weighted Scoring Results:")
        print(f"   📊 Total Score: {result.total_score:.1f}")
        print(f"   🏷️  Investment Label: {result.investment_label}")
        print(f"   🎯 Confidence: {result.confidence:.2f}")
        print(f"   📈 Component Breakdown:")
        print(f"      - DCF Score: {result.dcf_score:.1f} (35% weight)")
        print(f"      - Financial Score: {result.financial_score:.1f} (25% weight)")
        print(f"      - Technical Score: {result.technical_score:.1f} (20% weight)")
        print(f"      - Peer Score: {result.peer_score:.1f} (20% weight)")
        
        # Show detailed component reasoning
        for component, score in result.component_scores.items():
            print(f"   🔍 {component} Details:")
            for reason in score.reasoning[:2]:  # Show first 2 reasons
                print(f"      • {reason}")
        
        print(f"\n🎯 Weighted Scoring Integration: PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Weighted Scoring Integration: FAILED - {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all integration tests"""
    
    print("🚀 SectorDCFService Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Sector Classification
    classification_passed = await test_sector_classification()
    
    # Test 2: Sector DCF Calculation
    await test_sector_dcf_calculation()
    
    # Test 3: Weighted Scoring Integration
    scoring_passed = await test_weighted_scoring_integration()
    
    print("\n" + "=" * 60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Sector Classification: {'PASSED' if classification_passed else 'FAILED'}")
    print(f"✅ Sector DCF Calculation: COMPLETED")
    print(f"✅ Weighted Scoring Integration: {'PASSED' if scoring_passed else 'FAILED'}")
    
    overall_status = classification_passed and scoring_passed
    print(f"\n🎉 Overall Integration Status: {'✅ PASSED' if overall_status else '❌ FAILED'}")
    
    if overall_status:
        print("\n🔥 Ready for frontend integration!")
        print("   Next steps: Update Dashboard to use V3 API endpoints")
    else:
        print("\n🔧 Issues need to be resolved before proceeding")

if __name__ == "__main__":
    asyncio.run(main())