import { useEffect, useState } from 'react';
import { getStudentStats } from '../../services/games.service';

export default function useStudentDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    getStudentStats()
      .then(({ data }) => {
        if (active) setStats(data);
      })
      .catch(() => {
        if (active) setError('No fue posible cargar tus estadísticas.');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, []);

  return { stats, loading, error };
}
