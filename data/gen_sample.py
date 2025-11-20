#!/usr/bin/env python3
"""
Sample Data Generator for Omniverse Market API
Author: Abhi

Generates deterministic sample market data for testing and demo purposes.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_sample_markets() -> List[Dict]:
    """Generate sample market data."""
    markets = [
        {
            "id": "KALSHI-PRES2024",
            "title": "Will Joe Biden win the 2024 US Presidential Election?",
            "description": "Market resolves to Yes if Joe Biden wins the 2024 presidential election",
            "provider": "kalshi",
            "status": "active",
            "category": "politics",
            "created_at": "2024-01-01T00:00:00Z",
            "close_date": "2024-11-05T23:59:59Z",
            "settle_date": "2024-11-06T12:00:00Z",
            "outcomes": [
                {"id": "yes", "name": "Yes", "price": 0.65, "volume": 15420.50},
                {"id": "no", "name": "No", "price": 0.35, "volume": 8930.25}
            ],
            "total_volume": 24350.75,
            "liquidity": 5420.30
        },
        {
            "id": "POLY-CRYPTO2024",
            "title": "Will Bitcoin reach $100,000 by end of 2024?",
            "description": "Market resolves to Yes if Bitcoin reaches $100,000 USD by December 31, 2024",
            "provider": "polymarket",
            "status": "active",
            "category": "crypto",
            "created_at": "2024-01-01T00:00:00Z",
            "close_date": "2024-12-31T23:59:59Z",
            "settle_date": "2025-01-01T12:00:00Z",
            "outcomes": [
                {"id": "yes", "name": "Yes", "price": 0.42, "volume": 28750.80},
                {"id": "no", "name": "No", "price": 0.58, "volume": 19240.60}
            ],
            "total_volume": 47991.40,
            "liquidity": 8750.20
        },
        {
            "id": "KALSHI-TECH2024",
            "title": "Will Apple stock reach $250 by end of 2024?",
            "description": "Market resolves to Yes if AAPL closes above $250 on any trading day in 2024",
            "provider": "kalshi",
            "status": "active",
            "category": "stocks",
            "created_at": "2024-01-15T00:00:00Z",
            "close_date": "2024-12-31T21:00:00Z",
            "settle_date": "2025-01-02T09:00:00Z",
            "outcomes": [
                {"id": "yes", "name": "Yes", "price": 0.73, "volume": 12890.30},
                {"id": "no", "name": "No", "price": 0.27, "volume": 4560.70}
            ],
            "total_volume": 17451.00,
            "liquidity": 3240.80
        }
    ]
    return markets


def generate_timeseries_data(market_id: str, days: int = 30) -> List[Dict]:
    """Generate sample timeseries data for a market."""
    data_points = []
    base_price = 0.50
    
    # Set different base prices for different markets
    if "PRES2024" in market_id:
        base_price = 0.65
    elif "CRYPTO2024" in market_id:
        base_price = 0.42
    elif "TECH2024" in market_id:
        base_price = 0.73
    
    current_time = datetime.utcnow() - timedelta(days=days)
    
    for i in range(days * 24):  # Hourly data
        # Add some random walk with slight trend
        price_change = random.uniform(-0.02, 0.02)
        base_price = max(0.01, min(0.99, base_price + price_change))
        
        volume = random.uniform(50, 500)
        
        data_points.append({
            "timestamp": current_time.isoformat() + "Z",
            "price": round(base_price, 4),
            "volume": round(volume, 2),
            "outcome_id": "yes"
        })
        
        current_time += timedelta(hours=1)
    
    return data_points


def generate_sample_data() -> Dict:
    """Generate complete sample dataset."""
    markets = generate_sample_markets()
    
    # Generate timeseries for each market
    timeseries = {}
    for market in markets:
        timeseries[market["id"]] = generate_timeseries_data(market["id"])
    
    return {
        "markets": markets,
        "timeseries": timeseries,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }


def main():
    """Generate and save sample data."""
    print("Generating sample market data...")
    
    # Set seed for reproducible data
    random.seed(42)
    
    sample_data = generate_sample_data()
    
    # Save to file
    with open("data/sample_timeseries.json", "w") as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Generated sample data with {len(sample_data['markets'])} markets")
    print("Saved to data/sample_timeseries.json")


if __name__ == "__main__":
    main()