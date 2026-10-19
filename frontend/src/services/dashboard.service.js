import api from './api';

export const getDashboardSummary = () => api.get('/api/dashboard/resumen/');
export const getDashboardStudent = (studentId) => api.get(`/api/dashboard/estudiantes/${studentId}/`);
