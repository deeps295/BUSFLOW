import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Bus, 
  MapPin, 
  Clock, 
  AlertTriangle, 
  RefreshCw, 
  ChevronDown, 
  Thermometer, 
  Droplets, 
  Wind, 
  Navigation, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  Bell, 
  Route as RouteIcon,
  Sparkles,
  ArrowRight,
  Info,
  Sliders,
  History,
  TrendingUp,
  Zap
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { studentService } from '../services/studentService';

import BubbleBackground from '../components/layout/BubbleBackground';
import Navbar from '../components/layout/Navbar';
import LoadingSkeleton from '../components/common/LoadingSkeleton';
import ErrorState from '../components/common/ErrorState';
import EmptyState from '../components/common/EmptyState';

const formatTime = (timeStr) => {
  if (!timeStr) return '--:--';
  if (timeStr === 'Trip Completed') return 'Trip Completed';
  try {
    const parts = timeStr.split(':');
    if (parts.length < 2) return timeStr;
    const hour = parseInt(parts[0], 10);
    const minute = parts[1];
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const h12 = hour % 12 || 12;
    return `${h12}:${minute} ${ampm}`;
  } catch {
    return timeStr;
  }
};

const SEVERITY_CONFIG = {
  ON_TIME: {
    label: '🟢 On Time / Nominal',
    style: 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30',
    description: 'Operating on schedule. Arriving within 2 minutes of timetable.'
  },
  MINOR_DELAY: {
    label: '🟡 Minor Delay (3–7 mins)',
    style: 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30',
    description: 'Slight delay due to intermediate boarding delays or local traffic.'
  },
  MODERATE_DELAY: {
    label: '🟠 Moderate Delay (8–15 mins)',
    style: 'text-orange-400 bg-orange-500/20 border-orange-500/30',
    description: 'Noticeable congestion along the corridor. Plan boarding accordingly.'
  },
  SEVERE_DELAY: {
    label: '🔴 Severe Delay (>15 mins)',
    style: 'text-red-400 bg-red-500/20 border-red-500/30',
    description: 'Heavy bottle-neck or severe weather. Significant delay expected.'
  }
};

const StudentDashboard = () => {
  const { currentUser } = useAuth();
  const { showToast } = useToast();

  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [selectedStop, setSelectedStop] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [tripStatus, setTripStatus] = useState(null);
  const [routeStats, setRouteStats] = useState(null);

  const [isLoadingRoutes, setIsLoadingRoutes] = useState(true);
  const [isLoadingPrediction, setIsLoadingPrediction] = useState(false);
  const [isLoadingStats, setIsLoadingStats] = useState(false);
  const [predictionError, setPredictionError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Helper getters for robust ID resolution
  const getRouteId = (r) => (r ? (r.id != null ? r.id : r.route_id) : null);
  const getStopId = (s) => (s ? (s.id != null ? s.id : s.stop_id) : null);

  // Fetch routes on mount
  useEffect(() => {
    let isMounted = true;
    const fetchRoutes = async () => {
      try {
        setIsLoadingRoutes(true);
        const data = await studentService.getRoutes();
        if (isMounted) {
          const routesList = Array.isArray(data) ? data : (data?.routes || []);
          setRoutes(routesList);
        }
      } catch (err) {
        if (isMounted) {
          showToast(err.response?.data?.detail || 'Failed to load SECE routes', 'error');
        }
      } finally {
        if (isMounted) {
          setIsLoadingRoutes(false);
        }
      }
    };

    fetchRoutes();
    return () => {
      isMounted = false;
    };
  }, [showToast]);

  // Fetch Prediction
  const fetchPrediction = useCallback(async (isSilent = false) => {
    const routeId = getRouteId(selectedRoute);
    const stopId = getStopId(selectedStop);
    if (!routeId || !stopId) return;

    if (!isSilent) setIsLoadingPrediction(true);
    else setIsRefreshing(true);
    setPredictionError(null);

    try {
      // Driver controls real-time traffic updates in BusFlow
      const data = await studentService.getPrediction(routeId, stopId);
      setPrediction(data);
      setLastUpdated(new Date());
    } catch (err) {
      setPredictionError(err.response?.data?.detail || 'Unable to fetch prediction');
      if (!isSilent) {
        showToast('Failed to load arrival prediction', 'error');
      }
    } finally {
      if (!isSilent) setIsLoadingPrediction(false);
      setIsRefreshing(false);
    }
  }, [selectedRoute, selectedStop, showToast]);

  // Fetch Trip Status & Route Stats
  const fetchRouteDetails = useCallback(async () => {
    const routeId = getRouteId(selectedRoute);
    if (!routeId) return;

    try {
      const statusData = await studentService.getTripStatus(routeId);
      setTripStatus(statusData);
    } catch (err) {
      console.error('Error fetching trip status:', err);
    }

    try {
      setIsLoadingStats(true);
      const statsData = await studentService.getRouteStats(routeId);
      setRouteStats(statsData);
    } catch (err) {
      console.error('Error fetching route stats:', err);
    } finally {
      setIsLoadingStats(false);
    }
  }, [selectedRoute]);

  // Handle route change
  const handleRouteChange = (e) => {
    const routeIdStr = e.target.value;
    if (!routeIdStr) {
      setSelectedRoute(null);
      setSelectedStop(null);
      setPrediction(null);
      setTripStatus(null);
      setRouteStats(null);
      setTrafficSimulation(null);
      return;
    }

    const route = routes.find((r) => String(getRouteId(r)) === String(routeIdStr));
    setSelectedRoute(route || null);
    setSelectedStop(null);
    setPrediction(null);
    setTripStatus(null);
    setRouteStats(null);
    setTrafficSimulation(null);
  };

  // Handle stop change
  const handleStopChange = (e) => {
    const stopIdStr = e.target.value;
    if (!stopIdStr || !selectedRoute) {
      setSelectedStop(null);
      setPrediction(null);
      return;
    }

    const stop = selectedRoute.stops?.find((s) => String(getStopId(s)) === String(stopIdStr));
    setSelectedStop(stop || null);
  };

  // Trigger prediction and trip status fetch on route/stop selection
  useEffect(() => {
    if (selectedRoute && selectedStop) {
      fetchPrediction();
      fetchRouteDetails();
    }
  }, [selectedRoute, selectedStop, fetchPrediction, fetchRouteDetails]);

  // Auto-refresh interval (15s)
  useEffect(() => {
    if (!autoRefreshEnabled || !selectedRoute || !selectedStop) return;

    const interval = setInterval(() => {
      fetchPrediction(true);
      fetchRouteDetails();
    }, 15000);

    return () => clearInterval(interval);
  }, [autoRefreshEnabled, selectedRoute, selectedStop, fetchPrediction, fetchRouteDetails]);

  // Compute severity classification
  const severityKey = prediction?.severity_status || 'ON_TIME';
  const severity = SEVERITY_CONFIG[severityKey] || SEVERITY_CONFIG.ON_TIME;
  const isSignificantDelay = (prediction?.expected_delay_minutes != null && prediction.expected_delay_minutes >= 7.0) ||
    ['MODERATE_DELAY', 'SEVERE_DELAY'].includes(prediction?.severity_status);

  return (
    <div 
      className="min-h-screen text-white relative overflow-hidden" 
      style={{ background: 'linear-gradient(135deg, #071B3A 0%, #0F2D5E 50%, #071B3A 100%)' }}
    >
      <BubbleBackground />
      <Navbar />

      <main className="relative z-10 max-w-6xl mx-auto px-4 py-8">
        {/* Welcome Card */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-8 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute -right-8 -top-8 w-44 h-44 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/15 text-sky-300 border border-sky-400/20 mb-2">
                <Sparkles className="w-3.5 h-3.5" /> Sri Eshwar College of Engineering Transit
              </span>
              <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                🎓 Welcome, {currentUser?.full_name || 'Student'}
              </h1>
              <p className="text-white/70 text-sm md:text-base mt-1">
                Real-time college bus arrival and delay predictions powered by Machine Learning.
              </p>
            </div>

            <div className="flex items-center gap-3 self-start md:self-auto">
              <span className="text-xs text-sky-200/90 bg-white/5 px-3 py-1.5 rounded-lg border border-white/10 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Live Dispatch Ready
              </span>
            </div>
          </div>
        </motion.div>

        {/* 1. Route & Stop Selector Row */}
        <motion.div 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
        >
          {/* 1. Bus Route Selection */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 shadow-lg hover:border-sky-500/30 transition-all">
            <label className="block text-sky-300 text-sm font-semibold mb-2 flex items-center gap-2">
              <Bus className="w-4 h-4 text-sky-400" />
              1. Select College Bus Route
            </label>
            <div className="relative">
              <select
                disabled={isLoadingRoutes}
                value={selectedRoute ? String(getRouteId(selectedRoute)) : ''}
                onChange={handleRouteChange}
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white appearance-none focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent transition-all disabled:opacity-50 cursor-pointer"
              >
                <option value="" className="bg-[#071B3A] text-white/70">— Select a route ({routes.length} available) —</option>
                {routes.map((route) => {
                  const rId = getRouteId(route);
                  return (
                    <option key={rId} value={String(rId)} className="bg-[#071B3A] text-white">
                      {route.route_number}: {route.route_name}
                    </option>
                  );
                })}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-white/50">
                {isLoadingRoutes ? <Loader2 className="w-4 h-4 animate-spin text-sky-400" /> : <ChevronDown className="w-4 h-4" />}
              </div>
            </div>
            {selectedRoute && (
              <p className="text-xs text-sky-300/80 mt-2">
                Origin: <span className="text-white font-medium">{selectedRoute.origin_name}</span> · {selectedRoute.stops?.length || 0} stops · {selectedRoute.total_distance_km} km
              </p>
            )}
          </div>

          {/* Boarding Stop Selection */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-5 shadow-lg hover:border-sky-500/30 transition-all">
            <label className="block text-sky-300 text-sm font-semibold mb-2 flex items-center gap-2">
              <MapPin className="w-4 h-4 text-sky-400" />
              2. Select Your Boarding Stop
            </label>
            <div className="relative">
              <select
                disabled={!selectedRoute || (selectedRoute?.stops?.length === 0)}
                value={selectedStop ? String(getStopId(selectedStop)) : ''}
                onChange={handleStopChange}
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white appearance-none focus:outline-none focus:ring-2 focus:ring-sky-400 focus:border-transparent transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
              >
                <option value="" className="bg-[#071B3A] text-white/70">
                  {!selectedRoute ? '— Select a route first —' : `— Select your stop (${selectedRoute.stops?.length || 0} stops) —`}
                </option>
                {selectedRoute?.stops?.map((stop) => {
                  const sId = getStopId(stop);
                  return (
                    <option key={sId} value={String(sId)} className="bg-[#071B3A] text-white">
                      {stop.stop_name} (Stop #{stop.stop_sequence})
                    </option>
                  );
                })}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-white/50">
                <ChevronDown className="w-4 h-4" />
              </div>
            </div>
            {selectedStop && (
              <p className="text-xs text-sky-300/80 mt-2">
                Sequence: <span className="text-white font-medium">#{selectedStop.stop_sequence}</span> · Distance from origin: <span className="text-white font-medium">{selectedStop.distance_from_origin_km} km</span>
              </p>
            )}
          </div>
        </motion.div>

        {/* 11. Delay Alerts Banner (When significant delay is predicted) */}
        <AnimatePresence>
          {isSignificantDelay && (
            <motion.div
              initial={{ opacity: 0, height: 0, y: -10 }}
              animate={{ opacity: 1, height: 'auto', y: 0 }}
              exit={{ opacity: 0, height: 0, y: -10 }}
              className="bg-red-500/20 border-2 border-red-500/50 rounded-2xl p-4 mb-8 shadow-xl flex items-start gap-3 backdrop-blur-md"
            >
              <div className="p-2 rounded-xl bg-red-500/30 text-red-300 shrink-0 mt-0.5">
                <Bell className="w-5 h-5 animate-bounce" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h4 className="text-sm font-bold text-red-200 uppercase tracking-wider">
                    ⚠️ Significant Delay Alert Notification
                  </h4>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-red-500/40 text-red-100 font-semibold">
                    +{prediction.expected_delay_minutes.toFixed(1)} mins
                  </span>
                </div>
                <p className="text-sm text-red-100/90 mt-1">
                  Bus <strong>{selectedRoute?.route_number}</strong> is experiencing heavy delays along the corridor. 
                  Predicted arrival at <strong>{selectedStop?.stop_name}</strong> has shifted to approximately <strong>{formatTime(prediction.predicted_arrival_time)}</strong>. Please adjust your boarding schedule accordingly.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 8. Peak-Hour Detection Advisory Banner */}
        {routeStats?.peak_hour_analysis && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`rounded-2xl p-4 mb-8 border backdrop-blur-md flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg ${
              routeStats.peak_hour_analysis.is_currently_peak_hour
                ? 'bg-amber-500/15 border-amber-500/30 text-amber-200'
                : 'bg-white/5 border-white/10 text-white/80'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-xl ${routeStats.peak_hour_analysis.is_currently_peak_hour ? 'bg-amber-500/30 text-amber-300' : 'bg-sky-500/20 text-sky-400'}`}>
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <span className="text-xs uppercase font-bold tracking-wider block opacity-75">
                  Peak-Hour Congestion Status
                </span>
                <span className="text-sm font-semibold">
                  {routeStats.peak_hour_analysis.current_peak_status}
                </span>
              </div>
            </div>
            <div className="text-xs flex items-center gap-4 flex-wrap">
              <span>Morning Peak: <strong className="text-sky-300">{routeStats.peak_hour_analysis.morning_peak_window}</strong></span>
              <span>Evening Peak: <strong className="text-sky-300">{routeStats.peak_hour_analysis.evening_peak_window}</strong></span>
            </div>
          </motion.div>
        )}

        {/* Prediction Card Section */}
        {selectedRoute && selectedStop ? (
          isLoadingPrediction ? (
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-8">
              <div className="flex items-center gap-3 mb-6">
                <Loader2 className="w-6 h-6 text-sky-400 animate-spin" />
                <h3 className="text-lg font-bold text-white">Running Machine Learning Regression Engine...</h3>
              </div>
              <LoadingSkeleton lines={4} />
            </div>
          ) : prediction ? (
            <motion.div 
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-8 mb-8 shadow-2xl relative overflow-hidden"
            >
              <div className="absolute top-0 right-0 w-96 h-96 bg-royal/10 rounded-full blur-3xl pointer-events-none" />

              {/* Header row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl md:text-2xl font-bold text-white flex items-center gap-2">
                      <Sparkles className="w-5 h-5 text-sky-400" />
                      Arrival & Delay Prediction
                    </h2>
                  </div>
                  <p className="text-white/60 text-xs mt-1">
                    Route: <span className="text-sky-300 font-semibold">{selectedRoute.route_number}</span> · Stop: <span className="text-sky-300 font-semibold">{selectedStop.stop_name}</span>
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  {lastUpdated && (
                    <span className="text-xs text-white/60 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-sky-400" />
                      Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </span>
                  )}
                  <button
                    onClick={() => fetchPrediction(false)}
                    disabled={isRefreshing || isLoadingPrediction}
                    className="p-2 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 text-white transition-all disabled:opacity-50"
                    title="Refresh prediction"
                  >
                    <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-sky-400' : ''}`} />
                  </button>
                </div>
              </div>

              {/* 2. Delay Prediction Severity & 4. Delay Duration */}
              <div className="text-center py-6 my-2">
                <div className="inline-block mb-3">
                  <span className={`inline-flex items-center px-4 py-1.5 rounded-full text-sm font-semibold border ${severity.style} shadow-sm`}>
                    {severity.label}
                  </span>
                </div>
                <div className="text-4xl md:text-6xl font-black text-white tracking-tight flex items-center justify-center gap-2">
                  <span>
                    {prediction.expected_delay_minutes > 0 ? `+${prediction.expected_delay_minutes.toFixed(1)}` : prediction.expected_delay_minutes.toFixed(1)}
                  </span>
                  <span className="text-xl md:text-2xl font-normal text-sky-300/90">min delay</span>
                </div>
                <p className="text-white/70 text-xs mt-2 max-w-md mx-auto">
                  {severity.description}
                </p>
              </div>

              {/* 3. Estimated Arrival Time & Primary Metric Boxes */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center gap-4 hover:border-sky-500/30 transition-all">
                  <div className="p-3 rounded-lg bg-sky-500/20 text-sky-400">
                    <Clock className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-sky-300 uppercase tracking-wider block">Predicted Arrival Time</span>
                    <span className="text-2xl font-extrabold text-white">
                      {formatTime(prediction.predicted_arrival_time)}
                    </span>
                  </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center gap-4 hover:border-sky-500/30 transition-all">
                  <div className="p-3 rounded-lg bg-royal/20 text-blue-400">
                    <Bus className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-sky-300 uppercase tracking-wider block">Remaining Travel to SECE</span>
                    <span className="text-2xl font-extrabold text-white">
                      {prediction.predicted_remaining_travel_minutes != null 
                        ? `${prediction.predicted_remaining_travel_minutes.toFixed(0)} min`
                        : '--'}
                    </span>
                  </div>
                </div>

                <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center gap-4 hover:border-sky-500/30 transition-all">
                  <div className="p-3 rounded-lg bg-emerald-500/20 text-emerald-400">
                    <MapPin className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="text-xs font-medium text-sky-300 uppercase tracking-wider block">Remaining Stops</span>
                    <span className="text-2xl font-extrabold text-white">
                      {prediction.remaining_stops != null ? `${prediction.remaining_stops} stops away` : '--'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Scheduled vs Predicted Comparison */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 divide-y sm:divide-y-0 sm:divide-x divide-white/10">
                  <div className="flex flex-col items-center sm:items-start p-2">
                    <span className="text-xs text-white/60 mb-1">Official Timetable Scheduled Arrival</span>
                    <span className="text-lg font-semibold text-white/90">
                      {formatTime(prediction.scheduled_arrival)}
                    </span>
                  </div>
                  <div className="flex flex-col items-center sm:items-start p-2 sm:pl-6">
                    <span className="text-xs text-white/60 mb-1">Actual Arrival Time</span>
                    <div className="flex items-center gap-2">
                      <span className="text-lg font-bold text-sky-300">
                        {formatTime(prediction.predicted_arrival_time)}
                      </span>
                      {prediction.expected_delay_minutes > 0 && (
                        <span className="text-xs text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                          +{prediction.expected_delay_minutes.toFixed(1)}m delay
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Live Driver-Reported Road Traffic (Read-Only for Students) */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-sky-400" />
                    <span className="text-sm font-semibold text-sky-300">Live Road Traffic (Driver Reported)</span>
                  </div>
                  <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-300 border border-sky-400/20 font-medium">
                    Updated by Driver
                  </span>
                </div>
                
                <div className="p-3.5 rounded-xl bg-white/5 border border-white/10 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">
                      {prediction.traffic_level === 'SEVERE' ? '🔴' :
                       prediction.traffic_level === 'HIGH' ? '🟠' :
                       prediction.traffic_level === 'MEDIUM' ? '🟡' : '🟢'}
                    </span>
                    <div>
                      <span className="text-sm font-bold text-white block">
                        {prediction.traffic_level === 'SEVERE' ? 'Severe Traffic Congestion' :
                         prediction.traffic_level === 'HIGH' ? 'High Traffic Congestion' :
                         prediction.traffic_level === 'MEDIUM' ? 'Medium Traffic / Rush' : 'Normal / Low Traffic Flow'}
                      </span>
                      <p className="text-xs text-white/50 mt-0.5">
                        Live corridor congestion updated directly by the bus driver in real time. (Driver Controlled)
                      </p>
                    </div>
                  </div>
                  <span className="text-xs font-bold px-3 py-1 rounded-lg bg-white/10 text-sky-300 border border-white/10 shrink-0">
                    {prediction.traffic_level || 'LOW'}
                  </span>
                </div>
              </div>

              {/* Estimated Prediction Interval */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-4 mb-6">
                <div className="flex items-center gap-2 mb-2">
                  <Info className="w-4 h-4 text-sky-400" />
                  <span className="text-sm font-semibold text-sky-300">Statistical Estimated Prediction Interval</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                    <span className="text-white/60 text-xs block mb-1">Delay Range</span>
                    <span className="font-medium text-white">
                      {prediction.estimated_prediction_interval?.delay?.lower_bound_mins != null && prediction.estimated_prediction_interval?.delay?.upper_bound_mins != null
                        ? `${prediction.estimated_prediction_interval.delay.lower_bound_mins.toFixed(1)} to ${prediction.estimated_prediction_interval.delay.upper_bound_mins.toFixed(1)} min`
                        : `${(prediction.expected_delay_minutes - 2.3).toFixed(1)} to ${(prediction.expected_delay_minutes + 2.3).toFixed(1)} min`}
                    </span>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                    <span className="text-white/60 text-xs block mb-1">Travel Time Range</span>
                    <span className="font-medium text-white">
                      {prediction.estimated_prediction_interval?.remaining_travel?.lower_bound_mins != null && prediction.estimated_prediction_interval?.remaining_travel?.upper_bound_mins != null
                        ? `${prediction.estimated_prediction_interval.remaining_travel.lower_bound_mins.toFixed(0)} to ${prediction.estimated_prediction_interval.remaining_travel.upper_bound_mins.toFixed(0)} min`
                        : `${Math.max(0, prediction.predicted_remaining_travel_minutes - 4).toFixed(0)} to ${(prediction.predicted_remaining_travel_minutes + 4).toFixed(0)} min`}
                    </span>
                  </div>
                </div>
                <p className="text-[11px] text-white/50 mt-2 italic">
                  80% estimated prediction interval based on validation residuals. Road and climate conditions may vary.
                </p>
              </div>

              {/* Auto Refresh Toggle */}
              <div className="pt-4 border-t border-white/10 flex items-center justify-end text-xs text-white/60">
                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer select-none">
                    <input 
                      type="checkbox"
                      checked={autoRefreshEnabled}
                      onChange={(e) => setAutoRefreshEnabled(e.target.checked)}
                      className="rounded bg-white/10 border-white/20 text-sky-500 focus:ring-0 focus:outline-none w-4 h-4 cursor-pointer"
                    />
                    <span className={autoRefreshEnabled ? 'text-sky-300 font-medium' : 'text-white/40'}>
                      Auto-refresh every 15s
                    </span>
                  </label>
                </div>
              </div>
            </motion.div>
          ) : (
            <ErrorState 
              message={predictionError || "Prediction unavailable for the chosen stop"} 
              onRetry={() => fetchPrediction(false)} 
            />
          )
        ) : (
          <EmptyState 
            icon={Bus} 
            title="10. Student Transit Dashboard" 
            description="Select your SECE college bus route and boarding stop above to inspect live arrival predictions, delays, traffic, and weather" 
          />
        )}

        {/* 6. Weather-Based Prediction Snapshot */}
        {prediction?.weather && (
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-8 shadow-xl"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Thermometer className="w-5 h-5 text-sky-400" />
                  6. Weather-Based Prediction Factors
                </h3>
                <span className="text-xs text-white/60">Live Local Meteorological Grid: Kinathukadavu / Coimbatore Area (10.85° N, 76.98° E)</span>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-sky-500/20 text-sky-300 border border-sky-500/30">
                {prediction.weather.condition || 'CLEAR'}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              <div className="flex items-center gap-3 bg-white/5 p-3.5 rounded-xl border border-white/5">
                <Thermometer className="w-5 h-5 text-orange-400" />
                <div>
                  <span className="text-xs text-white/60 block">Temperature</span>
                  <span className="text-base font-bold text-white">
                    {prediction.weather.temperature_c != null ? `${prediction.weather.temperature_c}°C` : '--'}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-white/5 p-3.5 rounded-xl border border-white/5">
                <Droplets className="w-5 h-5 text-sky-400" />
                <div>
                  <span className="text-xs text-white/60 block">Precipitation / Rainfall</span>
                  <span className="text-base font-bold text-white">
                    {prediction.weather.precipitation_mm != null ? `${prediction.weather.precipitation_mm} mm` : '0.0 mm'}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 bg-white/5 p-3.5 rounded-xl border border-white/5">
                <Wind className="w-5 h-5 text-teal-400" />
                <div>
                  <span className="text-xs text-white/60 block">Relative Humidity</span>
                  <span className="text-base font-bold text-white">
                    {prediction.weather.humidity_percent != null ? `${prediction.weather.humidity_percent}%` : '--'}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* 7. Historical Delay Analysis & 9. Route-Wise Statistics */}
        {selectedRoute && routeStats && (
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-8 shadow-xl"
          >
            <div className="flex items-center gap-2 mb-4">
              <History className="w-5 h-5 text-sky-400" />
              <h3 className="text-lg font-bold text-white">
                7 & 9. Historical Delay Analysis & Route Statistics
              </h3>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
              <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Corridor Avg Delay</span>
                <span className="text-xl font-bold text-sky-300">
                  {routeStats.average_delay_minutes != null ? `${routeStats.average_delay_minutes.toFixed(1)} min` : '--'}
                </span>
                <span className="text-[10px] text-white/40 block mt-1">Historical benchmark</span>
              </div>

              <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Punctuality Rate</span>
                <span className="text-xl font-bold text-emerald-400">
                  {routeStats.punctuality_rate_percentage != null ? `${routeStats.punctuality_rate_percentage.toFixed(1)}%` : '--'}
                </span>
                <span className="text-[10px] text-white/40 block mt-1">Arrivals within 5 mins</span>
              </div>

              <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Corridor Length</span>
                <span className="text-xl font-bold text-white">
                  {routeStats.total_distance_km} km
                </span>
                <span className="text-[10px] text-white/40 block mt-1">Total route distance</span>
              </div>

              <div className="bg-white/5 p-4 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Congestion Risk</span>
                <span className={`text-xl font-bold ${
                  routeStats.risk_level === 'HIGH' || routeStats.risk_level === 'SEVERE' ? 'text-red-400' : 'text-yellow-400'
                }`}>
                  {routeStats.risk_level}
                </span>
                <span className="text-[10px] text-white/40 block mt-1">Peak sensitivity</span>
              </div>
            </div>

            {/* Congestion Hotspots */}
            {routeStats.peak_hour_analysis?.congestion_hotspots?.length > 0 && (
              <div className="mb-4 p-3.5 bg-white/5 rounded-xl border border-white/5">
                <span className="text-xs text-sky-300 font-semibold uppercase tracking-wider block mb-1.5">
                  Frequent Congestion Bottlenecks Along This Route:
                </span>
                <div className="flex flex-wrap gap-2">
                  {routeStats.peak_hour_analysis.congestion_hotspots.map((spot, idx) => (
                    <span key={idx} className="text-xs px-2.5 py-1 rounded-lg bg-white/10 text-white/80 border border-white/10 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-red-400" />
                      {spot}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Recorded Trips Log */}
            {routeStats.recent_trips?.length > 0 && (
              <div>
                <span className="text-xs text-white/60 block mb-2 font-medium">Recent Recorded Trips on this Route:</span>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs text-white/80">
                    <thead className="bg-white/5 text-white/50 uppercase">
                      <tr>
                        <th className="p-2.5 rounded-l-lg">Date</th>
                        <th className="p-2.5">Departure</th>
                        <th className="p-2.5">Delay</th>
                        <th className="p-2.5">Weather</th>
                        <th className="p-2.5 rounded-r-lg">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {routeStats.recent_trips.map((t) => (
                        <tr key={t.trip_id} className="hover:bg-white/5">
                          <td className="p-2.5 font-medium text-white">{t.trip_date}</td>
                          <td className="p-2.5">{formatTime(t.departure)}</td>
                          <td className="p-2.5">
                            <span className={t.delay_minutes > 5 ? 'text-amber-400 font-semibold' : 'text-emerald-400'}>
                              {t.delay_minutes > 0 ? `+${t.delay_minutes.toFixed(1)}m` : 'On-Time'}
                            </span>
                          </td>
                          <td className="p-2.5">{t.weather}</td>
                          <td className="p-2.5">
                            <span className="px-2 py-0.5 rounded text-[10px] bg-white/10 text-sky-300">
                              {t.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </motion.div>
        )}

        {/* Live Trip Progress Section */}
        {tripStatus && tripStatus.trip_status === 'IN_PROGRESS' && (
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 mb-8 shadow-xl"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-2">
                <Navigation className="w-5 h-5 text-sky-400 animate-pulse" />
                <h3 className="text-lg font-bold text-white">Live Bus Dispatch Progress</h3>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                {tripStatus.trip_status}
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-white/10 rounded-full h-3 mb-6 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-sky-400 via-royal to-teal h-full rounded-full transition-all duration-500 shadow-sm"
                style={{ width: `${Math.min(100, Math.round(tripStatus.progress_percentage || 50))}%` }}
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Last Check-in Stop</span>
                <span className="text-sm font-semibold text-white">
                  {tripStatus.current_stop_name || 'Departing campus'}
                </span>
              </div>
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Next Approaching Stop</span>
                <span className="text-sm font-semibold text-sky-300">
                  {tripStatus.next_stop_name || 'En route'}
                </span>
              </div>
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <span className="text-xs text-white/50 block">Stops Completed</span>
                <span className="text-sm font-semibold text-white">
                  {tripStatus.completed_stops_count} of {tripStatus.total_stops_count} stops
                </span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Route Info Card */}
        {selectedRoute && (
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
          >
            <div>
              <div className="flex items-center gap-2 mb-1">
                <RouteIcon className="w-5 h-5 text-sky-400" />
                <h3 className="text-lg font-bold text-white">Authentic Sri Eshwar Route Corridor</h3>
              </div>
              <p className="text-sm text-white/80">
                <span className="text-sky-300 font-semibold">{selectedRoute.route_number}</span> — {selectedRoute.route_name}
              </p>
              <p className="text-xs text-white/50 mt-0.5">
                {selectedRoute.stops?.length || 0} designated boarding stops along Coimbatore / Pollachi highway
              </p>
            </div>

            <Link
              to={`/routes/${getRouteId(selectedRoute)}`}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-sky-500/20 hover:bg-sky-500/30 text-sky-300 border border-sky-500/30 font-semibold text-sm transition-all hover:gap-3"
            >
              <span>View Interactive Route Map</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </motion.div>
        )}
      </main>
    </div>
  );
};

export default StudentDashboard;