import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import CourseManagement from './CourseManagement';
import {
  addStudentToCourse,
  createCourse,
  createSubject,
  deleteCourse,
  getCourses,
  getCourseStudents,
  updateCourse,
} from '../../services/courses.service';
import { listUsers } from '../../services/users.service';

jest.mock('../../services/courses.service');
jest.mock('../../services/users.service');

beforeEach(() => {
  getCourses.mockResolvedValue({ data: [{
    id: 21,
    nombre: 'A1',
    descripcion: 'Grupo de primaria',
    profesor: 7,
    asignaturas_nombres: ['Matemáticas', 'Lenguaje'],
  }] });
  getCourseStudents.mockResolvedValue({ data: { estudiantes: [{
    id: 42,
    inscripcion_id: 88,
    username: 'ana',
    nombre_completo: 'Ana Pérez',
  }] } });
});

afterEach(() => jest.clearAllMocks());

describe('vista de cursos del profesor', () => {
  it('presenta cursos en tarjetas y permite consultar estudiantes en modo de solo lectura', async () => {
    render(<CourseManagement user={{ rol: 'profesor', usuario_id: 7 }} />);

    const courseCard = await screen.findByRole('article', { name: /A1/ });
    expect(within(courseCard).getByText('Grupo de primaria')).toBeInTheDocument();
    expect(within(courseCard).getByText('Matemáticas')).toBeInTheDocument();
    expect(within(courseCard).getByText('Lenguaje')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Crear curso|Editar A1|Eliminar A1|Gestionar estudiantes/ })).not.toBeInTheDocument();

    fireEvent.click(within(courseCard).getByRole('button', { name: /Ver estudiantes/ }));
    expect(await within(courseCard).findByText('Ana Pérez')).toBeInTheDocument();
    expect(getCourseStudents).toHaveBeenCalledWith(21);
    expect(listUsers).not.toHaveBeenCalled();
    expect(addStudentToCourse).not.toHaveBeenCalled();
    expect(createCourse).not.toHaveBeenCalled();
    expect(createSubject).not.toHaveBeenCalled();
    expect(updateCourse).not.toHaveBeenCalled();
    expect(deleteCourse).not.toHaveBeenCalled();
  });

  it('muestra un estado vacío cuando no hay cursos asignados', async () => {
    getCourses.mockResolvedValueOnce({ data: [] });
    render(<CourseManagement user={{ rol: 'profesor', usuario_id: 7 }} />);

    expect(await screen.findByText('Aún no tienes cursos asignados')).toBeInTheDocument();
  });

  it('permite volver a intentar la carga de estudiantes si falla', async () => {
    getCourseStudents.mockRejectedValueOnce(new Error('forbidden'));
    render(<CourseManagement user={{ rol: 'profesor', usuario_id: 7 }} />);

    const card = await screen.findByRole('article', { name: /A1/ });
    fireEvent.click(within(card).getByRole('button', { name: /Ver estudiantes/ }));
    expect(await within(card).findByRole('alert')).toHaveTextContent('No se pudo cargar la lista de estudiantes.');
    fireEvent.click(within(card).getByRole('button', { name: 'Reintentar' }));
    await waitFor(() => expect(getCourseStudents).toHaveBeenCalledTimes(2));
    expect(await within(card).findByText('Ana Pérez')).toBeInTheDocument();
  });
});
