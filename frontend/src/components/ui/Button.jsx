import React from 'react';
import { cva } from 'class-variance-authority';
import './ui.css';

const buttonStyles = cva('ui-button', {
  variants: {
    variant: {
      primary: 'ui-button--primary',
      secondary: 'ui-button--secondary',
      outline: 'ui-button--outline',
      ghost: 'ui-button--ghost',
      danger: 'ui-button--danger',
    },
    size: {
      sm: 'ui-button--sm',
      md: 'ui-button--md',
      lg: 'ui-button--lg',
    },
  },
  defaultVariants: {
    variant: 'primary',
    size: 'md',
  },
});

export default function Button({
  variant,
  size,
  isLoading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  className = '',
  children,
  type = 'button',
  ...props
}) {
  const isDisabled = disabled || isLoading;

  return (
    <button
      className={`${buttonStyles({ variant, size })} ${className}`.trim()}
      type={type}
      disabled={isDisabled}
      aria-disabled={isDisabled || undefined}
      aria-busy={isLoading || undefined}
      {...props}
    >
      {isLoading ? <span className="ui-button__spinner" aria-hidden="true" /> : leftIcon}
      <span>{children}</span>
      {!isLoading && rightIcon}
    </button>
  );
}
