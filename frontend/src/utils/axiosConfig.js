import axios from 'axios';

const baseURL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

// Interceptor para añadir headers de autenticación si es necesario
axios.interceptors.request.use(
  (config) => {
    // Puedes añadir headers adicionales aquí si es necesario
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores de respuesta
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      console.log('No autenticado - redirigir al login si es necesario');
    }
    return Promise.reject(error);
  }
);

export default axios;
