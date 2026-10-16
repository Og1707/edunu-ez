import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ClipboardList, Pencil, Plus, Search, Send, Trash2 } from 'lucide-react';
import ManagementDrawer from '../../components/ui/ManagementDrawer';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import EmptyState from '../../components/ui/EmptyState';
import { assignActivityToCourse, deleteActivity, getActivities, getActivityTypes, getTeacherActivities, updateActivity } from '../../services/activities.service';
import { getCourses } from '../../services/courses.service';
import './ActivityManagement.css';

const emptyForm = { titulo: '', descripcion: '', curso: '', tipo: 'otro', estado: 'pendiente', fecha_limite: '' };

export default function ActivityManagement({ user }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [activities, setActivities] = useState([]);
  const [courses, setCourses] = useState([]);
  const [types, setTypes] = useState([]);
  const [search, setSearch] = useState('');
  const [courseFilter, setCourseFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [selected, setSelected] = useState(null);
  const [toDelete, setToDelete] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const activityRequest = user?.rol === 'administrador' ? getActivities() : getTeacherActivities();
      const [activityResponse, courseResponse, typeResponse] = await Promise.all([activityRequest, getCourses(), getActivityTypes()]);
      setActivities(Array.isArray(activityResponse.data) ? activityResponse.data : activityResponse.data.actividades || []);
      setCourses(Array.isArray(courseResponse.data) ? courseResponse.data : courseResponse.data.cursos || []);
      setTypes(typeResponse.data || []);
      setError('');
    } catch (_) { setError('No se pudieron cargar las actividades. Inténtalo de nuevo.'); }
    finally { setLoading(false); }
  }, [user?.rol]);
  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (location.state?.notice) {
      setSuccess(location.state.notice);
      navigate(location.pathname, { replace: true, state: null });
    }
  }, [location.key, location.pathname, location.state, navigate]);

  const filtered = useMemo(() => activities.filter((item) => {
    const query = search.trim().toLocaleLowerCase();
    return (!query || `${item.titulo || ''} ${item.descripcion || ''} ${item.curso_nombre || ''}`.toLocaleLowerCase().includes(query))
      && (!courseFilter || String(item.curso) === courseFilter)
      && (!typeFilter || item.tipo === typeFilter);
  }), [activities, search, courseFilter, typeFilter]);

  const edit = (item) => {
    setSelected(item);
    setForm({ titulo: item.titulo || '', descripcion: item.descripcion || '', curso: item.curso || '', tipo: item.tipo || 'otro', estado: item.estado || 'pendiente', fecha_limite: item.fecha_limite || '' });
    setError(''); setDrawerOpen(true);
  };
  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  const save = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    try {
      await updateActivity(selected.id, { ...form, curso: Number(form.curso) });
      setDrawerOpen(false); setSuccess('Actividad actualizada.'); await load();
    } catch (failure) { setError(failure.response?.data?.mensaje || 'No se pudo actualizar la actividad.'); }
    finally { setSaving(false); }
  };
  const assign = async (item) => {
    setError(''); setSuccess('');
    try {
      await assignActivityToCourse({ curso_id: item.curso, actividad_ids: [item.id] });
      setSuccess(`Actividad asignada al curso ${item.curso_nombre || ''}.`);
      await load();
    } catch (failure) { setError(failure.response?.data?.mensaje || 'No se pudo asignar la actividad. Verifica que el curso tenga estudiantes inscritos.'); }
  };
  const remove = async () => {
    if (!toDelete) return;
    try { await deleteActivity(toDelete.id); setSuccess('Actividad eliminada.'); setToDelete(null); await load(); }
    catch (failure) { setError(failure.response?.data?.mensaje || 'No se pudo eliminar la actividad.'); setToDelete(null); }
  };

  return <section className="activity-management">
    <header className="activity-management__header"><div><span>Contenido educativo</span><h1>Actividades</h1><p>Administra las actividades y sus asignaciones por curso.</p></div><button type="button" onClick={() => navigate('/activities/create')}><Plus size={18} aria-hidden="true"/> Crear actividad</button></header>
    {success && <p className="activity-management__notice" role="status">{success}</p>}{error && !drawerOpen && <p className="activity-management__error" role="alert">{error}</p>}
    <div className="activity-management__filters"><label><span className="sr-only">Buscar actividades</span><Search size={18} aria-hidden="true"/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por título, descripción o curso…"/></label><label>Curso<select value={courseFilter} onChange={(event) => setCourseFilter(event.target.value)}><option value="">Todos los cursos</option>{courses.map((course) => <option key={course.id} value={course.id}>{course.nombre}</option>)}</select></label><label>Tipo<select value={typeFilter} onChange={(event) => setTypeFilter(event.target.value)}><option value="">Todos los tipos</option>{types.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}</select></label></div>
    {loading ? <p role="status" className="activity-management__loading">Cargando actividades…</p> : filtered.length ? <div className="activity-management__grid">{filtered.map((item) => <article className="activity-management__card" key={item.id}><div className="activity-management__card-top"><ClipboardList size={20} aria-hidden="true"/><span>{item.template_type || 'actividad'}</span></div><h2>{item.titulo}</h2><p>{item.descripcion}</p><dl><div><dt>Curso</dt><dd>{item.curso_nombre || courses.find((course) => Number(course.id) === Number(item.curso))?.nombre || 'Sin curso'}</dd></div><div><dt>Tipo</dt><dd>{types.find((type) => type.value === item.tipo)?.label || item.tipo}</dd></div><div><dt>Fecha límite</dt><dd>{item.fecha_limite ? new Date(`${item.fecha_limite}T00:00:00`).toLocaleDateString() : 'Sin fecha'}</dd></div></dl>{item.estadisticas && <div className="activity-management__stats"><span>{item.estadisticas.total_asignaciones} asignaciones</span><span>{item.estadisticas.completadas} completadas</span></div>}<footer><button type="button" onClick={() => assign(item)}><Send size={16} aria-hidden="true"/> Asignar al curso</button><button type="button" aria-label={`Editar ${item.titulo}`} onClick={() => edit(item)}><Pencil size={17} aria-hidden="true"/></button><button type="button" aria-label={`Eliminar ${item.titulo}`} onClick={() => setToDelete(item)}><Trash2 size={17} aria-hidden="true"/></button></footer></article>)}</div> : <EmptyState icon={<ClipboardList/>} title={activities.length ? 'No hay coincidencias' : 'Aún no hay actividades'} description={activities.length ? 'Ajusta los filtros para encontrar una actividad.' : 'Crea una actividad para comenzar.'} action={!activities.length && <button type="button" onClick={() => navigate('/activities/create')}>Crear primera actividad</button>}/>}
    <ManagementDrawer open={drawerOpen} onOpenChange={setDrawerOpen} title="Editar actividad" description="Actualiza la información y guarda los cambios." footer={<div className="activity-management__form-actions"><button type="button" onClick={() => setDrawerOpen(false)}>Cancelar</button><button type="submit" form="activity-edit-form" disabled={saving}>{saving ? 'Guardando…' : 'Guardar cambios'}</button></div>}>
      {error && <p className="activity-management__error" role="alert">{error}</p>}<form id="activity-edit-form" className="activity-management__form" onSubmit={save}><label>Título<input name="titulo" required maxLength="200" value={form.titulo} onChange={change}/></label><label>Descripción<textarea name="descripcion" required rows="4" value={form.descripcion} onChange={change}/></label><label>Curso<select name="curso" required value={form.curso} onChange={change}>{courses.map((course) => <option key={course.id} value={course.id}>{course.nombre}</option>)}</select></label><label>Tipo<select name="tipo" value={form.tipo} onChange={change}>{types.map((type) => <option key={type.value} value={type.value}>{type.label}</option>)}</select></label><label>Estado<select name="estado" value={form.estado} onChange={change}><option value="pendiente">Pendiente</option><option value="completada">Completada</option><option value="en_revision">En revisión</option></select></label><label>Fecha límite<input type="date" name="fecha_limite" value={form.fecha_limite} onChange={change}/></label></form>
    </ManagementDrawer>
    <ConfirmDialog open={Boolean(toDelete)} title="Eliminar actividad" description={`¿Eliminar “${toDelete?.titulo || ''}”? Esta acción no se puede deshacer.`} onOpenChange={(open) => { if (!open) setToDelete(null); }} onConfirm={remove}/>
  </section>;
}
