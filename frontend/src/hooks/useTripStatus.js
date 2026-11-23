import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';

const useTripStatus = (routeId) => {
  const [tripStatus, setTripStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const fetchStatus = useCallback(async () => {
    if (!routeId) return;
    setIsLoading(true);
    try {
      const res = await api.get(`/student/trip-status?route_id=${routeId}`);
      setTripStatus(res.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Trip status unavailable');
    } finally {
      setIsLoading(false);
    }
  }, [routeId]);

  useEffect(() => {
    if (!routeId) {
      setTripStatus(null);
      return;
    }
    fetchStatus();
    intervalRef.current = setInterval(fetchStatus, 20000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [routeId, fetchStatus]);

  return { tripStatus, isLoading, error };
};

export default useTripStatus;
