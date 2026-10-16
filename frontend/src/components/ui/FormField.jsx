import React from 'react';
import './ui.css';

export default function FormField({
  label,
  id,
  error,
  helperText,
  required = false,
  disabled = false,
  className = '',
  inputClassName = '',
  ...inputProps
}) {
  const messageId = `${id}-message`;
  const describedBy = [inputProps['aria-describedby'], error || helperText ? messageId : null]
    .filter(Boolean)
    .join(' ') || undefined;

  return (
    <div className={`ui-form-field ${className}`.trim()}>
      {label && <label className="ui-form-field__label" htmlFor={id}>{label}</label>}
      <input
        {...inputProps}
        id={id}
        disabled={disabled}
        required={required}
        className={`ui-form-field__input${error ? ' ui-form-field__input--error' : ''} ${inputClassName}`.trim()}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={describedBy}
      />
      {(error || helperText) && (
        <span
          id={messageId}
          className={`ui-form-field__message${error ? ' ui-form-field__message--error' : ''}`}
          role={error ? 'alert' : undefined}
        >
          {error || helperText}
        </span>
      )}
    </div>
  );
}
