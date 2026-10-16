import React, { useState } from 'react';
import './Dashboard.css';
import useAuth from '../hooks/useAuth';
import AddActivity from '../features/activities/AddActivity';

const Dashboard = () => {
  const { user } = useAuth();
  const [showAddActivity, setShowAddActivity] = useState(false);

  const handleAddActivity = () => {
    setShowAddActivity(true);
  };

  const handleCloseAddActivity = () => {
    setShowAddActivity(false);
  };

  const handleActivityAdded = (newActivity) => {
    // Aquí puedes actualizar la lista de actividades si es necesario
    console.log('Nueva actividad añadida:', newActivity);
  };

  if (!user) {
    return <div className="loading">Cargando...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-main">
        <DashboardHome user={user} onAddActivity={handleAddActivity} />
      </div>
      {showAddActivity && (
        <AddActivity onClose={handleCloseAddActivity} onActivityAdded={handleActivityAdded} />
      )}
    </div>
  );
};

// Componente Dashboard Home
const DashboardHome = ({ user, onAddActivity }) => {
  return (
    <div className="dashboard-home">
      {/* Header de bienvenida */}
      <div className="welcome-header">
        <div className="welcome-text">
          <h1>¡Bienvenido, {user.nombre_completo || user.username}! 👋</h1>
          <p>Aquí tienes un resumen de tu actividad en EduNúñez</p>
        </div>
        <div className="welcome-actions">
          {(user.rol === 'profesor' || user.rol === 'administrador') && (
            <button className="add-activity-btn" onClick={onAddActivity}>
              <span className="btn-icon">➕</span>
              Añadir Actividad
            </button>
          )}
        </div>
      </div>

      {/* Tarjetas de estadísticas */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-content">
            <h3>12</h3>
            <p>Actividades Completadas</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🎯</div>
          <div className="stat-content">
            <h3>85%</h3>
            <p>Promedio General</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <h3>24h</h3>
            <p>Tiempo de Estudio</p>
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-icon">🏆</div>
          <div className="stat-content">
            <h3>5</h3>
            <p>Logros Obtenidos</p>
          </div>
        </div>
      </div>

      {/* Accesos rápidos */}
      <div className="quick-access">
        <h2>Accesos Rápidos</h2>
        <div className="quick-access-grid">
          <div className="quick-access-card">
            <div className="quick-icon">🎮</div>
            <h3>Juegos Interactivos</h3>
            <p>Aprende jugando con nuestras actividades gamificadas</p>
            <button className="quick-btn">Explorar</button>
          </div>
          
          <div className="quick-access-card">
            <div className="quick-icon">📝</div>
            <h3>Evaluaciones</h3>
            <p>Realiza pruebas y evalúa tu progreso</p>
            <button className="quick-btn">Comenzar</button>
          </div>
          
          <div className="quick-access-card">
            <div className="quick-icon">📈</div>
            <h3>Mi Progreso</h3>
            <p>Revisa tu rendimiento y estadísticas detalladas</p>
            <button className="quick-btn">Ver Detalles</button>
          </div>
        </div>
      </div>

      {/* Actividades recientes */}
      <div className="recent-activities">
        <h2>Actividades Recientes</h2>
        <div className="activities-list">
          <div className="activity-item">
            <div className="activity-icon">🧩</div>
            <div className="activity-info">
              <h4>Sopa de Letras - Matemáticas</h4>
              <p>Completado hace 2 horas</p>
            </div>
            <div className="activity-score">95%</div>
          </div>
          
          <div className="activity-item">
            <div className="activity-icon">🎯</div>
            <div className="activity-info">
              <h4>Crucigrama - Historia</h4>
              <p>Completado ayer</p>
            </div>
            <div className="activity-score">88%</div>
          </div>
          
          <div className="activity-item">
            <div className="activity-icon">🎮</div>
            <div className="activity-info">
              <h4>Juego de Palabras - Español</h4>
              <p>Completado hace 3 días</p>
            </div>
            <div className="activity-score">92%</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
