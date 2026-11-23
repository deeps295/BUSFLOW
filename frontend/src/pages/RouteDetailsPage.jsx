import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  MapPin, 
  Bus, 
  ArrowLeft, 
  Clock, 
  Navigation, 
  ChevronRight, 
  Info, 
  GraduationCap, 
  Calendar,
  Sparkles
} from 'lucide-react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

import BubbleBackground from '../components/layout/BubbleBackground';
import Navbar from '../components/layout/Navbar';
import api from '../services/api';

// Fix Leaflet default marker icons issue in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Hardcoded mapping for known Coimbatore area coordinates
const STOP_COORDS = {
  'SECE Main Gate': [10.8284, 77.0146],
  'Sri Eshwar College': [10.8284, 77.0146],
  'Bharathiar University': [11.0168, 76.9558],
  'Saravanampatti': [11.0710, 76.9961],
  'Kovaipudur': [10.9000, 76.9800],
  'Gandhipuram': [11.0168, 76.9676],
  'Ukkadam': [10.9880, 76.9620],
  'Singanallur': [10.9997, 77.0259],
  'Peelamedu': [11.0252, 77.0101],
  'Sundarapuram': [10.9500, 76.9700],
  'Kinathukadavu': [10.8200, 77.0200],
  'Pollachi': [10.6609, 77.0048],
};

const getStopCoords = (stop, index = 0) => {
  if (stop.latitude && stop.longitude) {
    return [parseFloat(stop.latitude), parseFloat(stop.longitude)];
  }
  const stopName = stop.stop_name?.trim();
  if (STOP_COORDS[stopName]) {
    return STOP_COORDS[stopName];
  }
  const seq = Number(stop.stop_sequence) || (index + 1);
  return [10.8284 + (seq * 0.015), 77.0146 - (seq * 0.008)];
};

export default function RouteDetailsPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [route, setRoute] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let isMounted = true;

    const fetchRoute = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch routes list
        const res = await api.get('/student/routes');
        const routesList = Array.isArray(res.data) ? res.data : (res.data?.routes || []);

        const matchedRoute = routesList.find(
          (r) =>
            String(r.route_id) === String(id) ||
            String(r.id) === String(id) ||
            String(r.route_number).toLowerCase() === String(id).toLowerCase()
        );

        if (isMounted) {
          if (matchedRoute) {
            setRoute(matchedRoute);
          } else {
            setError(`Route "${id}" not found.`);
          }
        }
      } catch (err) {
        console.error('Failed to load route details:', err);
        if (isMounted) {
          setError('Failed to fetch route information. Please try again.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchRoute();

    return () => {
      isMounted = false;
    };
  }, [id]);

  const stops = route?.stops || [];
  const sortedStops = [...stops].sort((a, b) => (a.stop_sequence || 0) - (b.stop_sequence || 0));

  const polylinePositions = sortedStops.map((stop, idx) => getStopCoords(stop, idx));
  const centerPosition = polylinePositions.length > 0 ? polylinePositions[0] : [10.8284, 77.0146];

  return (
    <div
      className="min-h-screen text-slate-100 relative overflow-hidden"
      style={{
        background: 'linear-gradient(135deg, #071B3A 0%, #0F2D5E 50%, #071B3A 100%)',
      }}
    >
      <BubbleBackground />
      <Navbar />

      <main className="relative z-10 max-w-5xl mx-auto px-4 py-8">
        {/* BACK LINK */}
        <Link
          to="/student"
          className="inline-flex items-center gap-2 text-sky-400 hover:text-sky-300 font-medium mb-6 transition-colors group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to Student Dashboard
        </Link>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 space-y-4">
            <div className="w-12 h-12 border-4 border-sky-400/20 border-t-sky-400 rounded-full animate-spin" />
            <p className="text-slate-400 animate-pulse text-sm">Loading route details...</p>
          </div>
        ) : error || !route ? (
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-8 text-center max-w-lg mx-auto">
            <Info className="w-12 h-12 text-rose-400 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Unable to Load Route</h2>
            <p className="text-slate-300 mb-6">{error || 'Route not found.'}</p>
            <Link
              to="/student"
              className="inline-flex items-center justify-center px-6 py-2.5 rounded-xl bg-sky-500 hover:bg-sky-400 text-white font-medium transition"
            >
              Return to Dashboard
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {/* PAGE HEADER */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-8"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="flex items-start md:items-center gap-4">
                  <div className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 font-extrabold text-2xl tracking-wider text-white shadow-lg shadow-sky-500/25 border border-sky-300/30">
                    {route.route_number || 'Route'}
                  </div>
                  <div>
                    <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
                      {route.route_name || 'College Route'}
                    </h1>
                    <p className="text-slate-400 text-sm mt-1 flex items-center gap-2">
                      <Bus className="w-4 h-4 text-sky-400" />
                      SECE Campus Bus Transit Network
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 self-start md:self-auto">
                  <div className="px-3.5 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-slate-300 flex items-center gap-1.5">
                    <MapPin className="w-3.5 h-3.5 text-sky-400" />
                    <span>{sortedStops.length} Stops</span>
                  </div>
                  <div className="px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-xs font-medium text-emerald-300 flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Morning & Evening Service</span>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* LEAFLET MAP */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Navigation className="w-5 h-5 text-sky-400" />
                  <h2 className="text-lg font-bold text-white">Route Visualizer & Live Geometry</h2>
                </div>
                <span className="text-xs text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                  Interactive Map
                </span>
              </div>

              <div className="rounded-2xl overflow-hidden border border-white/10 shadow-inner relative" style={{ height: '400px' }}>
                <MapContainer
                  center={centerPosition}
                  zoom={12}
                  scrollWheelZoom={false}
                  style={{ height: '100%', width: '100%' }}
                >
                  <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                  />

                  {sortedStops.map((stop, idx) => {
                    const coords = getStopCoords(stop, idx);
                    return (
                      <Marker key={stop.stop_id || idx} position={coords}>
                        <Popup>
                          <div className="text-slate-900 font-sans p-1">
                            <strong className="block text-sm border-b pb-1 mb-1">
                              {stop.stop_sequence || idx + 1}. {stop.stop_name}
                            </strong>
                            <span className="text-xs text-slate-600 block">
                              {stop.stop_name?.toLowerCase().includes('sece') ||
                              stop.stop_name?.toLowerCase().includes('eshwar')
                                ? '🎓 Destination Campus Stop'
                                : 'Bus Transit Stop'}
                            </span>
                            {stop.distance_from_prev && (
                              <span className="text-xs text-slate-500 block mt-0.5">
                                +{stop.distance_from_prev} km from prev
                              </span>
                            )}
                          </div>
                        </Popup>
                      </Marker>
                    );
                  })}

                  {polylinePositions.length > 1 && (
                    <Polyline
                      positions={polylinePositions}
                      color="#38bdf8"
                      weight={4}
                      opacity={0.85}
                      dashArray="8, 6"
                    />
                  )}
                </MapContainer>
              </div>
              <div className="flex items-center justify-between mt-3 text-xs text-slate-400">
                <p>Showing full route path from pickup to Sri Eshwar College of Engineering.</p>
                <p className="text-slate-500">Map: OpenStreetMap contributors (ODbL)</p>
              </div>
            </motion.div>

            {/* STOPS TABLE */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.2 }}
              className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-lg font-bold text-white">Route Stops Sequence</h2>
                </div>
                <span className="text-xs text-slate-400">
                  Total {sortedStops.length} designated boarding points
                </span>
              </div>

              <div className="overflow-x-auto rounded-xl border border-white/10">
                <table className="w-full text-left text-sm">
                  <thead className="bg-white/10 text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    <tr>
                      <th scope="col" className="px-4 py-3 text-center w-16">Seq #</th>
                      <th scope="col" className="px-6 py-3">Stop Name</th>
                      <th scope="col" className="px-6 py-3 text-right">Distance from Prev</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {sortedStops.length === 0 ? (
                      <tr>
                        <td colSpan="3" className="px-6 py-6 text-center text-slate-400">
                          No stops listed for this route.
                        </td>
                      </tr>
                    ) : (
                      sortedStops.map((stop, idx) => {
                        const isSece =
                          stop.stop_name?.toLowerCase().includes('sece') ||
                          stop.stop_name?.toLowerCase().includes('eshwar');

                        return (
                          <tr
                            key={stop.stop_id || idx}
                            className={`transition-colors ${
                              isSece
                                ? 'bg-sky-500/15 border-l-4 border-l-sky-400'
                                : idx % 2 === 0
                                ? 'bg-white/0 hover:bg-white/5'
                                : 'bg-white/[0.02] hover:bg-white/5'
                            }`}
                          >
                            <td className="px-4 py-3.5 text-center font-mono font-medium text-slate-300">
                              {stop.stop_sequence || idx + 1}
                            </td>
                            <td className="px-6 py-3.5">
                              <div className="flex items-center gap-2">
                                <span className={`font-medium ${isSece ? 'text-sky-300 font-semibold' : 'text-slate-200'}`}>
                                  {stop.stop_name}
                                </span>
                                {isSece && (
                                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-sky-400/20 text-sky-300 border border-sky-400/30">
                                    <GraduationCap className="w-3.5 h-3.5" />
                                    College Campus
                                  </span>
                                )}
                              </div>
                            </td>
                            <td className="px-6 py-3.5 text-right font-mono text-slate-400">
                              {stop.distance_from_prev != null
                                ? `${Number(stop.distance_from_prev).toFixed(1)} km`
                                : idx === 0
                                ? 'Origin (0.0 km)'
                                : '—'}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </motion.div>

            {/* SCHEDULE INFO & PREDICTION LINK */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* SCHEDULE INFO */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.3 }}
                className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-6 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 mb-4">
                    <Calendar className="w-5 h-5 text-emerald-400" />
                    <h3 className="text-lg font-bold text-white">Transit Schedule</h3>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
                      <Clock className="w-4 h-4 text-sky-400 mt-0.5 shrink-0" />
                      <div>
                        <div className="text-white font-medium">Morning Departure</div>
                        <div className="text-slate-300 text-xs mt-0.5">06:30 AM from origin terminal</div>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
                      <GraduationCap className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                      <div>
                        <div className="text-white font-medium">College Arrival</div>
                        <div className="text-slate-300 text-xs mt-0.5">Approximately 08:30 – 09:00 AM</div>
                      </div>
                    </div>

                    <div className="flex items-start gap-3 p-3 rounded-xl bg-white/5 border border-white/5">
                      <Bus className="w-4 h-4 text-indigo-400 mt-0.5 shrink-0" />
                      <div>
                        <div className="text-white font-medium">Evening Return</div>
                        <div className="text-slate-300 text-xs mt-0.5">05:00 PM from SECE Bus Bay</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/10 text-xs text-slate-400 flex items-center justify-between">
                  <span>Operating Days</span>
                  <span className="font-semibold text-slate-200">Monday – Saturday</span>
                </div>
              </motion.div>

              {/* PREDICTION LINK */}
              <motion.div
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: 0.35 }}
                className="bg-gradient-to-br from-white/5 to-sky-500/10 backdrop-blur-md border border-white/10 rounded-2xl p-6 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-5 h-5 text-sky-400" />
                    <h3 className="text-lg font-bold text-white">Live AI Delay Prediction</h3>
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed mb-6">
                    Get real-time ML-estimated arrival times and potential traffic delay predictions specifically calibrated for <strong className="text-white">{route.route_name || 'this route'}</strong>.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => navigate('/student', { state: { selectedRouteId: route.route_id || route.id || route.route_number } })}
                  className="w-full py-3.5 px-5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-sky-500/25 transition-all group cursor-pointer"
                >
                  <span>Get Arrival Prediction for This Route</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </motion.div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
