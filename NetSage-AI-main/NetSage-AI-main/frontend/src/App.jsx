import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import NewCase from './pages/NewCase';
import CaseList from './pages/CaseList';
import CaseDetail from './pages/CaseDetail';
import RuleCheckerPage from './pages/RuleCheckerPage';
import ResponsibleAILog from './pages/ResponsibleAILog';
import Verification from './pages/Verification';
import Settings from './pages/Settings';
import { getSystemStatus } from './services/api';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [selectedCaseId, setSelectedCaseId] = useState('CASE-101');
  const [aiStatus, setAiStatus] = useState(null);

  useEffect(() => {
    getSystemStatus().then(status => {
      setAiStatus(status);
    }).catch(() => {
      setAiStatus({ ai_mode: 'Mock AI Engine' });
    });
  }, []);

  return (
    <div className="app-container">
      <Navbar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        aiStatus={aiStatus} 
      />

      <main className="main-content">
        {activePage === 'dashboard' && (
          <Dashboard 
            setActivePage={setActivePage} 
            setSelectedCaseId={setSelectedCaseId} 
          />
        )}

        {activePage === 'new-case' && (
          <NewCase 
            setActivePage={setActivePage} 
            setSelectedCaseId={setSelectedCaseId} 
          />
        )}

        {activePage === 'cases' && (
          <CaseList 
            setActivePage={setActivePage} 
            setSelectedCaseId={setSelectedCaseId} 
          />
        )}

        {activePage === 'case-detail' && (
          <CaseDetail 
            caseId={selectedCaseId} 
            setActivePage={setActivePage} 
          />
        )}

        {activePage === 'rule-checker' && (
          <RuleCheckerPage />
        )}

        {activePage === 'responsible-ai' && (
          <ResponsibleAILog />
        )}

        {activePage === 'verification' && (
          <Verification selectedCaseId={selectedCaseId} />
        )}

        {activePage === 'settings' && (
          <Settings />
        )}
      </main>
    </div>
  );
}
