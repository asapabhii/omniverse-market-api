#!/bin/bash
# Omniverse Market API - cURL Examples
# Author: Abhi
# 
# Collection of example API calls for testing and demonstration.
# Make sure the API server is running: make run

BASE_URL="http://localhost:8000/api/v1"

echo "=========================================="
echo "Omniverse Market API - cURL Examples"
echo "Author: Abhi"
echo "=========================================="
echo

# Health Check
echo "1. Health Check"
echo "curl $BASE_URL/health"
curl -s "$BASE_URL/health" | python -m json.tool
echo
echo "----------------------------------------"

# Get All Markets
echo "2. Get All Markets"
echo "curl $BASE_URL/markets"
curl -s "$BASE_URL/markets" | python -m json.tool
echo
echo "----------------------------------------"

# Get Markets by Provider
echo "3. Get Markets by Provider (Kalshi)"
echo "curl '$BASE_URL/markets?provider=kalshi'"
curl -s "$BASE_URL/markets?provider=kalshi" | python -m json.tool
echo
echo "----------------------------------------"

# Get Markets by Status
echo "4. Get Markets by Status (Active)"
echo "curl '$BASE_URL/markets?status=active'"
curl -s "$BASE_URL/markets?status=active" | python -m json.tool
echo
echo "----------------------------------------"

# Search Markets
echo "5. Search Markets (Biden)"
echo "curl '$BASE_URL/markets?q=Biden'"
curl -s "$BASE_URL/markets?q=Biden" | python -m json.tool
echo
echo "----------------------------------------"

# Get Specific Market
echo "6. Get Specific Market"
echo "curl $BASE_URL/markets/KALSHI-PRES2024"
curl -s "$BASE_URL/markets/KALSHI-PRES2024" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Price
echo "7. Get Market Price"
echo "curl $BASE_URL/markets/KALSHI-PRES2024/price"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/price" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Timeseries
echo "8. Get Market Timeseries"
echo "curl $BASE_URL/markets/KALSHI-PRES2024/timeseries"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/timeseries" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Timeseries with Parameters
echo "9. Get Market Timeseries with Parameters"
echo "curl '$BASE_URL/markets/KALSHI-PRES2024/timeseries?interval=1h&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z'"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/timeseries?interval=1h&start=2024-01-01T00:00:00Z&end=2024-01-02T00:00:00Z" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Orderbook
echo "10. Get Market Orderbook"
echo "curl $BASE_URL/markets/KALSHI-PRES2024/orderbook"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/orderbook" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Orderbook with Depth
echo "11. Get Market Orderbook with Depth"
echo "curl '$BASE_URL/markets/KALSHI-PRES2024/orderbook?depth=5'"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/orderbook?depth=5" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Events
echo "12. Get Market Events"
echo "curl $BASE_URL/markets/KALSHI-PRES2024/events"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/events" | python -m json.tool
echo
echo "----------------------------------------"

# Get Market Events with Parameters
echo "13. Get Market Events with Parameters"
echo "curl '$BASE_URL/markets/KALSHI-PRES2024/events?limit=5&since=2024-01-01T00:00:00Z'"
curl -s "$BASE_URL/markets/KALSHI-PRES2024/events?limit=5&since=2024-01-01T00:00:00Z" | python -m json.tool
echo
echo "----------------------------------------"

# Sync Kalshi Data (Development)
echo "14. Sync Kalshi Data (Development)"
echo "curl -X POST $BASE_URL/ingest/kalshi/sync"
curl -s -X POST "$BASE_URL/ingest/kalshi/sync" | python -m json.tool
echo
echo "----------------------------------------"

# Sync Polymarket Data (Development)
echo "15. Sync Polymarket Data (Development)"
echo "curl -X POST $BASE_URL/ingest/polymarket/sync"
curl -s -X POST "$BASE_URL/ingest/polymarket/sync" | python -m json.tool
echo
echo "----------------------------------------"

# Test Error Handling (404)
echo "16. Test Error Handling (404)"
echo "curl $BASE_URL/markets/NONEXISTENT"
curl -s "$BASE_URL/markets/NONEXISTENT" | python -m json.tool
echo
echo "----------------------------------------"

# Test Error Handling (Invalid Provider)
echo "17. Test Error Handling (Invalid Provider)"
echo "curl -X POST $BASE_URL/ingest/invalid/sync"
curl -s -X POST "$BASE_URL/ingest/invalid/sync" | python -m json.tool
echo
echo "----------------------------------------"

echo "All examples completed!"
echo
echo "For interactive API documentation, visit:"
echo "  Swagger UI: http://localhost:8000/docs"
echo "  ReDoc:      http://localhost:8000/redoc"