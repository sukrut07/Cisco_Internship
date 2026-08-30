import React from 'react';
import { useGlowEffect } from '../../hooks/useGlowEffect';

interface GlowCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
}

export const GlowCard: React.FC<GlowCardProps> = ({ children, className = '', ...props }) => {
  const ref = useGlowEffect<HTMLDivElement>();

  return (
    <div
      ref={ref}
      className={`glow-card-container glass-card rounded-xl ${className}`}
      {...props}
    >
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </div>
  );
};
