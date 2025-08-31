from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def auth_info():
    """Authentication information endpoint"""
    return {
        "success": True,
        "message": "Auth endpoints coming soon",
        "endpoints": [
            "/login",
            "/signup", 
            "/refresh",
            "/logout"
        ]
    }
