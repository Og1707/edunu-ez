import axios from 'axios';

// Configurar axios para enviar credenciales automáticamente
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
