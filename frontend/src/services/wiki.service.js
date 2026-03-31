import api from './api';

export const getWikiContent = (tema) => api.get(`/api/wikipedia/contenido/?tema=${encodeURIComponent(tema)}`);
