import React from 'react';
import useAuth from '../hooks/useAuth';
import DashboardStaff from '../features/dashboard/DashboardStaff';
import StudentDashboard from '../features/student-dashboard/StudentDashboard';

export default function Dashboard() {
  const { user } = useAuth();
  if (user?.rol === 'administrador' || user?.rol === 'profesor') return <DashboardStaff />;
  return <StudentDashboard user={user} />;
}
