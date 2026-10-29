import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import StudentProfile from './StudentProfile';
import { BLUE_MATEMATICAS } from './subjectColors';

const mockStudent = {
  id: 14,
  nombre: 'María González',
  username: 'mgonzalez',
  cursos: ['10° A'],
  promedio: 87.0,
  materias: [
    { id: 1, nombre: 'Lenguaje', promedio: 92.0, total_actividades: 10, actividades_completadas: 8 },
    { id: 2, nombre: 'Matemáticas', promedio: 91.0, total_actividades: 12, actividades_completadas: 10 },
    { id: 3, nombre: 'Ciencias Naturales', promedio: 84.0, total_actividades: 5, actividades_completadas: 4 },
    { id: 4, nombre: 'Inglés', promedio: null, total_actividades: 2, actividades_completadas: 0 },
  ],
  historial: [
    { id: 101, actividad: 'Álgebra básica', curso: '10° A', estado: 'calificada', calificacion: 91.0, fecha: '2026-03-01T10:00:00' },
  ],
};

describe('StudentProfile Component', () => {
  it('renderiza la cabecera con el avatar de iniciales y los datos del estudiante', () => {
    render(<StudentProfile student={mockStudent} loading={false} onClose={jest.fn()} />);

    expect(screen.getByText('MG')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'María González' })).toBeInTheDocument();
    expect(screen.getByText('10° A')).toBeInTheDocument();
    expect(screen.getByText('87%')).toBeInTheDocument();
  });

  it('muestra las tarjetas de KPI por materia con sus calificaciones', () => {
    render(<StudentProfile student={mockStudent} loading={false} onClose={jest.fn()} />);

    expect(screen.getByText('Lenguaje')).toBeInTheDocument();
    expect(screen.getByLabelText(/Lenguaje: 92%/i)).toBeInTheDocument();

    expect(screen.getByText('Matemáticas')).toBeInTheDocument();
    expect(screen.getByLabelText(/Matemáticas: 91%/i)).toBeInTheDocument();

    expect(screen.getByText('Ciencias Naturales')).toBeInTheDocument();
    expect(screen.getByLabelText(/Ciencias Naturales: 84%/i)).toBeInTheDocument();
  });

  it('aplica el azul pastel exclusivo a Matemáticas', () => {
    render(<StudentProfile student={mockStudent} loading={false} onClose={jest.fn()} />);

    const mathCard = screen.getByLabelText(/Matemáticas: 91%/i);
    expect(mathCard).toHaveStyle({ background: BLUE_MATEMATICAS });
  });

  it('muestra un guión ("—") identificable para materias sin calificaciones sin poner ceros', () => {
    render(<StudentProfile student={mockStudent} loading={false} onClose={jest.fn()} />);

    expect(screen.getByText('Inglés')).toBeInTheDocument();
    const englishCard = screen.getByLabelText(/Inglés: —/i);
    expect(englishCard).toBeInTheDocument();
    expect(englishCard).toHaveTextContent('—');
  });

  it('muestra mensaje amigable cuando el estudiante no tiene materias inscritas', () => {
    const studentSinMaterias = { ...mockStudent, materias: [] };
    render(<StudentProfile student={studentSinMaterias} loading={false} onClose={jest.fn()} />);

    expect(screen.getByText('Sin asignaturas vinculadas a este estudiante.')).toBeInTheDocument();
  });

  it('invoca onClose al hacer clic en el botón de cerrar', () => {
    const handleClose = jest.fn();
    render(<StudentProfile student={mockStudent} loading={false} onClose={handleClose} />);

    fireEvent.click(screen.getByRole('button', { name: 'Cerrar perfil' }));
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('invoca onClose al presionar la tecla Escape', () => {
    const handleClose = jest.fn();
    render(<StudentProfile student={mockStudent} loading={false} onClose={handleClose} />);

    fireEvent.keyDown(window, { key: 'Escape' });
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it('aplica la clase is-closing cuando isClosing es verdadero para la animación de salida', () => {
    render(<StudentProfile student={mockStudent} loading={false} onClose={jest.fn()} isClosing={true} />);

    const profileAside = screen.getByRole('complementary', { name: 'Perfil del estudiante' });
    expect(profileAside).toHaveClass('is-closing');
  });

  it('no renderiza nada si student es null y loading es false', () => {
    const { container } = render(<StudentProfile student={null} loading={false} onClose={jest.fn()} />);
    expect(container.firstChild).toBeNull();
  });
});
