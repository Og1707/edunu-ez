import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import StudentDashboard from './StudentDashboard';
import { getStudentStats } from '../../services/games.service';

jest.mock('../../services/games.service');

const stats = {
  actividades_completadas: 8,
  actividades_pendientes: 3,
  actividades_por_vencer: 1,
  puntuacion_promedio: 84,
  porcentaje_completado: 73.5,
};

beforeEach(() => {
  getStudentStats.mockResolvedValue({ data: stats });
});

afterEach(() => jest.clearAllMocks());

const renderDashboard = () => render(
  <MemoryRouter>
    <StudentDashboard user={{ nombre_completo: 'Ana Pérez' }} />
  </MemoryRouter>,
);

describe('StudentDashboard', () => {
  it('muestra bienvenida, estadísticas reales y accesos del estudiante', async () => {
    renderDashboard();

    expect(screen.getByRole('heading', { name: '¡Hola, Ana Pérez!' })).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(await screen.findByText('Actividades completadas')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('84%')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Mis actividades/ })).toHaveAttribute('href', '/activities');
    expect(screen.getByRole('link', { name: /Explorar juegos/ })).toHaveAttribute('href', '/games');
    expect(screen.getByRole('link', { name: /Mi progreso/ })).toHaveAttribute('href', '/progress');
    expect(getStudentStats).toHaveBeenCalledTimes(1);
  });

  it('presenta un error accesible cuando falla la carga', async () => {
    getStudentStats.mockRejectedValueOnce(new Error('offline'));
    renderDashboard();

    expect(await screen.findByRole('alert')).toHaveTextContent('No fue posible cargar tus estadísticas.');
    await waitFor(() => expect(screen.queryByRole('status')).not.toBeInTheDocument());
  });
});
