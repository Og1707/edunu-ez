import React, { useState, useEffect } from 'react';
import axios from '../../utils/axiosConfig';
import {
  getCourseStudents,
  assignActivityToCourse,
  addStudentToCourse,
  getTeacherActivities,
  getCourses,
  getActivityTypes,
  updateActivity,
  deleteActivity,
} from '../../services/activities.service';
import './ActivityManagement.css';

const ActivityManagement = ({ user, onAddActivity }) => {
  const [actividades, setActividades] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [tiposActividad, setTiposActividad] = useState([]);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedActivityForAssign, setSelectedActivityForAssign] = useState(null);
  const [estudiantes, setEstudiantes] = useState([]);
  const [selectedEstudiantes, setSelectedEstudiantes] = useState([]);
  const [assignToAll, setAssignToAll] = useState(false);
  const [filtros, setFiltros] = useState({
    curso: '',
    tipo: '',
    busqueda: ''
  });

  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    tipo: 'otro',
    curso: '',
    fecha_limite: '',
    estado: 'pendiente',
    recurso: null
  });

  const cargarEstudiantesCurso = async (cursoId) => {
    try {
      console.log('Cargando estudiantes del curso:', cursoId);
      const response = await axios.get(`/api/estudiantes-curso/?curso_id=${cursoId}&user_id=${user.usuario_id}`);
      console.log('Estudiantes cargados:', response.data.length);
      setEstudiantes(response.data);
    } catch (error) {
      console.error('Error al cargar estudiantes:', error);
      console.error('Response status:', error.response?.status);
      console.error('Response data:', error.response?.data);
      setErrors({ estudiantes: 'Error al cargar estudiantes del curso' });
    }
  };

  const openAssignModal = (actividad) => {
    setSelectedActivityForAssign(actividad);
    cargarEstudiantesCurso(actividad.curso);
    setSelectedEstudiantes([]);
    setAssignToAll(false);
    setShowAssignModal(true);
  };

  const handleAssignActivity = async () => {
    if (!selectedActivityForAssign || !selectedActivityForAssign.id) {
      setErrors({ general: "Debes seleccionar una actividad válida para asignar." });
      return;
    }

    try {
      setIsLoading(true);

      const requestData = {
        curso_id: selectedActivityForAssign.curso,
        actividad_ids: [selectedActivityForAssign.id],
        user_id: user.usuario_id
      };

      console.log('Enviando datos de asignación:', requestData);

      if (assignToAll) {
        if (estudiantes.length === 0) {
          throw new Error('No hay estudiantes matriculados en este curso. Primero debes agregar estudiantes al curso.');
        }
        // Asignar a todo el curso
        const response = await axios.post('/api/asignar-actividad-curso/', requestData);
        console.log('Respuesta de asignación exitosa:', response.data);
      } else if (selectedEstudiantes.length > 0) {
        // Asignar a estudiantes específicos
        for (const estudiante of selectedEstudiantes) {
          const estudianteData = {
            estudiante_id: estudiante.estudiante.id,
            curso_id: selectedActivityForAssign.curso,
            user_id: user.usuario_id
          };
          console.log('Asignando a estudiante específico:', estudianteData);
          await axios.post('/api/estudiantes-curso/agregar/', estudianteData);
        }
      }

      setSuccessMessage('Actividad asignada exitosamente');
      setShowAssignModal(false);
      setSelectedActivityForAssign(null);

      setTimeout(() => setSuccessMessage(''), 3000);

      // Recargar datos para mostrar las asignaciones actualizadas
      cargarDatos();

    } catch (error) {
      console.error('Error al asignar actividad:', error);
      console.error('Response status:', error.response?.status);
      console.error('Response data:', error.response?.data);

      // Mostrar mensaje de error personalizado para estudiantes faltantes
      if (error.message && error.message.includes('No hay estudiantes matriculados')) {
        setErrors({ general: error.message });
      } else if (error.response && error.response.data) {
        setErrors({ general: `Error: ${error.response.data.mensaje || 'Error desconocido'}` });
      } else {
        setErrors({ general: error.message || 'Error al asignar la actividad' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const cargarDatos = async () => {
    setIsLoading(true);
    setErrors({});
    try {
      console.log('Iniciando carga de datos para profesor:', user.usuario_id);

      // Cargar datos de manera secuencial para mejor manejo de errores
      const actividadesResponse = await axios.get(`/api/actividades/profesor/?user_id=${user.usuario_id}`);
      console.log('Actividades cargadas:', actividadesResponse.data.length);

      const cursosResponse = await axios.get('/api/cursos/');
      console.log('Cursos cargados:', cursosResponse.data.length);

      const tiposResponse = await axios.get('/api/tipos-actividad/');
      console.log('Tipos cargados:', tiposResponse.data.length);

      setActividades(actividadesResponse.data);
      setCursos(cursosResponse.data);
      setTiposActividad(tiposResponse.data);

      console.log('Datos cargados exitosamente');

    } catch (error) {
      console.error('Error detallado al cargar datos:', error);
      console.error('Response status:', error.response?.status);
      console.error('Response data:', error.response?.data);

      if (error.response) {
        // Error de respuesta del servidor
        if (error.response.status === 403) {
          setErrors({ general: 'No tienes permisos para ver las actividades. Verifica que seas profesor de algún curso.' });
        } else if (error.response.status === 404) {
          setErrors({ general: 'No se encontraron actividades. Crea tu primera actividad.' });
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

  const handleEditActivity = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const formDataToSend = new FormData();
      formDataToSend.append('titulo', formData.titulo);
      formDataToSend.append('descripcion', formData.descripcion);
      formDataToSend.append('tipo', formData.tipo);
      formDataToSend.append('curso', formData.curso);
      formDataToSend.append('estado', formData.estado);
      formDataToSend.append('user_id', user.usuario_id);
      
      if (formData.fecha_limite) {
        formDataToSend.append('fecha_limite', formData.fecha_limite);
      }
      
      if (formData.recurso) {
        formDataToSend.append('recurso', formData.recurso);
      }

      const response = await axios.put(
        `http://localhost:3000/api/actividades/${selectedActivity.id}/gestionar/`, 
        formDataToSend,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          }
        }
      );
      
      setSuccessMessage('Actividad actualizada exitosamente');
      setShowEditModal(false);
      setSelectedActivity(null);
      cargarDatos();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al actualizar actividad:', error);
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Error al actualizar la actividad' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteActivity = async (actividadId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar esta actividad? Esta acción no se puede deshacer.')) {
      return;
    }
    setIsLoading(true);
    try {
      await axios.delete(`/api/actividades/${actividadId}/gestionar/?user_id=${user.usuario_id}`);
      
      setSuccessMessage('Actividad eliminada exitosamente');
      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al eliminar actividad:', error);
      if (error.response && error.response.data) {
        setErrors({ general: error.response.data.mensaje });
      } else {
        setErrors({ general: 'Error al eliminar la actividad' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const openEditModal = (actividad) => {
    setSelectedActivity(actividad);
    setFormData({
      titulo: actividad.titulo,
      descripcion: actividad.descripcion,
      tipo: actividad.tipo,
      curso: actividad.curso,
      fecha_limite: actividad.fecha_limite || '',
      estado: actividad.estado,
      recurso: null // No mostrar archivo actual, solo permitir cambio
    });
    setErrors({});
    setShowEditModal(true);
  };

  const handleChange = (e) => {
    const { name, value, type, files } = e.target;
    
    if (type === 'file') {
      setFormData(prev => ({
        ...prev,
        [name]: files[0]
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };

  const handleFiltroChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const canEditActivity = (actividad) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor') {
      // Verificar si el profesor es dueño del curso de la actividad
      const curso = cursos.find(c => c.id === actividad.curso);
      return curso && curso.profesor === user.usuario_id;
    }
    return false;
  };

  const canDeleteActivity = (actividad) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor') {
      const curso = cursos.find(c => c.id === actividad.curso);
      return curso && curso.profesor === user.usuario_id;
    }
    return false;
  };

  // Filtrar actividades según los filtros aplicados
  const actividadesFiltradas = actividades.filter(actividad => {
    const curso = cursos.find(c => c.id === actividad.curso);
    const cumpleCurso = !filtros.curso || actividad.curso.toString() === filtros.curso;
    const cumpleTipo = !filtros.tipo || actividad.tipo === filtros.tipo;
    const cumpleBusqueda = !filtros.busqueda || 
      actividad.titulo.toLowerCase().includes(filtros.busqueda.toLowerCase()) ||
      actividad.descripcion.toLowerCase().includes(filtros.busqueda.toLowerCase());
    
    return cumpleCurso && cumpleTipo && cumpleBusqueda;
  });

  const getTipoLabel = (tipo) => {
    const tipoObj = tiposActividad.find(t => t.value === tipo);
    return tipoObj ? tipoObj.label : tipo;
  };

  const getCursoNombre = (cursoId) => {
    const curso = cursos.find(c => c.id === cursoId);
    return curso ? curso.nombre : 'Curso no encontrado';
  };

  const getEstadoColor = (estado) => {
    switch (estado) {
      case 'pendiente': return '#ffc107';
      case 'completada': return '#28a745';
      case 'en_revision': return '#17a2b8';
      default: return '#6c757d';
    }
  };

  const getEstadoLabel = (estado) => {
    switch (estado) {
      case 'pendiente': return 'Pendiente';
      case 'completada': return 'Completada';
      case 'en_revision': return 'En Revisión';
      default: return estado;
    }
  };

  useEffect(() => {
    if (user && user.usuario_id) {
      console.log('Usuario cargado:', user);
      cargarDatos();
    } else {
      console.log('Usuario no disponible aún');
    }
  }, [user]);

  return (
    <div className="activity-management">
      <div className="management-header">
        <div>
          <h2>Gestión de Actividades</h2>
          <p>
            {user.rol === 'profesor' 
              ? 'Como profesor, puedes gestionar actividades de tus cursos' 
              : 'Como administrador, puedes gestionar todas las actividades'
            }
          </p>
        </div>
        {(user.rol === 'profesor' || user.rol === 'administrador') && (
          <button className="create-activity-btn" onClick={onAddActivity}>
            <span className="btn-icon">📝➕</span>
            Nueva Actividad
          </button>
        )}
      </div>

      {/* Filtros */}
      <div className="filters-section">
        <div className="filters-grid">
          <div className="filter-group">
            <label>Buscar:</label>
            <input
              type="text"
              name="busqueda"
              value={filtros.busqueda}
              onChange={handleFiltroChange}
              placeholder="Buscar por título o descripción..."
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Curso:</label>
            <select
              name="curso"
              value={filtros.curso}
              onChange={handleFiltroChange}
              className="filter-select"
            >
              <option value="">Todos los cursos</option>
              {cursos.map(curso => (
                <option key={curso.id} value={curso.id}>
                  {curso.nombre}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label>Tipo:</label>
            <select
              name="tipo"
              value={filtros.tipo}
              onChange={handleFiltroChange}
              className="filter-select"
            >
              <option value="">Todos los tipos</option>
              {tiposActividad.map(tipo => (
                <option key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <button 
              className="clear-filters-btn"
              onClick={() => setFiltros({ curso: '', tipo: '', busqueda: '' })}
            >
              Limpiar Filtros
            </button>
          </div>
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
                <div className="activity-title-section">
                  <h3>{actividad.titulo}</h3>
                  <div className="activity-meta">
                    <span className="activity-type">{getTipoLabel(actividad.tipo)}</span>
                    <span 
                      className="activity-status"
                      style={{ backgroundColor: getEstadoColor(actividad.estado) }}
                    >
                      {getEstadoLabel(actividad.estado)}
                    </span>
                  </div>
                </div>
                
                <div className="activity-actions">
                  {canEditActivity(actividad) && (
                    <button 
                      className="edit-btn"
                      onClick={() => openEditModal(actividad)}
                      title="Editar actividad"
                    >
                      ✏️
                    </button>
                  )}
                  {canEditActivity(actividad) && (
                    <button 
                      className="assign-btn"
                      onClick={() => openAssignModal(actividad)}
                      title="Asignar a estudiantes"
                    >
                      👥
                    </button>
                  )}
                  {canDeleteActivity(actividad) && (
                    <button 
                      className="delete-btn"
                      onClick={() => handleDeleteActivity(actividad.id)}
                      title="Eliminar actividad"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
              
              <div className="activity-content">
                <p className="activity-description">{actividad.descripcion}</p>
                
                <div className="activity-info">
                  <div className="info-item">
                    <span className="info-label">Curso:</span>
                    <span className="info-value">{getCursoNombre(actividad.curso)}</span>
                  </div>
                  
                  {actividad.fecha_limite && (
                    <div className="info-item">
                      <span className="info-label">Fecha límite:</span>
                      <span className="info-value">
                        {new Date(actividad.fecha_limite).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                  
                  <div className="info-item">
                    <span className="info-label">Creado:</span>
                    <span className="info-value">
                      {new Date(actividad.fecha_creacion).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {actividadesFiltradas.length === 0 && (
            <div className="empty-state">
              <p>
                {actividades.length === 0 
                  ? 'No hay actividades para mostrar' 
                  : 'No se encontraron actividades con los filtros aplicados'
                }
              </p>
              {(user.rol === 'profesor' || user.rol === 'administrador') && (
                <button className="create-activity-btn" onClick={onAddActivity}>
                  Crear primera actividad
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Modal Editar Actividad */}
      {showEditModal && selectedActivity && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Editar Actividad: {selectedActivity.titulo}</h3>
              <button className="close-btn" onClick={() => setShowEditModal(false)}>✕</button>
            </div>

            <form onSubmit={handleEditActivity} className="activity-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Título de la Actividad *</label>
                  <input
                    type="text"
                    name="titulo"
                    value={formData.titulo}
                    onChange={handleChange}
                    required
                    className={errors.titulo ? 'error' : ''}
                  />
                  {errors.titulo && <span className="error-text">{errors.titulo}</span>}
                </div>

                <div className="form-group">
                  <label>Tipo de Actividad *</label>
                  <select
                    name="tipo"
                    value={formData.tipo}
                    onChange={handleChange}
                    required
                    className={errors.tipo ? 'error' : ''}
                  >
                    {tiposActividad.map(tipo => (
                      <option key={tipo.value} value={tipo.value}>
                        {tipo.label}
                      </option>
                    ))}
                  </select>
                  {errors.tipo && <span className="error-text">{errors.tipo}</span>}
                </div>
              </div>

              <div className="form-group">
                <label>Descripción *</label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleChange}
                  required
                  className={errors.descripcion ? 'error' : ''}
                  rows="4"
                />
                {errors.descripcion && <span className="error-text">{errors.descripcion}</span>}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Curso *</label>
                  <select
                    name="curso"
                    value={formData.curso}
                    onChange={handleChange}
                    required
                    className={errors.curso ? 'error' : ''}
                  >
                    <option value="">Seleccionar curso</option>
                    {cursos.map(curso => (
                      <option key={curso.id} value={curso.id}>
                        {curso.nombre}
                      </option>
                    ))}
                  </select>
                  {errors.curso && <span className="error-text">{errors.curso}</span>}
                </div>

                <div className="form-group">
                  <label>Estado</label>
                  <select
                    name="estado"
                    value={formData.estado}
                    onChange={handleChange}
                    className={errors.estado ? 'error' : ''}
                  >
                    <option value="pendiente">Pendiente</option>
                    <option value="completada">Completada</option>
                    <option value="en_revision">En Revisión</option>
                  </select>
                  {errors.estado && <span className="error-text">{errors.estado}</span>}
                </div>
              </div>

              <div className="form-group">
                <label>Fecha Límite (Opcional)</label>
                <input
                  type="date"
                  name="fecha_limite"
                  value={formData.fecha_limite}
                  onChange={handleChange}
                  className={errors.fecha_limite ? 'error' : ''}
                />
                {errors.fecha_limite && <span className="error-text">{errors.fecha_limite}</span>}
              </div>

              <div className="form-group">
                <label>Nuevo Archivo de Recurso (Opcional)</label>
                <input
                  type="file"
                  name="recurso"
                  onChange={handleChange}
                  className={errors.recurso ? 'error' : ''}
                  accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.mp4,.mp3"
                />
                <small className="file-help">
                  Dejar vacío para mantener el archivo actual
                </small>
                {errors.recurso && <span className="error-text">{errors.recurso}</span>}
              </div>

              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowEditModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="submit-btn" disabled={isLoading}>
                  {isLoading ? 'Actualizando...' : 'Actualizar Actividad'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Asignar Actividad */}
      {showAssignModal && selectedActivityForAssign && (
        <div className="modal-overlay">
          <div className="modal-content medium">
            <div className="modal-header">
              <h3>Asignar: {selectedActivityForAssign.titulo}</h3>
              <button className="close-btn" onClick={() => setShowAssignModal(false)}>✕</button>
            </div>

            <div className="assign-content">
              <div className="assign-options">
                <label className="assign-option">
                  <input
                    type="checkbox"
                    checked={assignToAll}
                    onChange={(e) => {
                      setAssignToAll(e.target.checked);
                      if (e.target.checked) setSelectedEstudiantes([]);
                    }}
                  />
                  <span>Asignar a todos los estudiantes del curso</span>
                </label>
              </div>

              {!assignToAll && (
                <div className="students-selection">
                  <h4>Seleccionar estudiantes específicos:</h4>
                  <div className="students-checkboxes">
                    {estudiantes.map(inscripcion => (
                      <label key={inscripcion.id} className="student-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedEstudiantes.some(s => s.id === inscripcion.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedEstudiantes(prev => [...prev, inscripcion]);
                            } else {
                              setSelectedEstudiantes(prev => prev.filter(s => s.id !== inscripcion.id));
                            }
                          }}
                        />
                        <span>{inscripcion.estudiante.nombre_completo}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              <div className="assign-actions">
                <button 
                  type="button" 
                  className="cancel-btn"
                  onClick={() => setShowAssignModal(false)}
                >
                  Cancelar
                </button>
                <button 
                  className="assign-btn-modal"
                  onClick={handleAssignActivity}
                  disabled={isLoading || (!assignToAll && selectedEstudiantes.length === 0)}
                >
                  {isLoading ? 'Asignando...' : 
                   assignToAll ? 'Asignar a Todo el Curso' : 
                   `Asignar a ${selectedEstudiantes.length} Estudiante${selectedEstudiantes.length !== 1 ? 's' : ''}`}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityManagement;
