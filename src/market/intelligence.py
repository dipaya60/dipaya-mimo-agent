"""
Market Intelligence Engine
Real CoinGecko integration for market analysis with MiMo AI reasoning.
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from ..client import MiMoClient, ChatMessage

logger = logging.getLogger(__name__)


class MarketIntelligence:
    """
    Market analysis engine combining real API data with MiMo AI reasoning.
    
    [REAL] CoinGecko API for market data (free tier: 10-30 calls/min)
    [REAL] MiMo-V2.5-Pro for AI analysis and reasoning
    
    Features:
    - Top coins analysis
    - Market overview
    - AI-powered insights
    - Trend detection
    """

    def __init__(self, mimo_client: MiMoClient, coingecko_api_key: str = ""):
        self.mimo = mimo_client
        self.cg_base = "https://api.coingecko.com/api/v3"
        self.cg_key = coingecko_api_key
        self._http: Optional[httpx.AsyncClient] = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            headers = {}
            if self.cg_key:
                headers["x-cg-demo-api-key"] = self.cg_key
            self._http = httpx.AsyncClient(base_url=self.cg_base, headers=headers, timeout=30)
        return self._http

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    # =========================================================================
    # REAL API: CoinGecko
    # =========================================================================

    async def get_market_overview(self, limit: int = 20) -> List[Dict[str, Any]]:
        """[REAL] Get top coins by market cap from CoinGecko."""
        client = await self._get_http()
        try:
            resp = await client.get("/coins/markets", params={
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "1h,24h,7d",
            })
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"CoinGecko error: {e}")
            return []

    async def get_global_data(self) -> Dict[str, Any]:
        """[REAL] Get global crypto market data."""
        client = await self._get_http()
        try:
            resp = await client.get("/global")
            resp.raise_for_status()
            return resp.json().get("data", {})
        except Exception as e:
            logger.warning(f"CoinGecko global error: {e}")
            return {}

    async def get_trending(self) -> List[Dict[str, Any]]:
        """[REAL] Get trending coins."""
        client = await self._get_http()
        try:
            resp = await client.get("/search/trending")
            resp.raise_for_status()
            return resp.json().get("coins", [])
        except Exception as e:
            logger.warning(f"CoinGecko trending error: {e}")
            return []

    async def get_coin_detail(self, coin_id: str) -> Dict[str, Any]:
        """[REAL] Get detailed coin data."""
        client = await self._get_http()
        try:
            resp = await client.get(f"/coins/{coin_id}", params={
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false",
            })
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"CoinGecko detail error: {e}")
            return {}

    # =========================================================================
    # REAL API: MiMo AI Analysis
    # =========================================================================

    async def analyze_market(self) -> Dict[str, Any]:
        """AI-powered market analysis using real CoinGecko data + MiMo reasoning."""
        # Fetch real data
        overview = await self.get_market_overview(10)
        global_data = await self.get_global_data()
        trending = await self.get_trending()

        # Format for MiMo
        market_summary = f"""
Global Market Data:
- Total Market Cap: ${global_data.get('total_market_cap', {}).get('usd', 0):,.0f}
- 24h Volume: ${global_data.get('total_volume', {}).get('usd', 0):,.0f}
- BTC Dominance: {global_data.get('market_cap_percentage', {}).get('btc', 0):.1f}%
- Active Cryptos: {global_data.get('active_cryptocurrencies', 0)}

Top 10 Coins:
"""
        for coin in overview:
            market_summary += (
                f"- {coin['symbol'].upper()}: ${coin.get('current_price', 0):,.2f} "
                f"({coin.get('price_change_percentage_24h', 0):+.2f}%) "
                f"MCap: ${coin.get('market_cap', 0):,.0f}\n"
            )

        trending_str = ", ".join(
            t.get("item", {}).get("symbol", "?") for t in trending[:7]
        )

        prompt = f"""Analyze this crypto market data and provide insights:

{market_summary}

Trending tokens: {trending_str}

Provide a JSON response with:
1. "overall_sentiment": "bullish"/"bearish"/"neutral"
2. "confidence": 0-100
3. "key_observations": list of 3-5 observations
4. "top_opportunities": list of 2-3 tokens with reasoning
5. "risk_factors": list of 2-3 risks
6. "market_phase": "accumulation"/"markup"/"distribution"/"markdown"
7. "brief_analysis": 2-3 sentence summary
"""

        system = (
            "You are an expert crypto market analyst. Analyze real market data and provide "
            "actionable insights. Be data-driven and specific. Always respond in valid JSON."
        )

        try:
            analysis = await self.mimo.chat_json(prompt, system)
            analysis["data_source"] = "CoinGecko (REAL)"
            analysis["model"] = "MiMo-V2.5-Pro"
            return analysis
        except Exception as e:
            logger.error(f"MiMo analysis error: {e}")
            return {
                "overall_sentiment": "neutral",
                "confidence": 0,
                "error": str(e),
                "data_source": "CoinGecko (REAL)",
            }

    async def generate_report(self) -> str:
        """Generate a comprehensive market report."""
        analysis = await self.analyze_market()
        overview = await self.get_market_overview(5)

        lines = [
            "📈 MARKET INTELLIGENCE REPORT",
            "=" * 50,
            f"Model: MiMo-V2.5-Pro | Data: CoinGecko (REAL)",
            "",
        ]

        if "error" not in analysis:
            sentiment_emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}.get(
                analysis.get("overall_sentiment", ""), "⚪"
            )
            lines.append(f"Sentiment: {sentiment_emoji} {analysis.get('overall_sentiment', 'N/A').upper()}")
            lines.append(f"Confidence: {analysis.get('confidence', 0)}/100")
            lines.append(f"Market Phase: {analysis.get('market_phase', 'N/A')}")
            lines.append(f"\n{analysis.get('brief_analysis', '')}")

            lines.append("\n🔍 Key Observations:")
            for obs in analysis.get("key_observations", []):
                lines.append(f"  • {obs}")

            lines.append("\n💡 Opportunities:")
            for opp in analysis.get("top_opportunities", []):
                lines.append(f"  • {opp}")

            lines.append("\n⚠️ Risk Factors:")
            for risk in analysis.get("risk_factors", []):
                lines.append(f"  • {risk}")

        lines.append("\n📊 Top 5 Coins:")
        for coin in overview:
            change = coin.get("price_change_percentage_24h", 0)
            emoji = "🟢" if change >= 0 else "🔴"
            lines.append(
                f"  {emoji} {coin['symbol'].upper()}: ${coin.get('current_price', 0):,.2f} "
                f"({change:+.2f}%) | MCap: ${coin.get('market_cap', 0):,.0f}"
            )

        return "\n".join(lines)
