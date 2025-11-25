from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.db.database import get_db
from app.db import models
from app.api.v1.endpoints.auth import get_current_user
from app.services.llm_service import refine_content
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class RefinementRequest(BaseModel):
    prompt: Optional[str] = None
    content: str
    feedback: Optional[str] = None  # "like" or "dislike"
    comments: Optional[str] = None


class RefinementResponse(BaseModel):
    id: int
    content: str
    prompt: Optional[str] = None
    feedback: Optional[str] = None
    comments: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RefinementUpdate(BaseModel):
    prompt: Optional[str] = None
    feedback: Optional[str] = None
    comments: Optional[str] = None


@router.post("/section/{section_id}/refine", response_model=RefinementResponse)
async def refine_section(
    section_id: int,
    request: RefinementRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refine a section with AI assistance"""
    section = db.query(models.Section).filter(
        models.Section.id == section_id
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == section.project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # If prompt provided, use AI to refine the CURRENT content (from request)
    refined_content = request.content
    if request.prompt:
        try:
            # Use request.content (current edited content) as the base for refinement
            original_content = request.content if request.content else (section.content or "")
            refined_content = refine_content(original_content, request.prompt, "section")
        except Exception as e:
            logger.error(f"Error refining section {section_id}: {e}")
            # If refinement fails, use the manually edited content from request
            refined_content = request.content
    
    # Update section content with refined or edited content
    section.content = refined_content
    db.commit()
    db.refresh(section)
    
    # Create refinement record
    refinement = models.Refinement(
        section_id=section_id,
        prompt=request.prompt,
        content=refined_content,
        feedback=request.feedback,
        comments=request.comments,
    )
    db.add(refinement)
    db.commit()
    db.refresh(refinement)
    
    return refinement


@router.post("/slide/{slide_id}/refine", response_model=RefinementResponse)
async def refine_slide(
    slide_id: int,
    request: RefinementRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Refine a slide with AI assistance"""
    slide = db.query(models.Slide).filter(
        models.Slide.id == slide_id
    ).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == slide.project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # If prompt provided, use AI to refine the CURRENT content (from request)
    refined_content = request.content
    if request.prompt:
        try:
            # Use request.content (current edited content) as the base for refinement
            original_content = request.content if request.content else (slide.content or "")
            refined_content = refine_content(original_content, request.prompt, "slide")
        except Exception as e:
            logger.error(f"Error refining slide {slide_id}: {e}")
            # If refinement fails, use the manually edited content from request
            refined_content = request.content
    
    # Update slide content with refined or edited content
    slide.content = refined_content
    db.commit()
    db.refresh(slide)
    
    # Create refinement record
    refinement = models.Refinement(
        slide_id=slide_id,
        prompt=request.prompt,
        content=refined_content,
        feedback=request.feedback,
        comments=request.comments,
    )
    db.add(refinement)
    db.commit()
    db.refresh(refinement)
    
    return refinement


@router.get("/section/{section_id}/refinements", response_model=List[RefinementResponse])
async def get_section_refinements(
    section_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all refinements for a section"""
    section = db.query(models.Section).filter(
        models.Section.id == section_id
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == section.project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    refinements = db.query(models.Refinement).filter(
        models.Refinement.section_id == section_id
    ).order_by(models.Refinement.created_at.desc()).all()
    
    return refinements


@router.get("/slide/{slide_id}/refinements", response_model=List[RefinementResponse])
async def get_slide_refinements(
    slide_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all refinements for a slide"""
    slide = db.query(models.Slide).filter(
        models.Slide.id == slide_id
    ).first()
    
    if not slide:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slide not found"
        )
    
    # Verify project ownership
    project = db.query(models.Project).filter(
        models.Project.id == slide.project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    refinements = db.query(models.Refinement).filter(
        models.Refinement.slide_id == slide_id
    ).order_by(models.Refinement.created_at.desc()).all()
    
    return refinements


@router.post("/project/{project_id}/revision")
async def create_revision(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a revision snapshot of the project"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get current revision number
    last_revision = db.query(models.Revision).filter(
        models.Revision.project_id == project_id
    ).order_by(models.Revision.revision_number.desc()).first()
    
    revision_number = (last_revision.revision_number + 1) if last_revision else 1
    
    # Create snapshot
    content_snapshot = {}
    
    if project.project_type == "word":
        sections = db.query(models.Section).filter(
            models.Section.project_id == project_id
        ).order_by(models.Section.order_index).all()
        
        content_snapshot = {
            "type": "word",
            "sections": [
                {
                    "id": s.id,
                    "title": s.title,
                    "content": s.content,
                    "order_index": s.order_index,
                }
                for s in sections
            ]
        }
    elif project.project_type == "powerpoint":
        slides = db.query(models.Slide).filter(
            models.Slide.project_id == project_id
        ).order_by(models.Slide.order_index).all()
        
        content_snapshot = {
            "type": "powerpoint",
            "slides": [
                {
                    "id": s.id,
                    "title": s.title,
                    "content": s.content,
                    "order_index": s.order_index,
                }
                for s in slides
            ]
        }
    
    revision = models.Revision(
        project_id=project_id,
        revision_number=revision_number,
        content_snapshot=content_snapshot,
        created_by=current_user.username,
    )
    db.add(revision)
    db.commit()
    db.refresh(revision)
    
    return {
        "id": revision.id,
        "revision_number": revision.revision_number,
        "created_at": revision.created_at,
        "created_by": revision.created_by,
    }


@router.get("/project/{project_id}/revisions")
async def get_revisions(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all revisions for a project"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    revisions = db.query(models.Revision).filter(
        models.Revision.project_id == project_id
    ).order_by(models.Revision.revision_number.desc()).all()
    
    return [
        {
            "id": r.id,
            "revision_number": r.revision_number,
            "created_at": r.created_at,
            "created_by": r.created_by,
            "content_snapshot": r.content_snapshot,
        }
        for r in revisions
    ]

