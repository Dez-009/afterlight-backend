from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def cultural_info():
    """Cultural templates and preferences endpoint"""
    return {
        "success": True,
        "message": "Cultural endpoints coming soon",
        "endpoints": [
            "/templates",
            "/preferences",
            "/traditions"
        ]
    }
