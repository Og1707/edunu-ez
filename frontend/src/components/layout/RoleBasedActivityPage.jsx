import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import StudentActivities from '../../features/activities/StudentActivities';
import ActivityManagement from '../../features/activities/ActivityManagement';
import AddActivity from '../../features/activities/AddActivity';

export default function RoleBasedActivityPage() {
  const { user } = useAuth();
  const [showAddActivity, setShowAddActivity] = useState(false);
  const closeActivityBuilder = () => setShowAddActivity(false);

  if (user?.rol === 'estudiante') return <StudentActivities user={user} />;
  if (user?.rol === 'profesor' || user?.rol === 'administrador') {
    return (
      <>
        <ActivityManagement user={user} onAddActivity={() => setShowAddActivity(true)} />
        {showAddActivity && <AddActivity onClose={closeActivityBuilder} onActivityAdded={closeActivityBuilder} />}
      </>
    );
  }
  return <Navigate to="/dashboard" replace />;
}
