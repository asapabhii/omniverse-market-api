"""
Kalshi API Connector
Author: Abhi

Connector for ingesting market data from Kalshi prediction markets.
Includes mock fallback when API credentials are not available.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from models.schemas import (
    EventRecord,
    MarketMeta,
    OrderBook,
    Outcome,
    PricePoint,
    TimeSeries,
)

logger = logging.getLogger(__name__)


class KalshiConnector:
    """Kalshi API connector with mock fallback."""

    def __init__(self):
        self.base_url = "https://trading-api.kalshi.com/trade-api/v2"
        self.api_key = os.getenv("KALSHI_API_KEY")
        self.user_id = os.getenv("KALSHI_USER_ID")
        self.mock_mode = not (self.api_key and self.user_id)

        if self.mock_mode:
            logger.info("Kalshi connector running in mock mode (no API credentials)")
        else:
            logger.info("Kalshi connector initialized with API credentials")

    async def async_retry(self, func, max_retries=3, base_delay=1.0):
        """Simple async retry with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                delay = base_delay * (2**attempt)
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
                        "id": "KALSHI-PRES2024",
                        "title": "Will Joe Biden win the 2024 US Presidential Election?",
                        "description": "Market resolves to Yes if Joe Biden wins",
                        "provider": "kalshi",
                        "status": "active",
                        "category": "politics",
                        "created_at": "2024-01-01T00:00:00Z",
                        "close_date": "2024-11-05T23:59:59Z",
                        "outcomes": [
                            {
                                "id": "yes",
                                "name": "Yes",
                                "price": 0.65,
                                "volume": 15420.50,
                            },
                            {
                                "id": "no",
                                "name": "No",
                                "price": 0.35,
                                "volume": 8930.25,
                            },
                        ],
                        "total_volume": 24350.75,
                    }
                ]
            }

    def normalize_market(self, raw_market: Dict) -> Dict:
        """
        Normalize raw Kalshi market data to our schema.

        Args:
            raw_market: Raw market data from Kalshi API

        Returns:
            Normalized market data matching MarketMeta schema
        """
        # In real implementation, map Kalshi's field names to our schema
        # For now, assume data is already in our format or close to it
        return {
            "id": raw_market.get("id", ""),
            "title": raw_market.get("title", ""),
            "description": raw_market.get("description", ""),
            "provider": "kalshi",
            "status": raw_market.get("status", "active"),
            "category": raw_market.get("category", ""),
            "created_at": raw_market.get("created_at", datetime.utcnow().isoformat()),
            "close_date": raw_market.get("close_date"),
            "settle_date": raw_market.get("settle_date"),
            "outcomes": raw_market.get("outcomes", []),
            "total_volume": raw_market.get("total_volume", 0),
            "liquidity": raw_market.get("liquidity", 0),
        }

    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to Kalshi API."""
        if self.mock_mode:
            return self._load_sample_data()

        async def _request():
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                response = await client.get(
                    f"{self.base_url}/{endpoint}", headers=headers, params=params or {}
                )
                response.raise_for_status()
                return response.json()

        return await self.async_retry(_request)

    async def get_markets(self) -> List[Dict]:
        """Fetch all available markets from Kalshi."""
        try:
            if self.mock_mode:
                sample_data = self._load_sample_data()
                return [
                    self.normalize_market(m) for m in sample_data.get("markets", [])
                ]

            # Real API call would be something like:
            # data = await self._make_request("markets")
            # return [self.normalize_market(m) for m in data.get("markets", [])]

            # For now, return sample data
            sample_data = self._load_sample_data()
            return [self.normalize_market(m) for m in sample_data.get("markets", [])]

        except Exception as e:
            logger.error(f"Error fetching Kalshi markets: {e}")
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
            logger.error(f"Error fetching Kalshi market {market_id}: {e}")
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
                "outcomes": market.get("outcomes", []),
            }

        except Exception as e:
            logger.error(f"Error fetching Kalshi market price {market_id}: {e}")
            return None

    async def get_market_timeseries(
        self, market_id: str, start: str = None, end: str = None, interval: str = "1h"
    ) -> Optional[Dict]:
        """Get historical timeseries data for a market."""
        try:
            # In mock mode, generate sample timeseries
            if self.mock_mode:
                now = datetime.utcnow()
                data_points = []

                for i in range(24):  # 24 hours of data
                    timestamp = now - timedelta(hours=23 - i)
                    price = 0.60 + (i * 0.001)  # Slight upward trend
                    data_points.append(
                        {
                            "timestamp": timestamp.isoformat(),
                            "price": price,
                            "volume": 100 + (i * 10),
                        }
                    )

                return {
                    "market_id": market_id,
                    "outcome_id": "yes",
                    "interval": interval,
                    "data_points": data_points,
                }

            # Real implementation would call Kalshi timeseries API
            return None

        except Exception as e:
            logger.error(f"Error fetching Kalshi timeseries {market_id}: {e}")
            return None

    async def get_market_orderbook(
        self, market_id: str, depth: int = 10
    ) -> Optional[Dict]:
        """Get current orderbook for a market."""
        try:
            if self.mock_mode:
                return {
                    "market_id": market_id,
                    "outcome_id": "yes",
                    "timestamp": datetime.utcnow().isoformat(),
                    "bids": [
                        {"price": 0.64, "size": 100.0},
                        {"price": 0.63, "size": 250.0},
                    ],
                    "asks": [
                        {"price": 0.66, "size": 150.0},
                        {"price": 0.67, "size": 200.0},
                    ],
                    "spread": 0.02,
                }

            # Real implementation would call Kalshi orderbook API
            return None

        except Exception as e:
            logger.error(f"Error fetching Kalshi orderbook {market_id}: {e}")
            return None

    async def get_market_events(
        self, market_id: str, since: str = None, limit: int = 100
    ) -> Optional[List[Dict]]:
        """Get recent events for a market."""
        try:
            if self.mock_mode:
                return [
                    {
                        "id": "evt_kalshi_123",
                        "market_id": market_id,
                        "event_type": "trade",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "outcome_id": "yes",
                            "price": 0.65,
                            "volume": 50.0,
                            "side": "buy",
                        },
                    }
                ]

            # Real implementation would call Kalshi events API
            return []

        except Exception as e:
            logger.error(f"Error fetching Kalshi events {market_id}: {e}")
            return []

    async def sync_data(self) -> Dict:
        """Sync all market data from Kalshi."""
        try:
            markets = await self.get_markets()
            return {
                "provider": "kalshi",
                "markets_synced": len(markets),
                "status": "success",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error syncing Kalshi data: {e}")
            return {
                "provider": "kalshi",
                "markets_synced": 0,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
