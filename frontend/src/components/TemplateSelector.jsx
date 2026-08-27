import React, { useState, useEffect } from 'react';
import { getTemplates } from '../services/activities.service';
import './TemplateSelector.css';

const TemplateSelector = ({ onTemplateSelect, selectedTemplate }) => {
  const [templates, setTemplates] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      setLoading(true);
      const response = await getTemplates();
      setTemplates(response.data.plantillas);
      setError(null);
    } catch (err) {
      console.error('Error loading templates:', err);
      setError('No se pudieron cargar las plantillas');
    } finally {
      setLoading(false);
    }
  };

  const handleTemplateClick = (templateKey, template) => {
    onTemplateSelect(templateKey, template);
  };

  if (loading) {
    return (
      <div className="template-selector loading">
        <div className="loading-spinner">Cargando plantillas...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="template-selector error">
        <div className="error-message">{error}</div>
        <button onClick={loadTemplates} className="retry-button">
          Reintentar
        </button>
      </div>
    );
  }

  return (
    <div className="template-selector">
      <h3 className="selector-title">Selecciona una plantilla</h3>
      <div className="templates-grid">
        {Object.entries(templates).map(([key, template]) => (
          <div
            key={key}
            className={`template-card ${selectedTemplate === key ? 'selected' : ''}`}
            onClick={() => handleTemplateClick(key, template)}
          >
            <div className="template-icon">
              {getTemplateIcon(key)}
            </div>
            <h4 className="template-name">{template.nombre}</h4>
            <p className="template-description">{template.descripcion}</p>
            
            <div className="template-features">
              {template.requiere_archivo && (
                <span className="feature-tag file-required">
                  Requiere archivo
                </span>
              )}
              {template.preguntas_requeridas && (
                <span className="feature-tag questions-required">
                  Preguntas requeridas
                </span>
              )}
              {template.tiempo_limite_opcional && (
                <span className="feature-tag time-limit">
                  Tiempo límite opcional
                </span>
              )}
            </div>

            {template.requiere_archivo && (
              <div className="file-info">
                <span className="file-types">
                  {template.tipos_archivo?.join(', ') || 'Todos los formatos'}
                </span>
                {template.max_tamaño_mb && (
                  <span className="file-size">
                    Máx: {template.max_tamaño_mb}MB
                  </span>
                )}
              </div>
            )}

            {template.preguntas_requeridas && (
              <div className="questions-info">
                <span className="questions-range">
                  {template.min_preguntas}-{template.max_preguntas} preguntas
                </span>
              </div>
            )}

            {template.tiempo_limite_opcional && (
              <div className="time-info">
                <span className="time-range">
                  {template.min_tiempo}-{template.max_tiempo} minutos
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const getTemplateIcon = (templateKey) => {
  const icons = {
    multimedia: (
      <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <rect x="2" y="4" width="20" height="16" rx="2" />
        <circle cx="8" cy="10" r="2" />
        <path d="M14 10l4 4M14 14l4-4" />
      </svg>
    ),
    texto: (
      <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14,2 14,8 20,8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10,9 9,9 8,9" />
      </svg>
    ),
    legacy: (
      <svg className="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <line x1="10" y1="9" x2="18" y2="9" />
        <line x1="10" y1="13" x2="18" y2="13" />
        <line x1="10" y1="17" x2="18" y2="17" />
        <polyline points="14,2 14,8 20,8" />
      </svg>
    ),
  };
  
  return icons[templateKey] || icons.legacy;
};

export default TemplateSelector;
