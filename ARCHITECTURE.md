# Omniverse Market API - Architecture Documentation

**Author:** Abhi  
**Email:** dankalu.work@gmail.com

## Overview

The Omniverse Market API is designed as a production-ready, API-first engine for ingesting and normalizing prediction market data from multiple providers (Kalshi and Polymarket). The architecture emphasizes modularity, type safety, and robust error handling while maintaining simplicity and performance.

## System Architecture

### High-Level Design

```
┌─────────────────┐    ┌─────────────────┐
│   Kalshi API    │    │ Polymarket API  │
└─────────┬───────┘    └─────────┬───────┘
          │                      │
          └──────┬─────────┬─────┘
                 │         │
         ┌───────▼─────────▼───────┐
         │   Ingestion Layer       │
         │  ┌─────────────────────┐│
         │  │ Kalshi Connector    ││
         │  │ Polymarket Connector││
         │  │ Retry & Backoff     ││
         │  │ Mock Fallback       ││
         │  └─────────────────────┘│
         └─────────┬───────────────┘
                   │
         ┌─────────▼───────────────┐
         │   Normalization Layer   │
         │  ┌─────────────────────┐│
         │  │ Pydantic Models     ││
         │  │ Data Validation     ││
         │  │ Schema Mapping      ││
         │  └─────────────────────┘│
         └─────────┬───────────────┘
                   │
         ┌─────────▼───────────────┐
         │     API Layer           │
         │  ┌─────────────────────┐│
         │  │ FastAPI Routes      ││
         │  │ Response Envelopes  ││
         │  │ Error Handling      ││
         │  │ OpenAPI Docs        ││
         │  └─────────────────────┘│
         └─────────┬───────────────┘
                   │
         ┌─────────▼───────────────┐
         │    Client Layer         │
         │  ┌─────────────────────┐│
         │  │ HTTP Clients        ││
         │  │ Trading Models      ││
         │  │ Analytics Tools     ││
         │  └─────────────────────┘│
         └─────────────────────────┘
```

## Core Components

### 1. API Layer (`api/`)

**Responsibility:** HTTP request handling, response formatting, and API documentation.

**Key Files:**
- `main.py`: FastAPI application setup, middleware, and global error handlers
- `routes/markets.py`: Market data endpoints with filtering and pagination
- `routes/ingest.py`: Development endpoints for data synchronization

**Design Patterns:**
- **Dependency Injection**: Connectors injected into route handlers
- **Response Envelope**: Standardized `{ok, meta, data}` format
- **Error Handling**: Centralized exception handling with proper HTTP status codes

### 2. Data Models (`models/`)

**Responsibility:** Type definitions, validation, and serialization.

**Key Files:**
- `schemas.py`: Pydantic models for all API data structures

**Models:**
- `MarketMeta`: Core market information and metadata
- `Outcome`: Individual market outcomes with prices and volume
- `PricePoint`: Single price data point with timestamp
- `TimeSeries`: Historical price data collections
- `OrderBook`: Bid/ask order book data
- `EventRecord`: Market events and activities

**Design Principles:**
- **Type Safety**: Full Pydantic validation on all data
- **Immutability**: Models are read-only after creation
- **Documentation**: Rich schema examples for OpenAPI generation

### 3. Ingestion Layer (`ingestion/`)

**Responsibility:** External API integration, data fetching, and normalization.

**Key Files:**
- `kalshi.py`: Kalshi API connector with authentication and rate limiting
- `polymarket.py`: Polymarket API connector with retry logic

**Features:**
- **Async HTTP**: `httpx.AsyncClient` for non-blocking requests
- **Retry Logic**: Exponential backoff with configurable attempts
- **Mock Fallback**: Deterministic sample data when API keys unavailable
- **Normalization**: Provider-specific data mapping to common schema

**Error Handling:**
- Network timeouts and connection errors
- API rate limiting and quota exceeded
- Authentication failures
- Malformed response data

### 4. Data Layer (`data/`)

**Responsibility:** Sample data generation and storage for development/testing.

**Key Files:**
- `gen_sample.py`: Deterministic sample data generator
- `sample_timeseries.json`: Pre-generated market data for mock mode

## Data Flow

### 1. Request Processing

```
HTTP Request → FastAPI Router → Route Handler → Connector → External API
                     ↓
Response Envelope ← Pydantic Model ← Normalization ← Raw API Data
```

### 2. Mock Mode Flow

```
HTTP Request → FastAPI Router → Route Handler → Connector → Sample Data File
                     ↓
Response Envelope ← Pydantic Model ← Normalization ← Mock Data
```

### 3. Error Flow

```
Exception → Global Handler → Error Envelope → HTTP Response
```

## Configuration Management

### Environment Variables
- `KALSHI_API_KEY`: Kalshi authentication token
- `KALSHI_USER_ID`: Kalshi user identifier
- `POLYMARKET_API_KEY`: Polymarket authentication token
- `DEBUG`: Development mode flag
- `LOG_LEVEL`: Logging verbosity

### Mock Mode Detection
```python
mock_mode = not (api_key and user_id)
```

When credentials are missing, connectors automatically switch to mock mode using sample data.

## API Design Principles

### 1. Response Envelope
All endpoints return a consistent structure:
```json
{
  "ok": boolean,
  "meta": {
    "timestamp": "ISO8601",
    "pagination": {},
    "filters": {}
  },
  "data": any
}
```

### 2. RESTful Design
- `GET /markets` - Collection retrieval
- `GET /markets/{id}` - Resource retrieval
- `GET /markets/{id}/timeseries` - Sub-resource retrieval
- `POST /ingest/{provider}/sync` - Action endpoints

### 3. Query Parameters
- Filtering: `?provider=kalshi&status=active`
- Search: `?q=bitcoin`
- Pagination: `?limit=50&offset=100`
- Time ranges: `?start=2024-01-01&end=2024-01-31`

## Error Handling Strategy

### 1. HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error (system failure)

### 2. Error Response Format
```json
{
  "ok": false,
  "meta": {
    "error": "Human readable error message",
    "error_code": "MACHINE_READABLE_CODE",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  "data": null
}
```

### 3. Logging Strategy
- `INFO`: Normal operations and API calls
- `WARNING`: Retry attempts and recoverable errors
- `ERROR`: System failures and unrecoverable errors
- `DEBUG`: Detailed request/response data (development only)

## Performance Considerations

### 1. Async Operations
- All external API calls use `async/await`
- Non-blocking I/O for concurrent request handling
- Connection pooling via `httpx.AsyncClient`

### 2. Retry Logic
- Exponential backoff: `delay = base_delay * (2 ** attempt)`
- Maximum 3 retry attempts
- Jitter to prevent thundering herd

### 3. Caching Strategy (Future)
- Redis for market data caching
- TTL based on data freshness requirements
- Cache invalidation on data updates

## Security Considerations

### 1. API Key Management
- Environment variable storage
- No hardcoded credentials
- Secure transmission (HTTPS only in production)

### 2. Input Validation
- Pydantic model validation on all inputs
- SQL injection prevention (no direct DB queries)
- XSS prevention via proper serialization

### 3. Rate Limiting (Future)
- Per-client request limits
- Provider API quota management
- Graceful degradation under load

## Testing Strategy

### 1. Unit Tests
- Mock mode testing (no external dependencies)
- Pydantic model validation
- Error handling scenarios

### 2. Integration Tests
- End-to-end API testing
- External API mocking
- Database integration (future)

### 3. Load Testing (Future)
- Concurrent request handling
- Memory usage under load
- Response time benchmarks

## Deployment Architecture

### Development
```
Local Machine → uvicorn → FastAPI App → Mock Data
```

### Production (Future)
```
Load Balancer → Container Cluster → FastAPI Apps → External APIs
                      ↓
                 Redis Cache ← Database
```

## Monitoring & Observability

### 1. Logging
- Structured JSON logs
- Request/response correlation IDs
- Performance metrics

### 2. Health Checks
- `/api/v1/health` endpoint
- External API connectivity checks
- System resource monitoring

### 3. Metrics (Future)
- Request rate and latency
- Error rates by endpoint
- External API response times

## Scalability Considerations

### 1. Horizontal Scaling
- Stateless application design
- Load balancer compatibility
- Container orchestration ready

### 2. Data Partitioning (Future)
- Market data sharding by provider
- Time-based partitioning for historical data
- Read replicas for query performance

### 3. Caching Layers (Future)
- Application-level caching
- CDN for static content
- Database query optimization

## Future Enhancements

### 1. Real-time Features
- WebSocket endpoints for live data
- Server-sent events for price updates
- Push notifications for market events

### 2. Advanced Analytics
- Technical indicators calculation
- Volatility analysis
- Correlation analysis between markets

### 3. Machine Learning Integration
- Price prediction models
- Anomaly detection
- Sentiment analysis from market data

---

This architecture provides a solid foundation for a production prediction market API while maintaining flexibility for future enhancements and scaling requirements.