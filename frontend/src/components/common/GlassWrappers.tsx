import React from 'react';

interface GlassProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export const GlassPanel: React.FC<GlassProps> = ({ children, className = '', ...props }) => {
  return (
    <div className={`glass-panel rounded-xl ${className}`} {...props}>
      {children}
    </div>
  );
};

export const GlassCard: React.FC<GlassProps> = ({ children, className = '', ...props }) => {
  return (
    <div className={`glass-card rounded-lg ${className}`} {...props}>
      {children}
    </div>
  );
};

export const GlassDeep: React.FC<GlassProps> = ({ children, className = '', ...props }) => {
  return (
    <div className={`glass-deep rounded-xl ${className}`} {...props}>
      {children}
    </div>
  );
};
