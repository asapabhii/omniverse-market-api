"""
Pydantic Data Models for Omniverse Market API
Author: Abhi

Typed models for market data, prices, timeseries, orderbooks, and events.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class Outcome(BaseModel):
    """Represents a market outcome/option."""

    id: str = Field(..., description="Unique outcome identifier")
    name: str = Field(..., description="Human-readable outcome name")
    price: Optional[float] = Field(
        None, description="Current price (0-1 for probability)"
    )
    volume: Optional[float] = Field(None, description="Trading volume")

    class Config:
        schema_extra = {
            "example": {"id": "yes", "name": "Yes", "price": 0.65, "volume": 15420.50}
        }


class MarketMeta(BaseModel):
    """Core market metadata and information."""

    id: str = Field(..., description="Unique market identifier")
    title: str = Field(..., description="Market title/question")
    description: Optional[str] = Field(None, description="Detailed market description")
    provider: str = Field(..., description="Data provider (kalshi, polymarket)")
    status: str = Field(..., description="Market status (active, closed, settled)")
    category: Optional[str] = Field(None, description="Market category")
    created_at: datetime = Field(..., description="Market creation timestamp")
    close_date: Optional[datetime] = Field(None, description="Market close date")
    settle_date: Optional[datetime] = Field(None, description="Settlement date")
    outcomes: List[Outcome] = Field(..., description="Available market outcomes")
    total_volume: Optional[float] = Field(None, description="Total trading volume")
    liquidity: Optional[float] = Field(None, description="Current liquidity")

    class Config:
        schema_extra = {
            "example": {
                "id": "PRES2024",
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
                    {"id": "no", "name": "No", "price": 0.35, "volume": 8930.25},
                ],
                "total_volume": 24350.75,
                "liquidity": 5420.30,
            }
        }


class PricePoint(BaseModel):
    """Single price data point."""

    timestamp: datetime = Field(..., description="Price timestamp")
    price: float = Field(..., description="Price value (0-1 for probability)")
    volume: Optional[float] = Field(None, description="Volume at this price")
    outcome_id: Optional[str] = Field(None, description="Outcome identifier")


class TimeSeries(BaseModel):
    """Time series data for market prices."""

    market_id: str = Field(..., description="Market identifier")
    outcome_id: Optional[str] = Field(None, description="Outcome identifier")
    interval: str = Field(..., description="Time interval (1m, 5m, 1h, 1d)")
    data_points: List[PricePoint] = Field(..., description="Price data points")

    class Config:
        schema_extra = {
            "example": {
                "market_id": "PRES2024",
                "outcome_id": "yes",
                "interval": "1h",
                "data_points": [
                    {
                        "timestamp": "2024-01-01T00:00:00Z",
                        "price": 0.60,
                        "volume": 1250.0,
                    },
                    {
                        "timestamp": "2024-01-01T01:00:00Z",
                        "price": 0.62,
                        "volume": 890.5,
                    },
                ],
            }
        }


class OrderBookEntry(BaseModel):
    """Single order book entry."""

    price: float = Field(..., description="Order price")
    size: float = Field(..., description="Order size/quantity")


class OrderBook(BaseModel):
    """Market order book data."""

    market_id: str = Field(..., description="Market identifier")
    outcome_id: Optional[str] = Field(None, description="Outcome identifier")
    timestamp: datetime = Field(..., description="Order book timestamp")
    bids: List[OrderBookEntry] = Field(..., description="Buy orders")
    asks: List[OrderBookEntry] = Field(..., description="Sell orders")
    spread: Optional[float] = Field(None, description="Bid-ask spread")

    class Config:
        schema_extra = {
            "example": {
                "market_id": "PRES2024",
                "outcome_id": "yes",
                "timestamp": "2024-01-01T12:00:00Z",
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
        }


class EventRecord(BaseModel):
    """Market event record."""

    id: str = Field(..., description="Event identifier")
    market_id: str = Field(..., description="Market identifier")
    event_type: str = Field(..., description="Event type (trade, price_change, etc.)")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event-specific data")

    class Config:
        schema_extra = {
            "example": {
                "id": "evt_123456",
                "market_id": "PRES2024",
                "event_type": "trade",
                "timestamp": "2024-01-01T12:30:00Z",
                "data": {
                    "outcome_id": "yes",
                    "price": 0.65,
                    "volume": 50.0,
                    "side": "buy",
                },
            }
        }
