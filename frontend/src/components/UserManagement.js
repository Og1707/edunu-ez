import React, { useState, useEffect } from 'react';
import axios from '../utils/axiosConfig';
import './UserManagement.css';

const UserManagement = ({ user }) => {
  const [usuarios, setUsuarios] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [successMessage, setSuccessMessage] = useState('');

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    nombre_completo: '',
    rol: 'estudiante'
  });

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const cargarUsuarios = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`/api/usuarios/listar/?user_id=${user.usuario_id}`);
      setUsuarios(response.data);
    } catch (error) {
      console.error('Error al cargar usuarios:', error);
      setErrors({ general: 'Error al cargar la lista de usuarios' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const dataToSend = {
        ...formData,
        user_id: user.usuario_id
      };

      const response = await axios.post('/api/usuarios/crear/', dataToSend);
      
      setSuccessMessage('Usuario creado exitosamente');
      setShowCreateModal(false);
      setFormData({
        username: '',
        email: '',
        password: '',
        nombre_completo: '',
        rol: 'estudiante'
      });
      cargarUsuarios();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al crear usuario:', error);
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Error al crear el usuario' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditUser = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const dataToSend = {
        ...formData,
        user_id: user.usuario_id
      };

      const response = await axios.put(`/api/usuarios/${selectedUser.id}/gestionar/`, dataToSend);
      
      setSuccessMessage('Usuario actualizado exitosamente');
      setShowEditModal(false);
      setSelectedUser(null);
      cargarUsuarios();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al actualizar usuario:', error);
      if (error.response && error.response.data) {
        setErrors(error.response.data);
      } else {
        setErrors({ general: 'Error al actualizar el usuario' });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('¿Estás seguro de que deseas eliminar este usuario?')) {
      return;
    }

    setIsLoading(true);
    try {
      await axios.delete(`/api/usuarios/${userId}/gestionar/?user_id=${user.usuario_id}`);
      
      setSuccessMessage('Usuario eliminado exitosamente');
      cargarUsuarios();

      setTimeout(() => setSuccessMessage(''), 3000);

    } catch (error) {
      console.error('Error al eliminar usuario:', error);
      setErrors({ general: 'Error al eliminar el usuario' });
    } finally {
      setIsLoading(false);
    }
  };

  const openCreateModal = () => {
    setFormData({
      username: '',
      email: '',
      password: '',
      nombre_completo: '',
      rol: user.rol === 'profesor' ? 'estudiante' : 'estudiante' // Profesor solo puede crear estudiantes
    });
    setErrors({});
    setShowCreateModal(true);
  };

  const openEditModal = (usuario) => {
    setSelectedUser(usuario);
    setFormData({
      username: usuario.username,
      email: usuario.email,
      password: '', // No mostrar contraseña actual
      nombre_completo: usuario.nombre_completo,
      rol: usuario.rol
    });
    setErrors({});
    setShowEditModal(true);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Determinar qué roles puede crear según el usuario actual
  const getRolesDisponibles = () => {
    if (user.rol === 'profesor') {
      return [{ value: 'estudiante', label: 'Estudiante' }];
    } else if (user.rol === 'administrador') {
      return [
        { value: 'estudiante', label: 'Estudiante' },
        { value: 'profesor', label: 'Profesor' },
        { value: 'administrador', label: 'Administrador' }
      ];
    }
    return [];
  };

  const canEditUser = (usuario) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor' && usuario.rol === 'estudiante') return true;
    return false;
  };

  const canDeleteUser = (usuario) => {
    if (user.rol === 'administrador') return true;
    if (user.rol === 'profesor' && usuario.rol === 'estudiante') return true;
    return false;
  };

  return (
    <div className="user-management">
      <div className="management-header">
        <h2>Gestión de Usuarios</h2>
        <p>
          {user.rol === 'profesor' 
            ? 'Como profesor, puedes gestionar estudiantes' 
            : 'Como administrador, puedes gestionar todos los usuarios'
          }
        </p>
        <button className="create-user-btn" onClick={openCreateModal}>
          <span className="btn-icon">👤➕</span>
          {user.rol === 'profesor' ? 'Crear Estudiante' : 'Crear Usuario'}
        </button>
      </div>

      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}

      {errors.general && (
        <div className="error-message">
          {errors.general}
        </div>
      )}

      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Cargando usuarios...</p>
        </div>
      ) : (
        <div className="users-table-container">
          <table className="users-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre Completo</th>
                <th>Email</th>
                <th>Rol</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map(usuario => (
                <tr key={usuario.id}>
                  <td>
                    <div className="user-info">
                      <span className="user-avatar">
                        {usuario.rol === 'administrador' ? '👨‍💼' : 
                         usuario.rol === 'profesor' ? '👨‍🏫' : '👨‍🎓'}
                      </span>
                      <span className="username">{usuario.username}</span>
                    </div>
                  </td>
                  <td>{usuario.nombre_completo}</td>
                  <td>{usuario.email}</td>
                  <td>
                    <span className={`role-badge ${usuario.rol}`}>
                      {usuario.rol === 'administrador' ? 'Administrador' :
                       usuario.rol === 'profesor' ? 'Profesor' : 'Estudiante'}
                    </span>
                  </td>
                  <td>
                    <div className="action-buttons">
                      {canEditUser(usuario) && (
                        <button 
                          className="edit-btn"
                          onClick={() => openEditModal(usuario)}
                          title="Editar usuario"
                        >
                          ✏️
                        </button>
                      )}
                      {canDeleteUser(usuario) && (
                        <button 
                          className="delete-btn"
                          onClick={() => handleDeleteUser(usuario.id)}
                          title="Eliminar usuario"
                        >
                          🗑️
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {usuarios.length === 0 && (
            <div className="empty-state">
              <p>No hay usuarios para mostrar</p>
            </div>
          )}
        </div>
      )}

      {/* Modal Crear Usuario */}
      {showCreateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{user.rol === 'profesor' ? 'Crear Estudiante' : 'Crear Usuario'}</h3>
              <button className="close-btn" onClick={() => setShowCreateModal(false)}>✕</button>
            </div>

            <form onSubmit={handleCreateUser} className="user-form">
              <div className="form-group">
                <label>Nombre de Usuario *</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className={errors.username ? 'error' : ''}
                />
                {errors.username && <span className="error-text">{errors.username}</span>}
              </div>

              <div className="form-group">
                <label>Nombre Completo *</label>
                <input
                  type="text"
                  name="nombre_completo"
                  value={formData.nombre_completo}
                  onChange={handleChange}
                  required
                  className={errors.nombre_completo ? 'error' : ''}
                />
                {errors.nombre_completo && <span className="error-text">{errors.nombre_completo}</span>}
              </div>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>

              <div className="form-group">
                <label>Contraseña *</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className={errors.password ? 'error' : ''}
                />
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>

              {user.rol === 'administrador' && (
                <div className="form-group">
                  <label>Rol *</label>
                  <select
                    name="rol"
                    value={formData.rol}
                    onChange={handleChange}
                    required
                    className={errors.rol ? 'error' : ''}
                  >
                    {getRolesDisponibles().map(rol => (
                      <option key={rol.value} value={rol.value}>
                        {rol.label}
                      </option>
                    ))}
                  </select>
                  {errors.rol && <span className="error-text">{errors.rol}</span>}
                </div>
              )}

              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowCreateModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="submit-btn" disabled={isLoading}>
                  {isLoading ? 'Creando...' : 'Crear Usuario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Editar Usuario */}
      {showEditModal && selectedUser && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Editar Usuario: {selectedUser.username}</h3>
              <button className="close-btn" onClick={() => setShowEditModal(false)}>✕</button>
            </div>

            <form onSubmit={handleEditUser} className="user-form">
              <div className="form-group">
                <label>Nombre de Usuario *</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  required
                  className={errors.username ? 'error' : ''}
                />
                {errors.username && <span className="error-text">{errors.username}</span>}
              </div>

              <div className="form-group">
                <label>Nombre Completo *</label>
                <input
                  type="text"
                  name="nombre_completo"
                  value={formData.nombre_completo}
                  onChange={handleChange}
                  required
                  className={errors.nombre_completo ? 'error' : ''}
                />
                {errors.nombre_completo && <span className="error-text">{errors.nombre_completo}</span>}
              </div>

              <div className="form-group">
                <label>Email *</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="error-text">{errors.email}</span>}
              </div>

              <div className="form-group">
                <label>Nueva Contraseña (opcional)</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={errors.password ? 'error' : ''}
                  placeholder="Dejar vacío para mantener actual"
                />
                {errors.password && <span className="error-text">{errors.password}</span>}
              </div>

              {user.rol === 'administrador' && (
                <div className="form-group">
                  <label>Rol *</label>
                  <select
                    name="rol"
                    value={formData.rol}
                    onChange={handleChange}
                    required
                    className={errors.rol ? 'error' : ''}
                  >
                    {getRolesDisponibles().map(rol => (
                      <option key={rol.value} value={rol.value}>
                        {rol.label}
                      </option>
                    ))}
                  </select>
                  {errors.rol && <span className="error-text">{errors.rol}</span>}
                </div>
              )}

              <div className="form-actions">
                <button type="button" className="cancel-btn" onClick={() => setShowEditModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="submit-btn" disabled={isLoading}>
                  {isLoading ? 'Actualizando...' : 'Actualizar Usuario'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagement;
