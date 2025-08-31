from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def planning_info():
    """Planning and event management endpoint"""
    return {
        "success": True,
        "message": "Planning endpoints coming soon",
        "endpoints": [
            "/sessions",
            "/events",
            "/checklists",
            "/vendors"
        ]
    }
