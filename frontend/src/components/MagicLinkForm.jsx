import { useState } from 'react';
import api from '../services/api';

export default function MagicLinkForm() {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setMessage(null);
    setError(null);
    setLoading(true);

    try {
      const response = await api.post('/auth/magic-link/', { email });
      setMessage(response.data.mensaje || 'Revisa tu correo para continuar.');
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.mensaje || 'No se pudo enviar el enlace. Intenta nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <h2>Iniciar sesión sin contraseña</h2>
      <form onSubmit={submit}>
        <label htmlFor="magic-email">Correo electrónico</label>
        <input
          id="magic-email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Enviando...' : 'Enviar magic link'}
        </button>
      </form>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
