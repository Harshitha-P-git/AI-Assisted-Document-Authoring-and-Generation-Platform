from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db.database import get_db
from app.db import models
from app.api.v1.endpoints.auth import get_current_user
# Lazy import to avoid Python 3.14 compatibility issues
# from app.services.llm_service import generate_section_content, generate_slide_content
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerationRequest(BaseModel):
    section_ids: List[int] = None  # For Word projects
    slide_ids: List[int] = None  # For PPT projects
    generate_all: bool = False


class GenerationResponse(BaseModel):
    message: str
    generated_count: int


def verify_project_ownership(project_id: int, user_id: int, db: Session) -> models.Project:
    """Verify project ownership"""
    project = db.query(models.Project).filter(
        models.Project.id == project_id,
        models.Project.owner_id == user_id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


async def generate_sections_for_project(project_id: int, db: Session):
    """Background task to generate all sections"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return
    
    word_config = db.query(models.WordConfig).filter(
        models.WordConfig.project_id == project_id
    ).first()
    
    if not word_config:
        return
    
    sections = db.query(models.Section).filter(
        models.Section.project_id == project_id
    ).order_by(models.Section.order_index).all()
    
    previous_sections = []
    for section in sections:
        try:
            from app.services.llm_service import generate_section_content
            content = generate_section_content(
                section.title,
                word_config.context,
                previous_sections
            )
            section.content = content
            section.is_generated = True
            previous_sections.append(section.title)
            db.commit()
        except Exception as e:
            logger.error(f"Error generating content for section {section.id}: {e}")
            db.rollback()


async def generate_slides_for_project(project_id: int, db: Session):
    """Background task to generate all slides"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return
    
    ppt_config = db.query(models.PPTConfig).filter(
        models.PPTConfig.project_id == project_id
    ).first()
    
    if not ppt_config:
        return
    
    slides = db.query(models.Slide).filter(
        models.Slide.project_id == project_id
    ).order_by(models.Slide.order_index).all()
    
    previous_slides = []
    for slide in slides:
        try:
            from app.services.llm_service import generate_slide_content
            content = generate_slide_content(
                slide.title,
                ppt_config.context,
                previous_slides
            )
            slide.content = content
            slide.is_generated = True
            previous_slides.append(slide.title)
            db.commit()
        except Exception as e:
            logger.error(f"Error generating content for slide {slide.id}: {e}")
            db.rollback()


@router.post("/project/{project_id}/generate", response_model=GenerationResponse)
async def generate_content(
    project_id: int,
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate AI content for sections or slides"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    generated_count = 0
    
    if project.project_type == "word":
        if request.generate_all:
            # Generate all sections
            sections = db.query(models.Section).filter(
                models.Section.project_id == project_id
            ).order_by(models.Section.order_index).all()
            
            word_config = db.query(models.WordConfig).filter(
                models.WordConfig.project_id == project_id
            ).first()
            
            previous_sections = []
            for section in sections:
                try:
                    from app.services.llm_service import generate_section_content
                    content = generate_section_content(
                        section.title,
                        word_config.context if word_config else None,
                        previous_sections
                    )
                    section.content = content
                    section.is_generated = True
                    previous_sections.append(section.title)
                    generated_count += 1
                except Exception as e:
                    logger.error(f"Error generating content for section {section.id}: {e}")
            
            db.commit()
        elif request.section_ids:
            # Generate specific sections
            sections = db.query(models.Section).filter(
                models.Section.id.in_(request.section_ids),
                models.Section.project_id == project_id
            ).all()
            
            word_config = db.query(models.WordConfig).filter(
                models.WordConfig.project_id == project_id
            ).first()
            
            all_sections = db.query(models.Section).filter(
                models.Section.project_id == project_id
            ).order_by(models.Section.order_index).all()
            
            previous_sections = [s.title for s in all_sections if s.order_index < min(s.order_index for s in sections)]
            
            for section in sections:
                try:
                    from app.services.llm_service import generate_section_content
                    content = generate_section_content(
                        section.title,
                        word_config.context if word_config else None,
                        previous_sections
                    )
                    section.content = content
                    section.is_generated = True
                    previous_sections.append(section.title)
                    generated_count += 1
                except Exception as e:
                    logger.error(f"Error generating content for section {section.id}: {e}")
            
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either generate_all or section_ids must be provided"
            )
    
    elif project.project_type == "powerpoint":
        if request.generate_all:
            # Generate all slides
            slides = db.query(models.Slide).filter(
                models.Slide.project_id == project_id
            ).order_by(models.Slide.order_index).all()
            
            ppt_config = db.query(models.PPTConfig).filter(
                models.PPTConfig.project_id == project_id
            ).first()
            
            previous_slides = []
            for slide in slides:
                try:
                    from app.services.llm_service import generate_slide_content
                    content = generate_slide_content(
                        slide.title,
                        ppt_config.context if ppt_config else None,
                        previous_slides
                    )
                    slide.content = content
                    slide.is_generated = True
                    previous_slides.append(slide.title)
                    generated_count += 1
                except Exception as e:
                    logger.error(f"Error generating content for slide {slide.id}: {e}")
            
            db.commit()
        elif request.slide_ids:
            # Generate specific slides
            slides = db.query(models.Slide).filter(
                models.Slide.id.in_(request.slide_ids),
                models.Slide.project_id == project_id
            ).all()
            
            ppt_config = db.query(models.PPTConfig).filter(
                models.PPTConfig.project_id == project_id
            ).first()
            
            all_slides = db.query(models.Slide).filter(
                models.Slide.project_id == project_id
            ).order_by(models.Slide.order_index).all()
            
            previous_slides = [s.title for s in all_slides if s.order_index < min(s.order_index for s in slides)]
            
            for slide in slides:
                try:
                    from app.services.llm_service import generate_slide_content
                    content = generate_slide_content(
                        slide.title,
                        ppt_config.context if ppt_config else None,
                        previous_slides
                    )
                    slide.content = content
                    slide.is_generated = True
                    previous_slides.append(slide.title)
                    generated_count += 1
                except Exception as e:
                    logger.error(f"Error generating content for slide {slide.id}: {e}")
            
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either generate_all or slide_ids must be provided"
            )
    
    return GenerationResponse(
        message=f"Successfully generated {generated_count} items",
        generated_count=generated_count
    )


@router.get("/project/{project_id}/sections")
async def get_sections(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all sections for a Word project"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    if project.project_type != "word":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not a Word project"
        )
    
    sections = db.query(models.Section).filter(
        models.Section.project_id == project_id
    ).order_by(models.Section.order_index).all()
    
    return [
        {
            "id": s.id,
            "title": s.title,
            "content": s.content,
            "order_index": s.order_index,
            "is_generated": s.is_generated,
        }
        for s in sections
    ]


@router.get("/project/{project_id}/slides")
async def get_slides(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all slides for a PowerPoint project"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    if project.project_type != "powerpoint":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not a PowerPoint project"
        )
    
    slides = db.query(models.Slide).filter(
        models.Slide.project_id == project_id
    ).order_by(models.Slide.order_index).all()
    
    return [
        {
            "id": s.id,
            "title": s.title,
            "content": s.content,
            "order_index": s.order_index,
            "is_generated": s.is_generated,
        }
        for s in slides
    ]

