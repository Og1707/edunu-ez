import React from 'react';
import { render, screen } from '@testing-library/react';
import StudentProgressPage from './StudentProgressPage';
import { getStudentActivities, getStudentStats } from '../services/games.service';

jest.mock('../services/games.service');

beforeEach(() => {
  getStudentActivities.mockResolvedValue({ data: [{
    asignacion_id: 12,
    titulo: 'Lectura comprensiva',
    curso_nombre: 'A1',
    estado: 'completada',
    progreso: {
      completada: true,
      estado: 'completada',
      fecha_completado: '2026-06-15T10:00:00Z',
      puntuacion: 90,
    },
  }] });
  getStudentStats.mockResolvedValue({ data: {
    actividades_completadas: 1,
    actividades_pendientes: 2,
    actividades_por_vencer: 1,
    puntuacion_promedio: 90,
    porcentaje_completado: 33.33,
  } });
});

afterEach(() => jest.clearAllMocks());

describe('StudentProgressPage', () => {
  it('conserva el progreso y elimina cualquier indicador XP/Nivel', async () => {
    render(<StudentProgressPage />);

    expect(await screen.findByText('Lectura comprensiva')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Mi progreso' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Actividad' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Logros' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Historial' })).toBeInTheDocument();
    expect(screen.getByText('Actividades completadas')).toBeInTheDocument();
    expect(screen.getByText('Racha activa')).toBeInTheDocument();
    expect(screen.queryByText(/XP|Nivel/)).not.toBeInTheDocument();
    expect(getStudentActivities).toHaveBeenCalledTimes(1);
    expect(getStudentStats).toHaveBeenCalledTimes(1);
  });
});
