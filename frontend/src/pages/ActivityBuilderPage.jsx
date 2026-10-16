import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import TemplateSelector from '../components/TemplateSelector';
import TextActivityForm from '../components/TextActivityForm';
import MultimediaActivityForm from '../components/MultimediaActivityForm';
import ActivityPreview from '../components/ActivityPreview';
import { createTextActivity, createMultimediaActivity } from '../services/activities.service';
import './ActivityBuilderPage.css';

const DRAFT_KEY = 'edununez_activity_draft';

export default function ActivityBuilderPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [template, setTemplate] = useState('');
  const [draft, setDraft] = useState({});
  const [validatedData, setValidatedData] = useState(null);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const [previewTab, setPreviewTab] = useState('edit');

  const updateDraft = useCallback((data) => setDraft(data), []);
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(DRAFT_KEY) || 'null');
      if (saved?.template && ['multimedia', 'texto'].includes(saved.template)) {
        setTemplate(saved.template);
        setDraft(saved.draft || {});
        setStep(1);
      } else if (saved) {
        localStorage.removeItem(DRAFT_KEY);
      }
    } catch (_) { /* Draft corrupto: iniciar vacío. */ }
  }, []);

  const selectTemplate = (key) => {
    setTemplate(key);
    setDraft({});
    setStep(1);
  };

  const saveDraft = () => {
    const serializable = { ...draft };
    delete serializable.archivo_multimedia;
    localStorage.setItem(DRAFT_KEY, JSON.stringify({ template, draft: serializable }));
    setError(draft.archivo_multimedia ? 'Borrador guardado. Por seguridad, vuelve a seleccionar el archivo multimedia antes de publicar.' : 'Borrador guardado en este dispositivo.');
  };

  const requestExit = () => {
    const hasChanges = Boolean(draft.titulo || draft.descripcion || (draft.preguntas || []).length || draft.archivo_multimedia);
    if (hasChanges && !window.confirm('Hay cambios en la actividad. ¿Quieres salir del editor?')) return;
    navigate('/activities');
  };

  const publish = async () => {
    if (!validatedData) {
      setError('No hay una actividad validada para publicar. Vuelve al editor y valida su contenido.');
      return;
    }
    setSaving(true);
    setError('');
    try {
      if (template === 'multimedia') await createMultimediaActivity(validatedData);
      else await createTextActivity(validatedData);
      localStorage.removeItem(DRAFT_KEY);
      navigate('/activities', { state: { notice: 'Actividad publicada correctamente.' } });
    } catch (err) {
      setError(err.response?.data?.mensaje || 'No fue posible publicar la actividad. Revisa los datos e inténtalo de nuevo.');
    } finally {
      setSaving(false);
    }
  };

  const activityData = draft;
  const contentForm = template === 'multimedia'
    ? <MultimediaActivityForm deferSubmit onDraftChange={updateDraft} onActivityCreated={(data) => { setValidatedData(data); setStep(2); }} onCancel={requestExit} submitLabel="Validar y previsualizar" initialData={draft} />
    : <TextActivityForm deferSubmit onDraftChange={updateDraft} onActivityCreated={(data) => { setValidatedData(data); setStep(2); }} onCancel={requestExit} submitLabel="Validar y previsualizar" initialData={draft} />;

  return (
    <main className="activity-builder">
      <header className="activity-builder__header">
        <button type="button" className="activity-builder__back" onClick={requestExit}>← Volver a actividades</button>
        <div><h1>Crear actividad</h1><p>Diseña, revisa y publica una actividad para tus estudiantes.</p></div>
        <button type="button" className="activity-builder__draft" onClick={saveDraft}>Guardar borrador</button>
      </header>
      <ol className="activity-builder__steps" aria-label="Pasos de creación">
        {['Tipo de actividad', 'Contenido', 'Previsualización'].map((label, index) => <li key={label} className={step === index ? 'is-current' : step > index ? 'is-done' : ''}><span>{step > index ? '✓' : index + 1}</span>{label}</li>)}
      </ol>
      {error && <p className="activity-builder__message" role="alert">{error}</p>}
      {step === 0 && <TemplateSelector selectedTemplate={template} onTemplateSelect={selectTemplate} />}
      {step === 1 && <>
        <div className="activity-builder__mobile-tabs"><button type="button" aria-pressed={previewTab === 'edit'} onClick={() => setPreviewTab('edit')}>Editar</button><button type="button" aria-pressed={previewTab === 'preview'} onClick={() => setPreviewTab('preview')}>Ver preview</button></div>
        <div className="activity-builder__columns">
          <section className={previewTab === 'edit' ? '' : 'is-mobile-hidden'}>{contentForm}</section>
          <aside className={`activity-builder__live-preview ${previewTab === 'preview' ? '' : 'is-mobile-hidden'}`}><h2>Vista previa en vivo</h2><h3>{draft.titulo || 'Título de la actividad'}</h3><p>{draft.descripcion || 'La descripción aparecerá aquí.'}</p>{(draft.preguntas || []).map((q, i) => <div className="activity-builder__question" key={q.id || i}><strong>{i + 1}. {q.enunciado || 'Pregunta sin enunciado'}</strong><ul>{(q.opciones || []).map((o, j) => <li key={o.id || j}>{o.texto || 'Opción'}</li>)}</ul></div>)}</aside>
        </div>
      </>}
      {step === 2 && <section className="activity-builder__review"><div className="activity-builder__review-heading"><div><h2>Revisa tu actividad</h2><p>Confirma el contenido antes de publicarlo.</p></div><button type="button" onClick={() => setStep(1)}>Editar contenido</button></div><ActivityPreview templateType={template} activityData={activityData} isVisible onClose={() => setStep(1)} onConfirm={publish} isSaving={saving} /><div className="activity-builder__publish"><button type="button" onClick={() => setStep(1)}>Volver al editor</button><button type="button" disabled={saving} onClick={publish}>{saving ? 'Publicando…' : 'Publicar actividad'}</button></div></section>}
    </main>
  );
}
