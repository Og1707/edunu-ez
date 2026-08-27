import React from 'react';
import './OptionForm.css';

/**
 * OptionForm - Componente para cada opción de respuesta
 * 
 * Props:
 *   - option: {id, texto, es_correcta, orden}
 *   - optionIndex: Índice de la opción (0-based)
 *   - questionId: ID de la pregunta padre
 *   - onOptionChange: Callback(questionId, optionId, field, value)
 *   - onRemoveOption: Callback(questionId, optionId)
 */
const OptionForm = ({
  option,
  optionIndex,
  questionId,
  onOptionChange,
  onRemoveOption,
}) => {
  const handleTextChange = (e) => {
    onOptionChange(questionId, option.id, 'texto', e.target.value);
  };

  // Al seleccionar el radio, marcar como correcta
  // El parent se encargará de desmarcar las otras opciones
  const handleCorrectChange = (e) => {
    onOptionChange(questionId, option.id, 'es_correcta', e.target.checked);
  };

  const handleRemove = () => {
    if (window.confirm('¿Estás seguro que deseas eliminar esta opción?')) {
      onRemoveOption(questionId, option.id);
    }
  };

  return (
    <div className="option-form">
      <div className="option-content">
        <input
          type="radio"
          id={`correct-${option.id}`}
          name={`correct-${questionId}`}
          checked={option.es_correcta || false}
          onChange={handleCorrectChange}
          className="radio-correct"
          title="Marcar como respuesta correcta"
        />

        <div className="option-input-wrapper">
          <input
            type="text"
            value={option.texto || ''}
            onChange={handleTextChange}
            placeholder={`Opción ${optionIndex + 1}`}
            maxLength="200"
            className={`option-input ${option.es_correcta ? 'correct' : ''}`}
          />
          <span className="char-limit">
            {option.texto?.length || 0}/200
          </span>
        </div>

        <button
          type="button"
          onClick={handleRemove}
          className="btn-remove-option"
          title="Eliminar opción"
        >
          ✕
        </button>
      </div>

      {option.es_correcta && (
        <span className="label-correct">✓ Respuesta correcta</span>
      )}
    </div>
  );
};

export default OptionForm;
