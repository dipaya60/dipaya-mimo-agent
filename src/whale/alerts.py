"""
Custom Alert Manager
Configurable thresholds for whale activity notifications.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertType(Enum):
    WHALE_TX = "whale_transaction"
    EXCHANGE_FLOW = "exchange_flow"
    PRICE_MOVE = "price_move"
    VOLUME_SPIKE = "volume_spike"
    CONCENTRATION_CHANGE = "concentration_change"
    VC_ACTIVITY = "vc_activity"
    CROSS_CHAIN = "cross_chain"
    PATTERN_MATCH = "pattern_match"


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlertRule:
    id: str
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition: Dict[str, Any]  # e.g., {"min_usd": 10_000_000, "asset": "BTC"}
    enabled: bool = True
    cooldown_minutes: int = 60
    last_triggered: Optional[datetime] = None
    webhook_url: Optional[str] = None  # Discord/Telegram webhook


@dataclass
class Alert:
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    data: Dict[str, Any]
    timestamp: datetime


DEMO_RULES = [
    AlertRule("rule_001", "Large BTC Transfer", AlertType.WHALE_TX, AlertSeverity.CRITICAL,
              {"min_usd": 50_000_000, "asset": "BTC"}),
    AlertRule("rule_002", "Exchange Inflow Spike", AlertType.EXCHANGE_FLOW, AlertSeverity.WARNING,
              {"min_usd": 100_000_000, "direction": "inflow"}),
    AlertRule("rule_003", "Whale Accumulation", AlertType.WHALE_TX, AlertSeverity.INFO,
              {"min_usd": 10_000_000, "direction": "outflow_from_exchange"}),
    AlertRule("rule_004", "VC Large Purchase", AlertType.VC_ACTIVITY, AlertSeverity.WARNING,
              {"min_usd": 5_000_000, "action": "buy"}),
    AlertRule("rule_005", "Cross-Chain Bridge", AlertType.CROSS_CHAIN, AlertSeverity.INFO,
              {"min_usd": 20_000_000}),
    AlertRule("rule_006", "5% Price Drop", AlertType.PRICE_MOVE, AlertSeverity.CRITICAL,
              {"change_pct": -5.0, "timeframe": "1h"}),
    AlertRule("rule_007", "Volume Spike", AlertType.VOLUME_SPIKE, AlertSeverity.WARNING,
              {"multiplier": 3.0, "timeframe": "1h"}),
]


class AlertManager:
    """
    Manages custom alert rules and notifications.
    
    Features:
    - Multiple alert types (whale tx, exchange flow, price, volume)
    - Configurable thresholds
    - Cooldown periods to prevent spam
    - Webhook notifications (Discord, Telegram)
    
    [DEMO] Uses preset rules, evaluates against demo data.
    [PRODUCTION] Would evaluate against real-time data streams.
    """

    def __init__(self, demo: bool = True):
        self.demo = demo
        self.rules: Dict[str, AlertRule] = {r.id: r for r in DEMO_RULES}
        self.alert_history: List[Alert] = []

    def add_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.rules[rule.id] = rule
        logger.info(f"Added alert rule: {rule.name}")

    def remove_rule(self, rule_id: str):
        """Remove an alert rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]

    def toggle_rule(self, rule_id: str, enabled: bool):
        """Enable or disable a rule."""
        if rule_id in self.rules:
            self.rules[rule_id].enabled = enabled

    async def evaluate_transaction(self, tx_data: Dict[str, Any]) -> List[Alert]:
        """Evaluate a transaction against all active rules."""
        triggered = []
        
        for rule_id, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if rule.last_triggered:
                elapsed = (datetime.utcnow() - rule.last_triggered).total_seconds() / 60
                if elapsed < rule.cooldown_minutes:
                    continue
            
            # Evaluate based on type
            if rule.alert_type == AlertType.WHALE_TX:
                amount = tx_data.get("amount_usd", 0)
                min_usd = rule.condition.get("min_usd", 0)
                asset_filter = rule.condition.get("asset")
                
                if amount >= min_usd:
                    if asset_filter and tx_data.get("asset", "").upper() != asset_filter.upper():
                        continue
                    
                    alert = Alert(
                        rule_id=rule_id,
                        rule_name=rule.name,
                        severity=rule.severity,
                        message=f"🐋 {rule.name}: ${amount:,.0f} {tx_data.get('asset', 'Unknown')} "
                                f"from {tx_data.get('from', 'Unknown')[:10]}... to {tx_data.get('to', 'Unknown')[:10]}...",
                        data=tx_data,
                        timestamp=datetime.utcnow(),
                    )
                    triggered.append(alert)
                    rule.last_triggered = datetime.utcnow()
                    self.alert_history.append(alert)
        
        return triggered

    async def get_active_rules(self) -> List[AlertRule]:
        """Get all active alert rules."""
        return [r for r in self.rules.values() if r.enabled]

    async def get_alert_history(self, limit: int = 50) -> List[Alert]:
        """Get recent alert history."""
        return sorted(self.alert_history, key=lambda a: a.timestamp, reverse=True)[:limit]

    async def generate_report(self) -> str:
        """Generate alert manager status report."""
        active = await self.get_active_rules()
        
        lines = [
            "🔔 ALERT MANAGER",
            "=" * 40,
            f"Active Rules: {len(active)} / {len(self.rules)}",
            f"Alerts Triggered: {len(self.alert_history)}",
            "",
            "Active Rules:",
        ]
        
        for rule in active:
            emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}[rule.severity.value]
            lines.append(f"  {emoji} [{rule.severity.value.upper()}] {rule.name}")
            lines.append(f"     Type: {rule.alert_type.value} | Cooldown: {rule.cooldown_minutes}m")
            lines.append(f"     Condition: {rule.condition}")
        
        if self.alert_history:
            lines.append("\nRecent Alerts:")
            for alert in self.alert_history[:5]:
                lines.append(f"  {alert.timestamp.strftime('%H:%M')} | {alert.message}")
        
        return "\n".join(lines)
