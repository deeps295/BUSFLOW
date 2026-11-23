import React from 'react';
import BubbleBackground from '../components/layout/BubbleBackground';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

export const MainLayout = ({ children, backendConnected, activeTab, onNavigate }) => {
  return (
    <div className="relative min-h-screen flex flex-col font-sans selection:bg-brand-cyan selection:text-slate-900">
      {/* Lightweight GPU-accelerated floating bubbles background */}
      <BubbleBackground />

      {/* Main navigation header */}
      <Navbar 
        backendConnected={backendConnected} 
        activeTab={activeTab} 
        onNavigate={onNavigate} 
      />

      {/* Page Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-8 py-8 space-y-10">
        {children}
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default MainLayout;
