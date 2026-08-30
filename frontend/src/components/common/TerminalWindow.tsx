import React, { useState, useEffect } from 'react';
import { Terminal as TerminalIcon, Copy, Check } from 'lucide-react';

interface TerminalWindowProps {
  hostname?: string;
  title?: string;
  command?: string;
  content: string;
  enableTypewriter?: boolean;
  className?: string;
}

export const TerminalWindow: React.FC<TerminalWindowProps> = ({
  hostname = 'R1#',
  title = 'Cisco IOS Console',
  command,
  content,
  enableTypewriter = false,
  className = ''
}) => {
  const [copied, setCopied] = useState(false);
  const [displayedText, setDisplayedText] = useState(enableTypewriter ? '' : content);

  useEffect(() => {
    if (!enableTypewriter) {
      setDisplayedText(content);
      return;
    }

    setDisplayedText('');
    let idx = 0;
    const speed = 6; // fast typewriter
    const interval = setInterval(() => {
      idx += 12;
      if (idx >= content.length) {
        setDisplayedText(content);
        clearInterval(interval);
      } else {
        setDisplayedText(content.slice(0, idx));
      }
    }, speed);

    return () => clearInterval(interval);
  }, [content, enableTypewriter]);

  const handleCopy = () => {
    navigator.clipboard.writeText(command ? `${hostname} ${command}\n${content}` : content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`glass-terminal rounded-xl overflow-hidden border border-white/10 flex flex-col ${className}`}>
      {/* Chrome Top Bar */}
      <div className="bg-[#0b0d10] px-4 py-2.5 border-b border-white/10 flex items-center justify-between select-none">
        {/* Traffic Light Dots */}
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500/80 border border-red-400/40" />
          <div className="w-3 h-3 rounded-full bg-amber-500/80 border border-amber-400/40" />
          <div className="w-3 h-3 rounded-full bg-emerald-500/80 border border-emerald-400/40" />
          <span className="text-xs text-on-surface-variant font-mono ml-2 flex items-center gap-1.5">
            <TerminalIcon className="w-3.5 h-3.5 text-primary-container" />
            {title}
          </span>
        </div>

        {/* Copy / Host Action */}
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-mono text-outline uppercase tracking-wider hidden sm:inline">
            VT100 / UTF-8
          </span>
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-white/10 text-on-surface-variant hover:text-white transition-colors flex items-center gap-1 text-xs font-mono"
            aria-label="Copy terminal text"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[10px] text-emerald-400">COPIED</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span className="text-[10px]">COPY</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Monospace Body */}
      <div className="p-4 font-mono text-xs leading-relaxed overflow-x-auto text-[#b6ebff] max-h-[380px] overflow-y-auto">
        {command && (
          <div className="mb-2 flex items-center gap-2 text-white font-semibold">
            <span className="text-primary">{hostname}</span>
            <span className="text-primary-container">{command}</span>
          </div>
        )}
        <pre className="font-mono text-[11.5px] leading-5 whitespace-pre font-normal text-[#c4c6d0]">
          {displayedText}
          <span className="inline-block w-2 h-4 ml-0.5 bg-primary-container animate-pulse align-middle" />
        </pre>
      </div>
    </div>
  );
};
