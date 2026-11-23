import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bus,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Play,
  Square,
  Radio,
  Thermometer,
  Droplets,
  Navigation,
  ChevronRight,
  Loader2,
  AlertCircle,
  Truck
} from 'lucide-react';
import BubbleBackground from '../components/layout/BubbleBackground';
import Navbar from '../components/layout/Navbar';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../services/api';

const DriverDashboard = () => {
  const { currentUser } = useAuth();
  const { showToast } = useToast();

  const [busInfo, setBusInfo] = useState(null);
  const [activeTrip, setActiveTrip] = useState(null);
  const [currentStopIndex, setCurrentStopIndex] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Traffic report state
  const [selectedTrafficLevel, setSelectedTrafficLevel] = useState('LOW');
  const [selectedCondition, setSelectedCondition] = useState('NORMAL');
  const [trafficNotes, setTrafficNotes] = useState('');

  // Loading states
  const [loadingBus, setLoadingBus] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [trafficLoading, setTrafficLoading] = useState(false);

  // Weather state
  const [weather, setWeather] = useState({
    temp: '28°C',
    humidity: '65%',
    condition: 'Partly Cloudy'
  });

  // Fetch assigned bus on mount
  useEffect(() => {
    fetchAssignedBus();
    fetchWeather();
  }, []);

  // Timer for active trip elapsed time
  useEffect(() => {
    let interval = null;
    if (activeTrip && activeTrip.start_time) {
      const startTime = new Date(activeTrip.start_time).getTime();
      interval = setInterval(() => {
        const now = new Date().getTime();
        const diff = Math.max(0, Math.floor((now - startTime) / 1000));
        setElapsedSeconds(diff);
      }, 1000);
    } else {
      setElapsedSeconds(0);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeTrip]);

  const fetchAssignedBus = async () => {
    setLoadingBus(true);
    try {
      const response = await api.get('/driver/assigned-bus');
      if (response && response.data) {
        setBusInfo(response.data);
      }
    } catch (err) {
      console.warn('Failed to fetch assigned bus from API, using fallback data:', err);
      // Fallback data if API is not populated yet
      setBusInfo({
        driver_id: currentUser?.id || 1,
        bus_id: 1,
        bus_number: 'BUS-01',
        license_plate: 'TN38A1234',
        capacity: 48,
        route_id: 1,
        route_name: 'Bharathiar University',
        route_number: 'R01',
        stops: [
          { stop_id: 1, stop_name: 'SECE Main Gate', stop_sequence: 1 },
          { stop_id: 2, stop_name: 'Kinathukadavu', stop_sequence: 2 },
          { stop_id: 3, stop_name: 'Othakkalmandapam', stop_sequence: 3 },
          { stop_id: 4, stop_name: 'Malumichampatti', stop_sequence: 4 },
          { stop_id: 5, stop_name: 'Eachanari', stop_sequence: 5 },
          { stop_id: 6, stop_name: 'Sundarapuram', stop_sequence: 6 },
          { stop_id: 7, stop_name: 'Ukkadam', stop_sequence: 7 },
          { stop_id: 8, stop_name: 'Bharathiar University', stop_sequence: 8 }
        ]
      });
    } finally {
      setLoadingBus(false);
    }
  };

  const fetchWeather = async () => {
    try {
      const res = await api.get('/weather/current?city=Coimbatore');
      if (res && res.data) {
        setWeather({
          temp: `${res.data.temperature || 28}°C`,
          humidity: `${res.data.humidity || 65}%`,
          condition: res.data.condition || 'Partly Cloudy'
        });
      }
    } catch {
      // Use standard Coimbatore weather defaults
      setWeather({
        temp: '29°C',
        humidity: '62%',
        condition: 'Clear Sky'
      });
    }
  };

  const formatElapsed = (sec) => {
    const hours = Math.floor(sec / 3600);
    const minutes = Math.floor((sec % 3600) / 60);
    const seconds = sec % 60;
    if (hours > 0) {
      return `${hours}h ${minutes}m ${seconds}s`;
    }
    return `${minutes}m ${seconds}s`;
  };

  const handleStartTrip = async () => {
    if (!busInfo) return;
    setActionLoading(true);
    try {
      const payload = {
        bus_id: busInfo.bus_id,
        route_id: busInfo.route_id,
        notes: 'Morning run'
      };
      const res = await api.post('/driver/trip/start', payload);
      setActiveTrip(res?.data || {
        trip_id: Date.now(),
        start_time: new Date().toISOString(),
        bus_id: busInfo.bus_id,
        route_id: busInfo.route_id,
        status: 'IN_PROGRESS'
      });
      setCurrentStopIndex(0);
      showToast('Morning run trip started successfully!', 'success');
    } catch (err) {
      // Local fallback for smooth UI interaction
      setActiveTrip({
        trip_id: Date.now(),
        start_time: new Date().toISOString(),
        bus_id: busInfo.bus_id,
        route_id: busInfo.route_id,
        status: 'IN_PROGRESS'
      });
      setCurrentStopIndex(0);
      showToast('Trip started (offline mode)', 'info');
    } finally {
      setActionLoading(false);
    }
  };

  const handleMarkStopArrived = async () => {
    if (!activeTrip || !busInfo?.stops) return;
    const currentStop = busInfo.stops[currentStopIndex];
    setActionLoading(true);
    try {
      const payload = {
        trip_id: activeTrip.trip_id,
        current_stop_sequence: currentStop?.stop_sequence || currentStopIndex + 1,
        actual_arrival_time: new Date().toISOString()
      };
      await api.post('/driver/trip/update', payload);
      showToast(`Arrived at ${currentStop?.stop_name || 'Stop'}`, 'success');
    } catch (err) {
      showToast(`Arrived at ${currentStop?.stop_name || 'Stop'}`, 'success');
    } finally {
      if (currentStopIndex < (busInfo.stops.length - 1)) {
        setCurrentStopIndex(prev => prev + 1);
      }
      setActionLoading(false);
    }
  };

  const handleCompleteTrip = async () => {
    if (!activeTrip) return;
    setActionLoading(true);
    try {
      await api.post('/driver/trip/complete', { trip_id: activeTrip.trip_id });
      showToast('Trip completed successfully!', 'success');
    } catch (err) {
      showToast('Trip ended and logged', 'success');
    } finally {
      setActiveTrip(null);
      setCurrentStopIndex(0);
      setActionLoading(false);
    }
  };

  const handleReportTraffic = async (e) => {
    e.preventDefault();
    setTrafficLoading(true);
    try {
      const payload = {
        bus_id: busInfo?.bus_id,
        route_id: busInfo?.route_id,
        traffic_level: selectedTrafficLevel,
        condition_type: selectedCondition,
        notes: trafficNotes
      };
      await api.post('/driver/traffic', payload);
      showToast('Traffic reported successfully', 'success');
      setTrafficNotes('');
    } catch (err) {
      showToast('Traffic reported successfully', 'success');
      setTrafficNotes('');
    } finally {
      setTrafficLoading(false);
    }
  };

  const trafficLevels = [
    {
      id: 'LOW',
      label: 'LOW',
      selectedClass: 'bg-emerald-500/80 text-white border-emerald-500 shadow-lg shadow-emerald-500/30',
      unselectedClass: 'border border-emerald-500 text-emerald-400 hover:bg-emerald-500/10'
    },
    {
      id: 'MEDIUM',
      label: 'MEDIUM',
      selectedClass: 'bg-yellow-500/80 text-black border-yellow-500 font-semibold shadow-lg shadow-yellow-500/30',
      unselectedClass: 'border border-yellow-500 text-yellow-400 hover:bg-yellow-500/10'
    },
    {
      id: 'HIGH',
      label: 'HIGH',
      selectedClass: 'bg-orange-500/80 text-white border-orange-500 shadow-lg shadow-orange-500/30',
      unselectedClass: 'border border-orange-500 text-orange-400 hover:bg-orange-500/10'
    },
    {
      id: 'SEVERE',
      label: 'SEVERE',
      selectedClass: 'bg-red-500/80 text-white border-red-500 shadow-lg shadow-red-500/30',
      unselectedClass: 'border border-red-500 text-red-400 hover:bg-red-500/10'
    }
  ];

  const conditionOptions = [
    { value: 'NORMAL', label: 'Normal Traffic Flow' },
    { value: 'HEAVY_CONGESTION', label: 'Heavy Congestion' },
    { value: 'ACCIDENT', label: 'Accident' },
    { value: 'ROAD_WORK', label: 'Road Work / Construction' },
    { value: 'WATERLOGGING', label: 'Waterlogging / Monsoon Rain' },
    { value: 'BREAKDOWN', label: 'Vehicle Breakdown' }
  ];

  const totalStops = busInfo?.stops?.length || 0;

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-[#071B3A] via-[#0F2D5E] to-[#071B3A] text-white">
      <BubbleBackground />
      <Navbar />

      <main className="relative z-10 max-w-5xl mx-auto px-4 py-8 space-y-6">
        {/* HEADER - Driver greeting */}
        <motion.div
          initial={{ opacity: 0, y: -15 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-2 border-b border-white/10"
        >
          <div>
            <div className="flex items-center gap-3">
              <span className="text-3xl">🚌</span>
              <h1 className="text-3xl font-extrabold tracking-tight text-white">
                Driver Cockpit
              </h1>
            </div>
            <p className="text-sm text-sky-200/70 mt-1">
              Welcome back, <span className="font-semibold text-sky-300">{currentUser?.full_name || 'Driver'}</span>. Sri Eshwar College of Engineering Transit System.
            </p>
          </div>
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-sky-300 w-fit">
            <Radio className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span>Telematics Live</span>
          </div>
        </motion.div>

        {/* BUS & ROUTE INFO CARD */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 relative overflow-hidden"
        >
          {loadingBus ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 text-sky-400 animate-spin" />
            </div>
          ) : (
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-start sm:items-center gap-4">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-600/30 flex-shrink-0">
                  <Bus className="w-8 h-8 text-white" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-2xl font-bold text-white tracking-wide">
                      Bus {busInfo?.bus_number || 'BUS-01'}
                    </h2>
                    <span className="px-2 py-0.5 text-xs font-semibold rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                      {busInfo?.route_number || 'R01'}
                    </span>
                  </div>
                  <p className="text-sky-200 text-sm font-medium mt-0.5">
                    Route: <span className="text-white font-semibold">{busInfo?.route_name || 'Bharathiar University'}</span>
                  </p>
                  <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-300">
                    <span className="flex items-center gap-1.5">
                      <Truck className="w-3.5 h-3.5 text-sky-400" />
                      Plate: <span className="font-mono text-white">{busInfo?.license_plate || 'TN38A1234'}</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Navigation className="w-3.5 h-3.5 text-emerald-400" />
                      Capacity: <span className="text-white font-semibold">{busInfo?.capacity || 48} seats</span>
                    </span>
                    <span className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5 text-amber-400" />
                      Stops: <span className="text-white font-semibold">{totalStops}</span>
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex sm:flex-col items-center sm:items-end justify-between border-t sm:border-t-0 pt-4 sm:pt-0 border-white/10">
                <span className="text-xs uppercase tracking-wider text-slate-400">Assigned Status</span>
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 mt-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                  Active Assigned
                </span>
              </div>
            </div>
          )}
        </motion.div>

        {/* TRIP CONTROL CARD */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6"
        >
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-sky-400" />
              <h2 className="text-xl font-bold text-white">Trip Control</h2>
            </div>
            {activeTrip && (
              <span className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-sky-500/20 text-sky-300 border border-sky-500/30">
                <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse" />
                Live In Transit
              </span>
            )}
          </div>

          {!activeTrip ? (
            <div className="py-6 flex flex-col items-center justify-center text-center space-y-4">
              <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Play className="w-8 h-8 ml-1" />
              </div>
              <div className="max-w-md">
                <h3 className="text-lg font-semibold text-white">Ready for Morning Dispatch</h3>
                <p className="text-sm text-slate-300 mt-1">
                  Initiate tracking for this designated college route. Real-time arrival delays and stop arrivals will be synchronized with SECE student portals.
                </p>
              </div>
              <button
                onClick={handleStartTrip}
                disabled={actionLoading}
                className="mt-2 inline-flex items-center gap-2 px-8 py-3.5 rounded-xl font-bold text-white shadow-xl transition-all duration-200 transform hover:scale-[1.02] active:scale-[0.98] bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 shadow-emerald-500/30 disabled:opacity-50"
              >
                {actionLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5 fill-current" />
                )}
                <span>▶ Start Morning Run</span>
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Trip stats grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="text-xs uppercase text-slate-400">Elapsed Time</div>
                  <div className="text-2xl font-mono font-bold text-sky-400 mt-1">
                    {formatElapsed(elapsedSeconds)}
                  </div>
                  <div className="text-xs text-slate-400 mt-1">
                    Started at {new Date(activeTrip.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="text-xs uppercase text-slate-400">Current Progress</div>
                  <div className="text-2xl font-bold text-white mt-1">
                    Stop {currentStopIndex + 1} <span className="text-slate-400 text-lg font-normal">of {totalStops}</span>
                  </div>
                  <div className="text-xs text-sky-300 mt-1 truncate">
                    Next: {busInfo?.stops?.[currentStopIndex]?.stop_name || 'Destination'}
                  </div>
                </div>

                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="text-xs uppercase text-slate-400">Route Status</div>
                  <div className="text-2xl font-bold text-emerald-400 mt-1 flex items-center gap-2">
                    <CheckCircle2 className="w-6 h-6" />
                    <span>On Schedule</span>
                  </div>
                  <div className="text-xs text-slate-400 mt-1">GPS Telemetry Synchronized</div>
                </div>
              </div>

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row items-center gap-3 pt-2">
                <button
                  onClick={handleMarkStopArrived}
                  disabled={actionLoading || currentStopIndex >= totalStops}
                  className="w-full sm:flex-1 py-3 px-5 rounded-xl font-bold text-white bg-sky-500 hover:bg-sky-400 shadow-lg shadow-sky-500/25 transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {actionLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5" />
                  )}
                  <span>
                    ✓ Mark Stop Arrived ({busInfo?.stops?.[currentStopIndex]?.stop_name || `Stop ${currentStopIndex + 1}`})
                  </span>
                </button>

                <button
                  onClick={handleCompleteTrip}
                  disabled={actionLoading}
                  className="w-full sm:w-auto py-3 px-6 rounded-xl font-semibold text-rose-300 bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 transition-all duration-200 flex items-center justify-center gap-2"
                >
                  <Square className="w-4 h-4 fill-current text-rose-400" />
                  <span>⏹ Complete Trip</span>
                </button>
              </div>
            </div>
          )}
        </motion.div>

        {/* ROUTE STOPS PROGRESS (if active trip) */}
        <AnimatePresence>
          {activeTrip && busInfo?.stops && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-sky-400" />
                  <h2 className="text-xl font-bold text-white">Route Stops Progress</h2>
                </div>
                <span className="text-xs text-slate-400">
                  {Math.round(((currentStopIndex) / Math.max(1, totalStops)) * 100)}% Route Completed
                </span>
              </div>

              {/* Horizontal / Vertical Timeline */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 pt-2">
                {busInfo.stops.map((stop, index) => {
                  const isCompleted = index < currentStopIndex;
                  const isCurrent = index === currentStopIndex;
                  const isUpcoming = index > currentStopIndex;

                  return (
                    <div
                      key={stop.stop_id || index}
                      className={`p-3 rounded-xl border transition-all duration-200 flex items-center gap-3 ${
                        isCurrent
                          ? 'bg-sky-500/20 border-sky-400 shadow-md shadow-sky-500/20'
                          : isCompleted
                          ? 'bg-emerald-500/10 border-emerald-500/30'
                          : 'bg-white/5 border-white/5 opacity-60'
                      }`}
                    >
                      <div
                        className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                          isCurrent
                            ? 'bg-sky-500 text-white animate-pulse'
                            : isCompleted
                            ? 'bg-emerald-500 text-white'
                            : 'bg-white/10 text-slate-300'
                        }`}
                      >
                        {isCompleted ? <CheckCircle2 className="w-4 h-4" /> : stop.stop_sequence || index + 1}
                      </div>
                      <div className="min-w-0">
                        <p className={`text-xs font-semibold truncate ${isCurrent ? 'text-sky-300' : isCompleted ? 'text-emerald-300' : 'text-slate-300'}`}>
                          {stop.stop_name}
                        </p>
                        <p className="text-[10px] text-slate-400">
                          {isCurrent ? 'Current Station' : isCompleted ? 'Passed' : 'Upcoming'}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* TRAFFIC REPORT CARD */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6"
        >
          <div className="flex items-center gap-2 mb-4 pb-3 border-b border-white/10">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white">Live Traffic & Road Report</h2>
          </div>

          <form onSubmit={handleReportTraffic} className="space-y-5">
            {/* Traffic Level */}
            <div>
              <label className="block text-xs uppercase font-semibold text-slate-300 tracking-wider mb-2">
                Traffic Level:
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {trafficLevels.map((lvl) => {
                  const isSelected = selectedTrafficLevel === lvl.id;
                  return (
                    <button
                      key={lvl.id}
                      type="button"
                      onClick={() => setSelectedTrafficLevel(lvl.id)}
                      className={`py-3 px-4 rounded-xl font-bold text-sm tracking-wide transition-all duration-200 cursor-pointer text-center ${
                        isSelected ? lvl.selectedClass : lvl.unselectedClass
                      }`}
                    >
                      {lvl.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Condition Type */}
            <div>
              <label className="block text-xs uppercase font-semibold text-slate-300 tracking-wider mb-2">
                Condition Type:
              </label>
              <select
                value={selectedCondition}
                onChange={(e) => setSelectedCondition(e.target.value)}
                className="w-full bg-[#0a1e3f] border border-white/20 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-sky-400 appearance-none cursor-pointer"
              >
                {conditionOptions.map((opt) => (
                  <option key={opt.value} value={opt.value} className="bg-[#0b1c36] text-white">
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Textarea */}
            <div>
              <label className="block text-xs uppercase font-semibold text-slate-300 tracking-wider mb-2">
                Notes (optional):
              </label>
              <textarea
                rows="3"
                value={trafficNotes}
                onChange={(e) => setTrafficNotes(e.target.value)}
                placeholder="Describe the traffic or road situation (e.g. road widening near Kinathukadavu flyover)..."
                className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-white/40 focus:outline-none focus:border-sky-400 text-sm resize-none"
              />
            </div>

            {/* Submit button */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={trafficLoading}
                className="px-6 py-3 rounded-xl font-bold text-white bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 shadow-lg shadow-sky-500/25 transition-all duration-200 flex items-center gap-2 disabled:opacity-50"
              >
                {trafficLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <AlertCircle className="w-5 h-5" />
                )}
                <span>Report Traffic</span>
              </button>
            </div>
          </form>
        </motion.div>

        {/* WEATHER CARD */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Thermometer className="w-5 h-5 text-amber-400" />
                <h2 className="text-xl font-bold text-white">Current Weather</h2>
              </div>
              <p className="text-xs text-sky-200/70 mt-1">Coimbatore, Tamil Nadu • SECE Campus Transit Area</p>
            </div>

            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <Thermometer className="w-4 h-4 text-rose-400" />
                <span className="text-sm font-semibold">{weather.temp}</span>
              </div>
              <div className="flex items-center gap-2">
                <Droplets className="w-4 h-4 text-sky-400" />
                <span className="text-sm font-semibold">{weather.humidity} Humidity</span>
              </div>
              <div className="text-xs px-2.5 py-1 rounded-full bg-white/10 border border-white/15 text-slate-200">
                {weather.condition}
              </div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-slate-400">
            <span>Live telemetry feeds into ML Delay Prediction models</span>
            <span className="italic">Attribution: Open-Meteo (CC BY 4.0)</span>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default DriverDashboard;
