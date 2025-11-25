import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import CreateProject from './pages/CreateProject';
import ProjectDetail from './pages/ProjectDetail';
import WordBuilder from './pages/WordBuilder';
import PPTBuilder from './pages/PPTBuilder';
import RefinementEditor from './pages/RefinementEditor';
import Navbar from './components/Navbar';
import './App.css';

function PrivateRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/projects/create"
            element={
              <PrivateRoute>
                <CreateProject />
              </PrivateRoute>
            }
          />
          <Route
            path="/projects/:projectId"
            element={
              <PrivateRoute>
                <ProjectDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/projects/:projectId/word-builder"
            element={
              <PrivateRoute>
                <WordBuilder />
              </PrivateRoute>
            }
          />
          <Route
            path="/projects/:projectId/ppt-builder"
            element={
              <PrivateRoute>
                <PPTBuilder />
              </PrivateRoute>
            }
          />
          <Route
            path="/projects/:projectId/refine/:type/:id"
            element={
              <PrivateRoute>
                <RefinementEditor />
              </PrivateRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

