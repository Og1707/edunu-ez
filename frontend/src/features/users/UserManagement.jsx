import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Plus, Search, Pencil, Trash2 } from 'lucide-react';
import ManagementDrawer from '../../components/ui/ManagementDrawer';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import { listUsers, createUser, updateUser, deleteUser } from '../../services/users.service';
import './UserManagement.css';

const emptyUser = { username: '', email: '', password: '', nombre_completo: '', rol: 'estudiante' };
const roleLabels = { profesor: 'Docente', estudiante: 'Estudiante', administrador: 'Administrador' };

export default function UserManagement({ user }) {
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [userToDelete, setUserToDelete] = useState(null);
  const [form, setForm] = useState(emptyUser);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [roleFilter, setRoleFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const loadUsers = useCallback(async () => { setLoading(true); try { const response = await listUsers(); setUsers(Array.isArray(response.data) ? response.data : response.data.usuarios || []); setError(''); } catch (_) { setError('No fue posible cargar los usuarios.'); } finally { setLoading(false); } }, []);
  useEffect(() => { loadUsers(); }, [loadUsers]);
  const canManage = (item) => user?.rol === 'administrador' || (user?.rol === 'profesor' && item.rol === 'estudiante');
  const counts = useMemo(() => ({ all: users.length, profesor: users.filter((item) => item.rol === 'profesor').length, estudiante: users.filter((item) => item.rol === 'estudiante').length, administrador: users.filter((item) => item.rol === 'administrador').length }), [users]);
  const filtered = useMemo(() => users.filter((item) => {
    const q = search.trim().toLocaleLowerCase();
    return (roleFilter === 'all' || item.rol === roleFilter) && (!q || `${item.nombre_completo || ''} ${item.username || ''} ${item.email || ''}`.toLocaleLowerCase().includes(q));
  }), [users, roleFilter, search]);
  const closeDrawer = useCallback((open) => setDrawerOpen(open), []);
  const openCreate = () => { setSelected(null); setForm({ ...emptyUser, rol: 'estudiante' }); setError(''); setDrawerOpen(true); };
  const openEdit = (item) => { setSelected(item); setForm({ username: item.username || '', email: item.email || '', password: '', nombre_completo: item.nombre_completo || '', rol: item.rol }); setError(''); setDrawerOpen(true); };
  const change = (event) => setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  const save = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    const payload = { ...form };
    if (selected && !payload.password) delete payload.password;
    try { if (selected) await updateUser(selected.id, payload); else await createUser(payload); setDrawerOpen(false); setSuccess(selected ? 'Usuario actualizado.' : 'Usuario creado.'); await loadUsers(); }
    catch (e) { const data = e.response?.data; setError(typeof data === 'object' ? Object.values(data).flat().join(' ') : 'No fue posible guardar el usuario.'); }
    finally { setSaving(false); }
  };
  const remove = async () => { if (!userToDelete) return; try { await deleteUser(userToDelete.id); setSuccess('Usuario eliminado.'); setUserToDelete(null); await loadUsers(); } catch (_) { setError('No fue posible eliminar el usuario.'); setUserToDelete(null); } };
  const tabs = [['all', 'Todos'], ['profesor', 'Docentes'], ['estudiante', 'Estudiantes'], ['administrador', 'Admins']];

  return <section className="user-management"><header className="user-management__header"><div><h2>Gestión de usuarios</h2><p>{user?.rol === 'profesor' ? 'Gestiona los estudiantes de la plataforma.' : 'Administra docentes, estudiantes y administradores.'}</p></div><button className="user-management__primary" type="button" onClick={openCreate}><Plus size={18} aria-hidden="true"/>{user?.rol === 'profesor' ? 'Crear estudiante' : 'Registrar usuario'}</button></header>
    {success && <p className="user-management__notice" role="status">{success}</p>}{error && !drawerOpen && <p className="user-management__error" role="alert">{error}</p>}
    <nav className="user-management__tabs" aria-label="Filtrar usuarios por rol">{tabs.map(([key, label]) => <button type="button" key={key} aria-pressed={roleFilter === key} onClick={() => setRoleFilter(key)}>{label}<span>{counts[key]}</span></button>)}</nav>
    <label className="user-management__search"><Search size={18} aria-hidden="true"/><span className="sr-only">Buscar usuarios por nombre o correo</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar por nombre, usuario o email…" /></label>
    {loading ? <p className="user-management__empty" role="status">Cargando usuarios…</p> : filtered.length ? <div className="user-management__table-wrap"><table className="user-management__table"><thead><tr><th>Usuario</th><th>Nombre completo</th><th>Email</th><th>Rol</th><th><span className="sr-only">Acciones</span></th></tr></thead><tbody>{filtered.map((item) => <tr key={item.id}><td data-label="Usuario">{item.username}</td><td data-label="Nombre completo">{item.nombre_completo || '—'}</td><td data-label="Email">{item.email}</td><td data-label="Rol"><span className={`user-management__role user-management__role--${item.rol}`}>{roleLabels[item.rol] || item.rol}</span></td><td data-label="Acciones"><div className="user-management__actions">{canManage(item) && <><button type="button" title="Editar usuario" aria-label={`Editar ${item.nombre_completo || item.username}`} onClick={() => openEdit(item)}><Pencil size={17}/></button><button type="button" title="Eliminar usuario" aria-label={`Eliminar ${item.nombre_completo || item.username}`} onClick={() => setUserToDelete(item)}><Trash2 size={17}/></button></>}</div></td></tr>)}</tbody></table></div> : <p className="user-management__empty">No hay usuarios que coincidan con este filtro.</p>}
    <ManagementDrawer open={drawerOpen} onOpenChange={closeDrawer} title={selected ? 'Editar usuario' : user?.rol === 'profesor' ? 'Crear estudiante' : 'Registrar usuario'} description="Completa los datos de la cuenta." footer={<div className="user-management__form-actions"><button type="button" onClick={() => setDrawerOpen(false)}>Cancelar</button><button type="submit" form="user-form" disabled={saving}>{saving ? 'Guardando…' : selected ? 'Guardar cambios' : 'Crear usuario'}</button></div>}>
      {error && <p className="user-management__error" role="alert">{error}</p>}<form id="user-form" className="user-management__form" onSubmit={save}><label>Nombre de usuario<input autoComplete="username" name="username" required value={form.username} onChange={change}/></label><label>Nombre completo<input name="nombre_completo" required value={form.nombre_completo} onChange={change}/></label><label>Correo electrónico<input autoComplete="email" type="email" name="email" required value={form.email} onChange={change}/></label><label>{selected ? 'Nueva contraseña (opcional)' : 'Contraseña'}<input autoComplete={selected ? 'new-password' : 'new-password'} type="password" name="password" required={!selected} value={form.password} onChange={change} placeholder={selected ? 'Dejar en blanco para conservarla' : ''}/></label>{user?.rol === 'administrador' && <label>Rol<select name="rol" value={form.rol} onChange={change}><option value="estudiante">Estudiante</option><option value="profesor">Docente</option><option value="administrador">Administrador</option></select></label>}</form>
    </ManagementDrawer>
    <ConfirmDialog open={Boolean(userToDelete)} title="Eliminar usuario" description={`¿Eliminar a ${userToDelete?.nombre_completo || userToDelete?.username || 'este usuario'}? Esta acción no se puede deshacer.`} onOpenChange={(open) => { if (!open) setUserToDelete(null); }} onConfirm={remove} />
  </section>;
}
