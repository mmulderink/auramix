'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import BrainPanel, { BrainLog } from '@/components/BrainPanel';

const BACKEND = 'http://localhost:8001';
const CROSSFADE_DURATION = 4000;

interface Track {
  track: string;
  bpm: number;
  key: string;
  genre: string;
  distance: number;
  track_path?: string;
}

function VinylDeck({
  label,
  track,
  isPlaying,
  color,
  volume,
  onPlayPause,
}: {
  label: string;
  track: Track | null;
  isPlaying: boolean;
  color: 'blue' | 'fuchsia';
  volume: number;
  onPlayPause?: () => void;
}) {
  const c = color === 'blue'
    ? { border: 'border-blue-500/60', glow: 'shadow-[0_0_40px_rgba(59,130,246,0.3)]', ring: 'border-blue-400', dot: 'bg-blue-400', text: 'text-blue-400', label: 'text-blue-300', bg: 'bg-blue-500/5', btn: 'bg-blue-600 hover:bg-blue-500', btnA: 'bg-blue-900/60 text-blue-300 hover:bg-blue-900', bar: 'bg-blue-500', lbl: 'bg-blue-900/80' }
    : { border: 'border-fuchsia-500/60', glow: 'shadow-[0_0_40px_rgba(217,70,239,0.3)]', ring: 'border-fuchsia-400', dot: 'bg-fuchsia-400 shadow-[0_0_10px_#d946ef]', text: 'text-fuchsia-400', label: 'text-fuchsia-300', bg: 'bg-fuchsia-500/5', btn: 'bg-fuchsia-600 hover:bg-fuchsia-500', btnA: 'bg-fuchsia-900/60 text-fuchsia-300 hover:bg-fuchsia-900', bar: 'bg-fuchsia-500', lbl: 'bg-fuchsia-900/80' };

  return (
    <div className={`bg-gray-900 border ${c.border} rounded-xl p-6 flex flex-col items-center justify-center relative overflow-hidden ${isPlaying ? c.glow : ''} transition-shadow duration-1000`}>
      <div className={`absolute inset-0 ${c.bg}`} />

      {/* Spinning vinyl */}
      <div
        className={`w-44 h-44 rounded-full border-4 ${c.ring} flex items-center justify-center mx-auto z-10 mb-4 relative bg-gray-950`}
        style={isPlaying ? { animation: 'spin 2s linear infinite' } : {}}
      >
        <div className="absolute w-36 h-36 rounded-full border border-gray-700 opacity-50" />
        <div className="absolute w-28 h-28 rounded-full border border-gray-700 opacity-40" />
        <div className="absolute w-20 h-20 rounded-full border border-gray-700 opacity-30" />
        <div className={`w-14 h-14 rounded-full ${c.lbl} flex items-center justify-center`}>
          <div className={`w-3 h-3 ${c.dot} rounded-full`} />
        </div>
      </div>

      <h3 className={`text-sm font-bold uppercase tracking-widest z-10 ${c.label}`}>{label}</h3>

      {track ? (
        <div className="mt-2 text-center z-10 w-full px-2">
          <p className={`${c.text} font-bold text-sm truncate`} title={track.track}>
            {track.track.replace('.mp3', '')}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {Math.round(track.bpm)} BPM · {track.key} · {track.genre}
          </p>

          {/* Volume bar */}
          <div className="mt-2 flex items-center gap-2 justify-center">
            <div className="h-1 flex-1 bg-gray-800 rounded-full overflow-hidden">
              <div className={`h-full rounded-full transition-all duration-300 ${c.bar}`} style={{ width: `${volume * 100}%` }} />
            </div>
            <span className="text-xs text-gray-600 w-8 text-right">{Math.round(volume * 100)}%</span>
          </div>

          {/* Play/Pause button */}
          {onPlayPause && (
            <button
              onClick={onPlayPause}
              className={`mt-3 px-5 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest transition-all active:scale-95 text-white ${isPlaying ? c.btnA : c.btn}`}
            >
              {isPlaying ? '⏸ Pause' : '▶ Play'}
            </button>
          )}
        </div>
      ) : (
        <p className="text-xs text-gray-600 mt-2 z-10">No track loaded</p>
      )}

      {/* Equalizer bars */}
      {isPlaying && (
        <div className="mt-3 flex gap-1 z-10">
          {[0.4, 0.6, 0.5, 0.7, 0.45].map((dur, i) => (
            <div
              key={i}
              className={`w-1 rounded-full ${c.bar}`}
              style={{ height: '16px', animation: `bounce ${dur}s ease-in-out infinite alternate` }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function Home() {
  const [logs, setLogs] = useState<BrainLog[]>([]);
  const [prompt, setPrompt] = useState('');
  const [vibeWeight, setVibeWeight] = useState(50);
  const [deckA, setDeckA] = useState<Track | null>(null);
  const [deckB, setDeckB] = useState<Track | null>(null);
  const [mixHistory, setMixHistory] = useState<any[]>([]);
  const [folderPath, setFolderPath] = useState('/Users/mm/Desktop/gt_hack/v4_dj/backend/audio_samples');
  const [isIngesting, setIsIngesting] = useState(false);
  const [ingestProgress, setIngestProgress] = useState({ total: 0, current: 0, current_song: '' });
  const [isFading, setIsFading] = useState(false);
  const [playingA, setPlayingA] = useState(false);
  const [playingB, setPlayingB] = useState(false);
  const [volA, setVolA] = useState(1);
  const [volB, setVolB] = useState(0);

  const audioA = useRef<HTMLAudioElement | null>(null);
  const audioB = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioA.current = new Audio();
    audioB.current = new Audio();
    audioA.current.volume = 1;
    audioB.current.volume = 0;
    return () => { audioA.current?.pause(); audioB.current?.pause(); };
  }, []);

  useEffect(() => { if (audioA.current) audioA.current.volume = volA; }, [volA]);
  useEffect(() => { if (audioB.current) audioB.current.volume = volB; }, [volB]);

  const getAudioUrl = useCallback((track: Track) => {
    const path = track.track_path || track.track;
    return `${BACKEND}/api/audio?path=${encodeURIComponent(path)}`;
  }, []);

  const handlePlayPauseA = useCallback(() => {
    if (!audioA.current || !deckA) return;
    if (playingA) {
      audioA.current.pause();
      setPlayingA(false);
    } else {
      if (!audioA.current.src || audioA.current.src === window.location.href) {
        audioA.current.src = getAudioUrl(deckA);
        audioA.current.load();
      }
      audioA.current.play().then(() => setPlayingA(true)).catch(e => console.warn('Play error A:', e));
    }
  }, [deckA, playingA, getAudioUrl]);

  const handlePlayPauseB = useCallback(() => {
    if (!audioB.current || !deckB) return;
    if (playingB) {
      audioB.current.pause();
      setPlayingB(false);
    } else {
      if (!audioB.current.src || audioB.current.src === window.location.href) {
        audioB.current.src = getAudioUrl(deckB);
        audioB.current.load();
      }
      audioB.current.play().then(() => setPlayingB(true)).catch(e => console.warn('Play error B:', e));
    }
  }, [deckB, playingB, getAudioUrl]);

  const handleCrossfade = useCallback(() => {
    if (!deckB || isFading) return;
    setIsFading(true);
    const steps = 40;
    const stepDuration = CROSSFADE_DURATION / steps;
    let step = 0;

    // Start B — user-triggered so autoplay is allowed
    if (audioB.current) {
      if (!audioB.current.src || audioB.current.src === window.location.href) {
        audioB.current.src = getAudioUrl(deckB);
        audioB.current.load();
      }
      audioB.current.play().then(() => setPlayingB(true)).catch(e => console.warn('Crossfade B error:', e));
    }

    const fade = setInterval(() => {
      step++;
      const p = step / steps;
      setVolA(Math.max(0, 1 - p));
      setVolB(Math.min(1, p));

      if (step >= steps) {
        clearInterval(fade);
        audioA.current?.pause();
        // Swap refs
        const tmpEl = audioA.current;
        audioA.current = audioB.current;
        audioB.current = tmpEl;
        if (audioB.current) { audioB.current.pause(); audioB.current.volume = 0; audioB.current.src = ''; }
        setDeckA(deckB);
        setDeckB(null);
        setVolA(1);
        setVolB(0);
        setPlayingA(true);
        setPlayingB(false);
        setIsFading(false);
      }
    }, stepDuration);
  }, [deckB, isFading, getAudioUrl]);

  const addLog = (source: 'Sphinx' | 'Actian' | 'System', message: string, metadata?: any) => {
    setLogs(prev => [...prev, { id: Date.now().toString() + Math.random(), source, message, timestamp: new Date(), metadata } as BrainLog]);
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${BACKEND}/api/history`);
      const data = await res.json();
      if (data.history) setMixHistory(data.history);
    } catch { /* silent */ }
  };

  useEffect(() => { fetchHistory(); }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isIngesting) {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${BACKEND}/api/ingest/status`);
          const data = await res.json();
          setIngestProgress({ total: data.total, current: data.current, current_song: data.current_song });
          if (!data.is_ingesting && data.total > 0 && data.current === data.total) setIsIngesting(false);
        } catch { /* silent */ }
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isIngesting]);

  const handleIngest = async () => {
    if (!folderPath) return;
    setIsIngesting(true);
    addLog('System', `Initiating ingestion for folder: ${folderPath}`);
    try {
      const res = await fetch(`${BACKEND}/api/ingest`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ directory_path: folderPath }) });
      const data = await res.json();
      addLog('System', data.message || 'Ingestion started.', data);
    } catch { addLog('System', 'Failed to trigger ingestion.'); setIsIngesting(false); }
  };

  const handleExecute = async () => {
    addLog('System', `Initiating transition sequence for prompt: "${prompt}"`);
    try {
      const res = await fetch(`${BACKEND}/api/transition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, vibe_weight: vibeWeight }),
      });
      const data = await res.json();
      if (data.sphinx_analysis) addLog('Sphinx', 'Sphinx AI returned deconstructed narrative reasoning.', data.sphinx_analysis);
      if (data.suggested_tracks?.length > 0) {
        const top = data.suggested_tracks[0];
        addLog('Actian', 'VectorDB Query completed. Best matches found.', data.suggested_tracks);
        if (!deckA) {
          setDeckA(top);
          setVolA(1);
          if (audioA.current) {
            audioA.current.src = getAudioUrl(top);
            audioA.current.load();
            // EXECUTE is a user click — autoplay is allowed
            audioA.current.play().then(() => setPlayingA(true)).catch(e => console.warn('Autoplay blocked, use ▶ Play button:', e));
          }
        } else {
          setDeckB(top);
          setVolB(0);
          if (audioB.current) {
            audioB.current.src = getAudioUrl(top);
            audioB.current.load();
          }
        }
      }
      fetchHistory();
    } catch { addLog('System', 'Failed to contact backend API. Make sure it is running on port 8001.'); }
  };

  return (
    <main className="min-h-screen bg-gray-950 p-6 flex flex-col gap-5 text-white font-sans">
      <style>{`
        @keyframes bounce { from { transform: scaleY(0.3); } to { transform: scaleY(1); } }
      `}</style>

      <header className="flex justify-between items-center text-fuchsia-500 border-b border-fuchsia-900/50 pb-4">
        <h1 className="text-3xl font-bold tracking-tighter uppercase flex items-center gap-3">◈ AuraMix</h1>
        <em className="opacity-60 text-sm tracking-widest">Narrative DJ Mode Active</em>
      </header>

      {/* Folder Row */}
      <div className="flex flex-col gap-2 bg-gray-900 border border-emerald-600/30 p-3 rounded-lg">
        <div className="flex gap-4 items-center">
          <span className="text-emerald-500 font-bold uppercase tracking-widest text-xs whitespace-nowrap">Music Folder:</span>
          <input type="text" className="flex-1 bg-transparent text-white focus:outline-none placeholder:text-gray-600 truncate text-sm" value={folderPath} onChange={e => setFolderPath(e.target.value)} />
          <button onClick={handleIngest} disabled={isIngesting} className={`bg-emerald-800 hover:bg-emerald-700 text-white font-bold py-2 px-6 rounded-md transition-all active:scale-95 whitespace-nowrap ${isIngesting ? 'opacity-50 cursor-not-allowed' : ''}`}>
            {isIngesting ? 'INGESTING...' : 'LINK & INGEST'}
          </button>
        </div>
        {isIngesting && (
          <div className="mt-1 text-xs flex flex-col gap-1">
            <div className="flex justify-between text-emerald-400">
              <span className="truncate pr-4">Processing: <span className="font-bold text-white">{ingestProgress.current_song}</span></span>
              <span className="font-mono">{ingestProgress.current} / {ingestProgress.total || '?'}</span>
            </div>
            <div className="w-full bg-black/50 rounded-full h-1.5 overflow-hidden">
              <div className="bg-emerald-500 h-1.5 transition-all duration-500" style={{ width: `${ingestProgress.total > 0 ? (ingestProgress.current / ingestProgress.total) * 100 : 0}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Prompt Row */}
      <div className="flex gap-4 items-center bg-gray-900 border border-fuchsia-600/30 p-3 rounded-lg">
        <input
          type="text"
          placeholder="Enter Vibe Prompt (e.g., 'From a rainy jazz club to a high-speed neon chase')"
          className="flex-1 bg-transparent text-white focus:outline-none placeholder:text-gray-600"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleExecute()}
        />
        <div className="flex items-center gap-2 border-l border-fuchsia-900/50 pl-4 w-56">
          <span className="text-xs text-gray-400">Dark</span>
          <input type="range" min="0" max="100" value={vibeWeight} onChange={e => setVibeWeight(parseInt(e.target.value))} className="w-full accent-fuchsia-500" />
          <span className="text-xs text-fuchsia-400 font-bold">Energy</span>
        </div>
        <button onClick={handleExecute} className="bg-fuchsia-800 hover:bg-fuchsia-700 text-white font-bold py-2 px-6 rounded-md transition-all active:scale-95 shadow-[0_0_15px_rgba(217,70,239,0.4)] whitespace-nowrap">
          EXECUTE
        </button>
      </div>

      <div className="flex-1 grid grid-cols-12 gap-5 min-h-[500px]">
        <div className="col-span-8 flex flex-col gap-5">
          {/* Decks */}
          <div className="grid grid-cols-2 gap-4">
            <VinylDeck label="Deck A · Playing" track={deckA} isPlaying={playingA} color="blue" volume={volA} onPlayPause={deckA ? handlePlayPauseA : undefined} />
            <VinylDeck label="Deck B · Cued" track={deckB} isPlaying={playingB} color="fuchsia" volume={volB} onPlayPause={deckB ? handlePlayPauseB : undefined} />
          </div>

          {/* Crossfader */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-center gap-6">
            <div className="flex flex-col items-center gap-1 flex-1">
              <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Crossfader</div>
              <div className="w-full flex items-center gap-3">
                <span className="text-xs text-blue-400 font-bold w-6 text-right">{Math.round(volA * 100)}</span>
                <div className="flex-1 relative h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div className="absolute left-0 top-0 h-full bg-blue-500 rounded-full transition-all duration-100" style={{ width: `${volA * 100}%` }} />
                  <div className="absolute right-0 top-0 h-full bg-fuchsia-500 rounded-full transition-all duration-100" style={{ width: `${volB * 100}%` }} />
                </div>
                <span className="text-xs text-fuchsia-400 font-bold w-6">{Math.round(volB * 100)}</span>
              </div>
            </div>
            <button
              onClick={handleCrossfade}
              disabled={!deckB || isFading}
              className={`px-8 py-3 rounded-lg font-bold uppercase tracking-widest text-sm transition-all active:scale-95 ${deckB && !isFading ? 'bg-gradient-to-r from-blue-700 to-fuchsia-700 hover:from-blue-600 hover:to-fuchsia-600 shadow-[0_0_20px_rgba(217,70,239,0.3)] text-white' : 'bg-gray-800 text-gray-600 cursor-not-allowed'}`}
            >
              {isFading ? '⟳ Fading...' : '⇌ Fade Now'}
            </button>
          </div>

          {/* Mix History */}
          <div className="flex-1 bg-gray-900 border border-gray-800 rounded-xl p-4 overflow-hidden flex flex-col">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-3 border-b border-gray-800 pb-2">Neon DB Mix History</h3>
            <div className="flex-1 overflow-y-auto space-y-2">
              {mixHistory.map(entry => (
                <div key={entry.id} className="text-xs bg-gray-950 p-3 rounded border border-gray-800/60 flex flex-col gap-1">
                  <div className="flex justify-between text-gray-500">
                    <span>#{entry.id} · {entry.created_at ? new Date(entry.created_at).toLocaleTimeString() : ''}</span>
                    {entry.actian_search_results?.[0] && <span className="text-fuchsia-400">{entry.actian_search_results[0].track?.replace('.mp3', '')}</span>}
                  </div>
                  <div className="font-mono text-gray-300">"{entry.prompt}"</div>
                </div>
              ))}
              {mixHistory.length === 0 && <p className="text-xs text-gray-600 italic text-center mt-4">No history recorded yet.</p>}
            </div>
          </div>
        </div>

        {/* Right: Log Panel */}
        <div className="col-span-4 max-h-[700px]">
          <BrainPanel incomingLogs={logs} />
        </div>
      </div>
    </main>
  );
}
