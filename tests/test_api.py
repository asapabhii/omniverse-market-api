"""
API Tests for Omniverse Market API
Author: Abhi

Unit tests for API endpoints using FastAPI TestClient.
Tests run in mock mode by default.
"""

import os

import pytest
from fastapi.testclient import TestClient

# Set mock mode for testing
os.environ["KALSHI_API_KEY"] = ""
os.environ["POLYMARKET_API_KEY"] = ""

from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self):
        """Test health endpoint returns correct response."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert data["data"]["status"] == "healthy"
        assert data["data"]["service"] == "omniverse-market-api"


class TestMarketsEndpoints:
    """Test market-related endpoints."""

    def test_get_markets(self):
        """Test getting all markets."""
        response = client.get("/api/v1/markets")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert isinstance(data["data"], list)
        assert "meta" in data
        assert "total" in data["meta"]

    def test_get_markets_with_provider_filter(self):
        """Test getting markets filtered by provider."""
        response = client.get("/api/v1/markets?provider=kalshi")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert isinstance(data["data"], list)

        # Check that all returned markets are from kalshi
        for market in data["data"]:
            assert market["provider"] == "kalshi"

    def test_get_markets_with_status_filter(self):
        """Test getting markets filtered by status."""
        response = client.get("/api/v1/markets?status=active")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert isinstance(data["data"], list)

    def test_get_markets_with_search_query(self):
        """Test getting markets with search query."""
        response = client.get("/api/v1/markets?q=Biden")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert isinstance(data["data"], list)

    def test_get_specific_market(self):
        """Test getting a specific market by ID."""
        # First get all markets to find a valid ID
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(f"/api/v1/markets/{market_id}")
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert data["data"]["id"] == market_id

    def test_get_nonexistent_market(self):
        """Test getting a market that doesn't exist."""
        response = client.get("/api/v1/markets/NONEXISTENT")
        assert response.status_code == 404

    def test_get_market_price(self):
        """Test getting market price."""
        # Get a valid market ID first
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(f"/api/v1/markets/{market_id}/price")
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert "data" in data
            assert "meta" in data
            assert data["meta"]["market_id"] == market_id

    def test_get_market_timeseries(self):
        """Test getting market timeseries."""
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(f"/api/v1/markets/{market_id}/timeseries")
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert "data" in data

    def test_get_market_timeseries_with_params(self):
        """Test getting market timeseries with parameters."""
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(
                f"/api/v1/markets/{market_id}/timeseries"
                "?start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z&interval=1h"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert data["meta"]["interval"] == "1h"

    def test_get_market_orderbook(self):
        """Test getting market orderbook."""
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(f"/api/v1/markets/{market_id}/orderbook")
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert "data" in data

    def test_get_market_orderbook_with_depth(self):
        """Test getting market orderbook with depth parameter."""
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(f"/api/v1/markets/{market_id}/orderbook?depth=5")
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert data["meta"]["depth"] == 5

    def test_get_market_events(self):
        """Test getting market events."""
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(f"/api/v1/markets/{market_id}/events")
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert "data" in data

    def test_get_market_events_with_params(self):
        """Test getting market events with parameters."""
        markets_response = client.get("/api/v1/markets")
        markets = markets_response.json()["data"]

        if markets:
            market_id = markets[0]["id"]
            response = client.get(
                f"/api/v1/markets/{market_id}/events"
                "?since=2024-01-01T00:00:00Z&limit=50"
            )
            assert response.status_code == 200

            data = response.json()
            assert data["ok"] is True
            assert data["meta"]["limit"] == 50


class TestIngestionEndpoints:
    """Test ingestion endpoints."""

    def test_sync_kalshi_data(self):
        """Test syncing Kalshi data."""
        response = client.post("/api/v1/ingest/kalshi/sync")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert data["data"]["provider"] == "kalshi"
        assert data["data"]["status"] == "success"

    def test_sync_polymarket_data(self):
        """Test syncing Polymarket data."""
        response = client.post("/api/v1/ingest/polymarket/sync")
        assert response.status_code == 200

        data = response.json()
        assert data["ok"] is True
        assert "data" in data
        assert data["data"]["provider"] == "polymarket"
        assert data["data"]["status"] == "success"

    def test_sync_invalid_provider(self):
        """Test syncing with invalid provider."""
        response = client.post("/api/v1/ingest/invalid/sync")
        assert response.status_code == 400


class TestErrorHandling:
    """Test error handling."""

    def test_404_handler(self):
        """Test custom 404 handler."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert data["ok"] is False
        assert "error" in data["meta"]


if __name__ == "__main__":
    pytest.main([__file__])
