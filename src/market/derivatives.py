"""
Derivatives Data Analyzer
Open Interest, Funding Rates, and Liquidation tracking.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class FundingRate:
    exchange: str
    pair: str
    rate: float  # % per 8h
    annualized: float
    signal: str


@dataclass
class OpenInterest:
    pair: str
    oi_usd: float
    change_24h_pct: float
    signal: str


@dataclass
class LiquidationData:
    pair: str
    long_liq_usd: float
    short_liq_usd: float
    total_liq_usd: float
    dominant_side: str


DEMO_FUNDING = [
    FundingRate("Binance", "BTC/USDT", 0.012, 13.14, "slightly_bullish"),
    FundingRate("Bybit", "BTC/USDT", 0.015, 16.43, "bullish"),
    FundingRate("OKX", "ETH/USDT", 0.008, 8.76, "neutral"),
    FundingRate("Binance", "SOL/USDT", 0.025, 27.38, "very_bullish"),
    FundingRate("dYdX", "BTC/USDC", 0.010, 10.95, "neutral"),
]

DEMO_OI = [
    OpenInterest("BTC", 18_500_000_000, 5.2, "increasing_interest"),
    OpenInterest("ETH", 8_200_000_000, 3.8, "increasing_interest"),
    OpenInterest("SOL", 2_100_000_000, 12.5, "high_interest"),
    OpenInterest("ARB", 450_000_000, -8.2, "declining_interest"),
    OpenInterest("DOGE", 890_000_000, 25.0, "speculative_frenzy"),
]

DEMO_LIQUIDATIONS = [
    LiquidationData("BTC", 125_000_000, 85_000_000, 210_000_000, "longs"),
    LiquidationData("ETH", 68_000_000, 42_000_000, 110_000_000, "longs"),
    LiquidationData("SOL", 35_000_000, 28_000_000, 63_000_000, "longs"),
]


class DerivativesAnalyzer:
    """
    Analyzes derivatives market data.
    
    Key metrics:
    - Funding Rate: positive = longs pay shorts (bullish crowding)
    - Open Interest: total outstanding derivative positions
    - Liquidations: forced closures indicating overleveraged positions
    
    [DEMO] Uses simulated derivatives data.
    [PRODUCTION] Integrate with:
        - Coinglass (FREE/Paid): derivatives data aggregator
        - Bybit API (FREE): funding rates + OI
        - Binance Futures API (FREE): funding + OI + liquidations
        - Coinalyze (FREE/Paid): aggregated derivatives data
    """

    def __init__(self, demo: bool = True):
        self.demo = demo

    async def get_funding_rates(self) -> List[FundingRate]:
        """Get current funding rates across exchanges."""
        if self.demo:
            return DEMO_FUNDING
        
        # Production: Coinglass API
        # GET https://open-api.coinglass.com/public/v2/funding
        return []

    async def get_open_interest(self) -> List[OpenInterest]:
        """Get open interest data."""
        if self.demo:
            return DEMO_OI
        
        # Production: Coinglass/Exchange APIs
        return []

    async def get_liquidations(self, hours: int = 24) -> List[LiquidationData]:
        """Get liquidation data."""
        if self.demo:
            return DEMO_LIQUIDATIONS
        
        # Production: Coinglass liquidation API
        return []

    async def analyze_leverage(self) -> Dict[str, Any]:
        """Analyze market leverage conditions."""
        funding = await self.get_funding_rates()
        oi = await self.get_open_interest()
        liqs = await self.get_liquidations()

        # High positive funding + rising OI = overleveraged longs (bearish warning)
        # High negative funding + rising OI = overleveraged shorts (bullish warning)
        avg_funding = sum(f.rate for f in funding) / len(funding) if funding else 0
        total_oi = sum(o.oi_usd for o in oi)
        total_liqs = sum(l.total_liq_usd for l in liqs)

        # Determine leverage risk
        if avg_funding > 0.03:
            risk = "high_long_crowding"
            signal = "bearish_warning"
        elif avg_funding < -0.01:
            risk = "high_short_crowding"
            signal = "bullish_warning"
        else:
            risk = "balanced"
            signal = "neutral"

        return {
            "avg_funding_rate": avg_funding,
            "total_open_interest_usd": total_oi,
            "total_liquidations_24h_usd": total_liqs,
            "leverage_risk": risk,
            "signal": signal,
            "funding_details": [f.__dict__ for f in funding],
            "oi_details": [o.__dict__ for o in oi],
        }

    async def detect_squeeze_potential(self) -> List[Dict[str, Any]]:
        """Detect potential short/long squeeze setups."""
        funding = await self.get_funding_rates()
        oi = await self.get_open_interest()

        squeezes = []
        for f in funding:
            matching_oi = [o for o in oi if o.pair in f.pair]
            if matching_oi:
                o = matching_oi[0]
                if f.rate > 0.02 and o.change_24h_pct > 10:
                    squeezes.append({
                        "pair": f.pair,
                        "type": "short_squeeze",
                        "funding": f.rate,
                        "oi_change": o.change_24h_pct,
                        "risk": "high",
                    })
                elif f.rate < -0.01 and o.change_24h_pct > 10:
                    squeezes.append({
                        "pair": f.pair,
                        "type": "long_squeeze",
                        "funding": f.rate,
                        "oi_change": o.change_24h_pct,
                        "risk": "high",
                    })

        return squeezes

    async def generate_report(self) -> str:
        """Generate derivatives analysis report."""
        leverage = await self.analyze_leverage()
        squeezes = await self.detect_squeeze_potential()

        lines = [
            "📊 DERIVATIVES ANALYSIS",
            "=" * 50,
            f"Avg Funding Rate: {leverage['avg_funding_rate']*100:.3f}%",
            f"Total Open Interest: ${leverage['total_open_interest_usd']:,.0f}",
            f"24h Liquidations: ${leverage['total_liquidations_24h_usd']:,.0f}",
            f"Leverage Risk: {leverage['leverage_risk'].upper()}",
            f"Signal: {leverage['signal'].upper()}",
            "",
            "Funding Rates:",
        ]

        for f in leverage.get("funding_details", []):
            emoji = "🟢" if f["rate"] < 0 else "🟡" if f["rate"] < 0.02 else "🔴"
            lines.append(f"  {emoji} {f['exchange']} {f['pair']}: {f['rate']*100:.3f}% ({f['annualized']:.1f}% APR)")

        lines.append("\nOpen Interest:")
        for o in leverage.get("oi_details", []):
            emoji = "📈" if o["change_24h_pct"] > 0 else "📉"
            lines.append(f"  {emoji} {o['pair']}: ${o['oi_usd']:,.0f} ({o['change_24h_pct']:+.1f}%)")

        if squeezes:
            lines.append("\n⚡ SQUEEZE ALERTS:")
            for s in squeezes:
                lines.append(f"  🔥 {s['pair']}: {s['type'].replace('_', ' ').upper()} potential!")

        return "\n".join(lines)
