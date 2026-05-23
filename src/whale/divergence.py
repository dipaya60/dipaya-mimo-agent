"""
Whale vs Retail Divergence Detector
Identifies when whale behavior diverges from retail sentiment.

Key insight: When whales buy while retail sells (or vice versa),
it often signals an upcoming price move.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DivergenceSignal:
    asset: str
    whale_sentiment: str  # "bullish", "bearish", "neutral"
    retail_sentiment: str
    divergence_type: str  # "bullish_div", "bearish_div", "aligned"
    strength: float  # 0-100
    whale_flow_usd: float
    retail_flow_usd: float
    description: str


DEMO_DIVERGENCES = [
    DivergenceSignal("BTC", "bullish", "bearish", "bullish_div", 82.5, 250_000_000, -85_000_000,
                     "Whales accumulating BTC while retail sells - strong bullish divergence"),
    DivergenceSignal("ETH", "bullish", "neutral", "bullish_div", 55.0, 120_000_000, 5_000_000,
                     "Whale accumulation outpacing retail interest in ETH"),
    DivergenceSignal("SOL", "bearish", "bullish", "bearish_div", 71.0, -90_000_000, 45_000_000,
                     "Whales distributing SOL while retail FOMOs in - caution"),
    DivergenceSignal("DOGE", "neutral", "bullish", "bearish_div", 45.0, 0, 30_000_000,
                     "Retail pumping DOGE with no whale participation"),
]


class DivergenceDetector:
    """
    Detects divergence between whale and retail behavior.
    
    Whale behavior: tracked via on-chain large transactions
    Retail behavior: estimated via social sentiment + small tx volume
    
    [DEMO] Uses preset divergence signals.
    [PRODUCTION] Integrate with:
        - LunarCrush (FREE/Paid): social sentiment metrics
        - Santiment (PAID): crowd sentiment vs whale behavior
        - IntoTheBlock (PAID): holder composition analysis
    """

    def __init__(self, demo: bool = True):
        self.demo = demo

    async def detect_divergences(self) -> List[DivergenceSignal]:
        """Detect current whale vs retail divergences."""
        if self.demo:
            return DEMO_DIVERGENCES
        
        # Production: combine whale flow data with social sentiment
        # 1. Get whale flows from tracker
        # 2. Get social sentiment from LunarCrush/Santiment
        # 3. Calculate divergence score
        return []

    async def get_signal_for_asset(self, asset: str) -> Optional[DivergenceSignal]:
        """Get divergence signal for a specific asset."""
        divergences = await self.detect_divergences()
        for d in divergences:
            if d.asset.upper() == asset.upper():
                return d
        return None

    async def rank_by_strength(self) -> List[DivergenceSignal]:
        """Rank divergences by signal strength."""
        divergences = await self.detect_divergences()
        return sorted(divergences, key=lambda d: d.strength, reverse=True)

    async def generate_report(self) -> str:
        """Generate divergence report."""
        signals = await self.rank_by_strength()
        
        lines = [
            "🔀 WHALE vs RETAIL DIVERGENCE",
            "=" * 45,
        ]
        for s in signals:
            emoji = "🟢" if "bullish" in s.divergence_type else "🔴" if "bearish" in s.divergence_type else "⚪"
            lines.append(f"{emoji} {s.asset}: {s.description}")
            lines.append(f"   Whale: {s.whale_sentiment} (${s.whale_flow_usd:+,.0f}) | "
                        f"Retail: {s.retail_sentiment} (${s.retail_flow_usd:+,.0f})")
            lines.append(f"   Strength: {s.strength:.0f}/100")
            lines.append("")
        
        return "\n".join(lines)
