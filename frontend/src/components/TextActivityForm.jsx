import React, { useState, useEffect } from 'react';
import { getCourses, createTextActivity } from '../services/activities.service';
import QuestionForm from './QuestionForm';
import './TextActivityForm.css';

const TextActivityForm = ({ 
  curso, 
  onActivityCreated, 
  onCancel,
  initialData = {} 
}) => {
  const [formData, setFormData] = useState({
    titulo: initialData.titulo || '',
    descripcion: initialData.descripcion || '',
    curso: curso || '',
    tiempo_limite_minutos: initialData.tiempo_limite_minutos || '',
    preguntas: initialData.preguntas || []
  });

  const [cursos, setCursos] = useState([]);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (curso) {
      setFormData(prev => ({ ...prev, curso: curso }));
    }
  }, [curso]);

  const loadCourses = async () => {
    try {
      const response = await getCourses();
      setCursos(response.data);
      
      if (!formData.curso && response.data.length > 0) {
        setFormData(prev => ({ ...prev, curso: response.data[0].id }));
      }
    } catch (err) {
      console.error('Error loading courses:', err);
      setErrors(prev => ({ ...prev, cursos: 'Error al cargar cursos' }));
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Validación especial para tiempo límite
    if (name === 'tiempo_limite_minutos') {
      const numValue = value === '' ? '' : parseInt(value);
      if (value === '' || (numValue >= 5 && numValue <= 180)) {
        setFormData(prev => ({ ...prev, [name]: numValue }));
      }
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
    
    // Limpiar error del campo
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleAddQuestion = () => {
    const newQuestion = {
      id: Date.now(),
      enunciado: '',
      orden: formData.preguntas.length + 1,
      opciones: [
        { id: 1, texto: '', es_correcta: false, orden: 1 },
        { id: 2, texto: '', es_correcta: false, orden: 2 }
      ]
    };
    
    setFormData(prev => ({
      ...prev,
      preguntas: [...prev.preguntas, newQuestion]
    }));
  };

  const handleQuestionChange = (questionId, field, value) => {
    setFormData(prev => ({
      ...prev,
      preguntas: prev.preguntas.map(q => 
        q.id === questionId ? { ...q, [field]: value } : q
      )
    }));
  };

  const handleOptionChange = (questionId, optionId, field, value) => {
    setFormData(prev => ({
      ...prev,
      preguntas: prev.preguntas.map(q => {
        if (q.id === questionId) {
          return {
            ...q,
            opciones: q.opciones.map(o => {
              // Si es cambio de es_correcta a true, desmarcar todas las otras
              if (field === 'es_correcta' && value === true) {
                return {
                  ...o,
                  es_correcta: o.id === optionId
                };
              }
              // Cambio normal de otros campos
              return o.id === optionId ? { ...o, [field]: value } : o;
            })
          };
        }
        return q;
      })
    }));
  };

  const handleAddOption = (questionId) => {
    setFormData(prev => ({
      ...prev,
      preguntas: prev.preguntas.map(q => {
        if (q.id === questionId) {
          const newOption = {
            id: Date.now(),
            texto: '',
            es_correcta: false,
            orden: q.opciones.length + 1
          };
          return { ...q, opciones: [...q.opciones, newOption] };
        }
        return q;
      })
    }));
  };

  const handleRemoveOption = (questionId, optionId) => {
    setFormData(prev => ({
      ...prev,
      preguntas: prev.preguntas.map(q => {
        if (q.id === questionId) {
          const filteredOptions = q.opciones.filter(o => o.id !== optionId);
          return {
            ...q,
            opciones: filteredOptions.map((o, index) => ({ ...o, orden: index + 1 }))
          };
        }
        return q;
      })
    }));
  };

  const handleRemoveQuestion = (questionId) => {
    setFormData(prev => ({
      ...prev,
      preguntas: prev.preguntas.filter(q => q.id !== questionId)
    }));
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

    // Validar tiempo límite si se proporciona
    if (formData.tiempo_limite_minutos !== '') {
      const timeLimit = parseInt(formData.tiempo_limite_minutos);
      if (timeLimit < 5 || timeLimit > 180) {
        newErrors.tiempo_limite_minutos = 'El tiempo límite debe estar entre 5 y 180 minutos';
      }
    }

    if (formData.preguntas.length === 0) {
      newErrors.preguntas = 'Debe agregar al menos una pregunta';
    } else {
      formData.preguntas.forEach((q, qIndex) => {
        if (!q.enunciado.trim()) {
          newErrors[`pregunta_${qIndex}_enunciado`] = 'El enunciado es requerido';
        }

        if (q.opciones.length < 2) {
          newErrors[`pregunta_${qIndex}_opciones`] = 'Debe agregar al menos 2 opciones';
        } else {
          const correctOptions = q.opciones.filter(o => o.es_correcta);
          if (correctOptions.length !== 1) {
            newErrors[`pregunta_${qIndex}_correcta`] = 'Debe seleccionar exactamente una respuesta correcta';
          }

          q.opciones.forEach((o, oIndex) => {
            if (!o.texto.trim()) {
              newErrors[`pregunta_${qIndex}_opcion_${oIndex}`] = 'El texto de la opción es requerido';
            }
          });
        }
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      // Preparar datos para enviar
      const dataToSend = {
        ...formData,
        // Solo incluir tiempo_limite_minutos si tiene valor
        ...(formData.tiempo_limite_minutos && { tiempo_limite_minutos: parseInt(formData.tiempo_limite_minutos) })
      };

      const response = await createTextActivity(dataToSend);
      
      onActivityCreated && onActivityCreated(response.data);
      
    } catch (err) {
      console.error('Error creating text activity:', err);
      if (err.response?.data) {
        const backendErrors = {};
        Object.keys(err.response.data).forEach(key => {
          backendErrors[key] = Array.isArray(err.response.data[key]) 
            ? err.response.data[key][0] 
            : err.response.data[key];
        });
        setErrors(backendErrors);
      } else {
        setErrors({ submit: 'Error al crear la actividad' });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="text-activity-form">
      <div className="form-header">
        <h3>Actividad de Texto</h3>
        <button type="button" onClick={onCancel} className="cancel-button">
          Cancelar
        </button>
      </div>

      <form onSubmit={handleSubmit} className="activity-form">
        {/* Información básica */}
        <div className="form-section">
          <h4>Información básica</h4>
          
          <div className="form-group">
            <label htmlFor="titulo">Título *</label>
            <input
              type="text"
              id="titulo"
              name="titulo"
              value={formData.titulo}
              onChange={handleInputChange}
              className={`form-input ${errors.titulo ? 'error' : ''}`}
              placeholder="Ingrese el título de la actividad"
            />
            {errors.titulo && <span className="error-message">{errors.titulo}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="descripcion">Descripción *</label>
            <textarea
              id="descripcion"
              name="descripcion"
              value={formData.descripcion}
              onChange={handleInputChange}
              className={`form-input ${errors.descripcion ? 'error' : ''}`}
              placeholder="Describa la actividad"
              rows={3}
            />
            {errors.descripcion && <span className="error-message">{errors.descripcion}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="curso">Curso *</label>
            <select
              id="curso"
              name="curso"
              value={formData.curso}
              onChange={handleInputChange}
              className={`form-input ${errors.curso ? 'error' : ''}`}
            >
              <option value="">Seleccione un curso</option>
              {cursos.map(curso => (
                <option key={curso.id} value={curso.id}>
                  {curso.nombre}
                </option>
              ))}
            </select>
            {errors.curso && <span className="error-message">{errors.curso}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="tiempo_limite_minutos">
              Tiempo límite (opcional)
            </label>
            <div className="time-input-group">
              <input
                type="number"
                id="tiempo_limite_minutos"
                name="tiempo_limite_minutos"
                value={formData.tiempo_limite_minutos}
                onChange={handleInputChange}
                className={`form-input ${errors.tiempo_limite_minutos ? 'error' : ''}`}
                placeholder="Ej: 30"
                min="5"
                max="180"
              />
              <span className="time-unit">minutos</span>
            </div>
            <small className="form-help">
              Entre 5 y 180 minutos. Si no se establece, no habrá límite de tiempo.
            </small>
            {errors.tiempo_limite_minutos && <span className="error-message">{errors.tiempo_limite_minutos}</span>}
          </div>
        </div>

        {/* Preguntas */}
        <div className="form-section">
          <div className="section-header">
            <h4>Preguntas y respuestas ({formData.preguntas.length})</h4>
            <button
              type="button"
              onClick={handleAddQuestion}
              className="add-question-btn"
            >
              + Agregar pregunta
            </button>
          </div>
          
          {errors.preguntas && <span className="error-message">{errors.preguntas}</span>}
          
          <div className="questions-container">
            {formData.preguntas.length > 0 ? (
              formData.preguntas.map((question, qIndex) => (
                <QuestionForm
                  key={question.id}
                  question={question}
                  questionIndex={qIndex}
                  onQuestionChange={handleQuestionChange}
                  onOptionChange={handleOptionChange}
                  onAddOption={handleAddOption}
                  onRemoveOption={handleRemoveOption}
                  onRemoveQuestion={handleRemoveQuestion}
                />
              ))
            ) : (
              <div className="no-questions-message">
                No hay preguntas agregadas. Haz clic en "+ Agregar pregunta" para crear una.
              </div>
            )}
          </div>
        </div>

        {/* Resumen */}
        <div className="form-section summary-section">
          <h4>Resumen de la actividad</h4>
          <div className="summary-grid">
            <div className="summary-item">
              <span className="summary-label">Título:</span>
              <span className="summary-value">{formData.titulo || 'Sin título'}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Descripción:</span>
              <span className="summary-value">{formData.descripcion || 'Sin descripción'}</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Curso:</span>
              <span className="summary-value">
                {cursos.find(c => c.id === formData.curso)?.nombre || 'No seleccionado'}
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Tiempo límite:</span>
              <span className="summary-value">
                {formData.tiempo_limite_minutos 
                  ? `${formData.tiempo_limite_minutos} minutos` 
                  : 'Sin límite'
                }
              </span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Preguntas:</span>
              <span className="summary-value">{formData.preguntas.length} preguntas</span>
            </div>
            <div className="summary-item">
              <span className="summary-label">Opciones totales:</span>
              <span className="summary-value">
                {formData.preguntas.reduce((total, q) => total + q.opciones.length, 0)} opciones
              </span>
            </div>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            className="btn btn-secondary"
            disabled={isSubmitting}
          >
            Cancelar
          </button>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Creando...' : 'Crear actividad'}
          </button>
        </div>
        
        {errors.submit && <span className="error-message">{errors.submit}</span>}
      </form>
    </div>
  );
};

export default TextActivityForm;
