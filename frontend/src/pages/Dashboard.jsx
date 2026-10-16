import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, BookOpen, CheckCircle2, ClipboardList, Gamepad2, Users } from 'lucide-react';
import useAuth from '../hooks/useAuth';
import StatCard from '../components/ui/StatCard';
import EmptyState from '../components/ui/EmptyState';
import { getStudentStats } from '../services/games.service';
import { getTeacherActivities, getActivities } from '../services/activities.service';
import { getCourses } from '../services/courses.service';
import { listUsers } from '../services/users.service';
import './Dashboard.css';

const asList = (data, key) => Array.isArray(data) ? data : data?.[key] || [];
const withRequestLabel = (promise, label) => promise.catch((failure) => {
  failure.requestLabel = label;
  throw failure;
});

const describeLoadError = (failure) => {
  const detail = failure.response?.data?.mensaje || failure.response?.data?.detail;
  const status = failure.response?.status;
  const source = failure.requestLabel ? `${failure.requestLabel}: ` : '';
  if (detail) return `${source}${detail}`;
  if (status) return `${source}el servidor respondió con HTTP ${status}.`;
  return `${source}no se pudo conectar con el servidor.`;
};

export default function Dashboard() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const isStudent = user?.rol === 'estudiante';
  const isAdmin = user?.rol === 'administrador';

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        if (isStudent) {
          const { data } = await getStudentStats();
          if (active) setMetrics([
            { label: 'Actividades completadas', value: data.actividades_completadas, icon: <CheckCircle2/>, description: `${data.porcentaje_completado}% de avance` },
            { label: 'Actividades pendientes', value: data.actividades_pendientes, icon: <ClipboardList/>, description: `${data.actividades_por_vencer} por vencer pronto` },
            { label: 'Promedio', value: `${data.puntuacion_promedio}%`, icon: <Activity/>, description: 'Según tus actividades calificadas' },
          ]);
        } else if (isAdmin) {
          const [activitiesResponse, coursesResponse, usersResponse] = await Promise.all([getActivities(), getCourses(), listUsers()]);
          if (active) setMetrics([
            { label: 'Actividades', value: asList(activitiesResponse.data, 'actividades').length, icon: <ClipboardList/>, description: 'Registradas en la plataforma' },
            { label: 'Cursos', value: asList(coursesResponse.data, 'cursos').length, icon: <BookOpen/>, description: 'Cursos disponibles' },
            { label: 'Usuarios', value: asList(usersResponse.data, 'usuarios').length, icon: <Users/>, description: 'Cuentas registradas' },
          ]);
        } else {
          const [activitiesResponse, coursesResponse] = await Promise.all([
            withRequestLabel(getTeacherActivities(), 'Actividades'),
            withRequestLabel(getCourses(), 'Cursos'),
          ]);
          const courses = asList(coursesResponse.data, 'cursos').filter((course) => Number(course.profesor) === Number(user?.usuario_id));
          if (active) setMetrics([
            { label: 'Mis actividades', value: asList(activitiesResponse.data, 'actividades').length, icon: <ClipboardList/>, description: 'En los cursos que orientas' },
            { label: 'Mis cursos', value: courses.length, icon: <BookOpen/>, description: 'Cursos a tu cargo' },
          ]);
        }
      } catch (failure) {
        console.error('Error loading dashboard:', failure);
        if (active) setError(`No fue posible cargar el resumen del panel. ${describeLoadError(failure)}`);
      } finally { if (active) setLoading(false); }
    };
    load();
    return () => { active = false; };
  }, [isStudent, isAdmin, user?.usuario_id]);

  const links = isStudent
    ? [{ to: '/activities', label: 'Mis actividades', description: 'Continúa tus tareas y revisa tus resultados.', icon: <ClipboardList/> }, { to: '/games', label: 'Explorar juegos', description: 'Practica con juegos educativos.', icon: <Gamepad2/> }, { to: '/progress', label: 'Mi progreso', description: 'Consulta estadísticas e historial.', icon: <Activity/> }]
    : [{ to: '/activities', label: 'Gestionar actividades', description: 'Crea y organiza actividades educativas.', icon: <ClipboardList/> }, { to: '/courses', label: 'Gestionar cursos', description: 'Administra cursos y estudiantes.', icon: <BookOpen/> }, ...(isAdmin ? [{ to: '/users', label: 'Gestionar usuarios', description: 'Administra las cuentas y sus roles.', icon: <Users/> }] : [])];

  return <main className="dashboard-page">
    <header className="dashboard-page__header"><div><span className="dashboard-page__eyebrow">Panel de EduNúñez</span><h1>Hola, {user?.nombre_completo || user?.username || 'bienvenido'}</h1><p>{isStudent ? 'Este es tu resumen de aprendizaje.' : 'Aquí tienes un resumen de la plataforma.'}</p></div><span className="dashboard-page__role">{user?.rol || 'Usuario'}</span></header>
    {error && <p className="dashboard-page__error" role="alert">{error}</p>}
    <section className="dashboard-page__metrics" aria-label="Resumen">{loading ? <p role="status">Cargando resumen…</p> : metrics.map((metric) => <StatCard key={metric.label} {...metric}/>)}</section>
    <section className="dashboard-page__links" aria-labelledby="dashboard-links-title"><h2 id="dashboard-links-title">Accesos directos</h2>{links.length ? <div className="dashboard-page__link-grid">{links.map((item) => <Link className="dashboard-page__link-card" to={item.to} key={item.to}><span aria-hidden="true">{item.icon}</span><div><h3>{item.label}</h3><p>{item.description}</p></div><span className="dashboard-page__arrow" aria-hidden="true">→</span></Link>)}</div> : <EmptyState title="No hay secciones disponibles" description="Tu cuenta no tiene accesos configurados."/>}</section>
  </main>;
}
