import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import FormField from '../components/ui/FormField';
import { login } from '../services/auth.service';
import HeroIllustration from './HeroIllustration';
import './Login.css';

/**
 * Login
 * Página de inicio de sesión de EduNúñez.
 *
 * Layout: CSS Grid de 2 columnas.
 *   - Columna izquierda → HeroIllustration (SVG ilustrativo)
 *   - Columna derecha   → Tarjeta glassmorphic con formulario
 *
 * Lógica de autenticación preservada íntegramente:
 *   - useState: formData, errors, isLoading
 *   - validateForm() con validación de email y contraseña
 *   - handleSubmit() llama a auth.service.login() y guarda en localStorage
 *   - useNavigate para redirección a /dashboard
 */
const Login = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors]       = useState({});
  const [isLoading, setIsLoading] = useState(false);

  /* ── Handlers ─────────────────────────────────────────── */

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Limpiar error del campo en cuanto el usuario empiece a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validación de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Por favor ingresa un email válido';
    }

    // Validación de contraseña
    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setIsLoading(true);
    setErrors({});

    try {
      const response = await login(formData);

      // Guardar información del usuario en localStorage
      localStorage.setItem('user', JSON.stringify(response.data));

      // Redirigir al dashboard
      console.log('Login exitoso:', response.data);
      navigate('/dashboard');

    } catch (error) {
      console.error('Error en el login:', error);

      if (error.response?.data) {
        setErrors({ general: error.response.data.mensaje || 'Credenciales incorrectas' });
      } else {
        setErrors({ general: 'Error al conectar con el servidor. Intenta nuevamente.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  /* ── Render ────────────────────────────────────────────── */

  return (
    <div className="login-page">

      {/* ── Columna izquierda: ilustración ── */}
      <div className="login-illustration" aria-hidden="true">
        <HeroIllustration />
      </div>

      {/* ── Columna derecha: formulario glassmorphic ── */}
      <div className="login-panel">
        <div className="login-card">

          {/* Encabezado */}
          <div className="login-header">
            <h1>Iniciar Sesión</h1>
            <p>Bienvenido a EduNúñez!</p>
          </div>

          {/* Error general (credenciales incorrectas / servidor caído) */}
          {errors.general && (
            <div className="login-error-banner" role="alert">
              {errors.general}
            </div>
          )}

          {/* Formulario */}
          <form onSubmit={handleSubmit} className="login-form" noValidate>

            {/* Campo: Username (email) */}
            <FormField
                className="form-group"
                label="Correo Electrónico"
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                inputClassName={errors.email ? 'input-error' : ''}
                placeholder="Ingresa tu correo electrónico"
                autoComplete="username"
                error={errors.email}
              />

            {/* Campo: Password */}
            <div className="form-group">
              <FormField
                label="Contraseña"
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                inputClassName={errors.password ? 'input-error' : ''}
                placeholder="Ingresa tu contraseña"
                autoComplete="current-password"
                error={errors.password}
                />
              <a href="/magic-link" className="forgot-link">Olvide mi contraseña</a>
            </div>

            {/* Botón submit */}
            <Button
              type="submit"
              className="login-btn"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? 'Logging in…' : 'INICIAR SESIÓN'}
            </Button>
          </form>
          {/* Footer */}
        </div>
      </div>
    </div>
  );
};

export default Login;
