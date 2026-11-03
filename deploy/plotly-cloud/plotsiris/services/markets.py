"""Financial markets intelligence: Defense contractors, energy, commodities, and risk indices."""

import random
from typing import List, Dict, Any
from plotsiris.domain.models import MarketTicker

BASELINE_TICKERS = [
    # Defense & Aerospace
    {"symbol": "LMT", "name": "Lockheed Martin", "category": "DEFENSE", "price": 584.20, "change": +6.45, "change_pct": +1.12},
    {"symbol": "RTX", "name": "RTX Corporation", "category": "DEFENSE", "price": 124.80, "change": +1.85, "change_pct": +1.50},
    {"symbol": "NOC", "name": "Northrop Grumman", "category": "DEFENSE", "price": 512.40, "change": +4.10, "change_pct": +0.81},
    {"symbol": "GD", "name": "General Dynamics", "category": "DEFENSE", "price": 302.15, "change": +2.70, "change_pct": +0.90},
    {"symbol": "PLTR", "name": "Palantir Technologies", "category": "DEFENSE", "price": 44.18, "change": +1.82, "change_pct": +4.30},
    {"symbol": "BA", "name": "Boeing Defense", "category": "DEFENSE", "price": 154.25, "change": -2.10, "change_pct": -1.34},
    # Energy & Commodities
    {"symbol": "BRENT", "name": "Brent Crude Oil", "category": "ENERGY", "price": 78.45, "change": +1.15, "change_pct": +1.49},
    {"symbol": "WTI", "name": "WTI Light Crude", "category": "ENERGY", "price": 74.20, "change": +1.08, "change_pct": +1.48},
    {"symbol": "GOLD", "name": "Gold Spot ($/oz)", "category": "COMMODITY", "price": 2748.50, "change": +18.20, "change_pct": +0.67},
    {"symbol": "SILVER", "name": "Silver Spot ($/oz)", "category": "COMMODITY", "price": 33.85, "change": +0.45, "change_pct": +1.35},
    {"symbol": "NATGAS", "name": "Henry Hub Gas", "category": "ENERGY", "price": 2.84, "change": -0.04, "change_pct": -1.39},
    # Crypto & Digital Assets
    {"symbol": "BTC", "name": "Bitcoin (USD)", "category": "CRYPTO", "price": 71450.0, "change": +1850.0, "change_pct": +2.66},
    {"symbol": "ETH", "name": "Ethereum (USD)", "category": "CRYPTO", "price": 2640.0, "change": +85.0, "change_pct": +3.33},
]

COUNTRY_RISK_RATINGS = [
    {"country": "Ukraine", "risk_index": 94, "rating": "EXTREME", "status": "Martial Law / Armed Conflict", "color": "#ef4444"},
    {"country": "Sudan", "risk_index": 92, "rating": "EXTREME", "status": "Civil War / Port Disruption", "color": "#ef4444"},
    {"country": "Israel/Lebanon", "risk_index": 86, "rating": "HIGH", "status": "Border Hostilities / Missile Risk", "color": "#f97316"},
    {"country": "Taiwan Strait", "risk_index": 72, "rating": "ELEVATED", "status": "Naval Drills / ADIZ Incursions", "color": "#eab308"},
    {"country": "Red Sea Shipping", "risk_index": 88, "rating": "CRITICAL", "status": "Commercial Transit Diversions (Cape route)", "color": "#ef4444"},
    {"country": "Baltic Corridor", "risk_index": 65, "rating": "ELEVATED", "status": "GPS Denial / Underwater Cable Vulnerability", "color": "#eab308"},
]


class MarketsService:
    """Manages strategic financial commodities, defense tickers, and sovereign risk scores."""

    def __init__(self):
        self._tickers = BASELINE_TICKERS

    def fetch_tickers(self) -> List[MarketTicker]:
        """Return updated market tickers with realistic price micro-fluctuations."""
        results = []
        for t in self._tickers:
            # gentle simulation
            pct_delta = random.uniform(-0.05, 0.05)
            new_price = round(t["price"] * (1 + pct_delta / 100), 2)
            results.append(MarketTicker(
                symbol=t["symbol"],
                name=t["name"],
                category=t["category"],
                price=new_price,
                change=t["change"],
                change_pct=t["change_pct"],
                unit="$"
            ))
        return results

    def fetch_country_risk(self) -> List[Dict[str, Any]]:
        """Return sovereign geopolitical risk assessments."""
        return list(COUNTRY_RISK_RATINGS)
