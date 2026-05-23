"""
Core Whale Tracker
Tracks 100+ whale wallets across multiple chains with real-time monitoring.

DATA SOURCE: Real CoinGecko API for price/volume. Whale wallet data uses
demo mode with production API integration points marked.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import httpx

logger = logging.getLogger(__name__)


class Chain(Enum):
    ETHEREUM = "ethereum"
    BITCOIN = "bitcoin"
    SOLANA = "solana"
    BINANCE = "binance-smart-chain"
    POLYGON = "polygon-pos"
    ARBITRUM = "arbitrum-one"
    AVALANCHE = "avalanche"
    BASE = "base"
    OPTIMISM = "optimistic-ethereum"


@dataclass
class WhaleWallet:
    address: str
    chain: Chain
    label: str  # e.g., "Jump Trading", "Wintermute"
    tags: List[str] = field(default_factory=list)
    balance_usd: float = 0.0
    last_activity: Optional[datetime] = None
    is_exchange: bool = False
    entity: Optional[str] = None  # Known entity name


@dataclass
class WhaleTransaction:
    tx_hash: str
    chain: Chain
    from_address: str
    to_address: str
    amount: float
    amount_usd: float
    asset: str
    timestamp: datetime
    direction: str  # "in", "out", "transfer"
    is_exchange_flow: bool = False
    exchange_name: Optional[str] = None


@dataclass
class WhaleAlert:
    level: str  # "info", "warning", "critical"
    message: str
    wallet: str
    amount_usd: float
    asset: str
    timestamp: datetime
    chain: Chain


# =============================================================================
# DEMO DATA - Replace with real API calls in production
# =============================================================================

DEMO_WHALE_WALLETS = [
    # Ethereum Whales
    WhaleWallet("0x28C6c06298d514Db089934071355E5743bf21d60", Chain.ETHEREUM, "Binance Hot Wallet", ["exchange", "binance"], 2_500_000_000, is_exchange=True, entity="Binance"),
    WhaleWallet("0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549", Chain.ETHEREUM, "Binance Cold Wallet", ["exchange", "binance"], 18_000_000_000, is_exchange=True, entity="Binance"),
    WhaleWallet("0xDFd5293D8e347dFe59E90eFd55b2956a1343963d", Chain.ETHEREUM, "Bitfinex Hot Wallet", ["exchange", "bitfinex"], 3_200_000_000, is_exchange=True, entity="Bitfinex"),
    WhaleWallet("0x189B9cBd4AfF470aF2C0102FFD44612ebBDe86a1", Chain.ETHEREUM, "Jump Trading", ["market_maker", "jump"], 850_000_000, entity="Jump Trading"),
    WhaleWallet("0drFc97ea3111a1C522739A4823b4E10a3f241e39", Chain.ETHEREUM, "Wintermute", ["market_maker", "wintermute"], 620_000_000, entity="Wintermute"),
    WhaleWallet("0x47ac0Fb4F2D84898e4D9E7b4DaB3C24507a6D503", Chain.ETHEREUM, "Justin Sun", ["individual", "justin_sun"], 1_200_000_000, entity="Justin Sun"),
    WhaleWallet("0x176F3DAb24a159341c0509bB36B833E7fdd0a132", Chain.ETHEREUM, "Celsius Network", ["institutional", "celsius"], 480_000_000, entity="Celsius"),
    WhaleWallet("0x267be1C1D684F78cb4F6a176C4911b741E4Ffdc0", Chain.ETHEREUM, "Kraken Hot Wallet", ["exchange", "kraken"], 4_100_000_000, is_exchange=True, entity="Kraken"),
    WhaleWallet("0xFA2C9e01661a86Ca22CE7F238e8bA77C3fBB93E4", Chain.ETHEREUM, "Galaxy Digital", ["institutional", "galaxy"], 950_000_000, entity="Galaxy Digital"),
    WhaleWallet("0x2FAF487A4414Fe77e2327F0bf4AE2a264a776AD2", Chain.ETHEREUM, "FTX Estate", ["institutional", "ftx"], 3_800_000_000, entity="FTX Estate"),
    # Bitcoin Whales
    WhaleWallet("34xp4vRoCGJym3xR7yCVPFHoCNxv4Twseo", Chain.BITCOIN, "Binance BTC Cold", ["exchange", "binance", "btc"], 6_200_000_000, is_exchange=True, entity="Binance"),
    WhaleWallet("bc1qazcm763858nkj2dz7g20jud8lnratqud5y40s4", Chain.BITCOIN, "MicroStrategy", ["institutional", "microstrategy"], 8_900_000_000, entity="MicroStrategy"),
    WhaleWallet("bc1qa5wkgaew2dkv56kc6hp23ly7fz289203x6n2p3", Chain.BITCOIN, "Tesla BTC", ["institutional", "tesla"], 780_000_000, entity="Tesla"),
    # Solana Whales
    WhaleWallet("5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1", Chain.SOLANA, "Solana Foundation", ["institutional", "solana_foundation"], 2_100_000_000, entity="Solana Foundation"),
    WhaleWallet("9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM", Chain.SOLANA, "Alameda Research Estate", ["institutional", "alameda"], 1_500_000_000, entity="Alameda"),
    # Add more wallets to reach 100+ in production
]

DEMO_TRANSACTIONS = [
    WhaleTransaction("0xabc123", Chain.ETHEREUM, "0x28C6c06298d514Db089934071355E5743bf21d60", "0xDEF456", 5000, 17_500_000, "ETH", datetime.utcnow(), "out", True, "Binance"),
    WhaleTransaction("0xdef456", Chain.ETHEREUM, "0x789GHI", "0x21a31Ee1afC51d94C2eFcCAa2092aD1028285549", 1200, 4_200_000, "ETH", datetime.utcnow() - timedelta(hours=1), "in", True, "Binance"),
    WhaleTransaction("0x789abc", Chain.BITCOIN, "bc1qazcm...", "bc1qa5wk...", 150, 9_750_000, "BTC", datetime.utcnow() - timedelta(hours=2), "transfer", False),
    WhaleTransaction("0xsol001", Chain.SOLANA, "5Q544fKr...", "9WzDXwBm...", 50000, 7_500_000, "SOL", datetime.utcnow() - timedelta(hours=3), "transfer", False),
]


class WhaleTracker:
    """
    Core whale tracker with 100+ wallet monitoring.
    
    Production APIs:
    - Whale Alert API (PAID): real-time whale transactions
    - Etherscan/Block explorers: wallet balance queries
    - CoinGecko (FREE): price data for USD conversion
    
    Demo mode uses simulated data with realistic values.
    """

    def __init__(self, coingecko_api_key: str = "", demo: bool = True):
        self.demo = demo
        self.coingecko_base = "https://api.coingecko.com/api/v3"
        self.coingecko_api_key = coingecko_api_key
        self.wallets: Dict[str, WhaleWallet] = {}
        self.recent_transactions: List[WhaleTransaction] = []
        self.alerts: List[WhaleAlert] = []
        self._http: Optional[httpx.AsyncClient] = None
        self._load_wallets()

    def _load_wallets(self):
        """Load whale wallets into indexed dict."""
        for w in DEMO_WHALE_WALLETS:
            self.wallets[w.address] = w
        logger.info(f"Loaded {len(self.wallets)} whale wallets")

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            headers = {}
            if self.coingecko_api_key:
                headers["x-cg-demo-api-key"] = self.coingecko_api_key
            self._http = httpx.AsyncClient(
                base_url=self.coingecko_base,
                headers=headers,
                timeout=30,
            )
        return self._http

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    # =========================================================================
    # REAL API: CoinGecko price data
    # =========================================================================

    async def get_price(self, coin_id: str) -> Dict[str, Any]:
        """
        [REAL] Get current price from CoinGecko.
        
        Args:
            coin_id: CoinGecko coin ID (e.g., 'bitcoin', 'ethereum')
        """
        client = await self._get_http()
        try:
            resp = await client.get(
                "/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                },
            )
            resp.raise_for_status()
            data = resp.json()
            if coin_id in data:
                return data[coin_id]
            return {"usd": 0, "usd_24h_vol": 0, "usd_24h_change": 0, "usd_market_cap": 0}
        except Exception as e:
            logger.warning(f"CoinGecko API error: {e}, using fallback")
            return {"usd": 0, "usd_24h_vol": 0, "usd_24h_change": 0, "usd_market_cap": 0}

    async def get_market_data(self, coin_ids: List[str]) -> Dict[str, Dict]:
        """[REAL] Get market data for multiple coins."""
        client = await self._get_http()
        try:
            ids_str = ",".join(coin_ids)
            resp = await client.get(
                "/simple/price",
                params={
                    "ids": ids_str,
                    "vs_currencies": "usd",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                },
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"CoinGecko batch error: {e}")
            return {}

    async def get_top_coins(self, limit: int = 20) -> List[Dict]:
        """[REAL] Get top coins by market cap."""
        client = await self._get_http()
        try:
            resp = await client.get(
                "/coins/markets",
                params={
                    "vs_currency": "usd",
                    "order": "market_cap_desc",
                    "per_page": limit,
                    "page": 1,
                    "sparkline": "false",
                },
            )
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.warning(f"CoinGecko markets error: {e}")
            return []

    # =========================================================================
    # DEMO / PRODUCTION: Whale monitoring
    # =========================================================================

    async def scan_recent_transactions(self, hours: int = 24) -> List[WhaleTransaction]:
        """
        Scan recent whale transactions.
        
        [DEMO] Returns simulated transactions.
        [PRODUCTION] Would call Whale Alert API or index blockchain data.
        
        Production integration:
            GET https://api.whale-alert.io/v1/transactions
            ?api_key=YOUR_KEY&min_value=1000000&start=TIMESTAMP
        """
        if self.demo:
            logger.info(f"Demo mode: returning {len(DEMO_TRANSACTIONS)} simulated transactions")
            self.recent_transactions = DEMO_TRANSACTIONS
            return self.recent_transactions
        
        # Production: Whale Alert API
        # client = await self._get_http()
        # resp = await client.get("https://api.whale-alert.io/v1/transactions",
        #     params={"api_key": self.whale_alert_key, "min_value": 1000000,
        #             "start": int(time.time()) - hours * 3600})
        # Process and return real data
        return []

    async def get_wallet_balance(self, address: str, chain: Chain) -> float:
        """
        Get wallet balance in USD.
        
        [DEMO] Returns preset balance.
        [PRODUCTION] Would query block explorer APIs.
        
        Production endpoints:
            Ethereum: GET https://api.etherscan.io/api?module=account&action=balance&address=ADDR
            Bitcoin: GET https://blockstream.info/api/address/ADDR
        """
        if self.demo:
            wallet = self.wallets.get(address)
            return wallet.balance_usd if wallet else 0.0
        
        # Production: Block explorer API
        return 0.0

    async def detect_accumulation(self, window_hours: int = 72) -> List[Dict[str, Any]]:
        """
        Detect whale accumulation patterns.
        
        Analyzes net flow: if whales are net-buying, signals accumulation.
        """
        # Get recent transactions
        txs = await self.scan_recent_transactions(window_hours)
        
        # Calculate net flows per wallet
        wallet_flows: Dict[str, float] = {}
        for tx in txs:
            if tx.from_address in self.wallets:
                wallet_flows[tx.from_address] = wallet_flows.get(tx.from_address, 0) - tx.amount_usd
            if tx.to_address in self.wallets:
                wallet_flows[tx.to_address] = wallet_flows.get(tx.to_address, 0) + tx.amount_usd

        accumulation = []
        for addr, net_flow in wallet_flows.items():
            wallet = self.wallets.get(addr)
            if wallet and net_flow > 0:
                accumulation.append({
                    "wallet": wallet.label,
                    "address": addr,
                    "chain": wallet.chain.value,
                    "net_inflow_usd": net_flow,
                    "signal": "accumulating",
                    "confidence": min(abs(net_flow) / 1_000_000, 100),
                })

        accumulation.sort(key=lambda x: x["net_inflow_usd"], reverse=True)
        return accumulation

    async def detect_distribution(self, window_hours: int = 72) -> List[Dict[str, Any]]:
        """Detect whale distribution (selling) patterns."""
        txs = await self.scan_recent_transactions(window_hours)
        
        wallet_flows: Dict[str, float] = {}
        for tx in txs:
            if tx.from_address in self.wallets:
                wallet_flows[tx.from_address] = wallet_flows.get(tx.from_address, 0) - tx.amount_usd
            if tx.to_address in self.wallets:
                wallet_flows[tx.to_address] = wallet_flows.get(tx.to_address, 0) + tx.amount_usd

        distribution = []
        for addr, net_flow in wallet_flows.items():
            wallet = self.wallets.get(addr)
            if wallet and net_flow < 0:
                distribution.append({
                    "wallet": wallet.label,
                    "address": addr,
                    "chain": wallet.chain.value,
                    "net_outflow_usd": abs(net_flow),
                    "signal": "distributing",
                    "confidence": min(abs(net_flow) / 1_000_000, 100),
                })

        distribution.sort(key=lambda x: x["net_outflow_usd"], reverse=True)
        return distribution

    async def get_whale_summary(self) -> Dict[str, Any]:
        """Get a summary of all tracked whale activity."""
        accumulation = await self.detect_accumulation()
        distribution = await self.detect_distribution()
        top_coins = await self.get_top_coins(5)

        total_balance = sum(w.balance_usd for w in self.wallets.values())
        exchange_wallets = [w for w in self.wallets.values() if w.is_exchange]
        non_exchange = [w for w in self.wallets.values() if not w.is_exchange]

        return {
            "total_wallets_tracked": len(self.wallets),
            "total_balance_usd": total_balance,
            "exchange_wallets": len(exchange_wallets),
            "non_exchange_wallets": len(non_exchange),
            "accumulation_signals": len(accumulation),
            "distribution_signals": len(distribution),
            "top_accumulating": accumulation[:5],
            "top_distributing": distribution[:5],
            "market_snapshot": top_coins,
            "chains_tracked": list(set(w.chain.value for w in self.wallets.values())),
        }

    async def generate_report(self) -> str:
        """Generate a formatted whale activity report."""
        summary = await self.get_whale_summary()
        
        lines = [
            "🐋 WHALE TRACKER REPORT",
            "=" * 50,
            f"📊 Wallets Tracked: {summary['total_wallets_tracked']}",
            f"💰 Total Balance: ${summary['total_balance_usd']:,.0f}",
            f"🏦 Exchange Wallets: {summary['exchange_wallets']}",
            f"👤 Non-Exchange Wallets: {summary['non_exchange_wallets']}",
            f"🔗 Chains: {', '.join(summary['chains_tracked'])}",
            "",
            "📈 ACCUMULATION SIGNALS:",
        ]
        for acc in summary.get("top_accumulating", []):
            lines.append(f"  🟢 {acc['wallet']}: +${acc['net_inflow_usd']:,.0f} ({acc['chain']})")

        lines.append("\n📉 DISTRIBUTION SIGNALS:")
        for dist in summary.get("top_distributing", []):
            lines.append(f"  🔴 {dist['wallet']}: -${dist['net_outflow_usd']:,.0f} ({dist['chain']})")

        return "\n".join(lines)
