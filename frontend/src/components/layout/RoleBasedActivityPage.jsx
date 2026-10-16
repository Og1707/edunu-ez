import React from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import StudentActivities from '../../features/activities/StudentActivities';
import ActivityManagement from '../../features/activities/ActivityManagement';

export default function RoleBasedActivityPage() {
  const { user } = useAuth();

  if (user?.rol === 'estudiante') return <StudentActivities user={user} />;
  if (user?.rol === 'profesor' || user?.rol === 'administrador') {
    return <ActivityManagement user={user} />;
  }
  return <Navigate to="/dashboard" replace />;
}
