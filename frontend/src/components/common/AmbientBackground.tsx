import React from 'react';

export const AmbientBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {/* Orange Glow - Top Left */}
      <div 
        className="absolute -top-32 -left-32 w-[550px] h-[550px] rounded-full bg-gradient-to-br from-primary-container/20 via-orange-500/10 to-transparent blur-[120px] transform-gpu"
      />
      {/* Cyan Glow - Bottom Right */}
      <div 
        className="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-gradient-to-tl from-secondary/15 via-secondary-fixed/5 to-transparent blur-[130px] transform-gpu"
      />
      {/* Blue / Indigo Glow - Center */}
      <div 
        className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[700px] h-[450px] rounded-full bg-blue-600/5 blur-[140px] transform-gpu"
      />
    </div>
  );
};
