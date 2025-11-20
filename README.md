# Omniverse Market API

**Author:** Abhinav   
**Engine:** Omniverse Market API (Full-Stack)

A production-ready FastAPI-based engine for ingesting and normalizing prediction market data from Kalshi and Polymarket. Designed for forecasting and trading model consumption with comprehensive API endpoints, mock fallbacks, and robust error handling.

##  Current Status: **FULLY OPERATIONAL**

 **Ready to run!** All core functionality is working:
-  API server starts successfully
-  All endpoints responding correctly  
-  Mock mode working with sample data
-  Interactive documentation available
-  Demo script functional
-  No external API keys required for testing

##  Quick Start

```bash
# Clone the repository
git clone https://github.com/asapabhii/omniverse-market-api.git
cd omniverse-market-api

# Install dependencies (core packages only)
python -m pip install fastapi uvicorn pydantic httpx python-dotenv

# Generate sample data
python data/gen_sample.py

# Start the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

** That's it!** The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

##  Features

- **Multi-Provider Support**: Kalshi and Polymarket data ingestion
- **Standardized API**: Consistent response format across all endpoints
- **Mock Fallback**: Runs without API keys using deterministic sample data
- **Type Safety**: Full Pydantic model validation
- **Production Ready**: Comprehensive error handling, logging, and testing
- **Developer Experience**: Pre-commit hooks, CI/CD, and extensive documentation

##  API Endpoints

All endpoints return responses in the standardized envelope format:
```json
{
  "ok": true,
  "meta": {},
  "data": {}
}
```

### Core Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/markets` - List all markets (filters: `provider`, `status`, `q`)
- `GET /api/v1/markets/{market_id}` - Get specific market
- `GET /api/v1/markets/{market_id}/price` - Current market price
- `GET /api/v1/markets/{market_id}/timeseries` - Historical price data
- `GET /api/v1/markets/{market_id}/orderbook` - Current order book
- `GET /api/v1/markets/{market_id}/events` - Recent market events

### Development Endpoints

- `POST /api/v1/ingest/{provider}/sync` - Trigger data synchronization

##  Architecture

```
omniverse-market-api/
├── api/                    # FastAPI application
│   ├── main.py            # Main application and middleware
│   └── routes/            # API route handlers
├── models/                # Pydantic data models
├── ingestion/             # Provider connectors (Kalshi, Polymarket)
├── data/                  # Sample data and generators
├── tests/                 # Comprehensive test suite
└── examples/              # Usage examples and collections
```

##  Configuration

Copy `.env.example` to `.env` and configure your API credentials:

```bash
cp .env.example .env
```

### API Keys Setup

**Kalshi:**
1. Sign up at [kalshi.com](https://kalshi.com/)
2. Generate API key in your account settings
3. Add `KALSHI_API_KEY` and `KALSHI_USER_ID` to `.env`

**Polymarket:**
1. Sign up at [polymarket.com](https://polymarket.com/)
2. Generate API key in developer settings
3. Add `POLYMARKET_API_KEY` to `.env`

**Mock Mode:** If no API keys are provided, the system automatically runs in mock mode with sample data.

##  Development

### Available Commands

```bash
# Core commands (no Makefile needed!)
python -m pip install -r requirements.txt    # Install all dependencies
python data/gen_sample.py                    # Generate sample data
uvicorn api.main:app --reload                # Start development server
python run_demo.py                           # Run prediction demo

# Optional: Use Makefile if available
make install      # Install dependencies
make run          # Start development server
make test         # Run test suite
make lint         # Run code quality checks
make format       # Format code
make gen-sample   # Generate sample data
make demo         # Run prediction demo
make dev          # Setup complete dev environment
```

### Code Quality

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **pre-commit** for git hooks
- **pytest** for testing

### Testing

```bash
# Install test dependencies first
python -m pip install pytest pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Or use Makefile if available
make test
```

###  Troubleshooting

**Server won't start?**
```bash
# Check if port 8000 is already in use
netstat -an | findstr :8000

# Try a different port
uvicorn api.main:app --host 0.0.0.0 --port 8001 --reload
```

**Missing dependencies?**
```bash
# Install core dependencies only
python -m pip install fastapi uvicorn pydantic httpx python-dotenv

# Or install everything
python -m pip install -r requirements.txt
```

**No sample data?**
```bash
# Generate sample data
python data/gen_sample.py
```

##  Data Models

### MarketMeta
Core market information with outcomes, volume, and metadata.

### PricePoint & TimeSeries
Historical price data with configurable intervals (1m, 5m, 1h, 1d).

### OrderBook
Real-time bid/ask data with configurable depth.

### EventRecord
Market events (trades, price changes, etc.) with structured data.

##  Provider Integration

### Kalshi Connector
- Endpoint: `https://trading-api.kalshi.com/trade-api/v2`
- Authentication: Bearer token
- Rate limiting: Built-in retry with exponential backoff
- Mock fallback: Deterministic sample data

### Polymarket Connector  
- Endpoint: `https://clob.polymarket.com`
- Authentication: API key
- Rate limiting: Built-in retry with exponential backoff
- Mock fallback: Deterministic sample data

##  Demo & Examples

###  Test the API (Copy & Paste Ready!)

Once your server is running, test these endpoints:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Get all markets
curl http://localhost:8000/api/v1/markets

# Get specific market
curl http://localhost:8000/api/v1/markets/KALSHI-PRES2024

# Get market price
curl http://localhost:8000/api/v1/markets/KALSHI-PRES2024/price

# Get market timeseries
curl http://localhost:8000/api/v1/markets/KALSHI-PRES2024/timeseries

# Sync provider data (development)
curl -X POST http://localhost:8000/api/v1/ingest/kalshi/sync
```

###  Run Prediction Demo
```bash
python run_demo.py
```

The demo script analyzes sample market data and generates toy predictions. **Not for actual trading use.**

###  Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

See `examples/curl_examples.sh` for more examples.

##  Deployment

### Local Development
```bash
make run
```

### Production Considerations
- Set `DEBUG=false` in environment
- Use proper API keys (not mock mode)
- Configure logging levels
- Set up monitoring and alerting
- Consider rate limiting and caching

##  Testing & QA

###  Quick Validation
```bash
# 1. Install dependencies
python -m pip install fastapi uvicorn pydantic httpx python-dotenv

# 2. Generate sample data
python data/gen_sample.py

# 3. Start server (in background or separate terminal)
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Test health check
curl http://localhost:8000/api/v1/health

# 5. Test markets endpoint
curl http://localhost:8000/api/v1/markets

# 6. Run demo script
python run_demo.py

# 7. Visit interactive docs
# Open browser: http://localhost:8000/docs
```

### CI/CD Pipeline
GitHub Actions automatically runs:
- Code quality checks (black, isort, flake8)
- Full test suite
- Demo script validation

##  Documentation

- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **ReDoc**: `http://localhost:8000/redoc`
- **Architecture**: See `ARCHITECTURE.md`
- **Changelog**: See `CHANGELOG.md`

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `make check` to validate
5. Submit a pull request

##  Disclaimer

This is a demonstration project for educational purposes. The prediction algorithms are toy implementations and should not be used for actual trading decisions. Always conduct proper research and risk assessment before making any financial decisions.

---

**Omniverse Fund Full-Stack Engineering Intern Sub**  
 by Abhi
