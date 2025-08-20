#!/usr/bin/env python3
"""
Test SectorIntelligenceService integration with DCF calculations
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.sector_intelligence_service import sector_intelligence_service
from app.services.dcf_service import DCFService
from app.services.data_service import DataService


async def test_sector_intelligence():
    print("🧪 Testing SectorIntelligenceService Integration")
    print("=" * 60)
    
    # Test 1: Sector Intelligence Service Basic Functions
    print("\n1. Testing SectorIntelligenceService Basic Functions")
    print("-" * 50)
    
    # Test sector mapping
    it_sector = sector_intelligence_service.get_sector_mapping("IT")
    print(f"IT sector mapping: {it_sector}")
    
    # Test sector intelligence
    it_intel = sector_intelligence_service.get_sector_intelligence("IT")
    if it_intel:
        print(f"IT Sector Intelligence:")
        print(f"  - Damodaran Name: {it_intel.damodaran_name}")
        print(f"  - Unlevered Beta: {it_intel.unlevered_beta}")
        print(f"  - Terminal Growth: {it_intel.terminal_growth_rate:.1%}")
        print(f"  - Tax Rate: {it_intel.effective_tax_rate:.1%}")
    
    # Test WACC calculation
    try:
        it_wacc = await sector_intelligence_service.calculate_wacc("IT")
        print(f"  - Calculated WACC: {it_wacc:.1%}")
    except Exception as e:
        print(f"  - WACC Calculation Error: {e}")
    
    # Test 2: Enhanced DCF Defaults with Sector Intelligence
    print("\n2. Testing Enhanced DCF Defaults")
    print("-" * 50)
    
    try:
        # Get financial data for TCS (IT sector)
        financial_data = DataService.get_financial_data("TCS.NS")
        if financial_data:
            print(f"Retrieved financial data for TCS.NS: {len(financial_data.revenue)} years")
            
            # Calculate defaults with sector intelligence
            defaults = await DCFService.calculate_default_assumptions(
                financial_data, 
                ticker="TCS.NS", 
                sector="IT"
            )
            
            print(f"Enhanced DCF Defaults for TCS (IT):")
            print(f"  - Revenue Growth: {defaults.revenue_growth_rate:.1f}% (from historical data)")
            print(f"  - EBITDA Margin: {defaults.ebitda_margin:.1f}% (from historical data)")
            print(f"  - WACC: {defaults.wacc:.1f}% (from Damodaran + live risk-free rate)")
            print(f"  - Tax Rate: {defaults.tax_rate:.1f}% (from Damodaran sector data)")
            print(f"  - Terminal Growth: {defaults.terminal_growth_rate:.1f}% (from Damodaran)")
            print(f"  - Current Price: ₹{defaults.current_price:.2f}")
            
            print(f"\nRationale:")
            for key, reason in defaults.rationale.items():
                print(f"  - {key}: {reason}")
                
        else:
            print("❌ Could not retrieve financial data for TCS.NS")
            
    except Exception as e:
        print(f"❌ Error testing DCF defaults: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Multiple Sectors
    print("\n3. Testing Multiple Sectors")
    print("-" * 50)
    
    test_sectors = ["IT", "BFSI", "PHARMA"]
    for sector in test_sectors:
        try:
            wacc = await sector_intelligence_service.calculate_wacc(sector)
            intel = sector_intelligence_service.get_sector_intelligence(sector)
            multiples = sector_intelligence_service.get_industry_multiples(sector)
            
            print(f"{sector}:")
            print(f"  - WACC: {wacc:.1%}")
            if intel:
                print(f"  - Terminal Growth: {intel.terminal_growth_rate:.1%}")
                print(f"  - Tax Rate: {intel.effective_tax_rate:.1%}")
            print(f"  - P/E Multiple: {multiples.get('pe_ratio', 'N/A')}")
            
        except Exception as e:
            print(f"  - Error for {sector}: {e}")
    
    # Test 4: Supported Sectors
    print("\n4. Supported Sectors")
    print("-" * 50)
    supported = sector_intelligence_service.get_supported_sectors()
    print(f"Supported sectors: {', '.join(supported)}")
    
    print("\n" + "=" * 60)
    print("✅ SectorIntelligenceService testing completed!")


async def test_api_endpoint():
    """Test the API endpoint integration"""
    print("\n🌐 Testing API Endpoint Integration")
    print("-" * 50)
    
    import requests
    
    try:
        # Test the enhanced defaults endpoint
        response = requests.get(
            "http://localhost:8000/api/valuation/TCS.NS/defaults",
            params={"sector": "IT"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint working!")
            print(f"Response keys: {list(data.keys())}")
            print(f"Revenue Growth: {data.get('revenue_growth_rate', 'N/A'):.1f}%")
            print(f"WACC: {data.get('wacc', 'N/A'):.1f}%")
            print(f"Terminal Growth: {data.get('terminal_growth_rate', 'N/A'):.1f}%")
        else:
            print(f"❌ API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")


if __name__ == "__main__":
    # Run the tests
    asyncio.run(test_sector_intelligence())
    asyncio.run(test_api_endpoint())