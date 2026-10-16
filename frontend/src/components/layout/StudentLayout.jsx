import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { BookOpen, Gamepad2, LayoutDashboard, LogOut, Trophy } from 'lucide-react';
import useAuth from '../../hooks/useAuth';
import './layouts.css';

const studentItems = [
  { label: 'Mi inicio', to: '/dashboard', icon: LayoutDashboard, end: true },
  { label: 'Mis tareas', to: '/activities', icon: BookOpen },
  { label: 'Explorar juegos', to: '/games', icon: Gamepad2 },
];

export default function StudentLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const displayName = user?.nombre_completo || user?.username || 'Estudiante';
  const experience = Number(user?.puntos_xp ?? user?.xp ?? 0);
  const level = Number(user?.nivel ?? 1);

  const handleLogout = () => {
    logout();
    navigate('/', { replace: true });
  };

  return (
    <div className="student-layout">
      <aside className="student-sidebar">
        <NavLink className="layout-brand" to="/dashboard">
          <span className="layout-brand__mark" aria-hidden="true">E</span>
          <span>EduNúñez</span>
        </NavLink>
        <nav className="layout-nav" aria-label="Navegación principal">
          {studentItems.map(({ label, to, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) => `layout-nav__link${isActive ? ' is-active' : ''}`}
            >
              <Icon size={19} aria-hidden="true" />
              <span>{label}</span>
            </NavLink>
          ))}
          <span className="layout-nav__link layout-nav__link--disabled" aria-disabled="true" title="Disponible en una próxima fase">
            <Trophy size={19} aria-hidden="true" />
            <span>Mi progreso</span>
            <small>Próximamente</small>
          </span>
        </nav>
        <div className="student-sidebar__footer">
          <div className="student-xp" aria-label={`${experience} puntos de experiencia, nivel ${level}`}>
            <Trophy size={18} aria-hidden="true" />
            <span><strong>{experience} XP</strong><small>Nivel {level}</small></span>
          </div>
          <div className="layout-user-footer__identity">
            <span className="layout-avatar" aria-hidden="true">{displayName.charAt(0).toUpperCase()}</span>
            <strong>{displayName}</strong>
          </div>
          <button className="layout-logout" type="button" onClick={handleLogout}>
            <LogOut size={18} aria-hidden="true" />
            <span>Cerrar sesión</span>
          </button>
        </div>
      </aside>
      <div className="student-layout__workspace">
        <header className="student-layout__header">
          <div>
            <span className="student-layout__eyebrow">¡Sigue aprendiendo!</span>
            <strong>{displayName}</strong>
          </div>
          <div className="student-xp student-xp--compact" aria-label={`${experience} puntos de experiencia`}>
            <Trophy size={18} aria-hidden="true" />
            <strong>{experience} XP · Nivel {level}</strong>
          </div>
        </header>
        <main className="student-layout__content">
          <Outlet />
        </main>
      </div>
      <nav className="student-mobile-nav" aria-label="Navegación principal">
        {studentItems.map(({ label, to, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `student-mobile-nav__link${isActive ? ' is-active' : ''}`}
          >
            <Icon size={19} aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
