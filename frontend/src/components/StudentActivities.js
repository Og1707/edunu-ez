import React, { useState, useEffect } from 'react';
import axios from '../utils/axiosConfig';
import ColorGame from './ColorGame';
import './StudentActivities.css';

const StudentActivities = ({ user }) => {
  const [actividades, setActividades] = useState([]);
  const [estadisticas, setEstadisticas] = useState({});
  const [filtroEstado, setFiltroEstado] = useState('todas');
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [tiempoInicio, setTiempoInicio] = useState(null);
  const [playingGameType, setPlayingGameType] = useState(null); // 'color-game' o null

  useEffect(() => {
    if (user && user.usuario_id) {
      console.log('Usuario estudiante cargado:', user);
      cargarDatos();
    } else {
      console.log('Usuario estudiante no disponible aún');
    }
  }, [user]);

  const cargarDatos = async () => {
    setIsLoading(true);
    setErrors({});
    try {
      console.log('Cargando datos para estudiante:', user.usuario_id);

      const [actividadesResponse, estadisticasResponse] = await Promise.all([
        axios.get(`http://127.0.0.1:8000/api/estudiante/actividades/?user_id=${user.usuario_id}`),
        axios.get(`http://127.0.0.1:8000/api/estudiante/estadisticas/?user_id=${user.usuario_id}`)
      ]);

      console.log('Datos cargados exitosamente:', {
        actividades: actividadesResponse.data.length,
        estadisticas: estadisticasResponse.data
      });

      setActividades(actividadesResponse.data);
      setEstadisticas(estadisticasResponse.data);

    } catch (error) {
      console.error('Error al cargar datos del estudiante:', error);
      console.error('Response status:', error.response?.status);
      console.error('Response data:', error.response?.data);

      if (error.response) {
        // Error de respuesta del servidor
        if (error.response.status === 403) {
          setErrors({ general: 'No tienes permisos para ver las actividades. Verifica que seas estudiante.' });
        } else if (error.response.status === 404) {
          setErrors({ general: 'No se encontraron actividades asignadas.' });
        } else {
          setErrors({ general: `Error del servidor: ${error.response.data?.mensaje || 'Error desconocido'}` });
        }
      } else if (error.request) {
        // Error de red
        setErrors({ general: 'Error de conexión. Verifica que el servidor esté corriendo en http://127.0.0.1:8000' });
      } else {
        // Otro tipo de error
        setErrors({ general: 'Error inesperado al cargar los datos' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const iniciarActividad = async (actividadId) => {
    try {
      if (!user || !user.usuario_id) {
        setErrors({ general: 'Debes iniciar sesión para realizar esta acción' });
        return;
      }

      // Mostrar indicador de carga
      setIsLoading(true);
      setErrors({});
      
      const response = await axios.post('http://127.0.0.1:8000/api/estudiante/actividades/iniciar/', {
        user_id: user.usuario_id,
        actividad_id: actividadId
      });

      setTiempoInicio(new Date());
      setSuccessMessage('Actividad iniciada. ¡Buena suerte!');
      await cargarDatos();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al iniciar actividad:', error);
      setTiempoInicio(null);

      if (error.response) {
        // Error del servidor
        if (error.response.status === 403) {
          setErrors({ general: error.response.data.mensaje || 'No tienes permisos para iniciar esta actividad' });
        } else if (error.response.status === 404) {
          setErrors({ general: error.response.data.mensaje || 'La actividad no fue encontrada' });
        } else {
          setErrors({ general: error.response.data.mensaje || 'Error al iniciar la actividad' });
        }
      } else if (error.request) {
        // Error de red
        setErrors({ general: 'Error de conexión. Por favor verifica tu conexión a internet' });
      } else {
        setErrors({ general: 'Error inesperado al iniciar la actividad' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const completarActividad = async (actividadId, puntuacion = 85) => {
    if (!user || !user.usuario_id) {
      setErrors({ general: 'Debes iniciar sesión para realizar esta acción' });
      return;
    }

    if (!tiempoInicio) {
      setErrors({ general: 'Debes iniciar la actividad primero' });
      return;
    }

    const tiempoFin = new Date();
    const tiempoEmpleado = Math.round((tiempoFin - tiempoInicio) / (1000 * 60)); // en minutos

    try {
      // Mostrar indicador de carga
      setIsLoading(true);
      setErrors({});

      const response = await axios.post('http://127.0.0.1:8000/api/estudiante/actividades/completar/', {
        user_id: user.usuario_id,
        actividad_id: actividadId,
        puntuacion: puntuacion,
        tiempo_empleado: tiempoEmpleado
      });

      setSuccessMessage('¡Felicitaciones! Actividad completada exitosamente');
      setShowActivityModal(false);
      setSelectedActivity(null);
      setTiempoInicio(null);
      await cargarDatos();

      setTimeout(() => setSuccessMessage(''), 5000);

    } catch (error) {
      console.error('Error al completar actividad:', error);
      
      if (error.response) {
        // Error del servidor
        if (error.response.status === 403) {
          setErrors({ general: error.response.data.mensaje || 'No tienes permisos para completar esta actividad' });
        } else if (error.response.status === 404) {
          setErrors({ general: error.response.data.mensaje || 'La actividad no fue encontrada' });
        } else {
          setErrors({ general: error.response.data.mensaje || 'Error al completar la actividad' });
        }
      } else if (error.request) {
        // Error de red
        setErrors({ general: 'Error de conexión. Por favor verifica tu conexión a internet' });
      } else {
        setErrors({ general: 'Error inesperado al completar la actividad' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const abrirActividad = (actividad) => {
    setSelectedActivity(actividad);
    setShowActivityModal(true);
    setErrors({});
  };

  const getEstadoColor = (estadoTiempo, progreso) => {
    if (progreso.completada) return '#28a745'; // Verde para completadas
    
    switch (estadoTiempo) {
      case 'vencida': return '#dc3545'; // Rojo para vencidas
      case 'por_vencer': return '#ffc107'; // Amarillo para por vencer
      case 'activa': return '#17a2b8'; // Azul para activas
      default: return '#6c757d'; // Gris por defecto
    }
  };

  const getEstadoTexto = (estadoTiempo, progreso) => {
    if (progreso.completada) return 'Completada ✅';
    
    switch (estadoTiempo) {
      case 'vencida': return 'Vencida ⏰';
      case 'por_vencer': return 'Por vencer ⚠️';
      case 'activa': return 'Activa 📚';
      case 'sin_limite': return 'Sin límite 📖';
      default: return progreso.estado === 'asignada' ? 'Asignada 📋' : 'Pendiente';
    }
  };

  const getTipoIcon = (tipo) => {
    const iconos = {
      'video': '🎥',
      'juego': '🎮',
      'sopa_letras': '🔤',
      'crucigrama': '🧩',
      'palabras': '📝',
      'lectura_comprensiva': '📖',
      'experimento_virtual': '🧪',
      'quiz_ciencias': '🔬',
      'simulador': '💻',
      'laboratorio_virtual': '⚗️',
      'otro': '📋'
    };
    return iconos[tipo] || '📋';
  };

  const actividadesFiltradas = actividades.filter(actividad => {
    switch (filtroEstado) {
      case 'completadas':
        return actividad.progreso.completada;
      case 'pendientes':
        return !actividad.progreso.completada;
      case 'vencidas':
        return actividad.estado_tiempo === 'vencida' && !actividad.progreso.completada;
      case 'por_vencer':
        return actividad.estado_tiempo === 'por_vencer' && !actividad.progreso.completada;
      default:
        return true;
    }
  });

  const getDiasRestantes = (fechaLimite) => {
    if (!fechaLimite) return null;
    
    const hoy = new Date();
    const limite = new Date(fechaLimite);
    const diferencia = Math.ceil((limite - hoy) / (1000 * 60 * 60 * 24));
    
    if (diferencia < 0) return `Vencida hace ${Math.abs(diferencia)} días`;
    if (diferencia === 0) return 'Vence hoy';
    if (diferencia === 1) return 'Vence mañana';
    return `${diferencia} días restantes`;
  };

  return (
    <div className="student-activities">
      {/* Header con estadísticas */}
      <div className="activities-header">
        <div className="header-content">
          <h2>Mis Actividades</h2>
          <p>Gestiona y completa tus actividades asignadas</p>
        </div>
        
        <div className="stats-cards">
          <div className="stat-card total">
            <div className="stat-icon">📚</div>
            <div className="stat-info">
              <h3>{estadisticas.total_actividades || 0}</h3>
              <p>Total</p>
            </div>
          </div>
          
          <div className="stat-card completed">
            <div className="stat-icon">✅</div>
            <div className="stat-info">
              <h3>{estadisticas.actividades_completadas || 0}</h3>
              <p>Completadas</p>
            </div>
          </div>
          
          <div className="stat-card pending">
            <div className="stat-icon">⏳</div>
            <div className="stat-info">
              <h3>{estadisticas.actividades_pendientes || 0}</h3>
              <p>Pendientes</p>
            </div>
          </div>
          
          <div className="stat-card urgent">
            <div className="stat-icon">⚠️</div>
            <div className="stat-info">
              <h3>{estadisticas.actividades_por_vencer || 0}</h3>
              <p>Por vencer</p>
            </div>
          </div>
        </div>
      </div>

      {/* Progreso general */}
      {estadisticas.total_actividades > 0 && (
        <div className="progress-section">
          <div className="progress-info">
            <h4>Progreso General</h4>
            <span>{estadisticas.porcentaje_completado || 0}% completado</span>
          </div>
          <div className="progress-bar">
            <div 
              className="progress-fill"
              style={{ width: `${estadisticas.porcentaje_completado || 0}%` }}
            ></div>
          </div>
          <div className="progress-stats">
            <span>Promedio: {estadisticas.puntuacion_promedio || 0}/100</span>
          </div>
        </div>
      )}

      {/* Filtros */}
      <div className="filters-section">
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${filtroEstado === 'todas' ? 'active' : ''}`}
            onClick={() => setFiltroEstado('todas')}
          >
            Todas ({actividades.length})
          </button>
          <button 
            className={`filter-btn ${filtroEstado === 'pendientes' ? 'active' : ''}`}
            onClick={() => setFiltroEstado('pendientes')}
          >
            Pendientes ({actividades.filter(a => !a.progreso.completada).length})
          </button>
          <button 
            className={`filter-btn ${filtroEstado === 'completadas' ? 'active' : ''}`}
            onClick={() => setFiltroEstado('completadas')}
          >
            Completadas ({actividades.filter(a => a.progreso.completada).length})
          </button>
          <button 
            className={`filter-btn ${filtroEstado === 'por_vencer' ? 'active' : ''}`}
            onClick={() => setFiltroEstado('por_vencer')}
          >
            Por vencer ({actividades.filter(a => a.estado_tiempo === 'por_vencer' && !a.progreso.completada).length})
          </button>
          <button 
            className={`filter-btn ${filtroEstado === 'vencidas' ? 'active' : ''}`}
            onClick={() => setFiltroEstado('vencidas')}
          >
            Vencidas ({actividades.filter(a => a.estado_tiempo === 'vencida' && !a.progreso.completada).length})
          </button>
        </div>
      </div>

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      {errors.general && (
        <div className="error-message">
          {errors.general}
        </div>
      )}

      {/* Lista de actividades */}
      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Cargando actividades...</p>
        </div>
      ) : (
        <div className="activities-grid">
          {actividadesFiltradas.map(actividad => (
            <div key={actividad.id} className="activity-card">
              <div className="activity-header">
                <div className="activity-type">
                  <span className="type-icon">{getTipoIcon(actividad.tipo)}</span>
                  <span className="type-text">{actividad.tipo.replace('_', ' ')}</span>
                </div>
                <div 
                  className="activity-status"
                  style={{ backgroundColor: getEstadoColor(actividad.estado_tiempo, actividad.progreso) }}
                >
                  {getEstadoTexto(actividad.estado_tiempo, actividad.progreso)}
                </div>
              </div>

              <div className="activity-content">
                <h3>{actividad.titulo}</h3>
                <p className="activity-description">{actividad.descripcion}</p>
                
                <div className="activity-meta">
                  <div className="meta-item">
                    <span className="meta-label">Curso:</span>
                    <span className="meta-value">{actividad.curso_nombre}</span>
                  </div>
                  
                  {actividad.fecha_limite && (
                    <div className="meta-item">
                      <span className="meta-label">Fecha límite:</span>
                      <span className="meta-value">
                        {new Date(actividad.fecha_limite).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  
                  {actividad.fecha_limite && (
                    <div className="meta-item time-remaining">
                      <span className="meta-label">Estado:</span>
                      <span className="meta-value">{getDiasRestantes(actividad.fecha_limite)}</span>
                    </div>
                  )}
                </div>

                {actividad.progreso.completada ? (
                  <div className="completed-info">
                    <div className="completion-details">
                      <span>✅ Completada el {new Date(actividad.progreso.fecha_completado).toLocaleDateString()}</span>
                      {actividad.progreso.puntuacion && (
                        <span>Puntuación: {actividad.progreso.puntuacion}/100</span>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="activity-actions">
                    <button 
                      className="start-activity-btn"
                      onClick={() => abrirActividad(actividad)}
                    >
                      {actividad.progreso.estado === 'en_progreso' ? 'Continuar' : 'Iniciar'} Actividad
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}

          {actividadesFiltradas.length === 0 && (
            <div className="empty-state">
              <div className="empty-icon">📚</div>
              <h3>No hay actividades</h3>
              <p>
                {filtroEstado === 'todas' 
                  ? 'No tienes actividades asignadas aún. Los profesores asignarán actividades para que puedas realizarlas aquí.'
                  : `No tienes actividades ${filtroEstado}. Los profesores asignarán actividades para que puedas realizarlas aquí.`
                }
              </p>
            </div>
          )}
        </div>
      )}

      {/* Modal de actividad */}
      {showActivityModal && selectedActivity && (
        <div className="modal-overlay">
          <div className="modal-content activity-modal">
            {/* Si se está jugando el juego de colores, mostrar solo el juego */}
            {playingGameType === 'color-game' ? (
              <div className="game-modal-container">
                <ColorGame 
                  user={user}
                  actividad={selectedActivity}
                  onComplete={(results) => {
                    console.log('Juego completado:', results);
                    setSuccessMessage(`¡Actividad completada! Puntuación: ${results.puntuacion}%`);
                    setPlayingGameType(null);
                    setTimeout(() => {
                      setShowActivityModal(false);
                      setSelectedActivity(null);
                      cargarDatos();
                    }, 2000);
                  }}
                  onClose={() => {
                    setPlayingGameType(null);
                  }}
                />
              </div>
            ) : (
              <>
                <div className="modal-header">
                  <h3>{selectedActivity.titulo}</h3>
                  <button className="close-btn" onClick={() => setShowActivityModal(false)}>✕</button>
                </div>

                <div className="activity-modal-content">
                  <div className="activity-info">
                    <div className="info-section">
                      <h4>Descripción</h4>
                      <p>{selectedActivity.descripcion}</p>
                    </div>

                    <div className="info-section">
                      <h4>Detalles</h4>
                      <div className="details-grid">
                        <div className="detail-item">
                          <span>Tipo:</span>
                          <span>{getTipoIcon(selectedActivity.tipo)} {selectedActivity.tipo.replace('_', ' ')}</span>
                        </div>
                        <div className="detail-item">
                          <span>Curso:</span>
                          <span>{selectedActivity.curso_nombre}</span>
                        </div>
                        {selectedActivity.fecha_limite && (
                          <div className="detail-item">
                            <span>Fecha límite:</span>
                            <span>{new Date(selectedActivity.fecha_limite).toLocaleDateString()}</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {selectedActivity.recurso && (
                      <div className="info-section">
                        <h4>Recursos</h4>
                        <a 
                          href={selectedActivity.recurso} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="resource-link"
                        >
                          📎 Descargar recurso
                        </a>
                      </div>
                    )}
                  </div>

                  <div className="activity-simulation">
                    <div className="simulation-area">
                      <h4>Área de Trabajo</h4>
                      
                      {/* Mostrar juego de colores si el tipo de actividad es 'quiz_ciencias' o contiene 'juego' */}
                      {(selectedActivity.tipo === 'quiz_ciencias' || selectedActivity.tipo.includes('juego')) ? (
                        <div className="inline-game-area">
                          <p>🎮 Juego interactivo</p>
                          <button 
                            className="play-game-btn"
                            onClick={() => setPlayingGameType('color-game')}
                          >
                            ▶️ Jugar Reconocimiento de Colores
                          </button>
                        </div>
                      ) : (
                        <div className="work-area">
                          <p>🎯 Aquí realizarías la actividad</p>
                          <p>📝 Esta es una simulación del área de trabajo</p>
                          <p>⏱️ {tiempoInicio ? `Tiempo transcurrido: ${Math.round((new Date() - tiempoInicio) / 1000)}s` : 'Presiona "Iniciar" para comenzar'}</p>
                        </div>
                      )}
                    </div>

                    <div className="simulation-controls">
                      {(selectedActivity.tipo === 'quiz_ciencias' || selectedActivity.tipo.includes('juego')) ? null : (
                        <>
                          {!tiempoInicio ? (
                            <button 
                              className="start-btn"
                              onClick={() => iniciarActividad(selectedActivity.id)}
                            >
                              🚀 Iniciar Actividad
                            </button>
                          ) : (
                            <button 
                              className="complete-btn"
                              onClick={() => completarActividad(selectedActivity.id)}
                            >
                              ✅ Completar Actividad
                            </button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentActivities;
