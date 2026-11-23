import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const useRoutes = () => {
  const [routes, setRoutes] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchRoutes = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get('/student/routes');
      setRoutes(res.data || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load routes');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRoutes();
  }, [fetchRoutes]);

  return { routes, isLoading, error, refetch: fetchRoutes };
};

export default useRoutes;
