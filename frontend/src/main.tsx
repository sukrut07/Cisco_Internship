import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import { ToastProvider } from './context/ToastContext';
import { CaseProvider } from './context/CaseContext';
import './styles/tokens.css';

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ToastProvider>
      <CaseProvider>
        <App />
      </CaseProvider>
    </ToastProvider>
  </React.StrictMode>
);
