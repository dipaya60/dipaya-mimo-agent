#!/usr/bin/env python3
"""
MiMo Agent Advanced — Narrative Trade Intelligence
Powered by Xiaomi MiMo-V2.5-Pro

Usage:
    python main.py whale ETH
    python main.py whale ETH --divergence
    python main.py whale ETH --smart-money
    python main.py whale ETH --exchange-flows
    python main.py whale ETH --concentration
    python main.py whale ETH --heatmap
    python main.py whale ETH --vc-tracking
    python main.py whale ETH --orderbook
    python main.py whale ETH --historical
    python main.py whale ETH --alert --min-usd 500000
    python main.py analyze bitcoin
    python main.py sentiment "BTC ETH"
    python main.py demo
"""

import sys
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

sys.path.insert(0, str(Path(__file__).parent))

from src.client import MiMoClient
from src.config import Config
from src.whale.tracker import WhaleTracker
from src.market.intelligence import MarketIntelligence
from src.market.sentiment import SentimentAnalyzer

console = Console()


def banner():
    console.print(Panel.fit(
        "[bold cyan]MiMo Agent Advanced — Narrative Trade Intelligence[/bold cyan]\n"
        "[dim]Powered by Xiaomi MiMo-V2.5-Pro [/dim]",
        border_style="cyan"
    ))


def cmd_whale(args):
    client = MiMoClient()
    tracker = WhaleTracker(client)
    token = args.token.upper()

    if args.divergence:
        console.print(f"\n🐋 vs 👥 Divergence: [bold]{token}[/bold]\n")
        with console.status("Analyzing..."):
            r = tracker.detect_divergence(token, args.hours)
        emoji = "🟢" if "BULL" in r.get("direction", "") else "🔴" if "BEAR" in r.get("direction", "") else "⚪"
        console.print(f"{emoji} {r.get('direction', 'N/A')}")
        console.print(f"   Whales: {r.get('whale_action')} | Retail: {r.get('retail_action')}")
        console.print(f"   Strength: {r.get('strength', 0):.0%}\n")

    elif args.concentration:
        console.print(f"\n📏 Concentration: [bold]{token}[/bold]\n")
        with console.status("Calculating Gini..."):
            r = tracker.analyze_concentration(token)
        t = Table(title=f"Holder Concentration: {token}")
        t.add_column("Metric", style="cyan"); t.add_column("Value", style="green")
        t.add_row("Gini", f"{r.get('gini', 0):.4f}")
        t.add_row("Top 10", f"{r.get('top10_pct', 0)}%")
        t.add_row("Risk", r.get("risk", "N/A"))
        console.print(t); console.print()

    elif args.heatmap:
        console.print(f"\n🌡️ Heatmap: [bold]{token}[/bold]\n")
        with console.status("Generating..."):
            r = tracker.generate_heatmap(token)
        for h in r.get("peak_hours", [])[:8]:
            bar = "█" * int(h.get("score", 0) * 20)
            console.print(f"  {h.get('hour', 0):02d}:00  {bar} {h.get('score', 0):.2f}")
        console.print()

    elif args.vc_tracking:
        console.print(f"\n🏢 VC Tracking: [bold]{token}[/bold]\n")
        with console.status("Tracking VCs..."):
            r = tracker.track_vcs(token, args.hours)
        t = Table(title="VC Wallets")
        t.add_column("VC", style="cyan"); t.add_column("Score", style="green"); t.add_column("Action", style="yellow")
        for vc in r.get("vcs", [])[:5]:
            t.add_row(vc.get("name", "?"), str(vc.get("score", 0)), vc.get("action", "?"))
        console.print(t); console.print()

    elif args.smart_money:
        console.print(f"\n🧠 Smart Money: [bold]{token}[/bold]\n")
        with console.status("Ranking wallets..."):
            r = tracker.rank_smart_money(token)
        t = Table(title="Top Smart Money")
        t.add_column("#", style="dim"); t.add_column("Address", style="cyan"); t.add_column("Score", style="green"); t.add_column("Win Rate", style="yellow")
        for i, w in enumerate(r.get("wallets", [])[:10], 1):
            t.add_row(str(i), w.get("address", "?")[:14], str(w.get("score", 0)), f"{w.get('win_rate', 0):.0%}")
        console.print(t); console.print()

    elif args.exchange_flows:
        console.print(f"\n🏦 Exchange Flows: [bold]{token}[/bold]\n")
        with console.status("Analyzing flows..."):
            r = tracker.analyze_exchange_flows(token, args.hours)
        t = Table(title="Exchange Flows")
        t.add_column("Exchange", style="cyan"); t.add_column("Inflow", style="red"); t.add_column("Outflow", style="green"); t.add_column("Net", style="white")
        for f in r.get("flows", []):
            net_c = "green" if f.get("net", 0) > 0 else "red"
            t.add_row(f.get("exchange", "?"), f"${f.get('inflow', 0):,.0f}", f"${f.get('outflow', 0):,.0f}", f"[{net_c}]${f.get('net', 0):+,.0f}[/{net_c}]")
        console.print(t); console.print()

    elif args.orderbook:
        console.print(f"\n📊 Order Book: [bold]{token}[/bold]\n")
        with console.status("Scanning..."):
            r = tracker.scan_orderbook(token)
        t = Table(title="Order Book Walls")
        t.add_column("Exchange", style="cyan"); t.add_column("Side", style="white"); t.add_column("Price", style="green"); t.add_column("Size", style="yellow"); t.add_column("Spoof", style="red")
        for w in r.get("walls", []):
            t.add_row(w.get("exchange"), w.get("side"), f"${w.get('price', 0):,.2f}", f"${w.get('size', 0):,.0f}", "⚠️" if w.get("spoof") else "✅")
        console.print(t); console.print()

    elif args.historical:
        console.print(f"\n📈 Historical Match: [bold]{token}[/bold]\n")
        with console.status("Matching patterns..."):
            r = tracker.match_historical(token)
        console.print(f"  Best Match: [bold]{r.get('best_match', 'N/A')}[/bold]")
        console.print(f"  Similarity: {r.get('similarity', 0)}%")
        console.print(f"  Outcome: {r.get('outcome', 'N/A')}")
        console.print(f"  Prediction: {r.get('prediction', 'N/A')}\n")

    elif args.alert:
        r = tracker.create_alert(token, args.min_usd or 500000, args.alert_direction or "ANY")
        console.print(f"\n🔔 Alert Created: {token} > ${args.min_usd or 500000:,.0f} ({args.alert_direction or 'ANY'})\n")

    else:
        console.print(f"\n🐋 Full Whale Analysis: [bold]{token}[/bold]\n")
        with console.status("Running all 10 features..."):
            signal = tracker.full_analysis(token, args.hours)
        console.print(tracker.format_alert(signal))


def cmd_analyze(args):
    client = MiMoClient()
    market = MarketIntelligence(client)
    console.print(f"\n🔍 Analyzing [bold]{args.asset}[/bold]...\n")
    with console.status("MiMo thinking..."):
        r = market.analyze(args.asset)
    t = Table(title=f"{args.asset.upper()} Analysis")
    t.add_column("Metric", style="cyan"); t.add_column("Value", style="green")
    c = {"BUY": "green", "SELL": "red", "HOLD": "yellow"}.get(r.get("signal"), "white")
    t.add_row("Signal", f"[{c}]{r.get('signal', '?')}[/{c}]")
    t.add_row("Confidence", f"{r.get('confidence', 0)}%")
    t.add_row("Risk", r.get("risk", "?"))
    console.print(t)
    console.print(f"\n📝 {r.get('reasoning', '')}\n")


def cmd_sentiment(args):
    client = MiMoClient()
    analyzer = SentimentAnalyzer(client)
    console.print(f"\n📰 Sentiment: [bold]{args.query}[/bold]\n")
    with console.status("Analyzing..."):
        r = analyzer.analyze(args.query)
    c = "green" if r.get("score", 0) > 0 else "red"
    console.print(f"  [{c}]{r.get('label', '?')}[/{c}] ({r.get('score', 0):+.2f})")
    console.print(f"  {r.get('narrative', '')}\n")


def cmd_demo(args):
    banner()
    client = MiMoClient()
    console.print("[bold]Running full demo...[/bold]\n")

    console.print("1️⃣ MiMo Connection Test")
    with console.status("Connecting..."):
        r = client.chat("Say 'MiMo-V2.5-Pro ready' in 5 words or less.", system="Be extremely brief.")
    console.print(f"   ✅ {r[:100]}\n")

    console.print("2️⃣ Market Analysis (BTC)")
    market = MarketIntelligence(client)
    with console.status("Analyzing..."):
        s = market.analyze("bitcoin")
    console.print(f"   📊 {s.get('signal', '?')} | {s.get('confidence', 0)}%\n")

    console.print("3️⃣ Whale Tracker (ETH, all 10 features)")
    tracker = WhaleTracker(client)
    with console.status("Running..."):
        w = tracker.full_analysis("ETH", 24)
    console.print(f"   🐋 {w.get('signal', '?')} | {w.get('whale_count', 0)} whales")
    console.print(f"   💰 Net: ${w.get('net_flow', 0):+,.0f}")
    console.print(f"   📊 Vol: ${w.get('volume', 0):,.0f} | OI: ${w.get('oi', 0):,.0f}\n")

    console.print("[bold green]✅ Demo complete![/bold green]\n")


def main():
    p = argparse.ArgumentParser(description="MiMo Agent Advanced — Narrative Trade Intelligence")
    sub = p.add_subparsers(dest="cmd")

    # Whale
    w = sub.add_parser("whale", help="Whale tracker (10 features)")
    w.add_argument("token", help="Token (ETH, BTC, SOL...)")
    w.add_argument("--hours", type=int, default=24)
    w.add_argument("--divergence", action="store_true")
    w.add_argument("--concentration", action="store_true")
    w.add_argument("--heatmap", action="store_true")
    w.add_argument("--vc-tracking", action="store_true")
    w.add_argument("--smart-money", action="store_true")
    w.add_argument("--exchange-flows", action="store_true")
    w.add_argument("--orderbook", action="store_true")
    w.add_argument("--historical", action="store_true")
    w.add_argument("--alert", action="store_true")
    w.add_argument("--min-usd", type=float)
    w.add_argument("--alert-direction", choices=["BUY", "SELL", "ANY"])
    w.set_defaults(func=cmd_whale)

    # Analyze
    a = sub.add_parser("analyze", help="Market analysis")
    a.add_argument("asset", help="Coin ID")
    a.set_defaults(func=cmd_analyze)

    # Sentiment
    s = sub.add_parser("sentiment", help="Sentiment analysis")
    s.add_argument("query", help="Asset or topic")
    s.set_defaults(func=cmd_sentiment)

    # Demo
    d = sub.add_parser("demo", help="Run demo")
    d.set_defaults(func=cmd_demo)

    args = p.parse_args()
    if not args.cmd:
        p.print_help(); return
    args.func(args)


if __name__ == "__main__":
    main()
