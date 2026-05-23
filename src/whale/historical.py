"""
Historical Pattern Matcher
Matches current whale behavior against historical patterns
that preceded major price moves.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class HistoricalPattern:
    name: str
    description: str
    conditions: Dict[str, Any]
    outcome: str  # What happened after this pattern
    outcome_pct: float  # Average % move
    confidence: float  # How reliable is this pattern
    timeframe: str  # "1d", "7d", "30d"
    examples: List[str]  # Date examples when this occurred


DEMO_PATTERNS = [
    HistoricalPattern(
        "Whale Accumulation Pre-Breakout",
        "Whales accumulate heavily on-chain while price consolidates, followed by a breakout",
        {"whale_net_flow": "> 100M USD", "price_range": "tight (< 5%)", "exchange_outflow": "high"},
        "Price broke out 15-30% within 2 weeks",
        22.5, 78.0, "14d",
        ["Oct 2023 BTC pre-rally", "Jan 2024 BTC ETF anticipation"]
    ),
    HistoricalPattern(
        "Exchange Whale Dump",
        "Multiple whales deposit to exchanges simultaneously, followed by sell-off",
        {"exchange_inflow": "> 200M USD", "wallet_count": "> 5 whales", "timeframe": "< 24h"},
        "Price dropped 8-15% within 1 week",
        -11.5, 82.0, "7d",
        ["May 2021 crash", "Nov 2022 FTX collapse"]
    ),
    HistoricalPattern(
        "Smart Money Rotation",
        "VCs and smart money rotate from one sector to another",
        {"vc_sell_sector_A": True, "vc_buy_sector_B": True, "timeframe": "< 7d"},
        "Sector B outperforms by 20-40% over next month",
        30.0, 65.0, "30d",
        ["DeFi Summer 2020", "L1 rotation Q4 2021"]
    ),
    HistoricalPattern(
        "Stablecoin Whale Minting",
        "Large stablecoin minting events by known whale wallets",
        {"usdt_mint": "> 500M", "usdc_mint": "> 200M", "whale_source": True},
        "Price rally 5-15% within 2 weeks as capital enters market",
        10.0, 72.0, "14d",
        ["Mar 2023 USDC recovery", "Various USDT mints before rallies"]
    ),
]


class HistoricalPatternMatcher:
    """
    Matches current whale behavior against historical patterns.
    
    Uses pattern recognition to predict potential price moves
    based on similar whale behavior in the past.
    
    [DEMO] Uses preset patterns.
    [PRODUCTION] Integrate with:
        - Glassnode (PAID): historical on-chain data
        - CryptoQuant (PAID): historical exchange flow data
        - Custom ML models trained on historical data
    """

    def __init__(self, demo: bool = True):
        self.demo = demo
        self.patterns = DEMO_PATTERNS

    async def match_current_conditions(self, current_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Match current market conditions against known patterns."""
        if self.demo:
            # Simulate matching: return patterns with adjusted confidence
            matches = []
            for i, pattern in enumerate(self.patterns):
                # Simulate that some patterns match
                if i < 2:  # First two patterns "match"
                    matches.append({
                        "pattern": pattern.name,
                        "match_score": 60 + (i * 15),
                        "expected_outcome": pattern.outcome,
                        "expected_move_pct": pattern.outcome_pct,
                        "timeframe": pattern.timeframe,
                        "historical_confidence": pattern.confidence,
                        "description": pattern.description,
                        "past_examples": pattern.examples,
                    })
            return matches
        
        # Production: analyze real current data against pattern conditions
        return []

    async def get_pattern_details(self, pattern_name: str) -> Optional[HistoricalPattern]:
        """Get details for a specific pattern."""
        for p in self.patterns:
            if p.name.lower() == pattern_name.lower():
                return p
        return None

    async def add_custom_pattern(self, pattern: HistoricalPattern):
        """Add a custom pattern to the matcher."""
        self.patterns.append(pattern)
        logger.info(f"Added custom pattern: {pattern.name}")

    async def generate_report(self) -> str:
        """Generate historical pattern matching report."""
        matches = await self.match_current_conditions()
        
        lines = [
            "📚 HISTORICAL PATTERN MATCHER",
            "=" * 45,
            f"Patterns Database: {len(self.patterns)}",
            f"Active Matches: {len(matches)}",
            "",
        ]
        
        for m in matches:
            emoji = "🟢" if m["expected_move_pct"] > 0 else "🔴"
            lines.append(f"{emoji} MATCH: {m['pattern']}")
            lines.append(f"   Match Score: {m['match_score']}/100")
            lines.append(f"   Expected: {m['expected_outcome']}")
            lines.append(f"   Move: {m['expected_move_pct']:+.1f}% in {m['timeframe']}")
            lines.append(f"   Historical Accuracy: {m['historical_confidence']:.0f}%")
            lines.append(f"   Past Examples: {', '.join(m['past_examples'])}")
            lines.append("")
        
        return "\n".join(lines)
