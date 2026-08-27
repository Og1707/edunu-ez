import React, { useState } from 'react';
import OptionForm from './OptionForm';
import './QuestionForm.css';

/**
 * QuestionForm - Componente reutilizable para formulario de preguntas
 * 
 * Props:
 *   - question: Objeto {id, enunciado, orden, opciones}
 *   - questionIndex: Número del índice de la pregunta (0-based)
 *   - onQuestionChange: Callback(questionId, field, value)
 *   - onOptionChange: Callback(questionId, optionId, field, value)
 *   - onAddOption: Callback(questionId)
 *   - onRemoveOption: Callback(questionId, optionId)
 *   - onRemoveQuestion: Callback(questionId)
 */
const QuestionForm = ({
  question,
  questionIndex,
  onQuestionChange,
  onOptionChange,
  onAddOption,
  onRemoveOption,
  onRemoveQuestion,
}) => {
  const [errors, setErrors] = useState({});

  const validateQuestion = () => {
    const newErrors = {};

    // Validar enunciado
    if (!question.enunciado?.trim()) {
      newErrors.enunciado = 'El enunciado es requerido';
    } else if (question.enunciado.length < 10) {
      newErrors.enunciado = 'Mínimo 10 caracteres';
    } else if (question.enunciado.length > 500) {
      newErrors.enunciado = 'Máximo 500 caracteres';
    }

    // Validar opciones
    if (!question.opciones || question.opciones.length < 2) {
      newErrors.opciones = 'Mínimo 2 opciones de respuesta';
    }

    // Validar opciones con texto
    const filledOptions = question.opciones?.filter(o => o.texto?.trim());
    if (filledOptions?.length < 2) {
      newErrors.opcionesTexto = 'Al menos 2 opciones deben tener texto';
    }

    // Validar exactamente 1 opción correcta
    const correctCount = question.opciones?.filter(o => o.es_correcta).length || 0;
    if (correctCount !== 1) {
      newErrors.correctAnswer = correctCount === 0 
        ? 'Debe marcar una opción como correcta'
        : 'Solo puede haber 1 opción correcta';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleEnunciadoChange = (e) => {
    const { value } = e.target;
    onQuestionChange(question.id, 'enunciado', value);
    if (errors.enunciado) setErrors(prev => ({ ...prev, enunciado: '' }));
  };

  const handleRemoveClick = () => {
    if (window.confirm('¿Estás seguro que deseas eliminar esta pregunta? No se puede deshacer.')) {
      onRemoveQuestion(question.id);
    }
  };

  const handleAddOptionClick = () => {
    onAddOption(question.id);
  };

  const isValid = Object.keys(errors).length === 0;
  const correctAnswerCount = (question.opciones || []).filter(opt => opt.es_correcta).length;

  return (
    <div className={`question-form ${isValid ? 'valid' : 'has-errors'}`}>
      {/* Encabezado con número y botón eliminar */}
      <div className="question-header">
        <h4 className="question-title">
          Pregunta {questionIndex + 1}
        </h4>
        <button
          type="button"
          onClick={handleRemoveClick}
          className="btn-remove-question"
          title="Eliminar pregunta"
        >
          ✕
        </button>
      </div>

      {/* Campo de enunciado */}
      <div className="form-group">
        <label htmlFor={`question-${question.id}`} className="form-label">
          Enunciado *
          <span className="char-counter">
            {question.enunciado?.length || 0}/500
          </span>
        </label>
        <textarea
          id={`question-${question.id}`}
          name="enunciado"
          value={question.enunciado || ''}
          onChange={handleEnunciadoChange}
          placeholder="Escribe el texto de la pregunta aquí..."
          rows="3"
          maxLength="500"
          className={`form-control textarea-input ${errors.enunciado ? 'is-invalid' : ''}`}
        />
        {errors.enunciado && (
          <div className="error-message">{errors.enunciado}</div>
        )}
      </div>

      {/* Opciones de respuesta */}
      <div className="options-section">
        <div className="options-header">
          <h5 className="options-title">
            Opciones de respuesta
            <span className="badge-count">
              {question.opciones?.length || 0}
            </span>
          </h5>
          {correctAnswerCount !== 1 && (
            <span className="warning-badge">
              ⚠️ {correctAnswerCount === 0 ? 'Sin respuesta correcta' : 'Múltiples correctas'}
            </span>
          )}
        </div>

        {errors.opciones && (
          <div className="error-message">{errors.opciones}</div>
        )}
        {errors.opcionesTexto && (
          <div className="error-message">{errors.opcionesTexto}</div>
        )}
        {errors.correctAnswer && (
          <div className="error-message">{errors.correctAnswer}</div>
        )}

        <div className="options-list">
          {question.opciones && question.opciones.length > 0 ? (
            question.opciones.map((option, optionIndex) => (
              <OptionForm
                key={option.id}
                option={option}
                optionIndex={optionIndex}
                questionId={question.id}
                onOptionChange={onOptionChange}
                onRemoveOption={onRemoveOption}
              />
            ))
          ) : (
            <div className="no-options-message">
              No hay opciones agregadas
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={handleAddOptionClick}
          className="btn-add-option"
        >
          + Agregar opción
        </button>
      </div>

      {/* Indicador de validación */}
      {isValid && question.opciones?.length >= 2 && (
        <div className="validation-success">
          ✓ Pregunta completada
        </div>
      )}
    </div>
  );
};

export default QuestionForm;
