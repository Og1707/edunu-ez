import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Activity, BookOpen, CheckCircle2, ClipboardList, Printer, Users } from 'lucide-react';
import EmptyState from '../../components/ui/EmptyState';
import StatCard from '../../components/ui/StatCard';
import useAuth from '../../hooks/useAuth';
import useDashboard from '../../hooks/useDashboard';
import StudentProfile from './StudentProfile';
import StudentTrend from './StudentTrend';
import { CoursePerformanceChart, SubjectPerformanceChart } from './DashboardCharts';
import '../../pages/Dashboard.css';

// Must match the CSS animation duration so the panel finishes sliding before unmounting
const SLIDE_DURATION = 270;

const views = [
  { id: 'resumen', label: 'Resumen' },
  { id: 'estudiantes', label: 'Estudiantes' },
  { id: 'cursos', label: 'Cursos' },
  { id: 'rendimiento', label: 'Rendimiento' },
  { id: 'actividades', label: 'Actividades' },
  { id: 'reportes', label: 'Reportes' },
];

function StudentsTable({ students, onSelect }) {
  if (!students.length) return <EmptyState title="No hay estudiantes en este alcance" description="Los estudiantes inscritos en los cursos aparecerán aquí."/>;
  return <div className="dashboard-table-wrap"><table className="dashboard-table"><thead><tr><th>Estudiante</th><th>Cursos</th><th>Actividades</th><th>Promedio</th><th>Tendencia</th><th/></tr></thead><tbody>
    {students.map((student) => <tr key={student.id}><td><strong>{student.nombre}</strong><small>@{student.username}</small></td><td>{student.cursos.join(', ')}</td><td>{student.actividades_completadas}/{student.actividades_totales}</td><td>{student.promedio === null ? '—' : `${student.promedio}%`}</td><td><StudentTrend values={student.tendencia}/></td><td><button className="dashboard-text-button" type="button" onClick={() => onSelect(student.id)}>Ver perfil</button></td></tr>)}
  </tbody></table></div>;
}

export default function DashboardStaff() {
  const { user } = useAuth();
  const { data, student, loading, detailLoading, error, selectStudent } = useDashboard();
  const [view, setView] = useState('resumen');
  const [search, setSearch] = useState('');

  /**
   * panelState: 'closed' | 'open' | 'closing'
   *
   * 'closed'  -> panel is not rendered at all
   * 'open'    -> panel is visible with slide-in animation
   * 'closing' -> panel is still rendered but playing slide-out animation;
   *              after SLIDE_DURATION ms it switches to 'closed'
   */
  const [panelState, setPanelState] = useState('closed');
  const [selectedId, setSelectedId] = useState(null);

  /**
   * snapshot: keeps the last fetched student data alive while the panel is
   * animating out. Without this, clearing `student` in useDashboard while the
   * panel is still visible causes StudentProfile to render null and the
   * element disappears instantly, cutting the animation short.
   */
  const [snapshot, setSnapshot] = useState(null);

  const timerRef = useRef(null);
  const isAdmin = user?.rol === 'administrador';
  const students = useMemo(() => data?.estudiantes || [], [data]);
  const filteredStudents = useMemo(
    () => students.filter((item) =>
      `${item.nombre} ${item.username} ${item.cursos.join(' ')}`
        .toLocaleLowerCase()
        .includes(search.toLocaleLowerCase())
    ),
    [students, search]
  );

  // Keep snapshot fresh whenever the hook delivers real detail data
  useEffect(() => {
    if (student) setSnapshot(student);
  }, [student]);

  const clearTimer = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const openStudent = useCallback(async (id) => {
    clearTimer();                 // cancel any in-progress close animation
    setPanelState('open');
    setSelectedId(id);
    await selectStudent(id);
  }, [clearTimer, selectStudent]);

  const closeProfile = useCallback(() => {
    if (panelState === 'closing') return;  // already animating out
    setPanelState('closing');
    timerRef.current = setTimeout(() => {
      setPanelState('closed');
      setSelectedId(null);
      setSnapshot(null);          // now safe to clear snapshot — panel is gone
      selectStudent(null);
      timerRef.current = null;
    }, SLIDE_DURATION);
  }, [panelState, selectStudent]);

  // Clean up timer on unmount
  useEffect(() => () => clearTimer(), [clearTimer]);

  // Student data available from the detail endpoint; fall back to list summary
  const summaryStudent = useMemo(
    () => selectedId
      ? students.find((s) => Number(s.id) === Number(selectedId)) || null
      : null,
    [selectedId, students]
  );
  const displayStudent = snapshot || summaryStudent;

  const printReport = () => window.print();

  const metrics = data ? [
    { label: 'Cursos', value: data.kpis.cursos, icon: <BookOpen/>, description: isAdmin ? 'En toda la plataforma' : 'A tu cargo' },
    { label: 'Estudiantes', value: data.kpis.estudiantes, icon: <Users/>, description: isAdmin ? 'En todos los cursos' : 'Inscritos en tus cursos' },
    ...(isAdmin ? [{ label: 'Profesores', value: data.kpis.profesores, icon: <Users/>, description: 'Cuentas docentes' }] : []),
    { label: 'Actividades', value: data.kpis.actividades, icon: <ClipboardList/>, description: 'En cursos de este panel' },
    { label: 'Promedio general', value: data.kpis.promedio === null ? '—' : `${data.kpis.promedio}%`, icon: <Activity/>, description: 'Actividades calificadas' },
    { label: 'Resultados', value: data.kpis.completadas, icon: <CheckCircle2/>, description: 'Calificaciones registradas' },
  ] : [];

  const panelOpen    = panelState !== 'closed';
  const panelClosing = panelState === 'closing';

  return <main className="dashboard-page dashboard-staff">
    <header className="dashboard-page__header"><div><span className="dashboard-page__eyebrow">Panel de EduNúñez</span><h1>Hola, {user?.nombre_completo || user?.username || 'bienvenido'}</h1><p>{isAdmin ? 'Resumen global del sistema educativo.' : 'Resumen de tus cursos y estudiantes.'}</p></div><div className="dashboard-header-actions"><span className="dashboard-page__role">{user?.rol}</span><button type="button" className="dashboard-button" onClick={printReport}><Printer size={17}/> Imprimir</button></div></header>
    {error && <p className="dashboard-page__error" role="alert">{error}</p>}
    <nav className="dashboard-tabs" aria-label="Vistas del dashboard">{views.map((item) => <button key={item.id} type="button" className={view === item.id ? 'is-active' : ''} aria-current={view === item.id ? 'page' : undefined} onClick={() => setView(item.id)}>{item.label}</button>)}</nav>
    {loading ? <p role="status">Cargando resumen…</p> : data && <>
      {view === 'resumen' && <div className="dashboard-tab-content">
        <section className="dashboard-page__metrics" aria-label="Indicadores principales">{metrics.map((metric) => <StatCard key={metric.label} {...metric}/>)}</section>
        <div className="dashboard-grid dashboard-grid--two"><section className="dashboard-panel"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Visión académica</span><h2>Rendimiento por curso</h2></div><button type="button" className="dashboard-text-button" onClick={() => setView('rendimiento')}>Ver detalle</button></div><CoursePerformanceChart courses={data.cursos}/></section>
          <section className="dashboard-panel"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Materias vinculadas</span><h2>Rendimiento por asignatura</h2></div></div><SubjectPerformanceChart subjects={data.asignaturas} emptyDescription="Solo se muestran cursos asociados a una materia."/></section></div>
        <section className="dashboard-panel dashboard-panel--spaced"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Seguimiento individual</span><h2>Estudiantes</h2></div><button type="button" className="dashboard-text-button" onClick={() => setView('estudiantes')}>Ver todos ({students.length})</button></div><StudentsTable students={filteredStudents.slice(0, 6)} onSelect={openStudent}/></section>
      </div>}
      {view === 'estudiantes' && <div className="dashboard-tab-content"><section className="dashboard-panel"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Comunidad académica</span><h2>Estudiantes</h2></div><input className="dashboard-search" type="search" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar estudiante o curso" aria-label="Buscar estudiante o curso"/></div><StudentsTable students={filteredStudents} onSelect={openStudent}/></section></div>}
      {view === 'cursos' && <div className="dashboard-tab-content"><section className="dashboard-course-grid" aria-label="Cursos">{data.cursos.length ? data.cursos.map((course) => <article className="dashboard-course-card" key={course.id}><span className="dashboard-course-card__icon"><BookOpen/></span><h2>{course.nombre}</h2><p>{course.descripcion || 'Sin descripción'}</p>{course.materia && <span className="dashboard-chip">{course.materia.nombre}</span>}<div className="dashboard-course-card__stats"><span><strong>{course.total_estudiantes}</strong> estudiantes</span><span><strong>{course.total_actividades}</strong> actividades</span></div><div className="dashboard-course-card__grade"><span>Promedio del curso</span><strong>{course.promedio === null ? '—' : `${course.promedio}%`}</strong></div></article>) : <EmptyState title="No hay cursos" description="No se encontraron cursos dentro de tu alcance."/>}</section></div>}
      {view === 'rendimiento' && <div className="dashboard-tab-content"><div className="dashboard-grid dashboard-grid--two"><section className="dashboard-panel"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Comparativo</span><h2>Rendimiento por curso</h2></div></div><CoursePerformanceChart courses={data.cursos}/></section><section className="dashboard-panel"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Desglose por materia</span><h2>Asignaturas</h2></div></div><SubjectPerformanceChart subjects={data.asignaturas}/></section><section className="dashboard-panel dashboard-panel--wide"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Detalle</span><h2>Rendimiento por estudiante</h2></div></div><StudentsTable students={filteredStudents} onSelect={openStudent}/></section></div></div>}
      {view === 'actividades' && <div className="dashboard-tab-content"><section className="dashboard-panel"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Trabajo académico</span><h2>Actividades de los cursos</h2></div></div>{data.actividades.length ? <div className="dashboard-table-wrap"><table className="dashboard-table"><thead><tr><th>Actividad</th><th>Curso</th><th>Estado</th><th>Completadas</th><th>Promedio</th></tr></thead><tbody>{data.actividades.map((activity) => <tr key={activity.id}><td><strong>{activity.titulo}</strong></td><td>{activity.curso}</td><td>{activity.estado}</td><td>{activity.completadas}/{activity.asignaciones}</td><td>{activity.promedio === null ? '—' : `${activity.promedio}%`}</td></tr>)}</tbody></table></div> : <EmptyState title="No hay actividades" description="Las actividades de los cursos aparecerán aquí."/>}</section></div>}
      {view === 'reportes' && <div className="dashboard-tab-content"><section className="dashboard-panel dashboard-report"><div className="dashboard-section-heading"><div><span className="dashboard-eyebrow">Reporte actual</span><h2>{isAdmin ? 'Estado global del sistema' : 'Reporte de tus cursos'}</h2><p className="dashboard-muted">Generado el {new Date().toLocaleDateString()}</p></div><button type="button" className="dashboard-button" onClick={printReport}><Printer size={17}/> Imprimir o guardar PDF</button></div><section className="dashboard-page__metrics">{metrics.map((metric) => <StatCard key={metric.label} {...metric}/>)}</section><h3>Rendimiento por curso</h3><CoursePerformanceChart courses={data.cursos}/><h3>Estudiantes con seguimiento</h3><StudentsTable students={students} onSelect={openStudent}/></section></div>}
    </>}

    {/* Panel + backdrop: rendered as long as panelState is NOT 'closed'.
        The 'closing' sub-state keeps them mounted during the slide-out animation. */}
    {panelOpen && <>
      <div
        className={`dashboard-profile-backdrop${panelClosing ? ' is-closing' : ''}`}
        onClick={closeProfile}
        aria-hidden="true"
      />
      <StudentProfile
        student={displayStudent}
        loading={detailLoading && !displayStudent}
        error={error}
        onClose={closeProfile}
        isClosing={panelClosing}
      />
    </>}
  </main>;
}
