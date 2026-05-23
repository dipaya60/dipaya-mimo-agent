"""
Holder Concentration Analyzer
Measures token holder concentration using Gini coefficient and other metrics.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ConcentrationMetrics:
    token: str
    gini_coefficient: float  # 0 = equal, 1 = concentrated
    top_10_pct: float  # % of supply held by top 10
    top_20_pct: float
    top_50_pct: float
    whale_count: int  # Wallets holding > 1% of supply
    hhi: float  # Herfindahl-Hirschman Index
    nakamoto_coefficient: int  # Min entities to control 51%
    risk_level: str  # "low", "medium", "high", "critical"


DEMO_CONCENTRATION = [
    ConcentrationMetrics("BTC", 0.82, 12.5, 18.3, 42.1, 8, 0.045, 4, "low"),
    ConcentrationMetrics("ETH", 0.78, 15.2, 22.1, 48.3, 12, 0.062, 5, "medium"),
    ConcentrationMetrics("SOL", 0.91, 35.8, 48.2, 72.1, 5, 0.185, 3, "high"),
    ConcentrationMetrics("ARB", 0.88, 42.1, 55.3, 78.9, 4, 0.220, 2, "critical"),
    ConcentrationMetrics("DOGE", 0.85, 28.4, 38.7, 62.5, 6, 0.120, 4, "medium"),
    ConcentrationMetrics("PEPE", 0.94, 48.2, 62.1, 85.3, 3, 0.310, 2, "critical"),
]


class ConcentrationAnalyzer:
    """
    Analyzes token holder concentration and distribution.
    
    Metrics:
    - Gini Coefficient: 0 (equal) to 1 (one holder has everything)
    - Top N% Holdings: % of supply held by top N holders
    - HHI: Herfindahl-Hirschman Index (market concentration)
    - Nakamoto Coefficient: min entities for 51% control
    
    [DEMO] Uses preset concentration data.
    [PRODUCTION] Integrate with:
        - Etherscan Token Holders (FREE): top holder data
        - Dune Analytics (FREE): custom holder distribution queries
        - Nansen (PAID): labeled holder analysis
        - Solscan (FREE): Solana holder data
    """

    def __init__(self, demo: bool = True):
        self.demo = demo

    async def analyze(self, token: str) -> ConcentrationMetrics:
        """Analyze concentration for a specific token."""
        if self.demo:
            for c in DEMO_CONCENTRATION:
                if c.token.upper() == token.upper():
                    return c
            # Return a default for unknown tokens
            return ConcentrationMetrics(token.upper(), 0.85, 25.0, 35.0, 60.0, 7, 0.100, 4, "medium")
        
        # Production: fetch holder data from block explorers
        # etherscan: /api?module=token&action=tokenholderlist&contractaddress=ADDR
        return ConcentrationMetrics(token, 0, 0, 0, 0, 0, 0, 0, "unknown")

    async def compare_tokens(self, tokens: List[str]) -> List[ConcentrationMetrics]:
        """Compare concentration across multiple tokens."""
        results = []
        for token in tokens:
            metrics = await self.analyze(token)
            results.append(metrics)
        results.sort(key=lambda m: m.gini_coefficient, reverse=True)
        return results

    async def find_risky_tokens(self, threshold: float = 0.90) -> List[ConcentrationMetrics]:
        """Find tokens with dangerously high concentration."""
        all_tokens = [c.token for c in DEMO_CONCENTRATION]
        metrics = await self.compare_tokens(all_tokens)
        return [m for m in metrics if m.gini_coefficient >= threshold]

    async def generate_report(self, token: Optional[str] = None) -> str:
        """Generate concentration analysis report."""
        if token:
            metrics = await self.analyze(token)
            return self._format_single(metrics)
        
        all_metrics = await self.compare_tokens([c.token for c in DEMO_CONCENTRATION])
        
        lines = [
            "📊 HOLDER CONCENTRATION ANALYSIS",
            "=" * 50,
        ]
        
        for m in all_metrics:
            risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}[m.risk_level]
            lines.append(f"\n{risk_emoji} {m.token} (Risk: {m.risk_level.upper()})")
            lines.append(f"   Gini: {m.gini_coefficient:.3f} | HHI: {m.hhi:.3f}")
            lines.append(f"   Top 10: {m.top_10_pct:.1f}% | Top 20: {m.top_20_pct:.1f}% | Top 50: {m.top_50_pct:.1f}%")
            lines.append(f"   Whales (>1%): {m.whale_count} | Nakamoto: {m.nakamoto_coefficient}")
        
        return "\n".join(lines)

    def _format_single(self, m: ConcentrationMetrics) -> str:
        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}[m.risk_level]
        return (
            f"{risk_emoji} {m.token} Concentration Analysis\n"
            f"{'=' * 40}\n"
            f"Gini Coefficient: {m.gini_coefficient:.3f}\n"
            f"Herfindahl Index: {m.hhi:.3f}\n"
            f"Top 10 Holders: {m.top_10_pct:.1f}% of supply\n"
            f"Top 20 Holders: {m.top_20_pct:.1f}% of supply\n"
            f"Top 50 Holders: {m.top_50_pct:.1f}% of supply\n"
            f"Whales (>1% each): {m.whale_count}\n"
            f"Nakamoto Coefficient: {m.nakamoto_coefficient}\n"
            f"Risk Level: {m.risk_level.upper()}\n"
        )
