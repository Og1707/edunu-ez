import api from './api';

export const login = (credentials) => {
  return api.post('/api/login/', credentials, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};

export const register = (data) => {
  return api.post('/api/registro/', data, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
};
