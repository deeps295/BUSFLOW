import { useState, useEffect } from 'react';
import api from '../services/api';

const useBackendStatus = (intervalMs = 10000) => {
  const [isConnected, setIsConnected] = useState(false);
  const [healthData, setHealthData] = useState(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await api.get('/health');
        setIsConnected(true);
        setHealthData(res.data);
      } catch {
        setIsConnected(false);
        setHealthData(null);
      }
    };
    check();
    const id = setInterval(check, intervalMs);
    return () => clearInterval(id);
  }, [intervalMs]);

  return { isConnected, healthData };
};

export default useBackendStatus;
