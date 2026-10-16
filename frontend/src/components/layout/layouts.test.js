import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import AppShell from './AppShell';
import FocusLayout from './FocusLayout';
import ProtectedRoute from './ProtectedRoute';
import StudentLayout from './StudentLayout';

const setUser = (user) => {
  if (user) window.localStorage.setItem('user', JSON.stringify(user));
  else window.localStorage.removeItem('user');
};

beforeEach(() => {
  window.localStorage.clear();
});

describe('ProtectedRoute', () => {
  const renderProtectedRoute = (allowedRoles) => render(
    <MemoryRouter initialEntries={['/private']}>
      <Routes>
        <Route path="/login" element={<p>Página de inicio de sesión</p>} />
        <Route path="/dashboard" element={<p>Dashboard</p>} />
        <Route element={<ProtectedRoute allowedRoles={allowedRoles} />}>
          <Route path="/private" element={<p>Contenido protegido</p>} />
        </Route>
      </Routes>
    </MemoryRouter>
  );

  it('redirige al login cuando no hay sesión', () => {
    renderProtectedRoute(['administrador']);
    expect(screen.getByText('Página de inicio de sesión')).toBeInTheDocument();
  });

  it('redirige al dashboard si el rol no tiene acceso', () => {
    setUser({ rol: 'estudiante' });
    renderProtectedRoute(['administrador', 'profesor']);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('muestra la ruta para un rol autorizado', () => {
    setUser({ rol: 'administrador' });
    renderProtectedRoute(['administrador']);
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument();
  });
});

describe('role layouts', () => {
  it('muestra la navegación administrativa a administradores', () => {
    setUser({ rol: 'administrador', username: 'admin' });
    render(<MemoryRouter><AppShell /></MemoryRouter>);

    expect(screen.getByRole('link', { name: 'Usuarios' })).toBeInTheDocument();
    expect(screen.getByRole('navigation', { name: 'Navegación principal' })).toBeInTheDocument();
  });

  it('oculta Usuarios de la navegación del docente', () => {
    setUser({ rol: 'profesor', username: 'docente' });
    render(<MemoryRouter><AppShell /></MemoryRouter>);

    expect(screen.queryByRole('link', { name: 'Usuarios' })).not.toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Cursos' })).toBeInTheDocument();
  });

  it('muestra navegación de estudiante sin opciones administrativas', () => {
    setUser({ rol: 'estudiante', username: 'estudiante', puntos_xp: 120, nivel: 2 });
    render(<MemoryRouter><StudentLayout /></MemoryRouter>);

    expect(screen.getAllByRole('link', { name: 'Mis tareas' })).toHaveLength(2);
    expect(screen.queryByRole('link', { name: 'Cursos' })).not.toBeInTheDocument();
    expect(screen.getByText('120 XP')).toBeInTheDocument();
    expect(screen.getByText('Nivel 2')).toBeInTheDocument();
  });
});

describe('FocusLayout', () => {
  it('no muestra el menú lateral y pide confirmación antes de salir', () => {
    render(
      <MemoryRouter>
        <Routes>
          <Route path="*" element={<FocusLayout />} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.queryByRole('navigation')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Volver' }));
    expect(screen.getByRole('alertdialog')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Seguir aquí' })).toBeInTheDocument();
  });
});
