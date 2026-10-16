import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import './ManagementDrawer.css';

export default function ManagementDrawer({ open, onOpenChange, title, description, children, footer, size = 'default' }) {
  const panelRef = useRef(null);
  const returnFocusRef = useRef(null);
  useEffect(() => {
    if (!open) return undefined;
    returnFocusRef.current = document.activeElement;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    requestAnimationFrame(() => panelRef.current?.querySelector('input,select,textarea,button,[tabindex]:not([tabindex="-1"])')?.focus());
    const onKeyDown = (event) => {
      if (event.key === 'Escape') { event.preventDefault(); onOpenChange(false); }
      if (event.key !== 'Tab') return;
      const focusable = [...(panelRef.current?.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])') || [])];
      if (!focusable.length) { event.preventDefault(); return; }
      const first = focusable[0]; const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', onKeyDown);
      returnFocusRef.current?.focus?.();
    };
  }, [open, onOpenChange]);
  if (!open) return null;
  return createPortal(<div className="management-drawer__overlay" onMouseDown={(event) => { if (event.target === event.currentTarget) onOpenChange(false); }}>
    <section ref={panelRef} className={`management-drawer management-drawer--${size}`} role="dialog" aria-modal="true" aria-labelledby="management-drawer-title" aria-describedby={description ? 'management-drawer-description' : undefined}>
      <header className="management-drawer__header"><div><h2 id="management-drawer-title">{title}</h2>{description && <p id="management-drawer-description">{description}</p>}</div><button type="button" className="management-drawer__close" aria-label="Cerrar panel" onClick={() => onOpenChange(false)}><X aria-hidden="true" size={20} /></button></header>
      <div className="management-drawer__body">{children}</div>
      {footer && <footer className="management-drawer__footer">{footer}</footer>}
    </section>
  </div>, document.body);
}
