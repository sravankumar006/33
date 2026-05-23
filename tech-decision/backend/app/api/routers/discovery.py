import logging
from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.phone import PhoneDiscoverySearchResult
from app.services.discovery.discovery_service import DiscoveryService

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/api/discovery", tags=["Discovery"])

@router.get("/search", response_model=List[PhoneDiscoverySearchResult])
def search_and_discover_phones(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """
    Search for a phone on external sources, normalize it, store/update it in the DB,
    and return clean frontend-ready records.
    """
    logger.info(f"API: GET /api/discovery/search?q={q}")
    try:
        discovery_service = DiscoveryService()
        results = discovery_service.search_and_discover(q, db)
        return results
    except Exception as exc:
        logger.exception(f"API Error in /api/discovery/search: {exc}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while discovering products. Please try again."
        ) from exc
