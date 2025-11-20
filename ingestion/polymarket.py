"""
Polymarket API Connector
Author: Abhi

Connector for ingesting market data from Polymarket prediction markets.
Includes mock fallback when API credentials are not available.
"""

import os
import json
import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

import httpx
from models.schemas import MarketMeta, Outcome, PricePoint, TimeSeries, OrderBook, EventRecord

logger = logging.getLogger(__name__)


class PolymarketConnector:
    """Polymarket API connector with mock fallback."""
    
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self.api_key = os.getenv("POLYMARKET_API_KEY")
        self.mock_mode = not self.api_key
        
        if self.mock_mode:
            logger.info("Polymarket connector running in mock mode (no API credentials)")
        else:
            logger.info("Polymarket connector initialized with API credentials")
    
    async def async_retry(self, func, max_retries=3, base_delay=1.0):
        """Simple async retry with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                await asyncio.sleep(delay)
    
    def _load_sample_data(self) -> Dict:
        """Load sample data for mock mode."""
        try:
            with open("data/sample_timeseries.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback sample data if file doesn't exist
            return {
                "markets": [
                    {
                        "id": "POLY-CRYPTO2024",
                        "title": "Will Bitcoin reach $100,000 by end of 2024?",
                        "description": "Market resolves to Yes if Bitcoin reaches $100k",
                        "provider": "polymarket",
                        "status": "active",
                        "category": "crypto",
                        "created_at": "2024-01-01T00:00:00Z",
                        "close_date": "2024-12-31T23:59:59Z",
                        "outcomes": [
                            {"id": "yes", "name": "Yes", "price": 0.42, "volume": 28750.80},
                            {"id": "no", "name": "No", "price": 0.58, "volume": 19240.60}
                        ],
                        "total_volume": 47991.40
                    }
                ]
            }
    
    def normalize_market(self, raw_market: Dict) -> Dict:
        """
        Normalize raw Polymarket data to our schema.
        
        Args:
            raw_market: Raw market data from Polymarket API
            
        Returns:
            Normalized market data matching MarketMeta schema
        """
        # In real implementation, map Polymarket's field names to our schema
        # Polymarket uses different field names than our standardized schema
        return {
            "id": raw_market.get("id", ""),
            "title": raw_market.get("title", raw_market.get("question", "")),
            "description": raw_market.get("description", ""),
            "provider": "polymarket",
            "status": raw_market.get("status", "active"),
            "category": raw_market.get("category", raw_market.get("tags", [""])[0] if raw_market.get("tags") else ""),
            "created_at": raw_market.get("created_at", datetime.utcnow().isoformat()),
            "close_date": raw_market.get("close_date", raw_market.get("end_date")),
            "settle_date": raw_market.get("settle_date"),
            "outcomes": raw_market.get("outcomes", []),
            "total_volume": raw_market.get("total_volume", raw_market.get("volume", 0)),
            "liquidity": raw_market.get("liquidity", 0)
        }
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make request to Polymarket API."""
        if self.mock_mode:
            return self._load_sample_data()
        
        async def _request():
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Content-Type": "application/json"}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.get(
                    f"{self.base_url}/{endpoint}",
                    headers=headers,
                    params=params or {}
                )
                response.raise_for_status()
                return response.json()
        
        return await self.async_retry(_request)
    
    async def get_markets(self) -> List[Dict]:
        """Fetch all available markets from Polymarket."""
        try:
            if self.mock_mode:
                sample_data = self._load_sample_data()
                return [self.normalize_market(m) for m in sample_data.get("markets", [])]
            
            # Real API call would be something like:
            # data = await self._make_request("markets")
            # return [self.normalize_market(m) for m in data]
            
            # For now, return sample data
            sample_data = self._load_sample_data()
            return [self.normalize_market(m) for m in sample_data.get("markets", [])]
            
        except Exception as e:
            logger.error(f"Error fetching Polymarket markets: {e}")
            return []
    
    async def get_market(self, market_id: str) -> Optional[Dict]:
        """Fetch specific market by ID."""
        try:
            markets = await self.get_markets()
            for market in markets:
                if market["id"] == market_id:
                    return market
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Polymarket market {market_id}: {e}")
            return None
    
    async def get_market_price(self, market_id: str) -> Optional[Dict]:
        """Get current price for a market."""
        try:
            market = await self.get_market(market_id)
            if not market:
                return None
            
            # Return current prices from outcomes
            return {
                "market_id": market_id,
                "timestamp": datetime.utcnow().isoformat(),
                "outcomes": market.get("outcomes", [])
            }
            
        except Exception as e:
            logger.error(f"Error fetching Polymarket market price {market_id}: {e}")
            return None
    
    async def get_market_timeseries(self, market_id: str, start: str = None, 
                                  end: str = None, interval: str = "1h") -> Optional[Dict]:
        """Get historical timeseries data for a market."""
        try:
            # In mock mode, generate sample timeseries
            if self.mock_mode:
                now = datetime.utcnow()
                data_points = []
                
                for i in range(24):  # 24 hours of data
                    timestamp = now - timedelta(hours=23-i)
                    price = 0.42 + (i * 0.002)  # Slight upward trend
                    data_points.append({
                        "timestamp": timestamp.isoformat(),
                        "price": price,
                        "volume": 150 + (i * 15)
                    })
                
                return {
                    "market_id": market_id,
                    "outcome_id": "yes",
                    "interval": interval,
                    "data_points": data_points
                }
            
            # Real implementation would call Polymarket timeseries API
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Polymarket timeseries {market_id}: {e}")
            return None
    
    async def get_market_orderbook(self, market_id: str, depth: int = 10) -> Optional[Dict]:
        """Get current orderbook for a market."""
        try:
            if self.mock_mode:
                return {
                    "market_id": market_id,
                    "outcome_id": "yes",
                    "timestamp": datetime.utcnow().isoformat(),
                    "bids": [
                        {"price": 0.41, "size": 200.0},
                        {"price": 0.40, "size": 350.0}
                    ],
                    "asks": [
                        {"price": 0.43, "size": 180.0},
                        {"price": 0.44, "size": 220.0}
                    ],
                    "spread": 0.02
                }
            
            # Real implementation would call Polymarket orderbook API
            return None
            
        except Exception as e:
            logger.error(f"Error fetching Polymarket orderbook {market_id}: {e}")
            return None
    
    async def get_market_events(self, market_id: str, since: str = None, 
                              limit: int = 100) -> Optional[List[Dict]]:
        """Get recent events for a market."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": "evt_poly_456",
                        "market_id": market_id,
                        "event_type": "trade",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "outcome_id": "yes",
                            "price": 0.42,
                            "volume": 75.0,
                            "side": "sell"
                        }
                    }
                ]
            
            # Real implementation would call Polymarket events API
            return []
            
        except Exception as e:
            logger.error(f"Error fetching Polymarket events {market_id}: {e}")
            return []
    
    async def sync_data(self) -> Dict:
        """Sync all market data from Polymarket."""
        try:
            markets = await self.get_markets()
            return {
                "provider": "polymarket",
                "markets_synced": len(markets),
                "status": "success",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error syncing Polymarket data: {e}")
            return {
                "provider": "polymarket",
                "markets_synced": 0,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }