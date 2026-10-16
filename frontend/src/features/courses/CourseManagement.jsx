import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Plus, Search, Pencil, Trash2, Users, UserPlus, X } from 'lucide-react';
import ManagementDrawer from '../../components/ui/ManagementDrawer';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import { getCourses, createCourse, updateCourse, deleteCourse, getCourseStudents, addStudentToCourse, removeStudentFromCourse } from '../../services/courses.service';
import { listUsers } from '../../services/users.service';
import './CourseManagement.css';

const blankCourse = { nombre: '', descripcion: '', profesor: '' };
const hasTeacher = (course) => Boolean(course.profesor);

export default function CourseManagement({ user }) {
  const [courses, setCourses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [students, setStudents] = useState([]);
  const [availableStudents, setAvailableStudents] = useState([]);
  const [selected, setSelected] = useState(null);
  const [courseToDelete, setCourseToDelete] = useState(null);
  const [form, setForm] = useState(blankCourse);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [studentsDrawerOpen, setStudentsDrawerOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadCourses = useCallback(async () => {
    setLoading(true);
    try { const response = await getCourses(); setCourses(Array.isArray(response.data) ? response.data : response.data.cursos || []); setError(''); }
    catch (_) { setError('No fue posible cargar los cursos.'); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { loadCourses(); if (user?.rol === 'administrador') listUsers().then((r) => setTeachers((r.data.usuarios || r.data || []).filter((item) => item.rol === 'profesor'))).catch(() => {}); }, [loadCourses, user]);

  const visibleCourses = useMemo(() => courses.filter((course) => {
    const isAssignedToTeacher = user?.rol !== 'profesor'
      || Number(course.profesor) === Number(user?.usuario_id);
    const query = search.trim().toLocaleLowerCase();
    const matchesSearch = !query || `${course.nombre || ''} ${course.descripcion || ''} ${course.profesor_nombre || ''}`.toLocaleLowerCase().includes(query);
    return isAssignedToTeacher && matchesSearch
      && (assignmentFilter === 'all' || (assignmentFilter === 'assigned' ? hasTeacher(course) : !hasTeacher(course)));
  }), [courses, search, assignmentFilter, user?.rol, user?.usuario_id]);
  const canManage = (course) => user?.rol === 'administrador' || Number(course.profesor) === Number(user?.usuario_id);

  const openCreate = () => { setSelected(null); setForm(blankCourse); setError(''); setDrawerOpen(true); };
  const openEdit = (course) => { setSelected(course); setForm({ nombre: course.nombre || '', descripcion: course.descripcion || '', profesor: course.profesor || '' }); setError(''); setDrawerOpen(true); };
  const setField = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));

  const saveCourse = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    const payload = { ...form, profesor: user.rol === 'profesor' ? user.usuario_id : (form.profesor || null) };
    try {
      if (selected) await updateCourse(selected.id, payload); else await createCourse(payload);
      setDrawerOpen(false); setSuccess(selected ? 'Curso actualizado.' : 'Curso creado.'); await loadCourses();
    } catch (e) { setError(e.response?.data?.mensaje || 'No fue posible guardar el curso. Revisa los campos.'); }
    finally { setSaving(false); }
  };
  const deleteCourseById = async () => {
    if (!courseToDelete) return;
    try { await deleteCourse(courseToDelete.id); setSuccess('Curso eliminado.'); setCourseToDelete(null); await loadCourses(); }
    catch (_) { setError('No fue posible eliminar el curso.'); setCourseToDelete(null); }
  };
  const openStudents = async (course) => {
    setSelected(course); setStudentsDrawerOpen(true); setError('');
    try {
      const [enrolled, users] = await Promise.all([getCourseStudents(course.id), listUsers()]);
      setStudents(enrolled.data.estudiantes || enrolled.data || []);
      const enrolledRows = enrolled.data.estudiantes || enrolled.data || [];
      const enrolledIds = enrolledRows.map((row) => row.id);
      const userRows = users.data.usuarios || users.data || [];
      setAvailableStudents(userRows.filter((item) => item.rol === 'estudiante' && !enrolledIds.includes(item.id)));
    } catch (_) { setError('No se pudo cargar la lista de estudiantes.'); }
  };
  const addStudent = async (studentId) => { try { await addStudentToCourse({ estudiante_id: studentId, curso_id: selected.id }); await openStudents(selected); } catch (_) { setError('No se pudo agregar el estudiante.'); } };
  const removeStudent = async (row) => { if (!window.confirm('¿Retirar este estudiante del curso?')) return; try { await removeStudentFromCourse(row.inscripcion_id); await openStudents(selected); } catch (_) { setError('No se pudo retirar el estudiante.'); } };
  const closeDrawer = useCallback((open) => setDrawerOpen(open), []);
  const closeStudents = useCallback((open) => setStudentsDrawerOpen(open), []);

  return <section className="course-management">
    <header className="course-management__header"><div><h2>Gestión de cursos</h2><p>{user?.rol === 'profesor' ? 'Consulta tus cursos asignados y administra sus estudiantes.' : 'Administra cursos, docentes y estudiantes.'}</p></div>{user?.rol === 'administrador' && <button className="course-management__primary" onClick={openCreate}><Plus size={18} aria-hidden="true"/> Crear curso</button>}</header>
    {success && <p className="course-management__notice" role="status">{success}</p>}{error && !drawerOpen && !studentsDrawerOpen && <p className="course-management__error" role="alert">{error}</p>}
    <div className="course-management__filters"><label className="course-management__search"><Search size={18} aria-hidden="true"/><span className="sr-only">Buscar cursos</span><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar por curso o docente…" /></label>{user?.rol === 'administrador' && <label>Docente<select value={assignmentFilter} onChange={(e) => setAssignmentFilter(e.target.value)}><option value="all">Todos</option><option value="assigned">Con docente</option><option value="unassigned">Sin docente</option></select></label>}</div>
    {loading ? <div className="course-management__empty" role="status">Cargando cursos…</div> : visibleCourses.length ? <div className="course-management__table-wrap"><table className="course-management__table"><thead><tr><th>Curso</th><th>Descripción</th><th>Docente</th><th>Estado de asignación</th><th><span className="sr-only">Acciones</span></th></tr></thead><tbody>{visibleCourses.map((course) => <tr key={course.id}><td data-label="Curso">{course.nombre}</td><td data-label="Descripción">{course.descripcion || '—'}</td><td data-label="Docente">{course.profesor_nombre || 'Sin asignar'}</td><td data-label="Estado"><span className={`course-management__status ${hasTeacher(course) ? 'is-active' : 'is-inactive'}`}>{hasTeacher(course) ? 'Con docente' : 'Sin docente'}</span></td><td data-label="Acciones"><div className="course-management__actions">{canManage(course) && <><button type="button" aria-label={`Gestionar estudiantes de ${course.nombre}`} title="Gestionar estudiantes" onClick={() => openStudents(course)}><Users size={17}/></button><button type="button" aria-label={`Editar ${course.nombre}`} title="Editar curso" onClick={() => openEdit(course)}><Pencil size={17}/></button><button type="button" aria-label={`Eliminar ${course.nombre}`} title="Eliminar curso" onClick={() => setCourseToDelete(course)}><Trash2 size={17}/></button></>}</div></td></tr>)}</tbody></table></div> : <div className="course-management__empty">{courses.length ? 'No hay cursos que coincidan con esos filtros.' : user?.rol === 'profesor' ? 'Aún no tienes cursos asignados.' : 'Aún no hay cursos. Crea el primero para organizar las actividades.'}</div>}

    <ManagementDrawer open={drawerOpen} onOpenChange={closeDrawer} title={selected ? 'Editar curso' : 'Crear curso'} description="Completa la información del curso." footer={<div className="course-management__form-actions"><button type="button" onClick={() => setDrawerOpen(false)}>Cancelar</button><button type="submit" form="course-form" disabled={saving}>{saving ? 'Guardando…' : selected ? 'Guardar cambios' : 'Crear curso'}</button></div>}>
      {error && <p className="course-management__error" role="alert">{error}</p>}<form id="course-form" onSubmit={saveCourse} className="course-management__form"><label>Nombre del curso<input name="nombre" required value={form.nombre} onChange={setField} /></label><label>Descripción<textarea name="descripcion" required rows="4" value={form.descripcion} onChange={setField}/></label>{user?.rol === 'administrador' && <label>Docente<select name="profesor" value={form.profesor} onChange={setField}><option value="">Sin asignar</option>{teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.nombre_completo || teacher.username}</option>)}</select></label>}</form>
    </ManagementDrawer>
    <ManagementDrawer open={studentsDrawerOpen} onOpenChange={closeStudents} title={`Estudiantes · ${selected?.nombre || ''}`} description="Agrega o retira estudiantes inscritos en este curso." size="wide">
      {error && <p className="course-management__error" role="alert">{error}</p>}<h3>Inscritos ({students.length})</h3>{students.length ? students.map((row) => <div className="course-management__student" key={row.inscripcion_id}><span>{row.nombre_completo || row.username}</span><button type="button" aria-label={`Retirar ${row.nombre_completo || row.username}`} onClick={() => removeStudent(row)}><X size={17}/></button></div>) : <p>Aún no hay estudiantes inscritos.</p>}<h3>Agregar estudiante</h3>{availableStudents.map((student) => <div className="course-management__student" key={student.id}><span>{student.nombre_completo || student.username}</span><button type="button" aria-label={`Agregar ${student.nombre_completo || student.username}`} onClick={() => addStudent(student.id)}><UserPlus size={17}/></button></div>)}{!availableStudents.length && <p>No hay estudiantes disponibles para agregar.</p>}
    </ManagementDrawer>
    <ConfirmDialog open={Boolean(courseToDelete)} title="Eliminar curso" description={`¿Eliminar el curso “${courseToDelete?.nombre || ''}”? Esta acción no se puede deshacer.`} onOpenChange={(open) => { if (!open) setCourseToDelete(null); }} onConfirm={deleteCourseById} />
  </section>;
}
