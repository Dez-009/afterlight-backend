from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def admin_info():
    """Admin management endpoint"""
    return {
        "success": True,
        "message": "Admin endpoints coming soon",
        "endpoints": [
            "/users",
            "/analytics",
            "/templates",
            "/system"
        ]
    }
