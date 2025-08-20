from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, List
import logging
from ..services.technical_analysis import technical_analysis_service

router = APIRouter(prefix="/api/v2", tags=["Technical Analysis"])
logger = logging.getLogger(__name__)

@router.get("/technical-analysis/{ticker}")
async def get_technical_analysis(
    ticker: str,
    period: str = Query(default="1y", regex="^(3mo|6mo|1y|3y)$")
):
    """Get real technical analysis with professional indicators"""
    try:
        logger.info(f"Getting technical analysis for {ticker} with period {period}")
        
        # Get real technical analysis data using pandas-ta
        tech_data = technical_analysis_service.get_technical_analysis(ticker, period)
        if not tech_data:
            raise HTTPException(status_code=404, detail=f"Technical analysis data not found for ticker: {ticker}")
        
        # Add AI summary for agentic mode compatibility
        tech_data['ai_summary'] = generate_ai_summary(tech_data)
        
        return tech_data
        
    except Exception as e:
        logger.error(f"Error fetching technical analysis for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch technical analysis for {ticker}")

def generate_ai_summary(data: Dict[str, Any]) -> str:
    """Generate a simple AI-style summary for technical analysis"""
    try:
        ticker = data.get('ticker', 'Unknown')
        indicators = data.get('indicator_values', {})
        
        current_price = indicators.get('current_price', 0)
        rsi = indicators.get('rsi', 50)
        sma_50 = indicators.get('sma_50_current', 0)
        macd_current = indicators.get('macd_current', 0)
        macd_signal = indicators.get('macd_signal_current', 0)
        volume_trend = indicators.get('volume_trend', 'neutral')
        
        # Determine overall trend
        price_trend = "bullish" if current_price > sma_50 else "bearish"
        macd_trend = "bullish" if macd_current > macd_signal else "bearish"
        
        # RSI interpretation
        rsi_status = "overbought" if rsi >= 70 else "oversold" if rsi <= 30 else "neutral"
        
        summary = f"Technical analysis for {ticker} shows {price_trend} momentum with RSI at {rsi:.1f} ({rsi_status}). "
        summary += f"Current price of ₹{current_price:.2f} is {'above' if current_price > sma_50 else 'below'} the 50-day moving average. "
        summary += f"MACD indicates {macd_trend} signals, while volume shows {volume_trend} trend."
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating AI summary: {e}")
        return f"Technical analysis completed for {data.get('ticker', 'Unknown')} with professional indicators."