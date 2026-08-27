import api from './api';

export const getCourses = () => api.get('/api/cursos/');
export const getUsers = () => api.get('/api/usuarios/listar/');
export const createCourse = (data) => api.post('/api/cursos/crear/', data);
export const updateCourse = (courseId, data) => api.put(`/api/cursos/${courseId}/gestionar/`, data);
export const deleteCourse = (courseId) => api.delete(`/api/cursos/${courseId}/gestionar/`);
export const getCourseStudents = (cursoId) => api.get(`/api/estudiantes-curso/?curso_id=${cursoId}`);
export const addStudentToCourse = (data) => api.post('/api/estudiantes-curso/agregar/', data);
export const removeStudentFromCourse = (inscripcionId) => api.delete(`/api/estudiantes-curso/${inscripcionId}/remover/`);
