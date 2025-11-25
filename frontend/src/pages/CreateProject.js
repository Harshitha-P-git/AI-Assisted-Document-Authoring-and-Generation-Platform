import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './CreateProject.css';

function CreateProject() {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    project_type: 'word',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/projects', formData);
      const projectId = response.data.id;
      
      // Navigate to appropriate builder
      if (formData.project_type === 'word') {
        navigate(`/projects/${projectId}/word-builder`);
      } else {
        navigate(`/projects/${projectId}/ppt-builder`);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container main-content">
      <h1>Create New Project</h1>
      <div className="create-project-card">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name">Project Name</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              placeholder="e.g., Annual Report 2024"
            />
          </div>
          <div className="form-group">
            <label htmlFor="description">Description (Optional)</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Brief description of your project"
            />
          </div>
          <div className="form-group">
            <label htmlFor="project_type">Document Type</label>
            <select
              id="project_type"
              name="project_type"
              value={formData.project_type}
              onChange={handleChange}
              required
            >
              <option value="word">Word Document</option>
              <option value="powerpoint">PowerPoint Presentation</option>
            </select>
          </div>
          {error && <div className="error-message">{error}</div>}
          <div className="form-actions">
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateProject;

