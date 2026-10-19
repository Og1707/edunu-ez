import React from 'react';
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import CourseManagement from './CourseManagement';
import { getCourses, getSubjects, createCourse, createSubject, getCourseStudents, addStudentToCourse } from '../../services/courses.service';
import { listUsers } from '../../services/users.service';

jest.mock('../../services/courses.service');
jest.mock('../../services/users.service');

beforeEach(() => {
  getCourses.mockResolvedValue({ data: [] });
  getSubjects.mockResolvedValue({ data: [{ id: 1, nombre: 'Matemáticas' }, { id: 2, nombre: 'Lenguaje' }] });
  listUsers.mockResolvedValue({ data: { usuarios: [] } });
  createCourse.mockResolvedValue({ data: { id: 4 } });
  createSubject.mockResolvedValue({ data: { id: 3, nombre: 'Música' } });
  getCourseStudents.mockResolvedValue({ data: { estudiantes: [] } });
  addStudentToCourse.mockResolvedValue({ data: {} });
});

afterEach(() => jest.clearAllMocks());

describe('CourseManagement asignaturas', () => {
  it('envía varias asignaturas al crear un curso', async () => {
    render(<CourseManagement user={{ rol: 'administrador', usuario_id: 10 }}/>);
    fireEvent.click(await screen.findByRole('button', { name: /Crear curso/ }));
    fireEvent.change(screen.getByLabelText('Nombre del curso'), { target: { value: 'Grupo A1' } });
    fireEvent.change(screen.getByLabelText('Descripción'), { target: { value: 'Curso de prueba' } });
    fireEvent.click(screen.getByRole('checkbox', { name: 'Matemáticas' }));
    fireEvent.click(screen.getByRole('checkbox', { name: 'Lenguaje' }));
    fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Crear curso' }));

    await waitFor(() => expect(createCourse).toHaveBeenCalledWith(expect.objectContaining({
      nombre: 'Grupo A1',
      asignaturas: [1, 2],
    })));
  });

  it('permite agregar una asignatura al catálogo y la selecciona para el curso', async () => {
    render(<CourseManagement user={{ rol: 'administrador', usuario_id: 10 }}/>);
    fireEvent.click(await screen.findByRole('button', { name: /Crear curso/ }));
    fireEvent.change(screen.getByLabelText('Agregar asignatura al catálogo'), { target: { value: 'Música' } });
    fireEvent.click(screen.getByRole('button', { name: 'Agregar' }));

    expect(await screen.findByRole('checkbox', { name: 'Música' })).toBeChecked();
    expect(createSubject).toHaveBeenCalledWith({ nombre: 'Música' });
  });
});

describe('CourseManagement student enrollment search', () => {
  it('filters available students by name, username, or email and ignores accents', async () => {
    getCourses.mockResolvedValue({ data: [{ id: 5, nombre: 'A1', profesor: 10 }] });
    listUsers.mockResolvedValue({ data: { usuarios: [
      { id: 2, rol: 'estudiante', nombre_completo: 'Ángela Ruiz', username: 'angela_r', email: 'angela@example.edu' },
      { id: 3, rol: 'estudiante', nombre_completo: 'Bruno Díaz', username: 'bruno02', email: 'bruno@example.edu' },
      { id: 4, rol: 'profesor', nombre_completo: 'Docente Demo', username: 'docente' },
    ] } });
    render(<CourseManagement user={{ rol: 'administrador', usuario_id: 10 }}/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Gestionar estudiantes de A1' }));

    const searchInput = await screen.findByRole('searchbox', { name: 'Buscar estudiantes disponibles' });
    fireEvent.change(searchInput, { target: { value: 'angela' } });
    expect(await screen.findByText('Ángela Ruiz')).toBeInTheDocument();
    expect(screen.queryByText('Bruno Díaz')).not.toBeInTheDocument();
    expect(screen.queryByText('Docente Demo')).not.toBeInTheDocument();

    fireEvent.change(searchInput, { target: { value: 'bruno@example.edu' } });
    expect(await screen.findByText('Bruno Díaz')).toBeInTheDocument();
    expect(screen.queryByText('Ángela Ruiz')).not.toBeInTheDocument();
  });

  it('shows a clear-search action when there are no matches', async () => {
    getCourses.mockResolvedValue({ data: [{ id: 5, nombre: 'A1', profesor: 10 }] });
    listUsers.mockResolvedValue({ data: { usuarios: [
      { id: 3, rol: 'estudiante', nombre_completo: 'Bruno Díaz', username: 'bruno02' },
      { id: 4, rol: 'profesor', nombre_completo: 'Docente Demo', username: 'docente' },
    ] } });
    render(<CourseManagement user={{ rol: 'administrador', usuario_id: 10 }}/>);
    fireEvent.click(await screen.findByRole('button', { name: 'Gestionar estudiantes de A1' }));
    const searchInput = await screen.findByRole('searchbox', { name: 'Buscar estudiantes disponibles' });
    fireEvent.change(searchInput, { target: { value: 'inexistente' } });
    fireEvent.click(await screen.findByRole('button', { name: 'Limpiar búsqueda' }));

    expect(await screen.findByText('Bruno Díaz')).toBeInTheDocument();
    expect(screen.queryByText('Docente Demo')).not.toBeInTheDocument();
  });
});