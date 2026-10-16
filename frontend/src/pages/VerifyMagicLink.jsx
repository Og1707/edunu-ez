import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

export default function VerifyMagicLink() {
  const navigate = useNavigate();
  const [message, setMessage] = useState('Verificando token...');
  const [error, setError] = useState(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (!token) {
      setError('Token no proporcionado');
      return;
    }

    const verify = async () => {
      try {
        const response = await api.get('/auth/magic-link/verify/', { params: { token } });
        const data = response.data;
        window.history.replaceState({}, document.title, window.location.pathname);
        localStorage.setItem('user', JSON.stringify(data));
        setMessage('Inicio de sesión exitoso, redirigiendo...');
        setTimeout(() => navigate('/dashboard'), 800);
      } catch (err) {
        setError(err.response?.data?.error || err.response?.data?.mensaje || 'No se pudo verificar el enlace. Solicita uno nuevo.');
      }
    };

    verify();
  }, [navigate]);

  return (
    <main>
      <h2>Verificación de Magic Link</h2>
      {error ? <p className="error">{error}</p> : <p>{message}</p>}
    </main>
  );
}
