'use client';

import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

// Mock types for the 'Brain' logs
export type LogSource = 'Sphinx' | 'Actian' | 'System';

export interface BrainLog {
  id: string;
  source: LogSource;
  message: string;
  timestamp: Date;
  metadata?: any;
}

interface BrainPanelProps {
  incomingLogs?: BrainLog[];
}

export default function BrainPanel({ incomingLogs = [] }: BrainPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom as new logs stream in from Sphinx and Actian
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [incomingLogs]);

  return (
    <div className="flex flex-col h-full w-full bg-black border border-fuchsia-500/50 rounded-xl overflow-hidden shadow-[0_0_20px_rgba(217,70,239,0.3)] font-mono">
      {/* Header - Cyberpunk / Dark Mode Themed */}
      <div className="bg-fuchsia-900/30 border-b border-fuchsia-500/50 p-3 flex justify-between items-center backdrop-blur-sm">
        <h2 className="text-fuchsia-400 font-bold tracking-widest uppercase flex items-center gap-3">
          <span className="relative flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-fuchsia-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-fuchsia-500 shadow-[0_0_10px_#d946ef]"></span>
          </span>
          The Brain
        </h2>
        <span className="text-xs text-fuchsia-600 tracking-wider">REAL-TIME TELEMETRY</span>
      </div>
      
      {/* Log Feed */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-4 space-y-3 text-sm scrollbar-thin scrollbar-thumb-fuchsia-900 scrollbar-track-transparent bg-grid-white/[0.02]"
      >
        {incomingLogs.length === 0 ? (
          <div className="text-fuchsia-700/50 flex items-center justify-center h-full italic animate-pulse">
            Neural pathways idle. Awaiting vibe prompt...
          </div>
        ) : (
          incomingLogs.map((log) => (
            <motion.div 
              key={log.id}
              initial={{ opacity: 0, x: -15, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              transition={{ duration: 0.3, type: "spring" }}
              className={`p-3 rounded border-l-2 ${
                log.source === 'Sphinx' ? 'border-cyan-500 bg-cyan-900/10 text-cyan-300 shadow-[inset_0_0_15px_rgba(6,182,212,0.1)]' :
                log.source === 'Actian' ? 'border-emerald-500 bg-emerald-900/10 text-emerald-300 shadow-[inset_0_0_15px_rgba(16,185,129,0.1)]' :
                'border-fuchsia-500 bg-fuchsia-900/10 text-fuchsia-300 shadow-[inset_0_0_15px_rgba(217,70,239,0.1)]'
              }`}
            >
              <div className="flex justify-between text-xs opacity-60 mb-1.5 uppercase font-bold tracking-wider">
                <span className="flex items-center gap-1">
                  &rsaquo; [{log.source}]
                </span>
                <span>{log.timestamp.toLocaleTimeString()}</span>
              </div>
              
              <div className="break-words leading-relaxed text-sm">
                {log.message}
              </div>
              
              {log.metadata && (
                <pre className="mt-2 text-xs bg-black/60 p-2 rounded overflow-x-auto text-gray-400 border border-gray-800/50 shadow-inner">
                  {JSON.stringify(log.metadata, null, 2)}
                </pre>
              )}
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
}
