from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, documents, generation, refinement, export

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(generation.router, prefix="/generation", tags=["generation"])
api_router.include_router(refinement.router, prefix="/refinement", tags=["refinement"])
api_router.include_router(export.router, prefix="/export", tags=["export"])

