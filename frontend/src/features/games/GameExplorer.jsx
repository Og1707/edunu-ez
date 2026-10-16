import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock3, Gamepad2, Play, Users } from 'lucide-react';
import { getGameCategories, getGames } from '../../services/games.service';
import EmptyState from '../../components/ui/EmptyState';
import './GameExplorer.css';

const playableTypes = new Set(['colores_primarios', 'memoria_colores']);

export default function GameExplorer() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [games, setGames] = useState([]);
  const [category, setCategory] = useState('');
  const [age, setAge] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getGameCategories().then(({ data }) => setCategories(data.categorias || [])).catch(() => setError('No se pudieron cargar las categorías.'));
  }, []);

  const loadGames = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await getGames({ ...(category && { categoria_id: category }), ...(age && { edad: age }), ...(difficulty && { nivel_dificultad: difficulty }) });
      setGames(data.juegos || []);
      setError('');
    } catch (_) { setError('No se pudieron cargar los juegos. Inténtalo de nuevo.'); }
    finally { setLoading(false); }
  }, [category, age, difficulty]);
  useEffect(() => { loadGames(); }, [loadGames]);

  return <main className="game-explorer-page">
    <header className="game-explorer-page__header"><div><span>Aprendizaje interactivo</span><h1>Explorar juegos</h1><p>Elige un juego disponible para practicar y aprender.</p></div><Gamepad2 size={32} aria-hidden="true"/></header>
    <section className="game-explorer-page__filters" aria-label="Filtros de juegos">
      <label>Categoría<select value={category} onChange={(event) => setCategory(event.target.value)}><option value="">Todas las categorías</option>{categories.map((item) => <option key={item.id} value={item.id}>{item.nombre}</option>)}</select></label>
      <label>Edad<select value={age} onChange={(event) => setAge(event.target.value)}><option value="">Todas las edades</option>{Array.from({ length: 10 }, (_, index) => index + 3).map((value) => <option key={value} value={value}>{value} años</option>)}</select></label>
      <label>Dificultad<select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}><option value="">Todas</option><option value="muy_facil">Muy fácil</option><option value="facil">Fácil</option><option value="intermedio">Intermedio</option></select></label>
    </section>
    {error && <p className="game-explorer-page__error" role="alert">{error}</p>}
    {loading ? <p className="game-explorer-page__loading" role="status">Cargando juegos…</p> : games.length ? <section className="game-explorer-page__grid" aria-label="Juegos disponibles">{games.map((game) => {
      const playable = playableTypes.has(game.tipo_juego);
      return <article className="game-explorer-page__card" key={game.id}><div className="game-explorer-page__card-heading"><span aria-hidden="true">{game.categoria?.icono || '🎮'}</span><span className="game-explorer-page__difficulty">{game.nivel_dificultad_display || game.nivel_dificultad}</span></div><h2>{game.titulo}</h2><p>{game.descripcion}</p><div className="game-explorer-page__details"><span><Users size={16} aria-hidden="true"/>{game.edad_minima}–{game.edad_maxima} años</span><span><Clock3 size={16} aria-hidden="true"/>{game.tiempo_estimado} min</span></div>{playable ? <button type="button" onClick={() => navigate(`/games/${game.id}/play`)}><Play size={16} aria-hidden="true"/> Jugar</button> : <p className="game-explorer-page__unavailable">Este tipo de juego aún no tiene reproductor disponible.</p>}</article>;
    })}</section> : <EmptyState icon={<Gamepad2/>} title="No hay juegos para estos filtros" description="Prueba con otra categoría, edad o dificultad."/>}
  </main>;
}
