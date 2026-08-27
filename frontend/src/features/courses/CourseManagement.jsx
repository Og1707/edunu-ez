import React, { useState, useEffect } from 'react';
import axios from '../../utils/axiosConfig';
import {
  getCourses,
  getUsers,
  createCourse,
  updateCourse,
  deleteCourse,
  getCourseStudents,
  addStudentToCourse,
  removeStudentFromCourse,
} from '../../services/courses.service';
import './CourseManagement.css';

const CourseManagement = ({ user }) => {
  const [cursos, setCursos] = useState([]);
  const [profesores, setProfesores] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showStudentsModal, setShowStudentsModal] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [estudiantes, setEstudiantes] = useState([]);
  const [estudiantesDisponibles, setEstudiantesDisponibles] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  const [formData, setFormData] = useState({
    nombre: '',
    descripcion: '',
    profesor: ''
  });

  useEffect(() => {
    cargarCursos();
    if (user.rol === 'administrador') {
      cargarProfesores();
    }
  }, []);

  const cargarCursos = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/cursos/');
      setCursos(response.data);
    } catch (error) {
      console.error('Error al cargar cursos:', error);
      setErrors({ general: 'Error al cargar la lista de cursos' });
    } finally {
      setIsLoading(false);
    }
  };

  const cargarProfesores = async () => {
    try {
      const response = await axios.get('/api/usuarios/listar/');
      const profesoresList = response.data.filter(u => u.rol === 'profesor');
      setProfesores(profesoresList);
    } catch (error) {
      console.error('Error al cargar profesores:', error);
    }
  };

  const cargarEstudiantesDisponibles = async () => {
    try {
      const response = await axios.get('/api/usuarios/listar/');
      const estudiantesList = response.data.filter(u => u.rol === 'estudiante');
      setEstudiantesDisponibles(estudiantesList);
    } catch (error) {
      console.error('Error al cargar estudiantes:', error);
    }
  };

  const cargarEstudiantesCurso = async (cursoId) => {
    try {
      const response = await axios.get(`/api/estudiantes-curso/?curso_id=${cursoId}`);
      setEstudiantes(response.data.estudiantes);
    } catch (error) {
      console.error('Error al cargar estudiantes del curso:', error);
    }
  };

  const handleCreateCourse = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const dataToSend = {
        ...formData,
        profesor: user.rol === 'profesor' ? user.usuario_id : formData.profesor
      };

      const response = await axios.post('/api/cursos/crear/', dataToSend);
      
      // Actualizar la lista de cursos con el nuevo curso
      setCursos(prevCursos => [...prevCursos, response.data]);
      
      setSuccessMessage('Curso creado exitosamente');
      setShowCreateModal(false);
      setFormData({ nombre: '', descripcion: '', profesor: '' });

    } catch (error) {
      console.error('Error al crear curso:', error);
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Error al crear el curso' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditCourse = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const dataToSend = { ...formData };

      const response = await axios.put(`/api/cursos/${selectedCourse.id}/gestionar/`, dataToSend);
      
      setSuccessMessage('Curso actualizado exitosamente');
      setShowEditModal(false);
      setSelectedCourse(null);
      cargarCursos();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al actualizar curso:', error);
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Error al actualizar el curso' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCourse = async (cursoId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este curso? Esta acción no se puede deshacer.')) {
      return;
    }

    setIsLoading(true);
    try {
      await axios.delete(`/api/cursos/${cursoId}/gestionar/`);
      
      setSuccessMessage('Curso eliminado exitosamente');
      cargarCursos();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al eliminar curso:', error);
      setErrors({ general: 'Error al eliminar el curso' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddStudentToCourse = async (estudianteId) => {
    try {
      const dataToSend = {
        estudiante_id: estudianteId,
        curso_id: selectedCourse.id,
      };

      await axios.post('/api/estudiantes-curso/agregar/', dataToSend);
      
      setSuccessMessage('Estudiante agregado al curso exitosamente');
      cargarEstudiantesCurso(selectedCourse.id);
      cargarEstudiantesDisponibles();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al agregar estudiante:', error);
      if (error.response && error.response.data) {
        setErrors({ general: error.response.data.mensaje });
      } else {
        setErrors({ general: 'Error al agregar estudiante al curso' });
      }
    }
  };

  const handleRemoveStudentFromCourse = async (inscripcionId) => {
    if (!window.confirm('¿Estás seguro de que deseas remover este estudiante del curso?')) {
      return;
    }

    try {
      await axios.delete(`/api/estudiantes-curso/${inscripcionId}/remover/`);
      
      setSuccessMessage('Estudiante removido del curso exitosamente');
      cargarEstudiantesCurso(selectedCourse.id);
      cargarEstudiantesDisponibles();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al remover estudiante:', error);
      setErrors({ general: 'Error al remover estudiante del curso' });
    }
  };

  const openCreateModal = () => {
    setFormData({ nombre: '', descripcion: '', profesor: '' });
    setErrors({});
    setShowCreateModal(true);
  };

  const openEditModal = (curso) => {
    setSelectedCourse(curso);
    setFormData({
      nombre: curso.nombre,
      descripcion: curso.descripcion,
      profesor: curso.profesor || ''
    });
    setErrors({});
    setShowEditModal(true);
  };

  const openStudentsModal = (curso) => {
    setSelectedCourse(curso);
    cargarEstudiantesCurso(curso.id);
    cargarEstudiantesDisponibles();
    setShowStudentsModal(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const canEditCourse = (curso) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor' && curso.profesor === user.usuario_id) return true;
    return false;
  };

  const canDeleteCourse = (curso) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor' && curso.profesor === user.usuario_id) return true;
    return false;
  };

  const canManageStudents = (curso) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor' && curso.profesor === user.usuario_id) return true;
    return false;
  };

  // Filtrar estudiantes disponibles (que no estén ya en el curso)
  const getEstudiantesDisponiblesParaCurso = () => {
    const estudiantesEnCurso = estudiantes.map(e => e.estudiante.id);
    return estudiantesDisponibles.filter(e => !estudiantesEnCurso.includes(e.id));
  };

  return (
    <div className="course-management">
      <div className="management-header">
        <div>
          <h2>Gestión de Cursos</h2>
          <p>
            {user.rol === 'profesor' 
              ? 'Como profesor, puedes gestionar tus cursos asignados' 
              : 'Como administrador, puedes gestionar todos los cursos'
            }
          </p>
        </div>
        <button className="create-course-btn" onClick={openCreateModal}>
          <span className="btn-icon">📚➕</span>
          Crear Curso
        </button>
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
          <p>Cargando cursos...</p>
        </div>
      ) : (
        <div className="courses-grid">
          {cursos.map(curso => (
            <div key={curso.id} className="course-card">
              <div className="course-header">
                <h3>{curso.nombre}</h3>
                <div className="course-actions">
                  {canManageStudents(curso) && (
                    <button 
                      className="students-btn"
                      onClick={() => openStudentsModal(curso)}
                      title="Gestionar estudiantes"
                    >
                      👥
                    </button>
                  )}
                  {canEditCourse(curso) && (
                    <button 
                      className="edit-btn"
                      onClick={() => openEditModal(curso)}
                      title="Editar curso"
                    >
                      ✏️
                    </button>
                  )}
                  {canDeleteCourse(curso) && (
                    <button 
                      className="delete-btn"
                      onClick={() => handleDeleteCourse(curso.id)}
                      title="Eliminar curso"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              </div>
              
              <div className="course-content">
                <p className="course-description">{curso.descripcion}</p>
                
                <div className="course-info">
                  <div className="info-item">
                    <span className="info-label">Profesor:</span>
                    <span className="info-value">
                      {curso.profesor_nombre || 'Sin asignar'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {cursos.length === 0 && (
            <div className="empty-state">
              <p>No hay cursos para mostrar</p>
              <button className="create-course-btn" onClick={openCreateModal}>
                Crear primer curso
              </button>
            </div>
          )}
        </div>
      )}

      {/* Modal Crear Curso */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Crear Nuevo Curso</h3>
              <button className="close-btn" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>

            <form onSubmit={handleCreateCourse} className="course-form">
              <div className="form-group">
                <label>Nombre del Curso *</label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                  className={errors.nombre ? 'error' : ''}
                  placeholder="Ej: Matemáticas Básicas"
                />
                {errors.nombre && <span className="error-text">{errors.nombre}</span>}
              </div>

              <div className="form-group">
                <label>Descripción *</label>
                <textarea
                  name="descripcion"
                  value={formData.descripcion}
                  onChange={handleChange}
                  required
                  className={errors.descripcion ? 'error' : ''}
                  placeholder="Describe el contenido y objetivos del curso..."
                  rows="4"
                />
                {errors.descripcion && <span className="error-text">{errors.descripcion}</span>}
              </div>

              {user.rol === 'administrador' && (
                <div className="form-group">
                  <label>Profesor Asignado</label>
                  <select
                    name="profesor"
                    value={formData.profesor}
                    onChange={handleChange}
                    className={errors.profesor ? 'error' : ''}
                  >
                    <option value="">Seleccionar profesor (opcional)</option>
                    {profesores.map(profesor => (
                      <option key={profesor.id} value={profesor.id}>
                        {profesor.nombre_completo} ({profesor.username})
                      </option>
                    ))}
                  </select>
                  {errors.profesor && <span className="error-text">{errors.profesor}</span>}
                </div>
              )}

              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowCreateModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="submit-btn" disabled={isLoading}>
                  {isLoading ? 'Creando...' : 'Crear Curso'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Editar Curso */}
      {showEditModal && selectedCourse && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Editar Curso: {selectedCourse.nombre}</h3>
              <button className="close-btn" onClick={() => setShowEditModal(false)}>✕</button>
            </div>

            <form onSubmit={handleEditCourse} className="course-form">
              <div className="form-group">
                <label>Nombre del Curso *</label>
                <input
                  type="text"
                  name="nombre"
                  value={formData.nombre}
                  onChange={handleChange}
                  required
                  className={errors.nombre ? 'error' : ''}
                />
                {errors.nombre && <span className="error-text">{errors.nombre}</span>}
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

              {user.rol === 'administrador' && (
                <div className="form-group">
                  <label>Profesor Asignado</label>
                  <select
                    name="profesor"
                    value={formData.profesor}
                    onChange={handleChange}
                    className={errors.profesor ? 'error' : ''}
                  >
                    <option value="">Sin profesor asignado</option>
                    {profesores.map(profesor => (
                      <option key={profesor.id} value={profesor.id}>
                        {profesor.nombre_completo} ({profesor.username})
                      </option>
                    ))}
                  </select>
                  {errors.profesor && <span className="error-text">{errors.profesor}</span>}
                </div>
              )}

              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowEditModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="submit-btn" disabled={isLoading}>
                  {isLoading ? 'Actualizando...' : 'Actualizar Curso'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Gestionar Estudiantes */}
      {showStudentsModal && selectedCourse && (
        <div className="modal-overlay">
          <div className="modal-content large">
            <div className="modal-header">
              <h3>Estudiantes en: {selectedCourse.nombre}</h3>
              <button className="close-btn" onClick={() => setShowStudentsModal(false)}>✕</button>
            </div>

            <div className="students-management">
              <div className="students-section">
                <h4>Estudiantes Inscritos ({estudiantes.length})</h4>
                <div className="students-list">
                  {estudiantes.map(inscripcion => (
                    <div key={inscripcion.id} className="student-item">
                      <div className="student-info">
                        <span className="student-avatar">👨‍🎓</span>
                        <div>
                          <div className="student-name">{inscripcion.estudiante.nombre_completo}</div>
                          <div className="student-username">@{inscripcion.estudiante.username}</div>
                        </div>
                      </div>
                      <button 
                        className="remove-btn"
                        onClick={() => handleRemoveStudentFromCourse(inscripcion.id)}
                        title="Remover del curso"
                      >
                        ❌
                      </button>
                    </div>
                  ))}
                  
                  {estudiantes.length === 0 && (
                    <div className="empty-students">
                      <p>No hay estudiantes inscritos en este curso</p>
                    </div>
                  )}
                </div>
              </div>

              <div className="available-students-section">
                <h4>Agregar Estudiantes</h4>
                <div className="available-students-list">
                  {getEstudiantesDisponiblesParaCurso().map(estudiante => (
                    <div key={estudiante.id} className="available-student-item">
                      <div className="student-info">
                        <span className="student-avatar">👨‍🎓</span>
                        <div>
                          <div className="student-name">{estudiante.nombre_completo}</div>
                          <div className="student-username">@{estudiante.username}</div>
                        </div>
                      </div>
                      <button 
                        className="add-btn"
                        onClick={() => handleAddStudentToCourse(estudiante.id)}
                        title="Agregar al curso"
                      >
                        ➕
                      </button>
                    </div>
                  ))}
                  
                  {getEstudiantesDisponiblesParaCurso().length === 0 && (
                    <div className="empty-students">
                      <p>No hay más estudiantes disponibles para agregar</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseManagement;
