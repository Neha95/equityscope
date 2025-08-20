#!/usr/bin/env python3
"""
Temporary script to clear corrupted cache entries
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.services.intelligent_cache import IntelligentCacheManager, CacheType

async def clear_reliance_cache():
    """Clear corrupted cache entries for RELIANCE.NS"""
    
    cache_manager = IntelligentCacheManager()
    
    print("🧹 Clearing corrupted cache entries for RELIANCE.NS...")
    
    # Clear sector classification cache
    await cache_manager.invalidate(CacheType.FINANCIAL_DATA, "RELIANCE.NS_sector_classification")
    print("✅ Cleared sector classification cache")
    
    # Clear blended valuation cache  
    await cache_manager.invalidate(CacheType.FINANCIAL_DATA, "RELIANCE.NS_blended_valuation")
    print("✅ Cleared blended valuation cache")
    
    # Clear peer comparison cache
    await cache_manager.invalidate(CacheType.FINANCIAL_DATA, "RELIANCE.NS_peer_analysis")
    print("✅ Cleared peer comparison cache")
    
    print("🎉 Cache clearing complete! Next API calls will use fresh data.")

if __name__ == "__main__":
    asyncio.run(clear_reliance_cache())