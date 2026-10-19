import React, { useState, useEffect, useCallback } from 'react';
import { createMultimediaActivity } from '../services/activities.service';
import { getCourses } from '../services/courses.service';
import QuestionForm from './QuestionForm';
import './MultimediaActivityForm.css';
import './ActivityFormModern.css';

const MultimediaActivityForm = ({ 
  curso, 
  onActivityCreated, 
  onCancel,
  initialData = {},
  onDraftChange,
  deferSubmit = false,
  submitLabel
}) => {
  const [formData, setFormData] = useState({
    titulo: initialData.titulo || '',
    descripcion: initialData.descripcion || '',
    curso: curso || '',
    asignatura: initialData.asignatura || '',
    fecha_limite: initialData.fecha_limite || '',
    preguntas: initialData.preguntas || []
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [cursos, setCursos] = useState([]);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    onDraftChange?.({ ...formData, archivo_multimedia: selectedFile });
  }, [formData, selectedFile, onDraftChange]);

  useEffect(() => () => { if (previewUrl) URL.revokeObjectURL(previewUrl); }, [previewUrl]);

  const loadCourses = useCallback(async () => {
    try {
      const response = await getCourses();
      setCursos(response.data);

      setFormData(prev => prev.curso || response.data.length === 0
        ? prev
        : { ...prev, curso: response.data[0].id });
    } catch (err) {
      console.error('Error loading courses:', err);
      setErrors(prev => ({ ...prev, cursos: 'Error al cargar cursos' }));
    }
  }, []);

  useEffect(() => {
    loadCourses();
  }, [loadCourses]);

  useEffect(() => {
    if (curso) setFormData((prev) => ({ ...prev, curso: curso.id || curso }));
  }, [curso]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value, ...(name === 'curso' ? { asignatura: '' } : {}) }));
    
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      const validExtensions = new Set(['mp4', 'avi', 'mov', 'flv', 'wmv', 'webm', 'mkv', 'mp3', 'wav', 'aac', 'flac', 'ogg', 'm4a', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']);
      if (!validExtensions.has(extension)) {
        setErrors(prev => ({ ...prev, archivo: 'Formato no admitido. Usa imagen, video o audio compatible.' }));
        e.target.value = '';
        return;
      }

      // Validar tamaño (máximo 100MB)
      const maxSize = 100 * 1024 * 1024; // 100MB
      if (file.size > maxSize) {
        setErrors(prev => ({ ...prev, archivo: 'El archivo no puede superar los 100MB' }));
        e.target.value = '';
        return;
      }

      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setErrors(prev => ({ ...prev, archivo: '' }));
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
          // Reordenar opciones restantes
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

    if (!formData.asignatura) {
      newErrors.asignatura = 'Debe seleccionar una asignatura';
    }

    if (!selectedFile) {
      newErrors.archivo = 'Debe seleccionar un archivo multimedia';
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
      // Crear FormData para el archivo
      const formDataToSend = new FormData();
      formDataToSend.append('titulo', formData.titulo);
      formDataToSend.append('descripcion', formData.descripcion);
      formDataToSend.append('curso', formData.curso);
      formDataToSend.append('asignatura', formData.asignatura);
      if (formData.fecha_limite) formDataToSend.append('fecha_limite', formData.fecha_limite);
      formDataToSend.append('preguntas', JSON.stringify(formData.preguntas));
      formDataToSend.append('archivo_multimedia', selectedFile);

      if (deferSubmit) {
        onActivityCreated?.(formDataToSend);
        return;
      }

      const response = await createMultimediaActivity(formDataToSend);
      
      onActivityCreated && onActivityCreated(response.data);
      
    } catch (err) {
      console.error('Error creating activity:', err);
      if (err.response?.data) {
        // Convertir errores del backend a formato usable
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
    <div className="multimedia-activity-form">
      <div className="form-header">
        <h3>Actividad Multimedia</h3>
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
            <label htmlFor="asignatura">Asignatura *</label>
            <select id="asignatura" name="asignatura" value={formData.asignatura} onChange={handleInputChange} disabled={!formData.curso} className={`form-input ${errors.asignatura ? 'error' : ''}`}>
              <option value="">Seleccione una asignatura</option>
              {(cursos.find(item => String(item.id) === String(formData.curso))?.asignaturas || []).map((id, index) => (
                <option key={id} value={id}>{cursos.find(item => String(item.id) === String(formData.curso))?.asignaturas_nombres?.[index] || `Asignatura ${id}`}</option>
              ))}
            </select>
            {errors.asignatura && <span className="error-message">{errors.asignatura}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="fecha_limite">Fecha límite (opcional)</label>
            <input type="date" id="fecha_limite" name="fecha_limite" value={formData.fecha_limite} onChange={handleInputChange} className="form-input" />
          </div>
        </div>

        {/* Archivo multimedia */}
        <div className="form-section">
          <h4>Archivo multimedia</h4>
          
          <div className="file-upload">
            <input
              type="file"
              id="archivo_multimedia"
              accept=".mp4,.avi,.mov,.flv,.wmv,.webm,.mkv,.mp3,.wav,.aac,.flac,.ogg,.m4a,.jpg,.jpeg,.png,.gif,.webp,.bmp,.svg"
              onChange={handleFileChange}
              className="file-input"
            />
            <label htmlFor="archivo_multimedia" className="file-label">
              <div className="file-icon">
                📁
              </div>
              <div className="file-text">
                <p>Click para seleccionar archivo</p>
                <span>Imágenes, videos o audio (Máx: 100MB)</span>
              </div>
            </label>
            
            {previewUrl && (
              <div className="file-preview">
                {selectedFile.type.startsWith('image/') ? (
                  <img src={previewUrl} alt={`Vista previa de ${selectedFile.name}`} className="preview-image" />
                ) : selectedFile.type.startsWith('video/') ? (
                  <video src={previewUrl} className="preview-video" controls />
                ) : (
                  <audio src={previewUrl} className="preview-audio" controls />
                )}
                <div className="file-info">
                  <p className="file-name">{selectedFile.name}</p>
                  <p className="file-size">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFile(null);
                      setPreviewUrl('');
                      document.getElementById('archivo_multimedia').value = '';
                    }}
                    className="remove-file"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            )}
          </div>
          
          {errors.archivo && <span className="error-message">{errors.archivo}</span>}
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
            {isSubmitting ? 'Creando...' : (submitLabel || 'Crear actividad')}
          </button>
        </div>
        
        {errors.submit && <span className="error-message">{errors.submit}</span>}
      </form>
    </div>
  );
};

export default MultimediaActivityForm;
