import React, { useState, useEffect } from 'react';
import axios from '../../utils/axiosConfig';
import './GameExplorer.css';

const GameExplorer = ({ onGameSelect, onClose }) => {
  const [categorias, setCategorias] = useState([]);
  const [juegos, setJuegos] = useState([]);
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState('');
  const [filtroEdad, setFiltroEdad] = useState('');
  const [filtroDificultad, setFiltroDificultad] = useState('');
  const [loading, setLoading] = useState(true);
  const [juegoSeleccionado, setJuegoSeleccionado] = useState(null);

  useEffect(() => {
    cargarCategorias();
    cargarJuegos();
  }, []);

  useEffect(() => {
    cargarJuegos();
  }, [categoriaSeleccionada, filtroEdad, filtroDificultad]);

  const cargarCategorias = async () => {
    try {
      const response = await axios.get('/api/juegos/categorias/');
      setCategorias(response.data.categorias);
    } catch (error) {
      console.error('Error al cargar categorías:', error);
    }
  };

  const cargarJuegos = async () => {
    try {
      setLoading(true);
      let url = '/api/juegos/listar/';
      const params = new URLSearchParams();
      
      if (categoriaSeleccionada) params.append('categoria_id', categoriaSeleccionada);
      if (filtroEdad) params.append('edad', filtroEdad);
      if (filtroDificultad) params.append('nivel_dificultad', filtroDificultad);
      
      if (params.toString()) {
        url += '?' + params.toString();
      }

      const response = await axios.get(url);
      setJuegos(response.data.juegos);
    } catch (error) {
      console.error('Error al cargar juegos:', error);
    } finally {
      setLoading(false);
    }
  };

  const seleccionarJuego = (juego) => {
    setJuegoSeleccionado(juego);
  };

  const confirmarSeleccion = () => {
    if (juegoSeleccionado && onGameSelect) {
      onGameSelect(juegoSeleccionado);
      onClose();
    }
  };

  const getDificultadColor = (nivel) => {
    switch (nivel) {
      case 'muy_facil': return '#4CAF50';
      case 'facil': return '#FFC107';
      case 'intermedio': return '#FF9800';
      default: return '#9E9E9E';
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-5"
      style={{ 
        zIndex: 9999, 
        display: 'flex',
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh'
      }}
    >
      <div className="bg-white rounded-3xl w-full max-w-7xl h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-8 py-6 flex justify-between items-center">
          <h2 className="text-3xl font-bold">🎮 Explorar Juegos Educativos</h2>
          <button 
            className="bg-white bg-opacity-20 hover:bg-opacity-30 rounded-full w-10 h-10 flex items-center justify-center text-xl transition-all duration-300 hover:scale-110" 
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <div className="flex-1 p-8 overflow-y-auto flex flex-col gap-6">
          {/* Filtros */}
          <div className="flex flex-wrap gap-5 p-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-100">
            <div className="flex flex-col gap-2 min-w-[200px]">
              <label className="font-semibold text-gray-700 text-sm">📂 Categoría:</label>
              <select 
                value={categoriaSeleccionada} 
                onChange={(e) => setCategoriaSeleccionada(e.target.value)}
                className="px-4 py-3 border-2 border-gray-200 rounded-xl text-sm bg-white cursor-pointer transition-all duration-300 focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100"
              >
                <option value="">Todas las categorías</option>
                {categorias.map(categoria => (
                  <option key={categoria.id} value={categoria.id}>
                    {categoria.icono} {categoria.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-2 min-w-[200px]">
              <label className="font-semibold text-gray-700 text-sm">👶 Edad:</label>
              <select 
                value={filtroEdad} 
                onChange={(e) => setFiltroEdad(e.target.value)}
                className="px-4 py-3 border-2 border-gray-200 rounded-xl text-sm bg-white cursor-pointer transition-all duration-300 focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100"
              >
                <option value="">Todas las edades</option>
                <option value="3">3 años</option>
                <option value="4">4 años</option>
                <option value="5">5 años</option>
                <option value="6">6 años</option>
                <option value="7">7 años</option>
                <option value="8">8 años</option>
                <option value="9">9 años</option>
                <option value="10">10 años</option>
              </select>
            </div>

            <div className="flex flex-col gap-2 min-w-[200px]">
              <label className="font-semibold text-gray-700 text-sm">⭐ Dificultad:</label>
              <select 
                value={filtroDificultad} 
                onChange={(e) => setFiltroDificultad(e.target.value)}
                className="px-4 py-3 border-2 border-gray-200 rounded-xl text-sm bg-white cursor-pointer transition-all duration-300 focus:outline-none focus:border-primary-500 focus:ring-4 focus:ring-primary-100"
              >
                <option value="">Todas</option>
                <option value="muy_facil">Muy Fácil (3-5 años)</option>
                <option value="facil">Fácil (6-8 años)</option>
                <option value="intermedio">Intermedio (9-12 años)</option>
              </select>
            </div>
          </div>

          {/* Lista de juegos */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 flex-1">
            {loading ? (
              <div className="col-span-full flex flex-col items-center justify-center py-16 text-gray-500">
                <div className="w-12 h-12 border-4 border-gray-300 border-t-primary-500 rounded-full animate-spin mb-4"></div>
                <p className="text-lg">Cargando juegos...</p>
              </div>
            ) : juegos.length === 0 ? (
              <div className="col-span-full text-center py-16 text-gray-500">
                <p className="text-xl">😔 No se encontraron juegos con estos filtros</p>
              </div>
            ) : (
              juegos.map(juego => (
                <div 
                  key={juego.id} 
                  className={`bg-white border-2 rounded-2xl p-6 cursor-pointer transition-all duration-300 hover:-translate-y-2 hover:shadow-xl relative overflow-hidden ${
                    juegoSeleccionado?.id === juego.id 
                      ? 'border-green-500 bg-gradient-to-br from-green-50 to-emerald-50 shadow-lg shadow-green-200' 
                      : 'border-gray-200 hover:border-primary-500'
                  }`}
                  onClick={() => seleccionarJuego(juego)}
                >
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-4xl">{juego.categoria.icono}</span>
                    <div 
                      className="text-white px-3 py-1 rounded-full text-xs font-semibold uppercase"
                      style={{ backgroundColor: getDificultadColor(juego.nivel_dificultad) }}
                    >
                      {juego.nivel_dificultad_display}
                    </div>
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-800 mb-3">{juego.titulo}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed mb-4">{juego.descripcion}</p>
                  
                  <div className="flex flex-wrap gap-4 mb-4">
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <span>👶</span>
                      <span>{juego.edad_minima}-{juego.edad_maxima} años</span>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <span>⏱️</span>
                      <span>{juego.tiempo_estimado} min</span>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-gray-600">
                      <span>🎯</span>
                      <span>{juego.veces_jugado} veces</span>
                    </div>
                  </div>

                  <div className="mb-4 p-3 bg-blue-50 rounded-lg border-l-4 border-primary-500">
                    <strong className="text-sm text-gray-700 block mb-1">🎯 Objetivos:</strong>
                    <p className="text-sm text-gray-600 leading-relaxed">{juego.objetivos_aprendizaje}</p>
                  </div>

                  <div>
                    <strong className="text-sm text-gray-700 block mb-2">🧠 Desarrolla:</strong>
                    <div className="flex flex-wrap gap-2">
                      {juego.habilidades_desarrolla.map((habilidad, index) => (
                        <span 
                          key={index} 
                          className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white px-3 py-1 rounded-full text-xs font-medium"
                        >
                          {habilidad}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Panel de selección */}
          {juegoSeleccionado && (
            <div className="sticky bottom-0 bg-gradient-to-r from-green-500 to-emerald-600 text-white p-6 rounded-2xl flex justify-between items-center mt-6 shadow-lg shadow-green-300">
              <div>
                <h3 className="text-xl font-bold mb-1">
                  {juegoSeleccionado.categoria.icono} {juegoSeleccionado.titulo}
                </h3>
                <p className="opacity-90 text-sm">¿Quieres agregar este juego como actividad?</p>
              </div>
              <div className="flex gap-4">
                <button 
                  className="bg-white bg-opacity-20 hover:bg-opacity-30 border-2 border-white border-opacity-30 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-300"
                  onClick={() => setJuegoSeleccionado(null)}
                >
                  Cancelar
                </button>
                <button 
                  className="bg-white text-green-600 px-8 py-3 rounded-xl font-bold transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
                  onClick={confirmarSeleccion}
                >
                  ✅ Seleccionar este Juego
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GameExplorer;
