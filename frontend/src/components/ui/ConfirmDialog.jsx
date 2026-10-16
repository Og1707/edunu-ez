import React, { useEffect, useRef } from 'react';
import './ConfirmDialog.css';

export default function ConfirmDialog({ open, title, description, confirmLabel = 'Eliminar', onConfirm, onOpenChange }) {
  const dialogRef = useRef(null);
  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return undefined;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
    return undefined;
  }, [open]);
  return <dialog ref={dialogRef} className="confirm-dialog" aria-labelledby="confirm-dialog-title" aria-describedby="confirm-dialog-description" onCancel={(event) => { event.preventDefault(); onOpenChange(false); }} onClick={(event) => { if (event.target === dialogRef.current) onOpenChange(false); }}>
    <h2 id="confirm-dialog-title">{title}</h2><p id="confirm-dialog-description">{description}</p><div className="confirm-dialog__actions"><button type="button" onClick={() => onOpenChange(false)}>Cancelar</button><button type="button" className="is-danger" onClick={onConfirm}>{confirmLabel}</button></div>
  </dialog>;
}
