import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

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
        const response = await fetch(`/auth/magic-link/verify/?token=${encodeURIComponent(token)}`);
        const data = await response.json();
        window.history.replaceState({}, document.title, window.location.pathname);
        if (!response.ok) {
          setError(data.error || 'Token inválido');
          return;
        }
        window.sessionStorage.setItem('AUTH_TOKEN', data.access);
        setMessage('Inicio de sesión exitoso, redirigiendo...');
        setTimeout(() => navigate('/dashboard'), 800);
      } catch (err) {
        setError('Error de conexión al verificar token');
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
