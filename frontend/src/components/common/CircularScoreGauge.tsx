import React, { useEffect, useState } from 'react';

interface CircularScoreGaugeProps {
  value: number; // 0 - 100
  label?: string;
  sublabel?: string;
  size?: number;
  strokeWidth?: number;
  color?: 'primary' | 'secondary' | 'tertiary';
}

export const CircularScoreGauge: React.FC<CircularScoreGaugeProps> = ({
  value,
  label = 'VIABILITY',
  sublabel = 'SYSTEM SUPPORT SCORE',
  size = 140,
  strokeWidth = 9,
  color = 'primary'
}) => {
  const [animatedValue, setAnimatedValue] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValue(Math.max(0, Math.min(100, value)));
    }, 100);
    return () => clearTimeout(timer);
  }, [value]);

  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (animatedValue / 100) * circumference;

  const colorMap = {
    primary: {
      stroke: 'url(#orangeGaugeGradient)',
      glow: 'shadow-glow-critical',
      textColor: 'text-primary'
    },
    secondary: {
      stroke: 'url(#cyanGaugeGradient)',
      glow: 'shadow-glow-cyan',
      textColor: 'text-secondary'
    },
    tertiary: {
      stroke: 'url(#emeraldGaugeGradient)',
      glow: 'shadow-glow-emerald',
      textColor: 'text-tertiary'
    }
  };

  const selectedColor = colorMap[color];

  return (
    <div className="flex flex-col items-center justify-center p-3">
      <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <defs>
            <linearGradient id="orangeGaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#ff7a33" />
              <stop offset="100%" stopColor="#ffa170" />
            </linearGradient>
            <linearGradient id="cyanGaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#0284c7" />
              <stop offset="100%" stopColor="#a5e7ff" />
            </linearGradient>
            <linearGradient id="emeraldGaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#059669" />
              <stop offset="100%" stopColor="#4edea3" />
            </linearGradient>
          </defs>

          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="rgba(255, 255, 255, 0.08)"
            strokeWidth={strokeWidth}
            fill="transparent"
          />

          {/* Progress Ring */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={selectedColor.stroke}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 900ms cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="label-caps text-on-surface-variant text-[9px] tracking-wider mb-0.5">
            {label}
          </span>
          <span className="data-mono-bold text-2xl text-white font-bold tracking-tight">
            {animatedValue}
            <span className="text-xs text-primary-container font-mono ml-0.5">%</span>
          </span>
        </div>
      </div>

      {sublabel && (
        <span className="label-caps text-on-surface-variant text-center mt-2 text-[10px]">
          {sublabel}
        </span>
      )}
    </div>
  );
};
