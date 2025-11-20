"""
Markets API Routes
Author: Abhi

Endpoints for retrieving market data, prices, timeseries, orderbooks, and events.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import ValidationError

from ingestion.kalshi import KalshiConnector
from ingestion.polymarket import PolymarketConnector
from models.schemas import EventRecord, MarketMeta, OrderBook, PricePoint, TimeSeries

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize connectors
kalshi_connector = KalshiConnector()
polymarket_connector = PolymarketConnector()


def create_envelope(data=None, ok=True, meta=None):
    """Create standardized API response envelope."""
    return {"ok": ok, "meta": meta or {}, "data": data}


@router.get("/markets", response_model=dict)
async def get_markets(
    provider: Optional[str] = Query(
        None, description="Filter by provider (kalshi, polymarket)"
    ),
    status: Optional[str] = Query(None, description="Filter by market status"),
    q: Optional[str] = Query(None, description="Search query"),
):
    """
    Retrieve all markets with optional filtering.

    Returns a list of markets from both Kalshi and Polymarket providers.
    """
    try:
        markets = []

        # Fetch from Kalshi if not filtered to specific provider
        if not provider or provider.lower() == "kalshi":
            kalshi_markets = await kalshi_connector.get_markets()
            markets.extend(kalshi_markets)

        # Fetch from Polymarket if not filtered to specific provider
        if not provider or provider.lower() == "polymarket":
            polymarket_markets = await polymarket_connector.get_markets()
            markets.extend(polymarket_markets)

        # Apply filters
        if status:
            markets = [
                m for m in markets if m.get("status", "").lower() == status.lower()
            ]

        if q:
            markets = [m for m in markets if q.lower() in m.get("title", "").lower()]

        return create_envelope(
            data=markets,
            meta={
                "total": len(markets),
                "providers": ["kalshi", "polymarket"] if not provider else [provider],
            },
        )

    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch markets")


@router.get("/markets/{market_id}", response_model=dict)
async def get_market(market_id: str = Path(..., description="Market identifier")):
    """
    Retrieve detailed information for a specific market.
    """
    try:
        # Try Kalshi first
        market = await kalshi_connector.get_market(market_id)
        if not market:
            # Try Polymarket
            market = await polymarket_connector.get_market(market_id)

        if not market:
            raise HTTPException(status_code=404, detail="Market not found")

        return create_envelope(data=market, meta={"market_id": market_id})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market {market_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market")


@router.get("/markets/{market_id}/price", response_model=dict)
async def get_market_price(market_id: str = Path(..., description="Market identifier")):
    """
    Get current price information for a market.
    """
    try:
        # Try Kalshi first
        price = await kalshi_connector.get_market_price(market_id)
        if not price:
            # Try Polymarket
            price = await polymarket_connector.get_market_price(market_id)

        if not price:
            raise HTTPException(status_code=404, detail="Market price not found")

        return create_envelope(
            data=price,
            meta={"market_id": market_id, "timestamp": datetime.utcnow().isoformat()},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market price")


@router.get("/markets/{market_id}/timeseries", response_model=dict)
async def get_market_timeseries(
    market_id: str = Path(..., description="Market identifier"),
    start: Optional[str] = Query(None, description="Start date (ISO format)"),
    end: Optional[str] = Query(None, description="End date (ISO format)"),
    interval: Optional[str] = Query("1h", description="Time interval (1m, 5m, 1h, 1d)"),
):
    """
    Get historical price timeseries for a market.
    """
    try:
        # Try Kalshi first
        timeseries = await kalshi_connector.get_market_timeseries(
            market_id, start, end, interval
        )
        if not timeseries:
            # Try Polymarket
            timeseries = await polymarket_connector.get_market_timeseries(
                market_id, start, end, interval
            )

        if not timeseries:
            raise HTTPException(status_code=404, detail="Market timeseries not found")

        return create_envelope(
            data=timeseries,
            meta={
                "market_id": market_id,
                "interval": interval,
                "start": start,
                "end": end,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching timeseries for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market timeseries")


@router.get("/markets/{market_id}/orderbook", response_model=dict)
async def get_market_orderbook(
    market_id: str = Path(..., description="Market identifier"),
    depth: Optional[int] = Query(10, description="Order book depth"),
):
    """
    Get current order book for a market.
    """
    try:
        # Try Kalshi first
        orderbook = await kalshi_connector.get_market_orderbook(market_id, depth)
        if not orderbook:
            # Try Polymarket
            orderbook = await polymarket_connector.get_market_orderbook(
                market_id, depth
            )

        if not orderbook:
            raise HTTPException(status_code=404, detail="Market orderbook not found")

        return create_envelope(
            data=orderbook,
            meta={
                "market_id": market_id,
                "depth": depth,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching orderbook for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market orderbook")


@router.get("/markets/{market_id}/events", response_model=dict)
async def get_market_events(
    market_id: str = Path(..., description="Market identifier"),
    since: Optional[str] = Query(
        None, description="Events since timestamp (ISO format)"
    ),
    limit: Optional[int] = Query(100, description="Maximum number of events"),
):
    """
    Get recent events for a market.
    """
    try:
        # Try Kalshi first
        events = await kalshi_connector.get_market_events(market_id, since, limit)
        if not events:
            # Try Polymarket
            events = await polymarket_connector.get_market_events(
                market_id, since, limit
            )

        if not events:
            raise HTTPException(status_code=404, detail="Market events not found")

        return create_envelope(
            data=events,
            meta={
                "market_id": market_id,
                "since": since,
                "limit": limit,
                "count": len(events) if isinstance(events, list) else 0,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching events for market {market_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market events")
