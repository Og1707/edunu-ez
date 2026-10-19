import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Dashboard from './Dashboard';
import { getStudentStats } from '../services/games.service';

jest.mock('../features/dashboard/DashboardStaff', () => function DashboardStaffMock() {
  return <main>Panel de personal</main>;
});
jest.mock('../services/games.service');

const renderDashboard = (rol) => {
  window.localStorage.setItem('user', JSON.stringify({ rol, username: 'usuario' }));
  return render(<MemoryRouter><Dashboard /></MemoryRouter>);
};

beforeEach(() => {
  window.localStorage.clear();
  getStudentStats.mockResolvedValue({ data: {
    actividades_completadas: 0,
    actividades_pendientes: 0,
    actividades_por_vencer: 0,
    puntuacion_promedio: 0,
    porcentaje_completado: 0,
  } });
});

afterEach(() => {
  window.localStorage.clear();
  jest.clearAllMocks();
});

describe('Dashboard por rol', () => {
  it('muestra el panel estudiantil y no monta el panel de personal', () => {
    renderDashboard('estudiante');

    expect(screen.getByRole('main')).toHaveClass('student-dashboard');
    expect(screen.queryByText('Panel de personal')).not.toBeInTheDocument();
    expect(getStudentStats).toHaveBeenCalledTimes(1);
  });

  it.each(['administrador', 'profesor'])('%s conserva el panel de personal', (rol) => {
    renderDashboard(rol);

    expect(screen.getByText('Panel de personal')).toBeInTheDocument();
    expect(screen.queryByRole('main', { name: /Tu espacio de aprendizaje/ })).not.toBeInTheDocument();
    expect(getStudentStats).not.toHaveBeenCalled();
  });
});
