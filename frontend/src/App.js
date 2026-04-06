import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home.jsx';
import Register from './pages/Register.jsx';
import Login from './pages/Login.jsx';
import Dashboard from './pages/Dashboard.jsx';
import CourseManagement from './features/courses/CourseManagement.jsx';
import ActivityManagement from './features/activities/ActivityManagement.jsx';
import UserManagement from './features/users/UserManagement.jsx';
import GameExplorer from './features/games/GameExplorer.jsx';
import MagicLink from './pages/MagicLink.jsx';
import VerifyMagicLink from './pages/VerifyMagicLink.jsx';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
          <Route path="/login" element={<Login />} />
          <Route path="/magic-link" element={<MagicLink />} />
          <Route path="/verify" element={<VerifyMagicLink />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/courses" element={<CourseManagement />} />
          <Route path="/activities" element={<ActivityManagement />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/games" element={<GameExplorer />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
