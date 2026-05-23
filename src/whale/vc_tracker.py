"""
VC Wallet Tracker
Tracks venture capital firm wallets and their investment moves.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class VCFirm:
    name: str
    wallets: List[str]
    chains: List[str]
    portfolio_tokens: List[str]
    aum_estimate_usd: float


@dataclass
class VCActivity:
    firm: str
    action: str  # "buy", "sell", "transfer", "vest_claim", "stake"
    token: str
    amount_usd: float
    wallet: str
    chain: str
    timestamp: str


DEMO_VC_FIRMS = [
    VCFirm("a16z Crypto", ["0x05e793cE0c6027323Ac150F6d45C2344D28B6019", "0xa7EFae3B0B6Ea90131b4D0d9D7e5b9e2B7F7E4c8"],
           ["Ethereum", "Solana"], ["UNI", "COMP", "MKR", "SOL"], 7_600_000_000),
    VCFirm("Paradigm", ["0x2E6539ed607135b79e3f567890abcdef12345678", "0x3c7C0e83A0b2D5f7E9a1B4c6D8e0F2a3B5c7D9e1"],
           ["Ethereum", "Arbitrum"], ["UNI", "LDO", "ARB", "OP"], 8_700_000_000),
    VCFirm("Polychain Capital", ["0x4d8E5f6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C1D2E"],
           ["Ethereum", "Solana"], ["DOT", "ATOM", "NEAR", "SOL"], 3_200_000_000),
    VCFirm("Pantera Capital", ["0x5e9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7F"],
           ["Ethereum"], ["BTC", "ETH", "SOL", "AVAX"], 4_800_000_000),
    VCFirm("Multicoin Capital", ["0x6fA0B1C2D3E4F5A6B7C8D9E0F1A2B3C4D5E6F7A8"],
           ["Solana", "Ethereum"], ["SOL", "HNT", "RNDR"], 1_500_000_000),
]

DEMO_VC_ACTIVITIES = [
    VCActivity("a16z Crypto", "buy", "UNI", 15_000_000, "0x05e793cE", "Ethereum", "2025-01-15T10:00:00Z"),
    VCActivity("Paradigm", "transfer", "ARB", 25_000_000, "0x2E6539ed", "Arbitrum", "2025-01-15T09:30:00Z"),
    VCActivity("Polychain Capital", "stake", "DOT", 8_000_000, "0x4d8E5f6A", "Ethereum", "2025-01-15T08:00:00Z"),
    VCActivity("Pantera Capital", "sell", "BTC", 12_000_000, "0x5e9F0A1B", "Ethereum", "2025-01-14T22:00:00Z"),
    VCActivity("Multicoin Capital", "vest_claim", "SOL", 5_000_000, "0x6fA0B1C2", "Solana", "2025-01-14T20:00:00Z"),
]


class VCTracker:
    """
    Tracks VC firm wallet activity.
    
    Monitors:
    - Token purchases (new positions)
    - Token sales (exits)
    - Vesting claims
    - Staking activity
    - Fund transfers between wallets
    
    [DEMO] Uses preset VC firm data.
    [PRODUCTION] Integrate with:
        - Arkham Intelligence (PAID): entity-labeled wallets
        - Nansen (PAID): smart money/VC labels
        - Dune Analytics (FREE): custom queries for VC wallets
    """

    def __init__(self, demo: bool = True):
        self.demo = demo
        self.firms = {f.name: f for f in DEMO_VC_FIRMS}

    async def get_firm_activity(self, firm_name: str) -> List[VCActivity]:
        """Get recent activity for a specific VC firm."""
        if self.demo:
            return [a for a in DEMO_VC_ACTIVITIES if a.firm == firm_name]
        
        # Production: query labeled wallet data
        return []

    async def get_all_activities(self, hours: int = 72) -> List[VCActivity]:
        """Get all VC activities in time window."""
        if self.demo:
            return DEMO_VC_ACTIVITIES
        
        # Production: aggregate from all tracked VC wallets
        return []

    async def detect_vc_accumulation(self, token: str) -> Dict[str, Any]:
        """Check if VCs are accumulating a specific token."""
        activities = await self.get_all_activities()
        token_acts = [a for a in activities if a.token.upper() == token.upper()]
        
        buys = [a for a in token_acts if a.action == "buy"]
        sells = [a for a in token_acts if a.action == "sell"]
        
        total_buy = sum(a.amount_usd for a in buys)
        total_sell = sum(a.amount_usd for a in sells)
        
        return {
            "token": token.upper(),
            "vc_buys": len(buys),
            "vc_sells": len(sells),
            "net_flow_usd": total_buy - total_sell,
            "signal": "accumulating" if total_buy > total_sell else "distributing",
            "buy_firms": list(set(a.firm for a in buys)),
            "sell_firms": list(set(a.firm for a in sells)),
        }

    async def generate_report(self) -> str:
        """Generate VC tracking report."""
        activities = await self.get_all_activities()
        
        lines = [
            "🏦 VC WALLET TRACKER",
            "=" * 40,
            f"Tracked Firms: {len(self.firms)}",
            f"Recent Activities: {len(activities)}",
            "",
        ]
        
        for firm_name, firm in self.firms.items():
            firm_acts = [a for a in activities if a.firm == firm_name]
            if firm_acts:
                lines.append(f"📊 {firm_name} (AUM: ${firm.aum_estimate_usd/1e9:.1f}B)")
                for act in firm_acts:
                    emoji = "🟢" if act.action in ["buy", "stake"] else "🔴" if act.action == "sell" else "⚪"
                    lines.append(f"  {emoji} {act.action.upper()} {act.token} - ${act.amount_usd:,.0f} on {act.chain}")
                lines.append("")
        
        return "\n".join(lines)
