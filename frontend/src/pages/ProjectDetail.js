import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import './ProjectDetail.css';

function ProjectDetail() {
  const { projectId } = useParams();
  const [project, setProject] = useState(null);
  const [sections, setSections] = useState([]);
  const [slides, setSlides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const fetchProject = useCallback(async () => {
    try {
      const response = await api.get(`/projects/${projectId}`);
      setProject(response.data);
    } catch (err) {
      setError('Failed to load project');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  const fetchContent = useCallback(async () => {
    // Don't fetch content if project is not loaded yet
    if (!project) {
      return;
    }

    try {
      if (project.project_type === 'word') {
        const response = await api.get(`/generation/project/${projectId}/sections`);
        setSections(response.data || []);
      } else if (project.project_type === 'powerpoint') {
        const response = await api.get(`/generation/project/${projectId}/slides`);
        setSlides(response.data || []);
      }
    } catch (err) {
      // Content might not exist yet - this is normal for new projects
      // Only log if it's not a 404 or 400 (expected errors)
      if (err.response?.status !== 404 && err.response?.status !== 400) {
        console.warn('Failed to fetch content:', err.response?.status);
      }
    }
  }, [projectId, project]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  useEffect(() => {
    // Only fetch content after project is loaded
    if (project) {
      fetchContent();
    }
  }, [project, fetchContent]);

  const handleGenerate = async () => {
    setError('');
    setGenerating(true);

    try {
      await api.post(`/generation/project/${projectId}/generate`, {
        generate_all: true,
      });
      await fetchContent();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate content');
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async () => {
    try {
      const endpoint = project.project_type === 'word'
        ? `/export/project/${projectId}/word`
        : `/export/project/${projectId}/powerpoint`;
      
      const response = await api.get(endpoint, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${project.name}.${project.project_type === 'word' ? 'docx' : 'pptx'}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      setError('Failed to export document');
    }
  };

  if (loading) {
    return (
      <div className="container main-content">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading project...</p>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container main-content">
        <div className="error-message">Project not found</div>
      </div>
    );
  }

  return (
    <div className="container main-content">
      <div className="project-header">
        <div>
          <h1>{project.name}</h1>
          {project.description && <p className="project-description">{project.description}</p>}
        </div>
        <div className="project-header-actions">
          <button onClick={handleExport} className="btn btn-success">
            Export {project.project_type === 'word' ? 'Word' : 'PowerPoint'}
          </button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="content-actions">
        <button
          onClick={handleGenerate}
          className="btn btn-primary"
          disabled={generating}
        >
          {generating ? 'Generating...' : 'Generate All Content'}
        </button>
      </div>

      {project.project_type === 'word' ? (
        <div className="sections-list">
          {sections.length === 0 ? (
            <div className="empty-state">
              <p>No sections yet. Configure your document outline first.</p>
              <Link
                to={`/projects/${projectId}/word-builder`}
                className="btn btn-primary"
              >
                Configure Outline
              </Link>
            </div>
          ) : (
            sections.map((section) => (
              <div key={section.id} className="content-item">
                <h3>{section.title}</h3>
                {section.is_generated ? (
                  <>
                    <div className="content-preview">
                      {section.content ? (
                        <p>{section.content.substring(0, 200)}...</p>
                      ) : (
                        <p>No content generated yet</p>
                      )}
                    </div>
                    <Link
                      to={`/projects/${projectId}/refine/section/${section.id}`}
                      className="btn btn-primary btn-sm"
                    >
                      Refine
                    </Link>
                  </>
                ) : (
                  <p className="not-generated">Not generated yet</p>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="slides-list">
          {slides.length === 0 ? (
            <div className="empty-state">
              <p>No slides yet. Configure your slide titles first.</p>
              <Link
                to={`/projects/${projectId}/ppt-builder`}
                className="btn btn-primary"
              >
                Configure Slides
              </Link>
            </div>
          ) : (
            slides.map((slide) => (
              <div key={slide.id} className="content-item">
                <h3>{slide.title}</h3>
                {slide.is_generated ? (
                  <>
                    <div className="content-preview">
                      {slide.content ? (
                        <p>{slide.content.substring(0, 200)}...</p>
                      ) : (
                        <p>No content generated yet</p>
                      )}
                    </div>
                    <Link
                      to={`/projects/${projectId}/refine/slide/${slide.id}`}
                      className="btn btn-primary btn-sm"
                    >
                      Refine
                    </Link>
                  </>
                ) : (
                  <p className="not-generated">Not generated yet</p>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default ProjectDetail;

