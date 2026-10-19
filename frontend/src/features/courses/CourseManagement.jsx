import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Plus, Search, Pencil, Trash2, Users, UserPlus, X } from 'lucide-react';
import ManagementDrawer from '../../components/ui/ManagementDrawer';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import {
  getCourses, getSubjects, createSubject, createCourse, updateCourse,
  deleteCourse, getCourseStudents, addStudentToCourse, removeStudentFromCourse,
} from '../../services/courses.service';
import { listUsers } from '../../services/users.service';
import TeacherCourses from './TeacherCourses';
import './CourseManagement.css';

const blankCourse = { nombre: '', descripcion: '', profesor: '', asignaturas: [] };
const hasTeacher = (course) => Boolean(course.profesor);
const normalizeSearchText = (value) => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();

export default function CourseManagement({ user }) {
  if (user?.rol === 'profesor') return <TeacherCourses />;
  return <AdminCourseManagement user={user} />;
}

function AdminCourseManagement({ user }) {
  const [courses, setCourses] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [students, setStudents] = useState([]);
  const [availableStudents, setAvailableStudents] = useState([]);
  const [studentSearch, setStudentSearch] = useState('');
  const [studentsLoading, setStudentsLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [courseToDelete, setCourseToDelete] = useState(null);
  const [form, setForm] = useState(blankCourse);
  const [newSubject, setNewSubject] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [studentsDrawerOpen, setStudentsDrawerOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [assignmentFilter, setAssignmentFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [subjectSaving, setSubjectSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadCourses = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getCourses();
      setCourses(Array.isArray(response.data) ? response.data : response.data.cursos || []);
      setError('');
    } catch (_) {
      setError('No fue posible cargar los cursos.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadCourses();
    getSubjects().then(({ data }) => setSubjects(data)).catch(() => setError('No fue posible cargar las asignaturas.'));
    if (user?.rol === 'administrador') {
      listUsers()
        .then((response) => setTeachers((response.data.usuarios || response.data || []).filter((item) => item.rol === 'profesor')))
        .catch(() => {});
    }
  }, [loadCourses, user]);

  const visibleCourses = useMemo(() => courses.filter((course) => {
    const assignedToTeacher = user?.rol !== 'profesor' || Number(course.profesor) === Number(user?.usuario_id);
    const query = search.trim().toLocaleLowerCase();
    const matchesSearch = !query || `${course.nombre || ''} ${course.descripcion || ''} ${course.profesor_nombre || ''} ${(course.asignaturas_nombres || []).join(' ')}`.toLocaleLowerCase().includes(query);
    return assignedToTeacher && matchesSearch
      && (assignmentFilter === 'all' || (assignmentFilter === 'assigned' ? hasTeacher(course) : !hasTeacher(course)));
  }), [courses, search, assignmentFilter, user?.rol, user?.usuario_id]);

  const visibleAvailableStudents = useMemo(() => {
    const query = normalizeSearchText(studentSearch.trim());
    if (!query) return availableStudents;
    return availableStudents.filter((student) => normalizeSearchText(
      `${student.nombre_completo || ''} ${student.username || ''} ${student.email || ''}`,
    ).includes(query));
  }, [availableStudents, studentSearch]);

  const canManage = (course) => user?.rol === 'administrador' || Number(course.profesor) === Number(user?.usuario_id);
  const openCreate = () => {
    setSelected(null);
    setForm({ ...blankCourse, asignaturas: [] });
    setNewSubject('');
    setError('');
    setDrawerOpen(true);
  };
  const openEdit = (course) => {
    setSelected(course);
    setForm({ nombre: course.nombre || '', descripcion: course.descripcion || '', profesor: course.profesor || '', asignaturas: course.asignaturas || [] });
    setNewSubject('');
    setError('');
    setDrawerOpen(true);
  };
  const setField = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));

  const saveCourse = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    const payload = {
      ...form,
      profesor: user.rol === 'profesor' ? user.usuario_id : (form.profesor || null),
    };
    try {
      if (selected) await updateCourse(selected.id, payload);
      else await createCourse(payload);
      setDrawerOpen(false);
      setSuccess(selected ? 'Curso actualizado.' : 'Curso creado.');
      await loadCourses();
    } catch (failure) {
      setError(failure.response?.data?.mensaje || 'No fue posible guardar el curso. Revisa los campos.');
    } finally {
      setSaving(false);
    }
  };

  const toggleSubject = (subjectId) => setForm((current) => ({
    ...current,
    asignaturas: current.asignaturas.includes(subjectId)
      ? current.asignaturas.filter((id) => id !== subjectId)
      : [...current.asignaturas, subjectId],
  }));

  const addSubject = async () => {
    const nombre = newSubject.trim();
    if (!nombre) return;
    setSubjectSaving(true);
    setError('');
    try {
      const { data } = await createSubject({ nombre });
      setSubjects((current) => [...current, data].sort((left, right) => left.nombre.localeCompare(right.nombre)));
      setForm((current) => ({ ...current, asignaturas: [...current.asignaturas, data.id] }));
      setNewSubject('');
    } catch (failure) {
      setError(failure.response?.data?.nombre?.[0] || failure.response?.data?.mensaje || 'No fue posible crear la asignatura.');
    } finally {
      setSubjectSaving(false);
    }
  };

  const deleteCourseById = async () => {
    if (!courseToDelete) return;
    try {
      await deleteCourse(courseToDelete.id);
      setSuccess('Curso eliminado.');
      setCourseToDelete(null);
      await loadCourses();
    } catch (_) {
      setError('No fue posible eliminar el curso.');
      setCourseToDelete(null);
    }
  };

  const openStudents = async (course) => {
    setSelected(course);
    setStudentsDrawerOpen(true);
    setStudentSearch('');
    setError('');
    setStudentsLoading(true);
    try {
      const [enrolled, users] = await Promise.all([getCourseStudents(course.id), listUsers()]);
      const enrolledRows = enrolled.data.estudiantes || enrolled.data || [];
      setStudents(enrolledRows);
      const enrolledIds = enrolledRows.map((row) => row.id);
      const userRows = users.data.usuarios || users.data || [];
      setAvailableStudents(userRows.filter((item) => item.rol === 'estudiante' && !enrolledIds.includes(item.id)));
    } catch (_) {
      setError('No se pudo cargar la lista de estudiantes.');
    } finally {
      setStudentsLoading(false);
    }
  };

  const addStudent = async (studentId) => {
    try {
      await addStudentToCourse({ estudiante_id: studentId, curso_id: selected.id });
      await openStudents(selected);
    } catch (_) {
      setError('No se pudo agregar el estudiante.');
    }
  };

  const removeStudent = async (row) => {
    if (!window.confirm('¿Retirar este estudiante del curso?')) return;
    try {
      await removeStudentFromCourse(row.inscripcion_id);
      await openStudents(selected);
    } catch (_) {
      setError('No se pudo retirar el estudiante.');
    }
  };

  const closeDrawer = useCallback((open) => setDrawerOpen(open), []);
  const closeStudents = useCallback((open) => {
    setStudentsDrawerOpen(open);
    if (!open) setStudentSearch('');
  }, []);

  return <section className="course-management">
    <header className="course-management__header">
      <div><h2>Gestión de cursos</h2><p>{user?.rol === 'profesor' ? 'Consulta tus cursos asignados y administra sus estudiantes.' : 'Administra cursos, asignaturas, docentes y estudiantes.'}</p></div>
      {user?.rol === 'administrador' && <button className="course-management__primary" onClick={openCreate}><Plus size={18} aria-hidden="true"/> Crear curso</button>}
    </header>
    {success && <p className="course-management__notice" role="status">{success}</p>}
    {error && !drawerOpen && !studentsDrawerOpen && <p className="course-management__error" role="alert">{error}</p>}

    <div className="course-management__filters">
      <label className="course-management__search"><Search size={18} aria-hidden="true"/><span className="sr-only">Buscar cursos</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por curso, docente o asignatura…"/></label>
      {user?.rol === 'administrador' && <label>Docente<select value={assignmentFilter} onChange={(event) => setAssignmentFilter(event.target.value)}><option value="all">Todos</option><option value="assigned">Con docente</option><option value="unassigned">Sin docente</option></select></label>}
    </div>

    {loading ? <div className="course-management__empty" role="status">Cargando cursos…</div> : visibleCourses.length ? <div className="course-management__table-wrap"><table className="course-management__table">
      <thead><tr><th>Curso</th><th>Asignaturas</th><th>Descripción</th><th>Docente</th><th>Estado de asignación</th><th><span className="sr-only">Acciones</span></th></tr></thead>
      <tbody>{visibleCourses.map((course) => <tr key={course.id}>
        <td data-label="Curso">{course.nombre}</td>
        <td data-label="Asignaturas">{course.asignaturas_nombres?.length ? course.asignaturas_nombres.join(', ') : 'Sin asignaturas'}</td>
        <td data-label="Descripción">{course.descripcion || '—'}</td>
        <td data-label="Docente">{course.profesor_nombre || 'Sin asignar'}</td>
        <td data-label="Estado"><span className={`course-management__status ${hasTeacher(course) ? 'is-active' : 'is-inactive'}`}>{hasTeacher(course) ? 'Con docente' : 'Sin docente'}</span></td>
        <td data-label="Acciones"><div className="course-management__actions">{canManage(course) && <>
          <button type="button" aria-label={`Gestionar estudiantes de ${course.nombre}`} title="Gestionar estudiantes" onClick={() => openStudents(course)}><Users size={17}/></button>
          <button type="button" aria-label={`Editar ${course.nombre}`} title="Editar curso" onClick={() => openEdit(course)}><Pencil size={17}/></button>
          <button type="button" aria-label={`Eliminar ${course.nombre}`} title="Eliminar curso" onClick={() => setCourseToDelete(course)}><Trash2 size={17}/></button>
        </>}</div></td>
      </tr>)}</tbody>
    </table></div> : <div className="course-management__empty">{courses.length ? 'No hay cursos que coincidan con esos filtros.' : user?.rol === 'profesor' ? 'Aún no tienes cursos asignados.' : 'Aún no hay cursos. Crea el primero para organizar las actividades.'}</div>}

    <ManagementDrawer open={drawerOpen} onOpenChange={closeDrawer} title={selected ? 'Editar curso' : 'Crear curso'} description="Completa la información del curso." footer={<div className="course-management__form-actions"><button type="button" onClick={() => setDrawerOpen(false)}>Cancelar</button><button type="submit" form="course-form" disabled={saving}>{saving ? 'Guardando…' : selected ? 'Guardar cambios' : 'Crear curso'}</button></div>}>
      {error && <p className="course-management__error" role="alert">{error}</p>}
      <form id="course-form" onSubmit={saveCourse} className="course-management__form">
        <label>Nombre del curso<input name="nombre" required value={form.nombre} onChange={setField}/></label>
        <label>Descripción<textarea name="descripcion" required rows="4" value={form.descripcion} onChange={setField}/></label>
        <fieldset className="course-management__subjects">
          <legend>Asignaturas del curso</legend>
          <p>Selecciona las materias que se impartirán en este curso.</p>
          {subjects.length ? <div className="course-management__subject-options">{subjects.map((subject) => <label key={subject.id}><input type="checkbox" checked={form.asignaturas.includes(subject.id)} onChange={() => toggleSubject(subject.id)}/><span>{subject.nombre}</span></label>)}</div> : <p>No hay asignaturas disponibles.</p>}
          {user?.rol === 'administrador' && <div className="course-management__subject-create"><label htmlFor="new-subject">Agregar asignatura al catálogo</label><div><input id="new-subject" value={newSubject} onChange={(event) => setNewSubject(event.target.value)} placeholder="Ej. Música"/><button type="button" onClick={addSubject} disabled={subjectSaving || !newSubject.trim()}><Plus size={16}/>{subjectSaving ? 'Agregando…' : 'Agregar'}</button></div></div>}
        </fieldset>
        {user?.rol === 'administrador' && <label>Docente<select name="profesor" value={form.profesor} onChange={setField}><option value="">Sin asignar</option>{teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.nombre_completo || teacher.username}</option>)}</select></label>}
      </form>
    </ManagementDrawer>

    <ManagementDrawer open={studentsDrawerOpen} onOpenChange={closeStudents} title={`Estudiantes · ${selected?.nombre || ''}`} description="Administra las inscripciones de este curso." size="wide">
      {error && <p className="course-management__error" role="alert">{error}</p>}
      <section className="course-management__enrolled" aria-labelledby="enrolled-students-title">
        <div className="course-management__enrollment-heading"><div><h3 id="enrolled-students-title">Estudiantes inscritos</h3><p>Estudiantes que ya forman parte del curso.</p></div><span className="course-management__count">{students.length}</span></div>
        {studentsLoading ? <p className="course-management__student-state" role="status">Cargando estudiantes...</p> : students.length ? students.map((row) => <div className="course-management__student" key={row.inscripcion_id}><div className="course-management__student-identity"><span className="course-management__avatar" aria-hidden="true">{(row.nombre_completo || row.username || '?').slice(0, 1).toLocaleUpperCase()}</span><span><strong>{row.nombre_completo || row.username}</strong><small>{row.email || row.username}</small></span></div><button type="button" aria-label={`Retirar ${row.nombre_completo || row.username}`} onClick={() => removeStudent(row)}><X size={17}/></button></div>) : <p className="course-management__student-state">Aún no hay estudiantes inscritos.</p>}
      </section>
      <section className="course-management__available" aria-labelledby="available-students-title">
        <div className="course-management__enrollment-heading"><div><h3 id="available-students-title">Agregar estudiantes</h3><p>Busca por nombre, usuario o correo electrónico.</p></div></div>
        <label className="course-management__student-search"><Search size={18} aria-hidden="true"/><span className="sr-only">Buscar estudiantes disponibles</span><input type="search" value={studentSearch} onChange={(event) => setStudentSearch(event.target.value)} placeholder="Nombre, usuario o correo electrónico" disabled={studentsLoading || !availableStudents.length}/></label>
        {studentsLoading ? <p className="course-management__student-state" role="status">Cargando estudiantes disponibles...</p> : visibleAvailableStudents.length ? <div className="course-management__available-list" aria-live="polite">{visibleAvailableStudents.map((student) => <article className="course-management__available-card" key={student.id}><span className="course-management__avatar" aria-hidden="true">{(student.nombre_completo || student.username || '?').slice(0, 1).toLocaleUpperCase()}</span><span className="course-management__available-info"><strong>{student.nombre_completo || student.username}</strong><small>{student.email || student.username}</small></span><button type="button" aria-label={`Agregar ${student.nombre_completo || student.username}`} onClick={() => addStudent(student.id)}><UserPlus size={17}/><span>Agregar</span></button></article>)}</div> : availableStudents.length ? <div className="course-management__student-state"><p>No se encontraron estudiantes para “{studentSearch}”.</p><button type="button" onClick={() => setStudentSearch('')}>Limpiar búsqueda</button></div> : <p className="course-management__student-state">Todos los estudiantes ya están inscritos en este curso.</p>}
      </section>
    </ManagementDrawer>
    <ConfirmDialog open={Boolean(courseToDelete)} title="Eliminar curso" description={`¿Eliminar el curso “${courseToDelete?.nombre || ''}”? Esta acción no se puede deshacer.`} onOpenChange={(open) => { if (!open) setCourseToDelete(null); }} onConfirm={deleteCourseById}/>
  </section>;
}
