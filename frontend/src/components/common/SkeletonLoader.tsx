import React from 'react';

interface SkeletonProps {
  className?: string;
  count?: number;
}

export const SkeletonLoader: React.FC<SkeletonProps> = ({ className = 'h-6 w-full', count = 1 }) => {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          role="status"
          aria-label="Loading content..."
          className={`skeleton-shimmer rounded-xl bg-white/[0.04] border border-white/[0.04] ${className}`}
        />
      ))}
    </>
  );
};
