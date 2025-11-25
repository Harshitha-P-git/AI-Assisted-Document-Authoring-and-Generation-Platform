import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './Builder.css';

function PPTBuilder() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [slideTitles, setSlideTitles] = useState(['']);
  const [context, setContext] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      const response = await api.get(`/documents/powerpoint/${projectId}/config`);
      setSlideTitles(response.data.slide_titles || ['']);
      setContext(response.data.context || '');
    } catch (err) {
      // Config doesn't exist yet, that's okay
    }
  }, [projectId]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const handleAddSlide = () => {
    setSlideTitles([...slideTitles, '']);
  };

  const handleRemoveSlide = (index) => {
    if (slideTitles.length > 1) {
      setSlideTitles(slideTitles.filter((_, i) => i !== index));
    }
  };

  const handleSlideChange = (index, value) => {
    const newTitles = [...slideTitles];
    newTitles[index] = value;
    setSlideTitles(newTitles);
  };

  const handleSave = async () => {
    setError('');
    setSaving(true);

    const filteredTitles = slideTitles.filter(s => s.trim() !== '');

    if (filteredTitles.length === 0) {
      setError('Please add at least one slide');
      setSaving(false);
      return;
    }

    try {
      await api.post(`/documents/powerpoint/${projectId}/config`, {
        slide_titles: filteredTitles,
        context: context,
      });
      navigate(`/projects/${projectId}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container main-content">
      <h1>PowerPoint Slide Title Builder</h1>
      <div className="builder-card">
        <div className="form-group">
          <label>Presentation Context (Optional)</label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Provide context about your presentation (e.g., audience, purpose, tone)"
            rows="4"
          />
        </div>

        <div className="sections-container">
          <h3>Slide Titles</h3>
          {slideTitles.map((title, index) => (
            <div key={index} className="section-item">
              <input
                type="text"
                value={title}
                onChange={(e) => handleSlideChange(index, e.target.value)}
                placeholder={`Slide ${index + 1} title`}
                className="section-input"
              />
              {slideTitles.length > 1 && (
                <button
                  type="button"
                  onClick={() => handleRemoveSlide(index)}
                  className="btn btn-danger btn-sm"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddSlide}
            className="btn btn-secondary"
          >
            + Add Slide
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        <div className="builder-actions">
          <button
            onClick={() => navigate(`/projects/${projectId}`)}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="btn btn-primary"
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save & Continue'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default PPTBuilder;

