import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  BookOpen,
  GraduationCap,
  Mail,
  Pencil,
  Plus,
  Search,
  ShieldCheck,
  Trash2,
  UserRound,
  UsersRound,
  X,
} from 'lucide-react';
import ManagementDrawer from '../../components/ui/ManagementDrawer';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import { listUsers, createUser, updateUser, deleteUser } from '../../services/users.service';
import './UserManagement.css';

const emptyUser = { username: '', email: '', password: '', nombre_completo: '', rol: 'estudiante' };
const roleLabels = { profesor: 'Docente', estudiante: 'Estudiante', administrador: 'Administrador' };
const roleIcons = { profesor: GraduationCap, estudiante: UserRound, administrador: ShieldCheck };
const tabs = [['all', 'Todos'], ['profesor', 'Docentes'], ['estudiante', 'Estudiantes'], ['administrador', 'Administradores']];

const displayName = (item) => item?.nombre_completo || item?.username || 'Usuario';
const initials = (name) => name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join('').toUpperCase();

export default function UserManagement({ user }) {
  const [users, setUsers] = useState([]);
  const [previewUser, setPreviewUser] = useState(null);
  const [editingUser, setEditingUser] = useState(null);
  const [userToDelete, setUserToDelete] = useState(null);
  const [form, setForm] = useState(emptyUser);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [roleFilter, setRoleFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await listUsers();
      setUsers(Array.isArray(response.data) ? response.data : response.data.usuarios || []);
      setError('');
    } catch (_) {
      setError('No fue posible cargar los usuarios.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadUsers(); }, [loadUsers]);

  const canManage = (item) => user?.rol === 'administrador' || (user?.rol === 'profesor' && item.rol === 'estudiante');
  const counts = useMemo(() => ({
    all: users.length,
    profesor: users.filter((item) => item.rol === 'profesor').length,
    estudiante: users.filter((item) => item.rol === 'estudiante').length,
    administrador: users.filter((item) => item.rol === 'administrador').length,
  }), [users]);

  const filtered = useMemo(() => {
    const query = search.trim().toLocaleLowerCase();
    return users.filter((item) => {
      const matchesRole = roleFilter === 'all' || item.rol === roleFilter;
      const courseNames = (item.cursos || []).map((course) => course.nombre).join(' ');
      const matchesQuery = !query || `${displayName(item)} ${item.username || ''} ${item.email || ''} ${courseNames}`.toLocaleLowerCase().includes(query);
      return matchesRole && matchesQuery;
    });
  }, [users, roleFilter, search]);

  useEffect(() => {
    if (!filtered.length) {
      setPreviewUser(null);
      return;
    }
    const currentPreview = filtered.find((item) => item.id === previewUser?.id);
    if (currentPreview !== previewUser) setPreviewUser(currentPreview || filtered[0]);
  }, [filtered, previewUser]);

  const closeDrawer = useCallback((open) => setDrawerOpen(open), []);
  const openCreate = () => {
    setEditingUser(null);
    setForm({ ...emptyUser, rol: 'estudiante' });
    setError('');
    setDrawerOpen(true);
  };
  const openEdit = (item) => {
    setEditingUser(item);
    setForm({ username: item.username || '', email: item.email || '', password: '', nombre_completo: item.nombre_completo || '', rol: item.rol });
    setError('');
    setDrawerOpen(true);
  };
  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));

  const save = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError('');
    const payload = { ...form };
    if (editingUser && !payload.password) delete payload.password;
    try {
      if (editingUser) await updateUser(editingUser.id, payload);
      else await createUser(payload);
      setDrawerOpen(false);
      setSuccess(editingUser ? 'Usuario actualizado correctamente.' : 'Usuario creado correctamente.');
      await loadUsers();
    } catch (e) {
      const data = e.response?.data;
      setError(typeof data === 'object' ? Object.values(data).flat().join(' ') : 'No fue posible guardar el usuario.');
    } finally {
      setSaving(false);
    }
  };

  const remove = async () => {
    if (!userToDelete) return;
    try {
      await deleteUser(userToDelete.id);
      setSuccess('Usuario eliminado correctamente.');
      setUserToDelete(null);
      await loadUsers();
    } catch (_) {
      setError('No fue posible eliminar el usuario.');
      setUserToDelete(null);
    }
  };

  const previewRoleLabel = previewUser ? roleLabels[previewUser.rol] || previewUser.rol : '';
  const PreviewRoleIcon = previewUser ? roleIcons[previewUser.rol] || UserRound : UserRound;
  const title = user?.rol === 'profesor' ? 'Gestiona los estudiantes de tus cursos.' : 'Administra las cuentas y consulta sus datos académicos.';

  return (
    <section className="user-management">
      <header className="user-management__hero">
        <div className="user-management__hero-copy">
          <span className="user-management__eyebrow"><UsersRound size={15} aria-hidden="true" /> Administración</span>
          <h1>Gestión de usuarios</h1>
          <p>{title}</p>
        </div>
        <button className="user-management__primary" type="button" onClick={openCreate}>
          <Plus size={18} aria-hidden="true" />{user?.rol === 'profesor' ? 'Crear estudiante' : 'Registrar usuario'}
        </button>
        <div className="user-management__hero-orb" aria-hidden="true" />
      </header>

      {success && <div className="user-management__notice" role="status"><span>{success}</span><button type="button" aria-label="Cerrar aviso" onClick={() => setSuccess('')}><X size={16} /></button></div>}
      {error && !drawerOpen && <p className="user-management__error" role="alert">{error}</p>}

      <div className="user-management__stats" aria-label="Resumen de usuarios">
        <button type="button" className={`user-management__stat${roleFilter === 'all' ? ' is-active' : ''}`} onClick={() => setRoleFilter('all')}>
          <span className="user-management__stat-icon user-management__stat-icon--all"><UsersRound size={19} /></span><span><small>Total de usuarios</small><strong>{counts.all}</strong></span>
        </button>
        <button type="button" className={`user-management__stat${roleFilter === 'profesor' ? ' is-active' : ''}`} onClick={() => setRoleFilter('profesor')}>
          <span className="user-management__stat-icon user-management__stat-icon--teacher"><GraduationCap size={19} /></span><span><small>Docentes</small><strong>{counts.profesor}</strong></span>
        </button>
        <button type="button" className={`user-management__stat${roleFilter === 'estudiante' ? ' is-active' : ''}`} onClick={() => setRoleFilter('estudiante')}>
          <span className="user-management__stat-icon user-management__stat-icon--student"><UserRound size={19} /></span><span><small>Estudiantes</small><strong>{counts.estudiante}</strong></span>
        </button>
        {user?.rol === 'administrador' && <button type="button" className={`user-management__stat${roleFilter === 'administrador' ? ' is-active' : ''}`} onClick={() => setRoleFilter('administrador')}>
          <span className="user-management__stat-icon user-management__stat-icon--admin"><ShieldCheck size={19} /></span><span><small>Administradores</small><strong>{counts.administrador}</strong></span>
        </button>}
      </div>

      <div className="user-management__toolbar">
        <nav className="user-management__tabs" aria-label="Filtrar usuarios por rol">
          {tabs.filter(([key]) => key !== 'administrador' || user?.rol === 'administrador').map(([key, label]) => (
            <button type="button" key={key} aria-pressed={roleFilter === key} onClick={() => setRoleFilter(key)}>{label}<span>{counts[key]}</span></button>
          ))}
        </nav>
        <label className="user-management__search">
          <Search size={18} aria-hidden="true" /><span className="sr-only">Buscar por nombre, correo o curso</span>
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar nombre, correo o curso..." />
          {search && <button type="button" aria-label="Limpiar búsqueda" onClick={() => setSearch('')}><X size={16} /></button>}
        </label>
      </div>

      {loading ? <p className="user-management__empty" role="status">Cargando usuarios...</p> : filtered.length ? (
        <div className="user-management__workspace">
          <div className="user-management__directory">
            <div className="user-management__directory-heading"><div><h2>Directorio</h2><p>{filtered.length} {filtered.length === 1 ? 'persona' : 'personas'}</p></div></div>
            <div className="user-management__people" role="list" aria-label="Usuarios">
              {filtered.map((item) => {
                const RoleIcon = roleIcons[item.rol] || UserRound;
                const name = displayName(item);
                const isSelected = previewUser?.id === item.id;
                return <article className={`user-management__person${isSelected ? ' is-selected' : ''}`} key={item.id} role="listitem">
                  <button type="button" className="user-management__person-select" onClick={() => setPreviewUser(item)} aria-pressed={isSelected}>
                    <span className={`user-management__avatar user-management__avatar--${item.rol}`}>{initials(name)}</span>
                    <span className="user-management__person-copy"><strong>{name}</strong><small>{item.email || item.username}</small></span>
                    <span className={`user-management__role user-management__role--${item.rol}`}><RoleIcon size={13} aria-hidden="true" />{roleLabels[item.rol] || item.rol}</span>
                  </button>
                  <div className="user-management__person-meta">
                    <span><BookOpen size={14} aria-hidden="true" />{(item.cursos || []).length ? `${item.cursos.length} ${item.cursos.length === 1 ? 'curso' : 'cursos'}` : 'Sin cursos vinculados'}</span>
                    {canManage(item) && <div className="user-management__actions">
                      <button type="button" title="Editar usuario" aria-label={`Editar ${name}`} onClick={() => openEdit(item)}><Pencil size={15} /></button>
                      <button type="button" title="Eliminar usuario" aria-label={`Eliminar ${name}`} onClick={() => setUserToDelete(item)}><Trash2 size={15} /></button>
                    </div>}
                  </div>
                </article>;
              })}
            </div>
          </div>

          {previewUser && <aside className="user-management__preview" aria-label={`Vista previa de ${displayName(previewUser)}`}>
            <div className={`user-management__preview-banner user-management__preview-banner--${previewUser.rol}`}>
              <span className="user-management__preview-avatar">{initials(displayName(previewUser))}</span>
              <span className={`user-management__role user-management__role--${previewUser.rol}`}><PreviewRoleIcon size={14} aria-hidden="true" />{previewRoleLabel}</span>
            </div>
            <div className="user-management__preview-content">
              <h2>{displayName(previewUser)}</h2>
              <p className="user-management__username">@{previewUser.username}</p>
              <a className="user-management__email" href={`mailto:${previewUser.email}`}><Mail size={16} aria-hidden="true" /><span>{previewUser.email || 'Correo no registrado'}</span></a>
              <div className="user-management__preview-divider" />
              <div className="user-management__courses-heading"><div><h3>{previewUser.rol === 'profesor' ? 'Cursos asignados' : previewUser.rol === 'estudiante' ? 'Cursos inscritos' : 'Información académica'}</h3><p>{(previewUser.cursos || []).length} {(previewUser.cursos || []).length === 1 ? 'curso vinculado' : 'cursos vinculados'}</p></div><span className="user-management__course-count"><BookOpen size={16} />{(previewUser.cursos || []).length}</span></div>
              {(previewUser.cursos || []).length ? <ul className="user-management__course-list">{previewUser.cursos.map((course) => <li key={course.id}><span className="user-management__course-icon"><BookOpen size={16} /></span><span>{course.nombre}</span></li>)}</ul> : <div className="user-management__no-courses"><BookOpen size={20} /><span>{previewUser.rol === 'administrador' ? 'Este perfil no requiere cursos asignados.' : 'Este usuario todavía no tiene cursos vinculados.'}</span></div>}
              {canManage(previewUser) && <div className="user-management__preview-actions"><button type="button" onClick={() => openEdit(previewUser)}><Pencil size={16} />Editar usuario</button><button type="button" aria-label={`Eliminar ${displayName(previewUser)}`} onClick={() => setUserToDelete(previewUser)}><Trash2 size={16} /></button></div>}
            </div>
          </aside>}
        </div>
      ) : <div className="user-management__empty"><UsersRound size={24} /><strong>No encontramos usuarios</strong><span>Prueba con otro término o cambia el filtro seleccionado.</span></div>}

      <ManagementDrawer open={drawerOpen} onOpenChange={closeDrawer} title={editingUser ? 'Editar usuario' : user?.rol === 'profesor' ? 'Crear estudiante' : 'Registrar usuario'} description="Completa los datos de acceso y el perfil." footer={<div className="user-management__form-actions"><button type="button" onClick={() => setDrawerOpen(false)}>Cancelar</button><button type="submit" form="user-form" disabled={saving}>{saving ? 'Guardando...' : editingUser ? 'Guardar cambios' : 'Crear usuario'}</button></div>}>
        {error && <p className="user-management__error" role="alert">{error}</p>}
        <form id="user-form" className="user-management__form" onSubmit={save}>
          <label>Nombre de usuario<input autoComplete="username" name="username" required value={form.username} onChange={change} /></label>
          <label>Nombre completo<input name="nombre_completo" required value={form.nombre_completo} onChange={change} /></label>
          <label>Correo electrónico<input autoComplete="email" type="email" name="email" required value={form.email} onChange={change} /></label>
          <label>{editingUser ? 'Nueva contraseña (opcional)' : 'Contraseña'}<input autoComplete="new-password" type="password" name="password" required={!editingUser} value={form.password} onChange={change} placeholder={editingUser ? 'Déjala en blanco para conservarla' : ''} /></label>
          {user?.rol === 'administrador' && <label>Rol<select name="rol" value={form.rol} onChange={change}><option value="estudiante">Estudiante</option><option value="profesor">Docente</option><option value="administrador">Administrador</option></select></label>}
        </form>
      </ManagementDrawer>
      <ConfirmDialog open={Boolean(userToDelete)} title="Eliminar usuario" description={`¿Eliminar a ${displayName(userToDelete)}? Esta acción no se puede deshacer.`} onOpenChange={(open) => { if (!open) setUserToDelete(null); }} onConfirm={remove} />
    </section>
  );
}
