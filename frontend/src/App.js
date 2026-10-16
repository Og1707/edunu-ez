import React from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom';
import CourseManagement from './features/courses/CourseManagement';
import GameExplorer from './features/games/GameExplorer';
import UserManagement from './features/users/UserManagement';
import RoleBasedActivityPage from './components/layout/RoleBasedActivityPage';
import ProtectedRoute from './components/layout/ProtectedRoute';
import RoleBasedLayout from './components/layout/RoleBasedLayout';
import Dashboard from './pages/Dashboard';
import StudentProgressPage from './pages/StudentProgressPage';
import ActivityBuilderPage from './pages/ActivityBuilderPage';
import ActivityPlayerPage from './pages/ActivityPlayerPage';
import GamePlayerPage from './pages/GamePlayerPage';
import FocusLayout from './components/layout/FocusLayout';
import Home from './pages/Home';
import Login from './pages/Login';
import MagicLink from './pages/MagicLink';
import Register from './pages/Register';
import VerifyMagicLink from './pages/VerifyMagicLink';
import useAuth from './hooks/useAuth';

const ALL_ROLES = ['administrador', 'profesor', 'estudiante'];
const STAFF_ROLES = ['administrador', 'profesor'];

function UserManagementPage() {
  const { user } = useAuth();
  return <UserManagement user={user} />;
}

function CourseManagementPage() {
  const { user } = useAuth();
  return <CourseManagement user={user} />;
}

function GameExplorerPage() { return <GameExplorer />; }

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

          <Route element={<ProtectedRoute allowedRoles={STAFF_ROLES} />}>
            <Route path="/activities/create" element={<ActivityBuilderPage />} />
          </Route>
          <Route element={<ProtectedRoute allowedRoles={['estudiante']}><FocusLayout /></ProtectedRoute>}>
            <Route path="/activities/:id/play" element={<ActivityPlayerPage />} />
            <Route path="/games/:id/play" element={<GamePlayerPage />} />
          </Route>

          <Route element={<ProtectedRoute allowedRoles={ALL_ROLES}><RoleBasedLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/activities" element={<RoleBasedActivityPage />} />
            <Route path="/games" element={<GameExplorerPage />} />

            <Route element={<ProtectedRoute allowedRoles={['estudiante']} />}>
              <Route path="/progress" element={<StudentProgressPage />} />
            </Route>

            <Route element={<ProtectedRoute allowedRoles={STAFF_ROLES} />}>
              <Route path="/courses" element={<CourseManagementPage />} />
              <Route path="/users" element={<UserManagementPage />} />
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
