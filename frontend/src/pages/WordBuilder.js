import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './Builder.css';

function WordBuilder() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [outline, setOutline] = useState(['']);
  const [context, setContext] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchConfig = useCallback(async () => {
    try {
      const response = await api.get(`/documents/word/${projectId}/config`);
      setOutline(response.data.outline || ['']);
      setContext(response.data.context || '');
    } catch (err) {
      // Config doesn't exist yet, that's okay
    }
  }, [projectId]);

  useEffect(() => {
    fetchConfig();
  }, [fetchConfig]);

  const handleAddSection = () => {
    setOutline([...outline, '']);
  };

  const handleRemoveSection = (index) => {
    if (outline.length > 1) {
      setOutline(outline.filter((_, i) => i !== index));
    }
  };

  const handleSectionChange = (index, value) => {
    const newOutline = [...outline];
    newOutline[index] = value;
    setOutline(newOutline);
  };

  const handleSave = async () => {
    setError('');
    setSaving(true);

    const filteredOutline = outline.filter(s => s.trim() !== '');

    if (filteredOutline.length === 0) {
      setError('Please add at least one section');
      setSaving(false);
      return;
    }

    try {
      await api.post(`/documents/word/${projectId}/config`, {
        outline: filteredOutline,
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
      <h1>Word Document Outline Builder</h1>
      <div className="builder-card">
        <div className="form-group">
          <label>Project Context (Optional)</label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Provide context about your document (e.g., target audience, purpose, tone)"
            rows="4"
          />
        </div>

        <div className="sections-container">
          <h3>Document Sections</h3>
          {outline.map((section, index) => (
            <div key={index} className="section-item">
              <input
                type="text"
                value={section}
                onChange={(e) => handleSectionChange(index, e.target.value)}
                placeholder={`Section ${index + 1} title`}
                className="section-input"
              />
              {outline.length > 1 && (
                <button
                  type="button"
                  onClick={() => handleRemoveSection(index)}
                  className="btn btn-danger btn-sm"
                >
                  Remove
                </button>
              )}
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddSection}
            className="btn btn-secondary"
          >
            + Add Section
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

export default WordBuilder;

