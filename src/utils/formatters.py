"""Output formatters for terminal, JSON, and plain text."""

import json
from typing import Any, Dict, List, Optional


def format_currency(value: float, symbol: str = "$") -> str:
    if abs(value) >= 1e9:
        return f"{symbol}{value/1e9:.2f}B"
    elif abs(value) >= 1e6:
        return f"{symbol}{value/1e6:.2f}M"
    elif abs(value) >= 1e3:
        return f"{symbol}{value/1e3:.2f}K"
    return f"{symbol}{value:,.2f}"


def format_percentage(value: float) -> str:
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def format_whale_tx(tx: Dict[str, Any]) -> str:
    direction = "🟢 INFLOW" if tx.get("direction") == "in" else "🔴 OUTFLOW"
    return (
        f"{direction} | {tx.get('asset', 'Unknown')} | "
        f"{format_currency(tx.get('amount_usd', 0))} | "
        f"Wallet: {tx.get('wallet', 'Unknown')[:8]}...{tx.get('wallet', '')[-6:]}"
    )


def format_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None) -> str:
    """Simple ASCII table formatter."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    sep = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_line = "| " + " | ".join(h.ljust(w) for h, w in zip(headers, col_widths)) + " |"

    lines = []
    if title:
        lines.append(f"\n  {title}")
    lines.append(sep)
    lines.append(header_line)
    lines.append(sep)
    for row in rows:
        line = "| " + " | ".join(str(c).ljust(w) for c, w in zip(row, col_widths)) + " |"
        lines.append(line)
    lines.append(sep)
    return "\n".join(lines)


def to_json(data: Any, pretty: bool = True) -> str:
    return json.dumps(data, indent=2 if pretty else None, default=str)
