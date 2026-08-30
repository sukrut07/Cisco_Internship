import React from 'react';

interface ConfidenceMeterProps {
  value: number; // 0 - 100
  label?: string;
}

export const ConfidenceMeter: React.FC<ConfidenceMeterProps> = ({ value, label = 'AI CONFIDENCE' }) => {
  const clamped = Math.max(0, Math.min(100, value));

  // 4 stepped dots based on 25%, 50%, 75%, 90%
  const stepActive = [
    clamped >= 25,
    clamped >= 50,
    clamped >= 75,
    clamped >= 90
  ];

  return (
    <div className="flex flex-col gap-1.5 w-full">
      <div className="flex items-center justify-between">
        <span className="label-caps text-on-surface-variant flex items-center gap-1.5">
          {label}
        </span>
        <div className="flex items-center gap-2">
          {/* Stepped 4-dot indicator */}
          <div className="flex items-center gap-1">
            {stepActive.map((active, i) => (
              <span
                key={i}
                className={`w-1.5 h-1.5 rounded-full transition-colors ${
                  active ? 'bg-primary-container shadow-[0_0_6px_#ff7a33]' : 'bg-surface-container-high border border-white/10'
                }`}
              />
            ))}
          </div>
          <span className="data-mono-bold text-white text-xs">
            {clamped}%
          </span>
        </div>
      </div>

      {/* Gradient progress track */}
      <div className="h-2 w-full bg-surface-container-high rounded-full overflow-hidden p-0.5 border border-white/5">
        <div
          className="h-full rounded-full bg-gradient-to-r from-orange-600 via-primary-container to-primary transition-all duration-700 ease-out shadow-[0_0_12px_rgba(255,122,51,0.5)]"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
};
