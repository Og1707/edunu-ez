import React, { useState, useEffect } from 'react';
import { getCourses, createMultimediaActivity, getCloudinarySignature } from '../services/activities.service';
import { previewMultimediaTemplate } from '../services/activities.service';
import QuestionForm from './QuestionForm';
import './MultimediaActivityForm.css';

const MultimediaActivityForm = ({ 
  curso, 
  onActivityCreated, 
  onCancel,
  initialData = {} 
}) => {
  const [formData, setFormData] = useState({
    titulo: initialData.titulo || '',
    descripcion: initialData.descripcion || '',
    curso: curso || '',
    preguntas: initialData.preguntas || []
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState('');
  const [cursos, setCursos] = useState([]);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [preview, setPreview] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    loadCourses();
  }, []);

  useEffect(() => {
    if (formData.curso) {
      setFormData(prev => ({ ...prev, curso: formData.curso }));
    }
  }, [curso]);

  const loadCourses = async () => {
    try {
      const response = await getCourses();
      setCursos(response.data);
      
      // Si no hay curso seleccionado pero hay cursos disponibles, seleccionar el primero
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
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Limpiar error del campo cuando el usuario empieza a escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tipo de archivo
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/avi', 'video/mov', 'audio/mp3', 'audio/wav'];
      if (!validTypes.includes(file.type)) {
        setErrors(prev => ({ ...prev, archivo: 'Tipo de archivo no válido' }));
        return;
      }

      // Validar tamaño (máximo 100MB)
      const maxSize = 100 * 1024 * 1024; // 100MB
      if (file.size > maxSize) {
        setErrors(prev => ({ ...prev, archivo: 'El archivo no puede superar los 100MB' }));
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

  const handlePreview = async () => {
    if (!validateForm()) {
      return;
    }

    try {
      const previewData = {
        titulo: formData.titulo,
        descripcion: formData.descripcion,
        preguntas: JSON.stringify(formData.preguntas)
      };

      const response = await previewMultimediaTemplate(previewData);
      
      if (response.data.valido) {
        setPreview(response.data);
        setShowPreview(true);
      } else {
        setErrors(prev => ({ ...prev, preview: 'Estructura inválida' }));
      }
    } catch (err) {
      console.error('Error en preview:', err);
      setErrors(prev => ({ ...prev, preview: 'Error al generar preview' }));
    }
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
      formDataToSend.append('preguntas', JSON.stringify(formData.preguntas));
      formDataToSend.append('archivo_multimedia', selectedFile);

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
        </div>

        {/* Archivo multimedia */}
        <div className="form-section">
          <h4>Archivo multimedia</h4>
          
          <div className="file-upload">
            <input
              type="file"
              id="archivo_multimedia"
              accept="image/*,video/*,audio/*"
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
                  <img src={previewUrl} alt="Preview" className="preview-image" />
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

        {/* Preview */}
        <div className="form-section">
          <div className="section-header">
            <h4>Preview</h4>
            <button
              type="button"
              onClick={handlePreview}
              className="preview-btn"
              disabled={isSubmitting}
            >
              Generar preview
            </button>
          </div>
          
          {errors.preview && <span className="error-message">{errors.preview}</span>}
          
          {showPreview && preview && (
            <div className="preview-container">
              <div className="preview-header">
                <h5>Preview de la actividad</h5>
                <button
                  type="button"
                  onClick={() => setShowPreview(false)}
                  className="close-preview"
                >
                  ×
                </button>
              </div>
              <div className="preview-content">
                <p><strong>Título:</strong> {preview.preview.titulo}</p>
                <p><strong>Descripción:</strong> {preview.preview.descripcion}</p>
                <p><strong>Preguntas:</strong> {preview.preguntas_count}</p>
                <p><strong>Opciones totales:</strong> {preview.opciones_total}</p>
                <p className="preview-status">
                  <span className={`status-badge ${preview.valido ? 'valid' : 'invalid'}`}>
                    {preview.valido ? '✓ Estructura válida' : '✗ Estructura inválida'}
                  </span>
                </p>
              </div>
            </div>
          )}
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

export default MultimediaActivityForm;
