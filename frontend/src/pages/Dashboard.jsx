import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import { useNavigate } from 'react-router-dom';
import AddActivity from '../features/activities/AddActivity';
import UserManagement from '../features/users/UserManagement';
import CourseManagement from '../features/courses/CourseManagement';
import ActivityManagement from '../features/activities/ActivityManagement';
import StudentActivities from '../features/activities/StudentActivities';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [activeSection, setActiveSection] = useState('dashboard');
  const [showAddActivity, setShowAddActivity] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Verificar si el usuario está autenticado
    const userData = localStorage.getItem('user');
    if (userData) {
      setUser(JSON.parse(userData));
    } else {
      // Redirigir al login si no está autenticado
      navigate('/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/');
  };

  const handleSectionChange = (section) => {
    setActiveSection(section);
  };

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
      {/* Navbar */}
      <nav className="dashboard-navbar">
        <div className="navbar-brand">
          <img 
            src="/un-logo-header.svg" 
            alt="Logo UN" 
            style={{ 
              width: '40px', 
              height: '40px', 
              marginRight: '12px',
              display: 'block'
            }} 
          />
          <h2>EduNúñez</h2>
        </div>
        
        <div className="navbar-menu">
          <button 
            className={`nav-item ${activeSection === 'dashboard' ? 'active' : ''}`}
            onClick={() => handleSectionChange('dashboard')}
          >
            <span className="nav-icon">🏠</span>
            Dashboard
          </button>
          
          <button 
            className={`nav-item ${activeSection === 'perfil' ? 'active' : ''}`}
            onClick={() => handleSectionChange('perfil')}
          >
            <span className="nav-icon">👤</span>
            Perfil
          </button>
          
          <button 
            className={`nav-item ${activeSection === 'actividades' ? 'active' : ''}`}
            onClick={() => handleSectionChange('actividades')}
          >
            <span className="nav-icon">📚</span>
            Actividades
          </button>
          
          <button 
            className={`nav-item ${activeSection === 'reportes' ? 'active' : ''}`}
            onClick={() => handleSectionChange('reportes')}
          >
            <span className="nav-icon">📊</span>
            Reportes
          </button>

          {/* Mostrar gestión solo para profesores y administradores */}
          {(user.rol === 'profesor' || user.rol === 'administrador') && (
            <>
              <button 
                className={`nav-item ${activeSection === 'usuarios' ? 'active' : ''}`}
                onClick={() => handleSectionChange('usuarios')}
              >
                <span className="nav-icon">👥</span>
                {user.rol === 'profesor' ? 'Estudiantes' : 'Usuarios'}
              </button>

              <button 
                className={`nav-item ${activeSection === 'cursos' ? 'active' : ''}`}
                onClick={() => handleSectionChange('cursos')}
              >
                <span className="nav-icon">📚</span>
                Cursos
              </button>
            </>
          )}
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <span className="user-name">{user.nombre_completo || user.username}</span>
            <span className="user-role">{user.rol}</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <span className="nav-icon">🚪</span>
            Salir
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="dashboard-main">
        {activeSection === 'dashboard' && <DashboardHome user={user} onAddActivity={handleAddActivity} />}
        {activeSection === 'perfil' && <PerfilSection user={user} />}
        {activeSection === 'actividades' && (
          user.rol === 'estudiante' 
            ? <StudentActivities user={user} />
            : <ActivityManagement user={user} onAddActivity={handleAddActivity} />
        )}
        {activeSection === 'reportes' && <ReportesSection user={user} />}
        
        {/* Secciones de gestión solo para profesores y administradores */}
        {activeSection === 'usuarios' && (user.rol === 'profesor' || user.rol === 'administrador') && (
          <UserManagement user={user} />
        )}
        {activeSection === 'cursos' && (user.rol === 'profesor' || user.rol === 'administrador') && (
          <CourseManagement user={user} />
        )}
      </main>

      {/* Modal para añadir actividad */}
      {showAddActivity && (
        <AddActivity 
          onClose={handleCloseAddActivity}
          onActivityAdded={handleActivityAdded}
        />
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

// Componente Perfil
const PerfilSection = ({ user }) => {
  return (
    <div className="perfil-section">
      <h1>Mi Perfil</h1>
      <div className="perfil-content">
        <div className="perfil-card">
          <div className="perfil-avatar">
            <span className="avatar-icon">👤</span>
          </div>
          <div className="perfil-info">
            <h2>{user.nombre_completo || user.username}</h2>
            <p className="perfil-email">{user.email}</p>
            <p className="perfil-role">{user.rol}</p>
          </div>
          <button className="edit-perfil-btn">Editar Perfil</button>
        </div>
      </div>
    </div>
  );
};

// Componente Actividades
const ActividadesSection = ({ user, onAddActivity }) => {
  return (
    <div className="actividades-section">
      <div className="section-header">
        <h1>Actividades</h1>
        {(user.rol === 'profesor' || user.rol === 'administrador') && (
          <button className="add-activity-btn">
            <span className="btn-icon">➕</span>
            Nueva Actividad
          </button>
        )}
      </div>
      
      <div className="actividades-grid">
        <div className="actividad-card">
          <div className="actividad-icon">🧩</div>
          <h3>Sopa de Letras</h3>
          <p>Encuentra palabras relacionadas con el tema</p>
          <button className="actividad-btn">Jugar</button>
        </div>
        
        <div className="actividad-card">
          <div className="actividad-icon">🎯</div>
          <h3>Crucigrama</h3>
          <p>Resuelve pistas y completa el crucigrama</p>
          <button className="actividad-btn">Jugar</button>
        </div>
        
        <div className="actividad-card">
          <div className="actividad-icon">🎮</div>
          <h3>Juego de Palabras</h3>
          <p>Forma palabras y mejora tu vocabulario</p>
          <button className="actividad-btn">Jugar</button>
        </div>
      </div>
    </div>
  );
};

// Componente Reportes
const ReportesSection = ({ user }) => {
  return (
    <div className="reportes-section">
      <h1>Reportes</h1>
      <div className="reportes-content">
        <div className="reporte-card">
          <h3>📊 Rendimiento General</h3>
          <p>Promedio: 87%</p>
          <button className="reporte-btn">Ver Detalles</button>
        </div>
        
        <div className="reporte-card">
          <h3>📈 Progreso Semanal</h3>
          <p>+15% esta semana</p>
          <button className="reporte-btn">Ver Gráfico</button>
        </div>
        
        <div className="reporte-card">
          <h3>🎯 Actividades Pendientes</h3>
          <p>3 actividades por completar</p>
          <button className="reporte-btn">Ver Lista</button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
