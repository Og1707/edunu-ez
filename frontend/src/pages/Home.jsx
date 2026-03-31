import React from 'react';
import './Home.css';

const Home = () => {
  return (
    <div className="home-container">
      <div className="hero-section">
        <div className="hero-content">
          <h1>Bienvenido a EduNúñez</h1>
          <p>Una plataforma educativa moderna para estudiantes, profesores y administradores</p>
          <div className="hero-buttons">
            <a href="/register" className="btn-primary">Crear Cuenta</a>
            <a href="/login" className="btn-secondary">Iniciar Sesión</a>
          </div>
        </div>
        <div className="hero-image">
          <div className="floating-card">
            <h3>📚 Cursos Interactivos</h3>
            <p>Aprende con contenido dinámico y actividades personalizadas</p>
          </div>
          <div className="floating-card">
            <h3>🎯 Seguimiento del Progreso</h3>
            <p>Monitorea tu avance y recibe retroalimentación detallada</p>
          </div>
          <div className="floating-card">
            <h3>👥 Colaboración</h3>
            <p>Conecta con profesores y compañeros de clase</p>
          </div>
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2>¿Por qué elegir EduNúñez?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎮</div>
              <h3>Aprendizaje Gamificado</h3>
              <p>Juegos interactivos, sopas de letras, crucigramas y más actividades que hacen el aprendizaje divertido.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3>Reportes Detallados</h3>
              <p>Obtén análisis completos del progreso estudiantil con recomendaciones personalizadas.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔧</div>
              <h3>Herramientas para Profesores</h3>
              <p>Crea y gestiona cursos, actividades y evalúa el desempeño de tus estudiantes fácilmente.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3>Acceso Multiplataforma</h3>
              <p>Aprende desde cualquier dispositivo con nuestra interfaz responsive y moderna.</p>
            </div>
          </div>
        </div>
      </div>

      <div className="cta-section">
        <div className="container">
          <h2>¿Listo para comenzar tu experiencia educativa?</h2>
          <p>Únete a miles de estudiantes y profesores que ya están transformando la educación</p>
          <a href="/register" className="btn-primary large">Comenzar Ahora</a>
        </div>
      </div>
    </div>
  );
};

export default Home;
