import React from 'react';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import DashboardStaff from './DashboardStaff';
import { getDashboardStudent, getDashboardSummary } from '../../services/dashboard.service';

jest.mock('../../services/dashboard.service');

const summary = {
  rol: 'profesor',
  kpis: { cursos: 1, estudiantes: 1, profesores: null, actividades: 1, promedio: 86, completadas: 1 },
  cursos: [{ id: 5, nombre: 'Ciencias 6A', descripcion: '', profesor_id: 2, profesor_nombre: 'Docente', total_estudiantes: 1, total_actividades: 1, asignaciones: 1, completadas: 1, promedio: 86, materia: null }],
  estudiantes: [{ id: 9, nombre: 'Ana Pérez', username: 'ana', cursos: ['Ciencias 6A'], actividades_completadas: 1, actividades_totales: 1, promedio: 86, tendencia: [80, 86] }],
  asignaturas: [],
  actividades: [{ id: 4, titulo: 'Quiz', curso: 'Ciencias 6A', estado: 'pendiente', asignaciones: 1, completadas: 1, promedio: 86 }],
};

beforeEach(() => {
  localStorage.setItem('user', JSON.stringify({ rol: 'profesor', username: 'docente', nombre_completo: 'Docente' }));
  getDashboardSummary.mockResolvedValue({ data: summary });
  getDashboardStudent.mockResolvedValue({ data: { id: 9, nombre: 'Ana Pérez', username: 'ana', cursos: ['Ciencias 6A'], promedio: 86, historial: [] } });
});

afterEach(() => { localStorage.clear(); jest.clearAllMocks(); });

describe('DashboardStaff', () => {
  it('presenta las métricas y vistas del profesor', async () => {
    render(<DashboardStaff/>);
    expect((await screen.findAllByText('Ciencias 6A')).length).toBeGreaterThan(0);
    expect(screen.getByText('Inscritos en tus cursos')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Actividades' }));
    expect(screen.getByText('Quiz')).toBeInTheDocument();
  });

  it('abre el perfil de un estudiante desde su fila', async () => {
    render(<DashboardStaff/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Ver perfil' }));
    await waitFor(() => expect(getDashboardStudent).toHaveBeenCalledWith(9));
    expect(await screen.findByRole('complementary', { name: 'Perfil del estudiante' })).toBeInTheDocument();
    expect(screen.getAllByText('Ana Pérez').length).toBeGreaterThan(0);
  });

  it('aplica is-closing al panel inmediatamente al cerrarlo y lo desmonta tras la animación', async () => {
    jest.useFakeTimers();
    render(<DashboardStaff/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Ver perfil' }));
    const profile = await screen.findByRole('complementary', { name: 'Perfil del estudiante' });
    expect(profile).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Cerrar perfil' }));
    // Class should be applied synchronously
    expect(profile).toHaveClass('is-closing');

    // Advance timers to let the animation timer fire and unmount the panel
    jest.runAllTimers();
    await waitFor(() => {
      expect(screen.queryByRole('complementary', { name: 'Perfil del estudiante' })).not.toBeInTheDocument();
    });
    jest.useRealTimers();
  });

  it('permite imprimir el reporte', async () => {
    const print = jest.spyOn(window, 'print').mockImplementation(() => {});
    render(<DashboardStaff/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Imprimir' }));
    expect(print).toHaveBeenCalledTimes(1);
    print.mockRestore();
  });
});
