import React, { useState, useEffect } from 'react';
import axios from '../../utils/axiosConfig';
import {
  getCourses,
  getActivityTypes,
  getScienceSubjects,
  createActivity,
  assignActivityToCourse,
} from '../../services/activities.service';
import ScienceQuizGame from '../games/ScienceQuizGame';
import GameExplorer from '../games/GameExplorer';
import './AddActivity.css';

const AddActivity = ({ onClose, onActivityAdded }) => {
  const [formData, setFormData] = useState({
    titulo: '',
    descripcion: '',
    tipo: 'otro',
    curso: '',
    fecha_limite: '',
    recurso: null,
    tema_wikipedia: '',
    materia_ciencias: '',
    asignar_al_curso: true  // Nueva opción para asignar automáticamente
  });

  const [cursos, setCursos] = useState([]);
  const [tiposActividad, setTiposActividad] = useState([]);
  const [materiasCiencias, setMateriasCiencias] = useState([]);
  const [temasSugeridos, setTemasSugeridos] = useState([]);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  const [showScienceQuiz, setShowScienceQuiz] = useState(false);
  const [showWikipediaSearch, setShowWikipediaSearch] = useState(false);
  const [wikipediaResults, setWikipediaResults] = useState([]);
  const [showGameExplorer, setShowGameExplorer] = useState(false);
  const [juegoSeleccionado, setJuegoSeleccionado] = useState(null);

  useEffect(() => {
    // Cargar cursos y tipos de actividad al montar el componente
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      const [cursosResponse, tiposResponse, materiasCienciasResponse] = await Promise.all([
        axios.get('/api/cursos/'),
        axios.get('/api/tipos-actividad/'),
        axios.get('/api/ciencias/materias/')  
      ]);

      setCursos(cursosResponse.data);
      setTiposActividad(tiposResponse.data);
      setMateriasCiencias(materiasCienciasResponse.data);
    } catch (error) {
      console.error('Error al cargar datos:', error);
      setErrors({ general: 'Error al cargar los datos necesarios' });
    }
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
    
    // Limpiar error específico cuando el usuario empiece a escribir
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.titulo.trim()) {
      newErrors.titulo = 'El título es requerido';
    }

    if (!formData.descripcion.trim()) {
      newErrors.descripcion = 'La descripción es requerida';
    }

    if (!formData.curso) {
      newErrors.curso = 'Debe seleccionar un curso';
    }

    if (!formData.tipo) {
      newErrors.tipo = 'Debe seleccionar un tipo de actividad';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});
    setSuccessMessage('');

    try {
      // Obtener información del usuario del localStorage
      const userData = JSON.parse(localStorage.getItem('user'));
      if (!userData) {
        setErrors({ general: 'Usuario no autenticado' });
        return;
      }

      // Preparar datos para enviar
      const formDataToSend = new FormData();
      formDataToSend.append('titulo', formData.titulo);
      formDataToSend.append('descripcion', formData.descripcion);
      formDataToSend.append('tipo', formData.tipo);
      formDataToSend.append('curso', formData.curso);
      formDataToSend.append('user_id', userData.usuario_id);
      
      if (formData.fecha_limite) {
        formDataToSend.append('fecha_limite', formData.fecha_limite);
      }
      
      if (formData.recurso) {
        formDataToSend.append('recurso', formData.recurso);
      }

      const response = await axios.post('/api/actividades/', formDataToSend, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      });

      const actividadCreada = response.data;
      let mensajeExito = '¡Actividad creada exitosamente!';

      // Si está marcada la opción de asignar al curso, hacer la asignación
      if (formData.asignar_al_curso && formData.curso) {
        try {
          const asignacionResponse = await axios.post('/api/asignar-actividad-curso/', {
            user_id: Number(userData.usuario_id),
            actividad_ids: [Number(actividadCreada.id)],
            curso_id: Number(formData.curso)
          });

          const asignacion = asignacionResponse.data;
          mensajeExito = `¡Actividad creada y asignada exitosamente! 
          Asignada a ${asignacion.resumen.nuevas_asignaciones} estudiantes del curso ${asignacion.curso}.`;
          
        } catch (asignacionError) {
          console.error('Error al asignar actividad:', asignacionError);
          mensajeExito = '¡Actividad creada exitosamente! Sin embargo, hubo un error al asignarla al curso.';
        }
      }

      setSuccessMessage(mensajeExito);
      
      // Limpiar formulario
      setFormData({
        titulo: '',
        descripcion: '',
        tipo: 'otro',
        curso: '',
        fecha_limite: '',
        recurso: null,
        tema_wikipedia: '',
        materia_ciencias: '',
        asignar_al_curso: true
      });

      // Notificar al componente padre
      if (onActivityAdded) {
        onActivityAdded(actividadCreada);
      }

      // Cerrar modal después de 3 segundos (más tiempo para leer el mensaje)
      setTimeout(() => {
        onClose();
      }, 3000);

    } catch (error) {
      console.error('Error al crear actividad:', error);
      
      if (error.response && error.response.data) {
        const serverErrors = error.response.data;
        if (typeof serverErrors === 'object') {
          setErrors(serverErrors);
        } else {
          setErrors({ general: serverErrors.mensaje || 'Error al crear la actividad' });
        }
      } else {
        setErrors({ general: 'Error al conectar con el servidor. Intenta nuevamente.' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Funciones para manejar juegos educativos
  const handleGameSelect = (juego) => {
    setJuegoSeleccionado(juego);
    // Auto-llenar el formulario con datos del juego
    setFormData(prev => ({
      ...prev,
      titulo: juego.titulo,
      descripcion: juego.descripcion,
      tipo: 'juego'
    }));
    setShowGameExplorer(false);
  };

  // Si se está mostrando el juego de ciencias, renderizar solo el juego
  if (showScienceQuiz) {
    return (
      <ScienceQuizGame
        tema="biologia"
        onGameComplete={(stats) => {
          console.log('Juego completado:', stats);
          setShowScienceQuiz(false);
        }}
        onClose={() => setShowScienceQuiz(false)}
      />
    );
  }

  return (
    <div className="add-activity-modal" style={{ display: showGameExplorer ? 'none !important' : 'flex' }}>
      <div className="modal-overlay" onClick={onClose} style={{ display: showGameExplorer ? 'none !important' : 'block' }}></div>
      <div className="modal-content" style={{ display: showGameExplorer ? 'none !important' : 'block' }}>
        <div className="modal-header">
          <h2>Añadir Nueva Actividad</h2>
          <button className="close-btn" onClick={onClose}>✕</button>
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

        {/* Herramientas Educativas */}
        <div className="educational-tools-section" style={{marginTop: '20px', padding: '15px', backgroundColor: '#f0f8ff', borderRadius: '8px'}}>
          <h3>🎮 Herramientas Educativas</h3>
          <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
            <button 
              type="button" 
              onClick={() => setShowGameExplorer(true)}
              style={{padding: '10px 15px', backgroundColor: '#FF6B6B', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold'}}
            >
              🎯 Explorar Juegos para Niños
            </button>
            <button 
              type="button" 
              onClick={() => setShowScienceQuiz(true)}
              style={{padding: '10px 15px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
            >
              🎮 Quiz de Ciencias
            </button>
            <button 
              type="button" 
              onClick={() => alert('Funcionalidad de Wikipedia - Próximamente!')}
              style={{padding: '10px 15px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer'}}
            >
              📚 Buscar en Wikipedia
            </button>
          </div>
          
          {/* Mostrar juego seleccionado */}
          {juegoSeleccionado && (
            <div style={{marginTop: '15px', padding: '12px', backgroundColor: '#e8f5e9', borderRadius: '8px', border: '2px solid #4CAF50'}}>
              <h4 style={{margin: '0 0 8px 0', color: '#2e7d32'}}>
                ✅ Juego Seleccionado: {juegoSeleccionado.categoria.icono} {juegoSeleccionado.titulo}
              </h4>
              <p style={{margin: '0', fontSize: '14px', color: '#388e3c'}}>
                {juegoSeleccionado.descripcion}
              </p>
              <div style={{marginTop: '8px', fontSize: '12px', color: '#4caf50'}}>
                👶 Edades: {juegoSeleccionado.edad_minima}-{juegoSeleccionado.edad_maxima} años | 
                ⏱️ Duración: {juegoSeleccionado.tiempo_estimado} min | 
                ⭐ {juegoSeleccionado.nivel_dificultad_display}
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="activity-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="titulo">Título de la Actividad *</label>
              <input
                type="text"
                id="titulo"
                name="titulo"
                value={formData.titulo}
                onChange={handleChange}
                className={errors.titulo ? 'error' : ''}
                placeholder="Ej: Sopa de letras - Matemáticas básicas"
              />
              {errors.titulo && (
                <span className="error-text">{errors.titulo}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="tipo">Tipo de Actividad *</label>
              <select
                id="tipo"
                name="tipo"
                value={formData.tipo}
                onChange={handleChange}
                className={errors.tipo ? 'error' : ''}
              >
                <option value="juego">🎮 Juego Educativo</option>
                {tiposActividad.map(tipo => (
                  <option key={tipo.value} value={tipo.value}>
                    {tipo.label}
                  </option>
                ))}
              </select>
              {errors.tipo && (
                <span className="error-text">{errors.tipo}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="descripcion">Descripción *</label>
            <textarea
              id="descripcion"
              name="descripcion"
              value={formData.descripcion}
              onChange={handleChange}
              className={errors.descripcion ? 'error' : ''}
              placeholder="Describe la actividad, objetivos y instrucciones..."
              rows="4"
            />
            {errors.descripcion && (
              <span className="error-text">{errors.descripcion}</span>
            )}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="curso">Curso *</label>
              <select
                id="curso"
                name="curso"
                value={formData.curso}
                onChange={handleChange}
                className={errors.curso ? 'error' : ''}
              >
                <option value="">Seleccionar curso</option>
                {cursos.map(curso => (
                  <option key={curso.id} value={curso.id}>
                    {curso.nombre}
                  </option>
                ))}
              </select>
              {errors.curso && (
                <span className="error-text">{errors.curso}</span>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="fecha_limite">Fecha Límite (Opcional)</label>
              <input
                type="date"
                id="fecha_limite"
                name="fecha_limite"
                value={formData.fecha_limite}
                onChange={handleChange}
                className={errors.fecha_limite ? 'error' : ''}
              />
              {errors.fecha_limite && (
                <span className="error-text">{errors.fecha_limite}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="recurso">Archivo de Recurso (Opcional)</label>
            <input
              type="file"
              id="recurso"
              name="recurso"
              onChange={handleChange}
              className={errors.recurso ? 'error' : ''}
              accept=".pdf,.doc,.docx,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.mp4,.mp3"
            />
            <small className="file-help">
              Formatos permitidos: PDF, Word, PowerPoint, imágenes, videos, audio
            </small>
            {errors.recurso && (
              <span className="error-text">{errors.recurso}</span>
            )}
          </div>

          {/* Opción para asignar automáticamente al curso */}
          <div className="form-group assignment-option">
            <div className="checkbox-container">
              <input
                type="checkbox"
                id="asignar_al_curso"
                name="asignar_al_curso"
                checked={formData.asignar_al_curso}
                onChange={(e) => setFormData(prev => ({ ...prev, asignar_al_curso: e.target.checked }))}
              />
              <label htmlFor="asignar_al_curso" className="checkbox-label">
                <strong>📋 Asignar automáticamente a todos los estudiantes del curso</strong>
              </label>
            </div>
            <small className="assignment-help">
              Si está marcado, la actividad se asignará automáticamente a todos los estudiantes del curso seleccionado.
            </small>
          </div>

          <div className="form-actions">
            <button 
              type="button" 
              className="cancel-btn"
              onClick={onClose}
            >
              Cancelar
            </button>
            <button 
              type="submit" 
              className={`submit-btn ${isLoading ? 'loading' : ''}`}
              disabled={isLoading}
            >
              {isLoading ? 'Creando...' : 'Crear Actividad'}
            </button>
          </div>
        </form>
      </div>
      
      {/* Modal del explorador de juegos */}
      {showGameExplorer && (
        <GameExplorer
          onGameSelect={handleGameSelect}
          onClose={() => setShowGameExplorer(false)}
        />
      )}
    </div>
  );
};

export default AddActivity;
