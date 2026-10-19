import { useCallback, useEffect, useState } from 'react';
import { getDashboardStudent, getDashboardSummary } from '../services/dashboard.service';

export default function useDashboard() {
  const [data, setData] = useState(null);
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;
    getDashboardSummary()
      .then(({ data: summary }) => { if (active) setData(summary); })
      .catch((failure) => {
        const message = failure.response?.data?.mensaje || failure.response?.data?.detail;
        if (active) setError(message || 'No fue posible cargar los datos del dashboard.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);

  const selectStudent = useCallback(async (studentId) => {
    setDetailLoading(true);
    try {
      const { data: detail } = await getDashboardStudent(studentId);
      setStudent(detail);
    } catch (failure) {
      const message = failure.response?.data?.mensaje || failure.response?.data?.detail;
      setError(message || 'No fue posible cargar el perfil del estudiante.');
      setStudent(null);
    } finally {
      setDetailLoading(false);
    }
  }, []);

  return { data, student, loading, detailLoading, error, selectStudent };
}
