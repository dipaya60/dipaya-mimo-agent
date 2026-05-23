"""
On-Chain Metrics
Blockchain-native indicators for market analysis.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class OnChainMetric:
    name: str
    value: float
    change_24h: float
    signal: str  # "bullish", "bearish", "neutral"
    description: str


DEMO_METRICS = [
    OnChainMetric("Active Addresses", 920000, 5.2, "bullish", "Rising active addresses suggest growing network usage"),
    OnChainMetric("Transaction Count", 315000, 3.8, "bullish", "Healthy transaction volume"),
    OnChainMetric("Exchange Reserves", 2_340_000, -2.1, "bullish", "Decreasing exchange reserves = accumulation"),
    OnChainMetric("Stablecoin Supply", 142_000_000_000, 1.5, "bullish", "Growing stablecoin supply = dry powder entering"),
    OnChainMetric("MVRV Ratio", 1.85, -0.5, "neutral", "MVRV between 1-2 suggests fair value"),
    OnChainMetric("NVT Ratio", 45.2, 2.3, "bearish", "High NVT suggests network overvalued relative to tx volume"),
    OnChainMetric("Hash Rate", 650_000_000, 1.8, "bullish", "Rising hash rate = miner confidence"),
    OnChainMetric("Miner Revenue", 42_000_000, -3.2, "neutral", "Miner revenue stabilizing after halving"),
    OnChainMetric("DeFi TVL", 98_000_000_000, 4.5, "bullish", "DeFi TVL growing - capital returning to protocols"),
    OnChainMetric("Gas Price (Gwei)", 25, -15.0, "bullish", "Lower gas = more accessible network"),
]


class OnChainMetrics:
    """
    On-chain metrics for fundamental analysis.
    
    [DEMO] Uses preset metric values.
    [PRODUCTION] Integrate with:
        - Glassnode (PAID): comprehensive on-chain data
        - CryptoQuant (PAID): exchange flow + mining data
        - DeFiLlama (FREE): DeFi TVL data
        - Dune Analytics (FREE): custom on-chain queries
        - Blockchair (FREE/Paid): blockchain data API
    """

    def __init__(self, demo: bool = True):
        self.demo = demo

    async def get_all_metrics(self) -> List[OnChainMetric]:
        """Get all on-chain metrics."""
        if self.demo:
            return DEMO_METRICS
        
        # Production: aggregate from multiple APIs
        # Glassnode: /v1/metrics/addresses/active_count
        # CryptoQuant: /v1/btc/exchange-reserve
        # DeFiLlama: /v2/historicalChainTvl
        return []

    async def get_metric(self, name: str) -> OnChainMetric:
        """Get a specific metric by name."""
        metrics = await self.get_all_metrics()
        for m in metrics:
            if m.name.lower() == name.lower():
                return m
        return OnChainMetric(name, 0, 0, "unknown", "Metric not found")

    async def get_bullish_signals(self) -> List[OnChainMetric]:
        """Get metrics with bullish signals."""
        metrics = await self.get_all_metrics()
        return [m for m in metrics if m.signal == "bullish"]

    async def get_bearish_signals(self) -> List[OnChainMetric]:
        """Get metrics with bearish signals."""
        metrics = await self.get_all_metrics()
        return [m for m in metrics if m.signal == "bearish"]

    async def compute_on_chain_score(self) -> Dict[str, Any]:
        """Compute composite on-chain health score."""
        metrics = await self.get_all_metrics()
        
        bullish = sum(1 for m in metrics if m.signal == "bullish")
        bearish = sum(1 for m in metrics if m.signal == "bearish")
        total = len(metrics)
        
        score = ((bullish - bearish) / total * 50) + 50  # 0-100 scale
        
        return {
            "on_chain_score": round(score, 1),
            "bullish_signals": bullish,
            "bearish_signals": bearish,
            "neutral_signals": total - bullish - bearish,
            "total_metrics": total,
            "interpretation": "bullish" if score > 60 else "bearish" if score < 40 else "neutral",
        }

    async def generate_report(self) -> str:
        """Generate on-chain metrics report."""
        metrics = await self.get_all_metrics()
        score = await self.compute_on_chain_score()

        lines = [
            "⛓️ ON-CHAIN METRICS REPORT",
            "=" * 50,
            f"Composite Score: {score['on_chain_score']}/100 ({score['interpretation'].upper()})",
            f"Bullish: {score['bullish_signals']} | Bearish: {score['bearish_signals']} | Neutral: {score['neutral_signals']}",
            "",
        ]

        for m in metrics:
            emoji = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}[m.signal]
            lines.append(f"{emoji} {m.name}: {m.value:,.0f} ({m.change_24h:+.1f}%)")
            lines.append(f"   {m.description}")

        return "\n".join(lines)
