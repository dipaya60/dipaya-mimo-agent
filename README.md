# MiMo Agent Advanced — Narrative Trade Intelligence

> **v2.0** — Modular autonomous crypto analysis engine  
> Powered by **Xiaomi MiMo-V2.5-Pro** · 9 EVM Chains + Solana

Built for the [100T Token Creator Incentive Program](https://100t.xiaomimimo.com/)

---

## The Problem

Most crypto traders lose money because they lack institutional-grade intelligence. Whale movements, exchange flows, and concentration data are locked behind expensive platforms like Nansen ($150/mo) or Glassnode ($299/mo). Retail traders are flying blind while smart money moves silently.

## The Solution

MiMo Agent Advanced is a **free, open-source** narrative trade intelligence platform that uses MiMo-V2.5-Pro's reasoning engine to decode whale behavior across 9 EVM chains and Solana. It combines 10 whale tracking modules with AI-powered market analysis — all running locally on your machine.

No subscriptions. No API lock-in. Just MiMo reasoning + open data sources.

---

## 🐋 Whale Intelligence Suite

10 modules that decode whale behavior, not just track it:

```
┌─────────────────────────────────────────────────────────────────┐
│                    WHALE TRACKER PIPELINE                       │
├─────────────────┬───────────────────────────────────────────────┤
│  DATA LAYER     │  CoinGecko (live) · Etherscan · BSCScan      │
│                 │  Whale Alert · Nansen · Binance API           │
├─────────────────┼───────────────────────────────────────────────┤
│  REASONING      │  MiMo-V2.5-Pro Deep Reasoning Engine          │
├─────────────────┼───────────────────────────────────────────────┤
│  OUTPUT         │  Smart Money Score · Signal · Risk Level      │
└─────────────────┴───────────────────────────────────────────────┘
```

| Module | What It Does | Why It Matters |
|--------|-------------|----------------|
| 🧠 Smart Money Score | Scores each wallet 0-100 (win rate, ROI, timing) | Follow winners, not losers |
| 💱 Exchange Flow | Tracks CEX inflow/outflow | Whale deposits = sell pressure |
| ⚡ Divergence | Whale vs Retail buy/sell mismatch | Strongest signal in crypto |
| 🧱 Order Book Walls | Detects large limit orders + spoofing | See hidden support/resistance |
| 🔗 Cross-chain | Same wallet across ETH/SOL/BSC/ARB/BASE/OP | When whales bridge, moves coming |
| 🏢 VC Tracking | a16z, Paradigm, Coinbase Ventures, Jump | Smart smart money |
| 📈 Historical Match | Compares current patterns to pre-pump/dump | "80% similar to March 2024 ATH" |
| 🔔 Alert System | Custom: "notify if whale buys >$500k" | Never miss a whale move |
| 📊 Gini Index | Holder concentration coefficient | High Gini = manipulation risk |
| 🔥 Heatmap | Whale activity by hour/day | Optimal entry/exit timing |

---

## 📊 Market Intelligence Layer

Beyond whale tracking, the platform includes 2 AI-powered narrative engines:

**🎯 Trading Signals** — MiMo generates buy/sell signals with full reasoning chains explaining *why*, not just *what*. Includes confidence scores and position sizing recommendations.

**💭 Sentiment Analysis** — Aggregates social media (Twitter, Reddit, Telegram) and news sources. Outputs sentiment score (-1 to +1) with trend direction and influence weighting.

---

## 🏗️ Architecture

```
mimo-agent-advanced/
├── src/
│   ├── client.py              # MiMo API (async, retry, OpenAI-compatible)
│   ├── config.py              # Env-based configuration
│   │
│   ├── whale/                 # 10 whale intelligence modules
│   │   ├── tracker.py         # Core engine + 100+ wallet database
│   │   ├── profiler.py        # Smart Money Score (0-100)
│   │   ├── exchange_flow.py   # CEX inflow/outflow
│   │   ├── divergence.py      # Whale vs Retail signals
│   │   ├── orderbook.py       # Wall detection + spoofing
│   │   ├── cross_chain.py     # Multi-chain wallet tracking
│   │   ├── vc_tracker.py      # VC wallet monitoring
│   │   ├── historical.py      # Pattern matching engine
│   │   ├── alerts.py          # Threshold notification system
│   │   ├── concentration.py   # Gini coefficient calculator
│   │   └── heatmap.py         # Temporal activity visualization
│   │
│   ├── market/                # Market analysis engines
│   │   ├── intelligence.py    # AI trading signals
│   │   ├── sentiment.py       # Social + news sentiment
│   │   ├── onchain.py         # On-chain metrics
│   │   └── derivatives.py     # OI, Funding, Liquidations
│   │
│   └── utils/
│       ├── logger.py          # Structured logging
│       └── formatters.py      # Rich terminal formatters
│
├── main.py                    # CLI entry (Rich-powered)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## ⚡ Quick Start

```bash
# Clone & install
git clone https://github.com/dipaya60/dipaya-mimo-agent.git
cd dipaya-mimo-agent
pip install -r requirements.txt
cp .env.example .env   # add your MiMo API key

# Full whale analysis (all 10 modules)
python main.py whale ETH

# Specific modules
python main.py whale ETH --smart-money        # Wallet scoring
python main.py whale ETH --divergence         # Whale vs Retail
python main.py whale ETH --exchange-flows     # CEX flow
python main.py whale ETH --concentration      # Gini index
python main.py whale ETH --heatmap            # Activity heatmap
python main.py whale ETH --vc-tracking        # VC wallets
python main.py whale ETH --orderbook          # Wall detection
python main.py whale ETH --historical         # Pattern matching
python main.py whale ETH --alert --min-usd 500000  # Alerts

# Market analysis
python main.py analyze bitcoin

# Sentiment
python main.py sentiment "BTC ETH SOL"

# Full demo
python main.py demo
```

### Docker

```bash
docker-compose up -d
docker-compose run mimo-agent whale ETH
```

---

## 🔌 API Integration

```python
from src.client import MiMoClient
from src.whale.tracker import WhaleTracker

client = MiMoClient()
tracker = WhaleTracker(client)

# Full analysis — all 10 modules
result = tracker.full_analysis("ETH", hours=24)

print(f"Signal: {result.signal}")
print(f"Smart Money: {result.smart_money_scores[0].score}")
print(f"Exchange Flow: ${result.exchange_flows.net_flow_usd:,.0f}")
print(f"Divergence: {result.divergence.direction}")
print(f"Gini: {result.concentration.gini:.3f}")
print(f"Risk: {result.risk_level}")
```

---

## 📡 Data Sources

| Layer | Status | Source | Notes |
|-------|--------|--------|-------|
| Price & Volume | ✅ **Live** | CoinGecko | Free tier, no key needed |
| Market Cap | ✅ **Live** | CoinGecko | Real-time |
| Whale Transactions | ⚠️ Demo | Etherscan | Architecture ready for API key |
| Exchange Flow | ⚠️ Demo | Whale Alert | Pipeline built, needs API |
| Order Book | ⚠️ Demo | Binance | WebSocket architecture ready |
| Holder Distribution | ⚠️ Demo | Etherscan | Gini calculation implemented |
| Social Sentiment | ⚠️ Demo | Twitter/Reddit | MiMo reasoning pipeline |
| OI / Funding / Liq | ⚠️ Demo | Coinglass | Paid API integration ready |

All demo modules use realistic data generators with production-ready API integration architecture. Just add API keys to go live.

---

## 🧠 Why MiMo-V2.5-Pro?

This project is designed specifically to exploit MiMo's strengths:

1. **Deep Reasoning** — Correlating 10 whale modules + market data simultaneously
2. **Structured Output** — Reliable JSON for programmatic trading decisions
3. **Long Context** — 100+ whale transactions + derivatives in single analysis
4. **Cost Efficiency** — 100T program makes heavy daily usage accessible

Other models give you a whale tracker. MiMo gives you a **whale intelligence analyst**.

---

## 🛣️ Roadmap

- [x] 10 whale intelligence modules
- [x] CoinGecko real-time integration
- [x] MiMo-V2.5-Pro reasoning engine
- [x] Modular architecture (extensible)
- [x] Docker deployment
- [ ] Real-time on-chain API integration
- [ ] Telegram/Discord bot alerts
- [ ] Web dashboard (React)
- [ ] Historical backtesting framework
- [ ] Multi-agent orchestration (Hermes + MiMo)

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Powered by Xiaomi MiMo-V2.5-Pro**

[🌐 MiMo](https://mimo.xiaomi.com) · [📚 API Docs](https://platform.xiaomimimo.com/#/docs/welcome) · [🎮 Studio](https://aistudio.xiaomimimo.com)

*100T Token Creator Incentive Program*

</div>
