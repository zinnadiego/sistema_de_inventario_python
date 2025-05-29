from fastapi import APIRouter
from .endpoints import router as api_router

router = APIRouter()

# Incluir todos los endpoints bajo el prefijo /api
router.include_router(api_router, prefix="/api") 