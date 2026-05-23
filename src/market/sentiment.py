"""
Sentiment Analysis
MiMo-powered sentiment analysis from multiple data sources.
"""

import logging
from typing import Any, Dict, List, Optional

from ..client import MiMoClient

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Multi-source sentiment analysis powered by MiMo.
    
    Sources:
    - Social media sentiment (Twitter/Reddit - demo)
    - News sentiment (demo)
    - On-chain sentiment indicators (demo)
    - Fear & Greed Index concepts
    
    [DEMO] Uses simulated sentiment data.
    [REAL] MiMo reasoning on collected data.
    [PRODUCTION] Integrate with:
        - LunarCrush API (FREE/Paid): social metrics
        - Santiment (PAID): crowd sentiment
        - CryptoPanic (FREE): news aggregator
        - Alternative.me (FREE): Fear & Greed Index
    """

    def __init__(self, mimo_client: MiMoClient):
        self.mimo = mimo_client

    async def analyze_social_sentiment(self, asset: str = "BTC") -> Dict[str, Any]:
        """
        Analyze social sentiment for an asset.
        
        [DEMO] Simulated social metrics.
        [REAL] MiMo analysis on the data.
        """
        # Demo social data
        demo_data = {
            "BTC": {"mentions_24h": 125000, "positive_pct": 62, "negative_pct": 25, "neutral_pct": 13, "trending": True, "fear_greed": 72},
            "ETH": {"mentions_24h": 89000, "positive_pct": 58, "negative_pct": 28, "neutral_pct": 14, "trending": True, "fear_greed": 65},
            "SOL": {"mentions_24h": 45000, "positive_pct": 70, "negative_pct": 18, "neutral_pct": 12, "trending": True, "fear_greed": 78},
            "DOGE": {"mentions_24h": 67000, "positive_pct": 55, "negative_pct": 30, "neutral_pct": 15, "trending": False, "fear_greed": 58},
        }

        data = demo_data.get(asset.upper(), {"mentions_24h": 10000, "positive_pct": 50, "negative_pct": 30, "neutral_pct": 20, "trending": False, "fear_greed": 50})

        # MiMo analysis
        prompt = f"""Analyze this social sentiment data for {asset.upper()}:

Social Metrics (last 24h):
- Total Mentions: {data['mentions_24h']:,}
- Positive Sentiment: {data['positive_pct']}%
- Negative Sentiment: {data['negative_pct']}%
- Neutral: {data['neutral_pct']}%
- Trending: {data['trending']}
- Fear & Greed Index: {data['fear_greed']}/100

Provide JSON with:
1. "sentiment_score": -100 to 100 (bearish to bullish)
2. "interpretation": brief interpretation
3. "crowd_behavior": "fearful"/"greedy"/"neutral"/"euphoric"/"capitulating"
4. "contrarian_signal": what smart money should do opposite to crowd
5. "data_source": "DEMO (simulated social metrics)"
"""

        system = "You are a crypto sentiment analyst. Be concise and data-driven. Respond in JSON."

        try:
            result = await self.mimo.chat_json(prompt, system)
            result["raw_data"] = data
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment_score": 0, "error": str(e), "raw_data": data}

    async def analyze_news_sentiment(self, asset: str = "BTC") -> Dict[str, Any]:
        """Analyze news sentiment. [DEMO] simulated news data."""
        demo_news = {
            "BTC": [
                {"headline": "Bitcoin ETF sees record inflows", "sentiment": "positive", "impact": "high"},
                {"headline": "Fed signals potential rate cuts", "sentiment": "positive", "impact": "medium"},
                {"headline": "BTC whale moves 10K BTC to exchange", "sentiment": "negative", "impact": "medium"},
            ],
            "ETH": [
                {"headline": "Ethereum Dencun upgrade successful", "sentiment": "positive", "impact": "high"},
                {"headline": "L2 activity hits all-time high", "sentiment": "positive", "impact": "medium"},
            ],
        }

        news = demo_news.get(asset.upper(), [])
        prompt = f"""Analyze these news headlines for {asset.upper()}:

{chr(10).join(f"- [{n['sentiment'].upper()}|{n['impact']}] {n['headline']}" for n in news)}

Provide JSON with:
1. "news_sentiment": -100 to 100
2. "dominant_narrative": main theme
3. "impact_assessment": brief assessment
"""

        try:
            result = await self.mimo.chat_json(prompt, "You are a crypto news analyst. Respond in JSON.")
            result["articles_analyzed"] = len(news)
            return result
        except Exception as e:
            return {"news_sentiment": 0, "error": str(e)}

    async def get_comprehensive_sentiment(self, asset: str = "BTC") -> Dict[str, Any]:
        """Get comprehensive sentiment from all sources."""
        social = await self.analyze_social_sentiment(asset)
        news = await self.analyze_news_sentiment(asset)

        social_score = social.get("sentiment_score", 0)
        news_score = news.get("news_sentiment", 0)
        composite = (social_score * 0.6 + news_score * 0.4)

        return {
            "asset": asset.upper(),
            "composite_score": round(composite, 1),
            "social": social,
            "news": news,
            "overall": "bullish" if composite > 20 else "bearish" if composite < -20 else "neutral",
        }
