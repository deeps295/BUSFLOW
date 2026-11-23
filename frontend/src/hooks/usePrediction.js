import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../services/api';

const usePrediction = (routeId, stopId) => {
  const [prediction, setPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const intervalRef = useRef(null);

  const fetchPrediction = useCallback(async () => {
    if (!routeId || !stopId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.get(`/student/prediction?route_id=${routeId}&stop_id=${stopId}`);
      setPrediction(res.data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction unavailable');
    } finally {
      setIsLoading(false);
    }
  }, [routeId, stopId]);

  useEffect(() => {
    if (!routeId || !stopId) {
      setPrediction(null);
      setError(null);
      return;
    }
    fetchPrediction();
    intervalRef.current = setInterval(fetchPrediction, 15000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [routeId, stopId, fetchPrediction]);

  return { prediction, isLoading, error, lastUpdated, refresh: fetchPrediction };
};

export default usePrediction;
