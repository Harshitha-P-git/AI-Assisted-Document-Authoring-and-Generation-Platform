from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.db.database import get_db
from app.db import models
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


class WordConfigCreate(BaseModel):
    outline: List[str]
    context: Optional[str] = None


class WordConfigResponse(BaseModel):
    id: int
    project_id: int
    outline: List[str]
    context: Optional[str] = None
    
    class Config:
        from_attributes = True


class PPTConfigCreate(BaseModel):
    slide_titles: List[str]
    context: Optional[str] = None


class PPTConfigResponse(BaseModel):
    id: int
    project_id: int
    slide_titles: List[str]
    context: Optional[str] = None
    
    class Config:
        from_attributes = True


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


@router.post("/word/{project_id}/config", response_model=WordConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_word_config(
    project_id: int,
    config: WordConfigCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update Word document configuration"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    if project.project_type != "word":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not a Word project"
        )
    
    # Check if config exists
    existing_config = db.query(models.WordConfig).filter(
        models.WordConfig.project_id == project_id
    ).first()
    
    if existing_config:
        existing_config.outline = config.outline
        existing_config.context = config.context
        db.commit()
        db.refresh(existing_config)
        return existing_config
    
    # Create sections
    for idx, title in enumerate(config.outline):
        section = models.Section(
            project_id=project_id,
            title=title,
            order_index=idx,
            is_generated=False,
        )
        db.add(section)
    
    # Create config
    db_config = models.WordConfig(
        project_id=project_id,
        outline=config.outline,
        context=config.context,
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/word/{project_id}/config", response_model=WordConfigResponse)
async def get_word_config(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Word document configuration"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    config = db.query(models.WordConfig).filter(
        models.WordConfig.project_id == project_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Word configuration not found"
        )
    
    return config


@router.post("/powerpoint/{project_id}/config", response_model=PPTConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_ppt_config(
    project_id: int,
    config: PPTConfigCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update PowerPoint document configuration"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    if project.project_type != "powerpoint":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project is not a PowerPoint project"
        )
    
    # Check if config exists
    existing_config = db.query(models.PPTConfig).filter(
        models.PPTConfig.project_id == project_id
    ).first()
    
    if existing_config:
        existing_config.slide_titles = config.slide_titles
        existing_config.context = config.context
        db.commit()
        db.refresh(existing_config)
        return existing_config
    
    # Create slides
    for idx, title in enumerate(config.slide_titles):
        slide = models.Slide(
            project_id=project_id,
            title=title,
            order_index=idx,
            is_generated=False,
        )
        db.add(slide)
    
    # Create config
    db_config = models.PPTConfig(
        project_id=project_id,
        slide_titles=config.slide_titles,
        context=config.context,
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.get("/powerpoint/{project_id}/config", response_model=PPTConfigResponse)
async def get_ppt_config(
    project_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get PowerPoint document configuration"""
    project = verify_project_ownership(project_id, current_user.id, db)
    
    config = db.query(models.PPTConfig).filter(
        models.PPTConfig.project_id == project_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PowerPoint configuration not found"
        )
    
    return config

