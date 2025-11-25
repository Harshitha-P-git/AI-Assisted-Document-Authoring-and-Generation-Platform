import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './RefinementEditor.css';

function RefinementEditor() {
  const { projectId, type, id } = useParams();
  const navigate = useNavigate();
  const [content, setContent] = useState('');
  const [prompt, setPrompt] = useState('');
  const [feedback, setFeedback] = useState('');
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [refining, setRefining] = useState(false);
  const [error, setError] = useState('');
  const [refinements, setRefinements] = useState([]);
  const [revisions, setRevisions] = useState([]);
  const [showRevisions, setShowRevisions] = useState(false);

  const fetchContent = useCallback(async () => {
    try {
      const endpoint = type === 'section'
        ? `/generation/project/${projectId}/sections`
        : `/generation/project/${projectId}/slides`;
      
      const response = await api.get(endpoint);
      const item = response.data.find(item => item.id === parseInt(id));
      
      if (item) {
        setContent(item.content || '');
      }
    } catch (err) {
      setError('Failed to load content');
    } finally {
      setLoading(false);
    }
  }, [projectId, type, id]);

  const fetchRefinements = useCallback(async () => {
    try {
      const endpoint = type === 'section'
        ? `/refinement/section/${id}/refinements`
        : `/refinement/slide/${id}/refinements`;
      
      const response = await api.get(endpoint);
      setRefinements(response.data);
    } catch (err) {
      // Refinements might not exist yet
    }
  }, [type, id]);

  const fetchRevisions = useCallback(async () => {
    try {
      const response = await api.get(`/refinement/project/${projectId}/revisions`);
      setRevisions(response.data);
    } catch (err) {
      // Revisions might not exist yet
    }
  }, [projectId]);

  useEffect(() => {
    fetchContent();
    fetchRefinements();
    fetchRevisions();
  }, [fetchContent, fetchRefinements, fetchRevisions]);

  const handleRefine = async () => {
    if (!prompt.trim()) {
      setError('Please enter a refinement prompt');
      return;
    }

    setError('');
    setRefining(true);

    try {
      const endpoint = type === 'section'
        ? `/refinement/section/${id}/refine`
        : `/refinement/slide/${id}/refine`;
      
      const response = await api.post(endpoint, {
        prompt: prompt,
        content: content,
        feedback: feedback || null,
        comments: comments || null,
      });

      setContent(response.data.content);
      setPrompt('');
      await fetchRefinements();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to refine content');
    } finally {
      setRefining(false);
    }
  };

  const handleSave = async () => {
    setError('');
    setSaving(true);

    try {
      const endpoint = type === 'section'
        ? `/refinement/section/${id}/refine`
        : `/refinement/slide/${id}/refine`;
      
      await api.post(endpoint, {
        content: content,
        feedback: feedback || null,
        comments: comments || null,
      });

      await fetchRefinements();
      navigate(`/projects/${projectId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateRevision = async () => {
    try {
      await api.post(`/refinement/project/${projectId}/revision`);
      await fetchRevisions();
      alert('Revision created successfully');
    } catch (err) {
      setError('Failed to create revision');
    }
  };

  if (loading) {
    return (
      <div className="container main-content">
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container main-content">
      <div className="refinement-header">
        <h1>Refine {type === 'section' ? 'Section' : 'Slide'}</h1>
        <button
          onClick={() => navigate(`/projects/${projectId}`)}
          className="btn btn-secondary"
        >
          Back to Project
        </button>
      </div>

      <div className="refinement-container">
        <div className="refinement-main">
          <div className="form-group">
            <label>Content</label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              rows="15"
              className="content-editor"
            />
          </div>

          <div className="form-group">
            <label>Refinement Prompt (Optional)</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe how you want to refine this content..."
              rows="3"
            />
            <button
              onClick={handleRefine}
              className="btn btn-primary"
              disabled={refining || !prompt.trim()}
            >
              {refining ? 'Refining...' : 'Apply AI Refinement'}
            </button>
          </div>

          <div className="form-group">
            <label>Feedback</label>
            <select
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            >
              <option value="">None</option>
              <option value="like">Like</option>
              <option value="dislike">Dislike</option>
            </select>
          </div>

          <div className="form-group">
            <label>Comments (Optional)</label>
            <textarea
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Add any comments or notes..."
              rows="3"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="refinement-actions">
            <button
              onClick={handleSave}
              className="btn btn-success"
              disabled={saving}
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
            <button
              onClick={handleCreateRevision}
              className="btn btn-secondary"
            >
              Create Revision
            </button>
          </div>
        </div>

        <div className="refinement-sidebar">
          <div className="sidebar-section">
            <h3>Refinement History</h3>
            {refinements.length === 0 ? (
              <p className="empty-text">No refinements yet</p>
            ) : (
              <div className="refinements-list">
                {refinements.map((refinement) => (
                  <div key={refinement.id} className="refinement-item">
                    <p className="refinement-date">
                      {new Date(refinement.created_at).toLocaleString()}
                    </p>
                    {refinement.prompt && (
                      <p className="refinement-prompt">
                        <strong>Prompt:</strong> {refinement.prompt}
                      </p>
                    )}
                    {refinement.feedback && (
                      <p className="refinement-feedback">
                        <strong>Feedback:</strong> {refinement.feedback}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="sidebar-section">
            <h3>
              Revisions
              <button
                onClick={() => setShowRevisions(!showRevisions)}
                className="btn-toggle"
              >
                {showRevisions ? 'Hide' : 'Show'}
              </button>
            </h3>
            {showRevisions && (
              <div className="revisions-list">
                {revisions.length === 0 ? (
                  <p className="empty-text">No revisions yet</p>
                ) : (
                  revisions.map((revision) => (
                    <div key={revision.id} className="revision-item">
                      <p>
                        <strong>Revision {revision.revision_number}</strong>
                      </p>
                      <p className="revision-date">
                        {new Date(revision.created_at).toLocaleString()}
                      </p>
                      <p className="revision-author">
                        by {revision.created_by}
                      </p>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default RefinementEditor;

