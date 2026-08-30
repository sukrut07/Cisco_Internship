import React from 'react';
import { Outlet } from 'react-router-dom';
import { SideNavBar } from './SideNavBar';
import { TopAppBar } from './TopAppBar';
import { AppFooter } from './AppFooter';
import { AmbientBackground } from '../common/AmbientBackground';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { motion, AnimatePresence } from 'framer-motion';

export const AppLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-on-background flex flex-col relative overflow-x-hidden">
      {/* Skip to main content accessibility link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 z-50 px-4 py-2 bg-primary-container text-white font-bold rounded-lg shadow-2xl border border-white/20 focus:outline-none"
      >
        Skip to main content
      </a>

      {/* Ambient background blur blobs */}
      <AmbientBackground />

      {/* Main Layout Container */}
      <div className="flex flex-1 relative z-10">
        {/* Collapsible Sidebar */}
        <SideNavBar />

        {/* Dynamic Main Workspace Container */}
        <div className="flex-1 flex flex-col min-w-0 pl-16 md:pl-64 transition-all duration-300">
          <TopAppBar />

          {/* Page Route Outlet with ErrorBoundary wrapper and smooth fade transition */}
          <main id="main-content" role="main" className="flex-1 p-4 md:p-6 flex flex-col max-w-[1680px] w-full mx-auto">
            <ErrorBoundary fallbackTitle="Page Level Exception Caught">
              <AnimatePresence mode="wait">
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.2 }}
                  className="flex-1 flex flex-col"
                >
                  <Outlet />
                </motion.div>
              </AnimatePresence>
            </ErrorBoundary>
          </main>

          <AppFooter />
        </div>
      </div>
    </div>
  );
};
