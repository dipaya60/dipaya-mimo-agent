# 🤖 MiMo Crypto Intelligence Agent — Advanced

> Enterprise-grade crypto analysis platform powered by **Xiaomi MiMo-V2.5-Pro**
>
> Built for the [Xiaomi MiMo Orbit 100T Token Creator Incentive Program](https://100t.xiaomimimo.com/)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![MiMo](https://img.shields.io/badge/Powered%20by-MiMo--V2.5--Pro-orange.svg)](https://mimo.xiaomi.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](Dockerfile)

---

## 🎯 Overview

A modular, production-ready crypto intelligence platform with **10 whale tracking features**, market analysis, sentiment tracking, smart contract auditing, and airdrop detection — all powered by MiMo-V2.5-Pro's advanced reasoning.

## 🐋 Whale Tracker — 10 Advanced Features

| # | Feature | Description | Data Source |
|---|---------|-------------|-------------|
| 1 | 🧠 **Smart Money Score** | Wallet profiling 0-100 (win rate, ROI, timing) | Demo → Etherscan |
| 2 | 🏦 **Exchange Flows** | CEX inflow/outflow analysis | Demo → Whale Alert |
| 3 | 🐋👥 **Divergence** | Whale vs Retail behavior mismatch | Demo → On-chain |
| 4 | 📊 **Order Book Walls** | Large limit orders + spoofing detection | Demo → Binance API |
| 5 | 🔗 **Cross-chain** | Track wallet across 7 chains | Demo → Multi-explorer |
| 6 | 🏢 **VC Tracking** | a16z, Paradigm, Coinbase Ventures | Demo → Nansen |
| 7 | 📈 **Historical Match** | Compare to pre-pump/dump patterns | Demo → CoinGecko |
| 8 | 🔔 **Alerts** | Custom threshold notifications | ✅ Working |
| 9 | 📏 **Gini Index** | Holder concentration + manipulation risk | Demo → Etherscan |
| 10 | 🌡️ **Heatmap** | Activity patterns by hour/day | Demo → On-chain |

**Plus:** Volume ✅ (CoinGecko real), Price ✅ (CoinGecko real), OI, Funding Rate, Liquidation Levels

## 📦 Architecture

```
mimo-agent-advanced/
├── src/
│   ├── client.py              # MiMo API client (async, retry, OpenAI-compatible)
│   ├── config.py              # Configuration management
│   ├── whale/                 # 10 whale tracking modules
│   │   ├── tracker.py         # Core whale tracker (100+ wallets)
│   │   ├── profiler.py        # Smart Money Score
│   │   ├── exchange_flow.py   # Exchange flow analysis
│   │   ├── divergence.py      # Whale vs Retail divergence
│   │   ├── orderbook.py       # Order book wall detection
│   │   ├── cross_chain.py     # Cross-chain tracking
│   │   ├── vc_tracker.py      # VC wallet tracking
│   │   ├── historical.py      # Historical pattern matching
│   │   ├── alerts.py          # Alert threshold system
│   │   ├── concentration.py   # Gini concentration index
│   │   └── heatmap.py         # Activity heatmap
│   ├── market/                # Market analysis modules
│   │   ├── intelligence.py    # AI trading signals
│   │   ├── sentiment.py       # Sentiment analysis
│   │   ├── onchain.py         # On-chain metrics
│   │   └── derivatives.py     # OI, Funding, Liquidations
│   ├── security/
│   │   └── auditor.py         # Smart contract auditor
│   ├── airdrop/
│   │   └── detector.py        # Airdrop detector (9 EVM + Solana)
│   └── utils/
│       ├── logger.py          # Structured logging
│       └── formatters.py      # Output formatters
├── main.py                    # CLI (Rich terminal output)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 🚀 Quick Start

```bash
git clone https://github.com/dipaya60/mimo-crypto-agent.git
cd mimo-crypto-agent
pip install -r requirements.txt
cp .env.example .env
# Add your MiMo API key to .env

# Full whale analysis (all 10 features)
python main.py whale ETH

# Individual features
python main.py whale ETH --divergence
python main.py whale ETH --smart-money
python main.py whale ETH --exchange-flows
python main.py whale ETH --concentration
python main.py whale ETH --heatmap
python main.py whale ETH --vc-tracking
python main.py whale ETH --orderbook
python main.py whale ETH --historical
python main.py whale ETH --alert --min-usd 500000

# Market analysis
python main.py analyze bitcoin

# Sentiment
python main.py sentiment "BTC ETH SOL"

# Contract audit
python main.py audit contract.sol

# Demo (all modules)
python main.py demo
```

## 🐳 Docker

```bash
docker-compose up -d
docker-compose run mimo-agent whale ETH
```

## 🔧 API Integration

```python
from src.client import MiMoClient
from src.whale.tracker import WhaleTracker

client = MiMoClient()
tracker = WhaleTracker(client)

# Full analysis with all 10 features
signal = tracker.full_analysis("ETH", hours=24)
print(tracker.format_alert(signal))
```

## 📊 Data Sources

| Data | Status | Source |
|------|--------|--------|
| Volume 24h | ✅ REAL | CoinGecko (free) |
| Price | ✅ REAL | CoinGecko (free) |
| Market Cap | ✅ REAL | CoinGecko (free) |
| OI / Funding | ⚠️ Demo | Coinglass API (paid) |
| Whale Txs | ⚠️ Demo | Etherscan API (free) |
| Order Book | ⚠️ Demo | Binance API (free) |
| Holder Data | ⚠️ Demo | Etherscan (free) |

## 🎯 Use Cases

- **DeFi Traders** — Whale signals + divergence + OI/Funding
- **Airdrop Farmers** — Multi-chain opportunity detection
- **Security Auditors** — Smart contract vulnerability scanning
- **Researchers** — Sentiment + concentration analysis
- **Portfolio Managers** — Smart Money tracking + VC activity

## 🛣️ Roadmap

- [x] 10 whale tracking modules
- [x] Real CoinGecko integration
- [x] MiMo-V2.5-Pro reasoning engine
- [x] Modular architecture
- [x] Docker support
- [ ] Real-time on-chain APIs
- [ ] Telegram bot alerts
- [ ] Web dashboard
- [ ] Backtesting framework

## 📄 License

MIT — see [LICENSE](LICENSE)

---

<div align="center">

**Built with ❤️ using Xiaomi MiMo-V2.5-Pro**

[🌐 MiMo](https://mimo.xiaomi.com) • [📚 API Docs](https://platform.xiaomimimo.com/#/docs/welcome) • [🎮 Studio](https://aistudio.xiaomimimo.com)

</div>
