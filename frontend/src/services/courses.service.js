import api from './api';

export const getCourses = () => api.get('/api/cursos/');
export const getUsers = (userId) => api.get(`/api/usuarios/listar/?user_id=${userId}`);
export const createCourse = (data) => api.post('/api/cursos/crear/', data);
export const updateCourse = (courseId, data) => api.put(`/api/cursos/${courseId}/gestionar/`, data);
export const deleteCourse = (courseId, userId) => api.delete(`/api/cursos/${courseId}/gestionar/?user_id=${userId}`);
export const getCourseStudents = (cursoId, userId) => api.get(`/api/estudiantes-curso/?curso_id=${cursoId}&user_id=${userId}`);
export const addStudentToCourse = (data) => api.post('/api/estudiantes-curso/agregar/', data);
export const removeStudentFromCourse = (inscripcionId, userId) => api.delete(`/api/estudiantes-curso/${inscripcionId}/remover/?user_id=${userId}`);
