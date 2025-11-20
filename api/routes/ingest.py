"""
Ingestion API Routes
Author: Abhi

Development-only endpoints for triggering data synchronization from providers.
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Path

from ingestion.kalshi import KalshiConnector
from ingestion.polymarket import PolymarketConnector

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize connectors
kalshi_connector = KalshiConnector()
polymarket_connector = PolymarketConnector()


def create_envelope(data=None, ok=True, meta=None):
    """Create standardized API response envelope."""
    return {"ok": ok, "meta": meta or {}, "data": data}


@router.post("/ingest/{provider}/sync")
async def sync_provider_data(
    provider: str = Path(..., description="Provider to sync (kalshi, polymarket)")
):
    """
    Trigger data synchronization for a specific provider.

    This is a development-only endpoint for manually triggering data ingestion.
    In production, this would typically be handled by scheduled jobs.
    """
    try:
        provider = provider.lower()

        if provider == "kalshi":
            result = await kalshi_connector.sync_data()
        elif provider == "polymarket":
            result = await polymarket_connector.sync_data()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown provider: {provider}. Supported: kalshi, polymarket",
            )

        return create_envelope(
            data=result,
            meta={
                "provider": provider,
                "sync_timestamp": datetime.utcnow().isoformat(),
                "status": "completed",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error syncing data for provider {provider}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to sync data for provider {provider}"
        )
