import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { SkeletonLoader } from './components/common/SkeletonLoader';

// Route-level code splitting with React.lazy
const Dashboard = lazy(() => import('./pages/Dashboard').then(m => ({ default: m.Dashboard })));
const AIWorkbench = lazy(() => import('./pages/AIWorkbench').then(m => ({ default: m.AIWorkbench })));
const CaseList = lazy(() => import('./pages/CaseList').then(m => ({ default: m.CaseList })));
const ReviewPage = lazy(() => import('./pages/ReviewPage').then(m => ({ default: m.ReviewPage })));
const VerificationPage = lazy(() => import('./pages/VerificationPage').then(m => ({ default: m.VerificationPage })));
const ResponsibleAI = lazy(() => import('./pages/ResponsibleAI').then(m => ({ default: m.ResponsibleAI })));
const AuditLogPage = lazy(() => import('./pages/AuditLogPage').then(m => ({ default: m.AuditLogPage })));
const NetworkMapPage = lazy(() => import('./pages/NetworkMapPage').then(m => ({ default: m.NetworkMapPage })));
const TrafficAnalysisPage = lazy(() => import('./pages/TrafficAnalysisPage').then(m => ({ default: m.TrafficAnalysisPage })));
const SystemHealthPage = lazy(() => import('./pages/SystemHealthPage').then(m => ({ default: m.SystemHealthPage })));
const SupportPage = lazy(() => import('./pages/SupportPage').then(m => ({ default: m.SupportPage })));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })));

const RouteLoadingFallback = () => (
  <div className="space-y-4 p-4 animate-fadeIn" aria-label="Loading section content">
    <SkeletonLoader className="h-12 w-full rounded-xl" />
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <SkeletonLoader className="h-72 w-full rounded-xl" />
      <SkeletonLoader className="h-72 w-full rounded-xl" />
    </div>
  </div>
);

export const App: React.FC = () => {
  return (
    <ErrorBoundary fallbackTitle="Application Level Boundary Caught Error">
      <BrowserRouter>
        <Suspense fallback={<RouteLoadingFallback />}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/workbench" element={<AIWorkbench />} />
              <Route path="/cases" element={<CaseList />} />
              <Route path="/review" element={<ReviewPage />} />
              <Route path="/verification" element={<VerificationPage />} />
              <Route path="/responsible-ai" element={<ResponsibleAI />} />
              <Route path="/audit" element={<AuditLogPage />} />
              <Route path="/topology" element={<NetworkMapPage />} />
              <Route path="/traffic" element={<TrafficAnalysisPage />} />
              <Route path="/health" element={<SystemHealthPage />} />
              <Route path="/support" element={<SupportPage />} />
              {/* 404 Route */}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
      </BrowserRouter>
    </ErrorBoundary>
  );
};
