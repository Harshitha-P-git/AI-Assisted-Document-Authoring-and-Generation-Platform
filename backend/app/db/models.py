from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(String, nullable=False)  # "word" or "powerpoint"
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="projects")
    word_config = relationship("WordConfig", back_populates="project", uselist=False, cascade="all, delete-orphan")
    ppt_config = relationship("PPTConfig", back_populates="project", uselist=False, cascade="all, delete-orphan")
    sections = relationship("Section", back_populates="project", cascade="all, delete-orphan", order_by="Section.order_index")
    slides = relationship("Slide", back_populates="project", cascade="all, delete-orphan", order_by="Slide.order_index")
    revisions = relationship("Revision", back_populates="project", cascade="all, delete-orphan", order_by="Revision.created_at.desc()")


class WordConfig(Base):
    __tablename__ = "word_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    outline = Column(JSON, nullable=False)  # List of section titles
    context = Column(Text, nullable=True)  # Additional context for generation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="word_config")


class PPTConfig(Base):
    __tablename__ = "ppt_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), unique=True, nullable=False)
    slide_titles = Column(JSON, nullable=False)  # List of slide titles
    context = Column(Text, nullable=True)  # Additional context for generation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="ppt_config")


class Section(Base):
    __tablename__ = "sections"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="sections")
    refinements = relationship("Refinement", back_populates="section", cascade="all, delete-orphan")


class Slide(Base):
    __tablename__ = "slides"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False)
    is_generated = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    project = relationship("Project", back_populates="slides")
    refinements = relationship("Refinement", back_populates="slide", cascade="all, delete-orphan")


class Refinement(Base):
    __tablename__ = "refinements"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=True)
    slide_id = Column(Integer, ForeignKey("slides.id"), nullable=True)
    prompt = Column(Text, nullable=True)  # User's refinement prompt
    content = Column(Text, nullable=False)  # Refined content
    feedback = Column(String, nullable=True)  # "like" or "dislike"
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    section = relationship("Section", back_populates="refinements")
    slide = relationship("Slide", back_populates="refinements")


class Revision(Base):
    __tablename__ = "revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    content_snapshot = Column(JSON, nullable=False)  # Full snapshot of all sections/slides
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String, nullable=True)  # User identifier
    
    project = relationship("Project", back_populates="revisions")

