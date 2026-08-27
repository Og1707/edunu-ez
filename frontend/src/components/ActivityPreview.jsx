import React, { useState, useEffect } from 'react';
import { previewMultimediaTemplate } from '../services/activities.service';
import './ActivityPreview.css';

const ActivityPreview = ({ 
  templateType, 
  activityData, 
  onClose, 
  isVisible 
}) => {
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('content');

  useEffect(() => {
    if (isVisible && activityData) {
      generatePreview();
    }
  }, [isVisible, activityData, templateType]);

  const generatePreview = async () => {
    if (!activityData) return;

    setLoading(true);
    setError(null);
    setPreview(null);

    try {
      if (templateType === 'multimedia') {
        const previewData = {
          titulo: activityData.titulo || 'Actividad de ejemplo',
          descripcion: activityData.descripcion || 'Descripción de ejemplo',
          preguntas: JSON.stringify(activityData.preguntas || [])
        };

        const response = await previewMultimediaTemplate(previewData);
        setPreview(response.data);
      } else {
        // Para texto y legacy, generar preview local
        generateLocalPreview();
      }
    } catch (err) {
      console.error('Error generating preview:', err);
      setError('No se pudo generar el preview');
    } finally {
      setLoading(false);
    }
  };

  const generateLocalPreview = () => {
    const questions = activityData.preguntas || [];
    const totalOptions = questions.reduce((total, q) => total + (q.opciones?.length || 0), 0);

    const localPreview = {
      valido: validateActivityStructure(),
      mensaje: validateActivityStructure() ? 'Estructura válida' : 'Estructura inválida',
      preview: {
        titulo: activityData.titulo || 'Sin título',
        descripcion: activityData.descripcion || 'Sin descripción',
        template_type: templateType,
        preguntas: questions
      },
      preguntas_count: questions.length,
      opciones_total: totalOptions,
      tiempo_limite: activityData.tiempo_limite_minutos || null
    };

    setPreview(localPreview);
  };

  const validateActivityStructure = () => {
    if (!activityData.titulo?.trim()) return false;
    if (!activityData.descripcion?.trim()) return false;

    const questions = activityData.preguntas || [];
    if (questions.length === 0) return false;

    for (const question of questions) {
      if (!question.enunciado?.trim()) return false;
      
      const options = question.opciones || [];
      if (options.length < 2) return false;
      
      const correctOptions = options.filter(o => o.es_correcta);
      if (correctOptions.length !== 1) return false;
      
      for (const option of options) {
        if (!option.texto?.trim()) return false;
      }
    }

    return true;
  };

  const renderContentTab = () => {
    if (!preview) return null;

    return (
      <div className="preview-content">
        <div className="preview-header">
          <h4>{preview.preview.titulo}</h4>
          <span className={`template-badge ${templateType}`}>
            {getTemplateName(templateType)}
          </span>
        </div>
        
        <div className="preview-description">
          <p>{preview.preview.descripcion}</p>
        </div>

        {templateType === 'texto' && preview.tiempo_limite && (
          <div className="preview-time-limit">
            <span className="time-icon">⏱️</span>
            <span>Tiempo límite: {preview.tiempo_limite} minutos</span>
          </div>
        )}

        <div className="preview-stats">
          <div className="stat-item">
            <span className="stat-number">{preview.preguntas_count}</span>
            <span className="stat-label">preguntas</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{preview.opciones_total}</span>
            <span className="stat-label">opciones</span>
          </div>
          {templateType === 'texto' && preview.tiempo_limite && (
            <div className="stat-item">
              <span className="stat-number">{preview.tiempo_limite}</span>
              <span className="stat-label">minutos</span>
            </div>
          )}
        </div>

        <div className="preview-status">
          <span className={`status-badge ${preview.valido ? 'valid' : 'invalid'}`}>
            {preview.valido ? '✓ Estructura válida' : '✗ Estructura inválida'}
          </span>
        </div>
      </div>
    );
  };

  const renderQuestionsTab = () => {
    if (!preview?.preview?.preguntas) return null;

    return (
      <div className="questions-preview">
        <h4>Preguntas y respuestas</h4>
        <div className="questions-list">
          {preview.preview.preguntas.map((question, qIndex) => (
            <div key={qIndex} className="question-preview-item">
              <div className="question-header">
                <span className="question-number">Pregunta {qIndex + 1}</span>
              </div>
              <div className="question-text">
                {question.enunciado}
              </div>
              <div className="options-preview">
                {question.opciones?.map((option, oIndex) => (
                  <div 
                    key={oIndex} 
                    className={`option-preview-item ${option.es_correcta ? 'correct' : 'incorrect'}`}
                  >
                    <span className="option-marker">
                      {option.es_correcta ? '✓' : '○'}
                    </span>
                    <span className="option-text">
                      {option.texto}
                    </span>
                    {option.es_correcta && (
                      <span className="correct-label">Correcta</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderValidationTab = () => {
    if (!preview) return null;

    const validationResults = validateDetailedStructure();
    
    return (
      <div className="validation-preview">
        <h4>Validación detallada</h4>
        <div className="validation-results">
          {validationResults.map((result, index) => (
            <div key={index} className={`validation-item ${result.valid ? 'success' : 'error'}`}>
              <span className="validation-icon">
                {result.valid ? '✓' : '✗'}
              </span>
              <span className="validation-text">
                {result.message}
              </span>
            </div>
          ))}
        </div>
        
        {!preview.valido && (
          <div className="validation-help">
            <h5>Recomendaciones:</h5>
            <ul>
              <li>Asegúrese de que todas las preguntas tengan al menos 2 opciones</li>
              <li>Cada pregunta debe tener exactamente una respuesta correcta</li>
              <li>Complete todos los campos obligatorios</li>
              <li>Verifique que no haya preguntas sin enunciado</li>
            </ul>
          </div>
        )}
      </div>
    );
  };

  const validateDetailedStructure = () => {
    const results = [];
    
    // Validar título
    if (activityData.titulo?.trim()) {
      results.push({ valid: true, message: 'Título proporcionado' });
    } else {
      results.push({ valid: false, message: 'Falta el título' });
    }
    
    // Validar descripción
    if (activityData.descripcion?.trim()) {
      results.push({ valid: true, message: 'Descripción proporcionada' });
    } else {
      results.push({ valid: false, message: 'Falta la descripción' });
    }
    
    // Validar preguntas
    const questions = activityData.preguntas || [];
    if (questions.length > 0) {
      results.push({ valid: true, message: `${questions.length} pregunta(s) agregada(s)` });
      
      questions.forEach((q, index) => {
        if (q.enunciado?.trim()) {
          results.push({ valid: true, message: `Pregunta ${index + 1}: enunciado válido` });
        } else {
          results.push({ valid: false, message: `Pregunta ${index + 1}: falta enunciado` });
        }
        
        const options = q.opciones || [];
        if (options.length >= 2) {
          results.push({ valid: true, message: `Pregunta ${index + 1}: ${options.length} opciones` });
          
          const correctOptions = options.filter(o => o.es_correcta);
          if (correctOptions.length === 1) {
            results.push({ valid: true, message: `Pregunta ${index + 1}: respuesta correcta definida` });
          } else {
            results.push({ valid: false, message: `Pregunta ${index + 1}: debe tener exactamente 1 respuesta correcta` });
          }
        } else {
          results.push({ valid: false, message: `Pregunta ${index + 1}: necesita al menos 2 opciones` });
        }
      });
    } else {
      results.push({ valid: false, message: 'No hay preguntas agregadas' });
    }
    
    // Validar tiempo límite para actividades de texto
    if (templateType === 'texto' && activityData.tiempo_limite_minutos) {
      const timeLimit = parseInt(activityData.tiempo_limite_minutos);
      if (timeLimit >= 5 && timeLimit <= 180) {
        results.push({ valid: true, message: `Tiempo límite válido: ${timeLimit} minutos` });
      } else {
        results.push({ valid: false, message: 'Tiempo límite debe estar entre 5 y 180 minutos' });
      }
    }
    
    return results;
  };

  const getTemplateName = (type) => {
    const names = {
      multimedia: 'Multimedia',
      texto: 'Texto',
      legacy: 'Heredada'
    };
    return names[type] || type;
  };

  if (!isVisible) return null;

  return (
    <div className="activity-preview-overlay">
      <div className="activity-preview-modal">
        <div className="preview-modal-header">
          <h3>Preview de Actividad</h3>
          <button 
            onClick={onClose}
            className="close-preview-btn"
          >
            ×
          </button>
        </div>

        <div className="preview-tabs">
          <button
            className={`tab-btn ${activeTab === 'content' ? 'active' : ''}`}
            onClick={() => setActiveTab('content')}
          >
            Contenido
          </button>
          <button
            className={`tab-btn ${activeTab === 'questions' ? 'active' : ''}`}
            onClick={() => setActiveTab('questions')}
          >
            Preguntas
          </button>
          <button
            className={`tab-btn ${activeTab === 'validation' ? 'active' : ''}`}
            onClick={() => setActiveTab('validation')}
          >
            Validación
          </button>
        </div>

        <div className="preview-body">
          {loading && (
            <div className="preview-loading">
              <div className="loading-spinner">Generando preview...</div>
            </div>
          )}

          {error && (
            <div className="preview-error">
              <span className="error-icon">⚠️</span>
              <span className="error-message">{error}</span>
              <button onClick={generatePreview} className="retry-btn">
                Reintentar
              </button>
            </div>
          )}

          {!loading && !error && preview && (
            <>
              {activeTab === 'content' && renderContentTab()}
              {activeTab === 'questions' && renderQuestionsTab()}
              {activeTab === 'validation' && renderValidationTab()}
            </>
          )}
        </div>

        <div className="preview-modal-footer">
          <button onClick={onClose} className="btn btn-secondary">
            Cerrar
          </button>
          {preview?.valido && (
            <button className="btn btn-success">
              ✓ Estructura válida
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ActivityPreview;
