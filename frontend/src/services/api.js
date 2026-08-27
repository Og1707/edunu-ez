import axios from 'axios';

const baseURL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL,
  withCredentials: true,
});

api.interceptors.request.use(
  (config) => {
    const userRaw = localStorage.getItem('user');

    if (userRaw) {
      try {
        const user = JSON.parse(userRaw);

        if (user?.token && !config.headers?.Authorization) {
          config.headers = config.headers || {};
          config.headers.Authorization = `Bearer ${user.token}`;
        }
      } catch (error) {
        // Si el JSON está corrupto, no rompemos la request.
      }
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      console.warn('Acceso denegado');
    }
    return Promise.reject(error);
  }
);

export default api;
