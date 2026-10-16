import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Button from '../components/ui/Button';
import FormField from '../components/ui/FormField';
import { login } from '../services/auth.service';
import HeroIllustration from './HeroIllustration';
import './Login.css';

/**
 * Login
 * Pagina de inicio de sesion de EduNúñez. Contiene un formulario de login con validación de email y contraseña.
 *
 * Layout: CSS Grid de 2 columnas.
 *   - Columna izquierda â†’ HeroIllustration (SVG ilustrativo)
 *   - Columna derecha   â†’ Tarjeta glassmorphic con formulario
 *
 * LÃ³gica de autenticaciÃ³n preservada Ã­ntegramente:
 *   - useState: formData, errors, isLoading
 *   - validateForm() con validaciÃ³n de email y contraseÃ±a
 *   - handleSubmit() llama a auth.service.login() y guarda en localStorage
 *   - useNavigate para redirecciÃ³n a /dashboard
 */
const Login = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const [errors, setErrors]       = useState({});
  const [isLoading, setIsLoading] = useState(false);



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

    // Validacion de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email.trim()) {
      newErrors.email = 'El email es requerido';
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = 'Por favor ingresa un email vÃ¡lido';
    }

    // ValidaciÃ³n de contraseÃ±a
    if (!formData.password) {
      newErrors.password = 'La contraseÃ±a es requerida';
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

      // Guardar informacion del usuario en localStorage
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



  return (
    <div className="login-page">

      {/* â”€â”€ Columna izquierda: ilustraciÃ³n â”€â”€ */}
      <div className="login-illustration" aria-hidden="true">
        <HeroIllustration />
      </div>

      {/* â”€â”€ Columna derecha: formulario glassmorphic â”€â”€ */}
      <div className="login-panel">
        <div className="login-card">

          {/* Encabezado */}
          <div className="login-header">
            <h1>Iniciar sesión</h1>
            <p>¡Bienvenido a EduNúñez!</p>
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
                required
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
                required
                error={errors.password}
                />
              <Link to="/magic-link" className="forgot-link">Olvidé mi contraseña</Link>
            </div>

            {/* BotÃ³n submit */}
            <Button
              type="submit"
              className="login-btn"
              isLoading={isLoading}
              disabled={isLoading}
            >
              {isLoading ? 'Iniciando sesión…' : 'INICIAR SESIÓN'}
            </Button>
          </form>
          {/* Footer */}
        </div>
      </div>
    </div>
  );
};

export default Login;
