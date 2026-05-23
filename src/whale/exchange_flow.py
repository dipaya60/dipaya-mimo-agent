"""
Exchange Flow Analyzer
Tracks whale-to-exchange and exchange-to-whale movements.

Large inflows to exchanges often signal selling pressure.
Large outflows from exchanges suggest accumulation.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ExchangeFlow:
    exchange: str
    direction: str  # "inflow" or "outflow"
    asset: str
    amount: float
    amount_usd: float
    timestamp: datetime
    whale_address: str
    whale_label: str


# DEMO DATA
DEMO_FLOWS = [
    ExchangeFlow("Binance", "outflow", "BTC", 2500, 162_500_000, datetime.utcnow() - timedelta(hours=1), "0x21a31Ee1", "Binance Cold"),
    ExchangeFlow("Binance", "inflow", "ETH", 15000, 52_500_000, datetime.utcnow() - timedelta(hours=2), "0x189B9cBd", "Jump Trading"),
    ExchangeFlow("Kraken", "outflow", "BTC", 800, 52_000_000, datetime.utcnow() - timedelta(hours=3), "0x267be1C1", "Kraken Hot"),
    ExchangeFlow("Coinbase", "inflow", "ETH", 8000, 28_000_000, datetime.utcnow() - timedelta(hours=4), "0xDFd5293D", "Bitfinex"),
    ExchangeFlow("Binance", "outflow", "SOL", 500000, 75_000_000, datetime.utcnow() - timedelta(hours=5), "0x176F3DAb", "Celsius"),
]


class ExchangeFlowAnalyzer:
    """
    Analyzes whale-to-exchange and exchange-to-whale flows.
    
    Key signals:
    - High exchange inflow = potential selling pressure (bearish)
    - High exchange outflow = accumulation (bullish)
    - Net flow trend = directional bias
    
    [DEMO] Uses simulated flow data.
    [PRODUCTION] Integrate with:
        - Whale Alert API (PAID): real-time large transfers
        - CryptoQuant (PAID): exchange flow metrics
        - Glassnode (PAID): on-chain exchange reserves
    """

    def __init__(self, demo: bool = True):
        self.demo = demo
        self.flows: List[ExchangeFlow] = []

    async def get_recent_flows(self, hours: int = 24) -> List[ExchangeFlow]:
        """Get recent exchange flows."""
        if self.demo:
            self.flows = DEMO_FLOWS
            return self.flows
        
        # Production: Whale Alert API
        # GET https://api.whale-alert.io/v1/transactions?api_key=KEY&min_value=1000000
        return []

    async def calculate_net_flow(self, hours: int = 24) -> Dict[str, Any]:
        """
        Calculate net exchange flow.
        
        Positive net = more inflow (bearish pressure)
        Negative net = more outflow (bullish accumulation)
        """
        flows = await self.get_recent_flows(hours)
        
        total_inflow = sum(f.amount_usd for f in flows if f.direction == "inflow")
        total_outflow = sum(f.amount_usd for f in flows if f.direction == "outflow")
        net_flow = total_inflow - total_outflow
        
        # Per-exchange breakdown
        exchange_breakdown: Dict[str, Dict[str, float]] = {}
        for f in flows:
            if f.exchange not in exchange_breakdown:
                exchange_breakdown[f.exchange] = {"inflow": 0, "outflow": 0}
            exchange_breakdown[f.exchange][f.direction] += f.amount_usd
        
        signal = "bearish" if net_flow > 0 else "bullish"
        
        return {
            "total_inflow_usd": total_inflow,
            "total_outflow_usd": total_outflow,
            "net_flow_usd": net_flow,
            "signal": signal,
            "signal_strength": min(abs(net_flow) / 100_000_000, 100),
            "exchange_breakdown": exchange_breakdown,
            "top_flow": max(flows, key=lambda f: f.amount_usd).__dict__ if flows else None,
        }

    async def get_asset_flows(self, asset: str) -> Dict[str, Any]:
        """Get flows filtered by asset."""
        flows = await self.get_recent_flows()
        asset_flows = [f for f in flows if f.asset.upper() == asset.upper()]
        
        inflow = sum(f.amount_usd for f in asset_flows if f.direction == "inflow")
        outflow = sum(f.amount_usd for f in asset_flows if f.direction == "outflow")
        
        return {
            "asset": asset.upper(),
            "total_inflow_usd": inflow,
            "total_outflow_usd": outflow,
            "net_flow_usd": inflow - outflow,
            "flow_count": len(asset_flows),
        }

    async def generate_report(self) -> str:
        """Generate exchange flow report."""
        net = await self.calculate_net_flow()
        
        lines = [
            "🏦 EXCHANGE FLOW ANALYSIS",
            "=" * 40,
            f"📥 Total Inflow:  ${net['total_inflow_usd']:>15,.0f}",
            f"📤 Total Outflow: ${net['total_outflow_usd']:>15,.0f}",
            f"📊 Net Flow:      ${net['net_flow_usd']:>15,.0f}",
            f"🎯 Signal: {net['signal'].upper()} (strength: {net['signal_strength']:.0f}/100)",
            "",
            "Per Exchange:",
        ]
        for exchange, data in net.get("exchange_breakdown", {}).items():
            lines.append(f"  {exchange}: In ${data['inflow']:,.0f} | Out ${data['outflow']:,.0f}")
        
        return "\n".join(lines)
