from fastapi import APIRouter, HTTPException
from api.async_client import get_vlr_client
from utils.performance import track_request, get_performance_stats
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/matches/live")
@track_request
async def get_live_matches():
    """Get all currently live matches"""
    try:
        async with await get_vlr_client() as client:
            result = await client.get_live_matches()
            if not result or (isinstance(result, dict) and not result.get('data')):
                return {"status": "success", "message": "No live matches currently available.", "data": []}
            return result
    except Exception as e:
        logger.error(f"Error in get_live_matches: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/matches/{match_id}")
@track_request
async def get_match_details(match_id: str):
    """
    Get detailed information about a specific match by its ID
    
    Args:
        match_id: The VLR match ID (e.g., '551847' from the match URL)
    """
    try:
        async with await get_vlr_client() as client:
            result = await client.get_match_by_id(match_id)
            if result.get('status') == 'error':
                raise HTTPException(status_code=404, detail=result.get('message', 'Match not found'))
            return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_match_details: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/stats/performance", include_in_schema=False)
async def get_performance_stats_endpoint():
    """Get API performance statistics"""
    return get_performance_stats()
