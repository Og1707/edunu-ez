import React from 'react';
import { Outlet } from 'react-router-dom';
import useAuth from '../../hooks/useAuth';
import AppShell from './AppShell';
import StudentLayout from './StudentLayout';

export default function RoleBasedLayout() {
  const { user } = useAuth();

  if (user?.rol === 'estudiante') {
    return <StudentLayout />;
  }

  if (user?.rol === 'profesor' || user?.rol === 'administrador') {
    return <AppShell />;
  }

  return <Outlet />;
}
