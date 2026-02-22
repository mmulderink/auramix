'use client';

import React, { useEffect, useRef, useState, useCallback } from 'react';

const BACKEND = 'http://localhost:8001';

function emotionColor(emotion: string) {
    switch (emotion) {
        case 'happy': return '#d8923a';
        case 'excited': return '#f5a524';
        case 'sad': return '#7b6b8f';
        case 'surprised': return '#c97c5d';
        case 'concerned': return '#8d6e63';
        case 'thinking': return '#b08259';
        default: return '#9b6b3c';
    }
}

interface RatDJProps {
    djEvent?: { type: string; detail: string; timestamp: number } | null;
}

export default function RatDJ({ djEvent }: RatDJProps) {
    const [emotion, setEmotion] = useState('neutral');
    const [animation, setAnimation] = useState<string | null>(null);
    const [ratMessage, setRatMessage] = useState("Yo! I'm DJ Rat 🐀🎧 — drop a vibe and let's mix!");
    const [isThinking, setIsThinking] = useState(false);
    const [chatInput, setChatInput] = useState('');
    const [beatBounce, setBeatBounce] = useState(0);

    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const animationRef = useRef<number | null>(null);
    const lastEventRef = useRef<number>(0);

    // Send message to rat API
    const sendToRat = useCallback(async (message: string) => {
        setIsThinking(true);
        try {
            const res = await fetch(`${BACKEND}/api/rat/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message }),
            });
            const data = await res.json();
            setRatMessage(data.message || '');
            setEmotion(data.emotion || 'neutral');
            setAnimation(data.emotion === 'excited' ? 'wiggle' : null);
            // Clear animation after a few seconds
            setTimeout(() => setAnimation(null), 3000);
        } catch {
            setRatMessage("My headphones glitched! Backend might be loading... 🐀🔧");
            setEmotion('concerned');
        }
        setIsThinking(false);
    }, []);

    // React to DJ events
    useEffect(() => {
        if (!djEvent || djEvent.timestamp === lastEventRef.current) return;
        lastEventRef.current = djEvent.timestamp;
        sendToRat(`[DJ EVENT: ${djEvent.type}] ${djEvent.detail}`);
    }, [djEvent, sendToRat]);

    // Beat bounce
    useEffect(() => {
        const interval = setInterval(() => {
            setBeatBounce(prev => (prev + 1) % 4);
        }, 500);
        return () => clearInterval(interval);
    }, []);

    // Chat handler
    const handleChat = () => {
        if (!chatInput.trim()) return;
        sendToRat(chatInput);
        setChatInput('');
    };

    // Canvas animation — rat with DJ headphones
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const draw = (time: number) => {
            const t = time / 1000;
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2 + 10;
            const bob = Math.sin(t * 3.0) * 8;
            const wiggle = animation ? Math.sin(t * 10.0) * 10 : Math.sin(t * 2) * 3;
            const noseWiggle = Math.sin(t * 16.0) * 6;

            // Beat rings behind rat
            for (let i = 0; i < 3; i++) {
                const radius = 90 + i * 20 + Math.sin(t * 4 + i) * 5;
                const alpha = 0.1 - i * 0.025;
                ctx.strokeStyle = `rgba(217, 70, 239, ${alpha})`;
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
                ctx.stroke();
            }

            ctx.save();
            ctx.translate(centerX, centerY + bob);
            ctx.rotate(wiggle * (Math.PI / 180));

            // Body
            const bodyColor = emotionColor(emotion);
            ctx.fillStyle = bodyColor;
            ctx.shadowBlur = 20;
            ctx.shadowColor = bodyColor;
            ctx.beginPath();
            ctx.ellipse(0, 0, 80, 65, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.strokeStyle = 'rgba(255,255,255,0.08)';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Ears
            ctx.fillStyle = '#2b1f1b';
            ctx.beginPath();
            ctx.ellipse(-45, -55, 25, 18, -0.3, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(45, -55, 25, 18, 0.3, 0, Math.PI * 2);
            ctx.fill();
            // Inner ears
            ctx.fillStyle = '#f7b0b0';
            ctx.beginPath();
            ctx.ellipse(-45, -55, 14, 10, -0.3, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(45, -55, 14, 10, 0.3, 0, Math.PI * 2);
            ctx.fill();

            // Headphone band
            ctx.strokeStyle = '#333';
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.arc(0, -55, 52, Math.PI * 0.85, Math.PI * 0.15, true);
            ctx.stroke();
            // LED strip on band
            ctx.strokeStyle = '#d946ef';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(0, -55, 50, Math.PI * 0.88, Math.PI * 0.12, true);
            ctx.stroke();

            // Headphone cups
            for (const side of [-1, 1]) {
                ctx.fillStyle = '#1a1a2e';
                ctx.beginPath();
                ctx.ellipse(side * 52, -40, 16, 20, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#d946ef';
                ctx.lineWidth = 2.5;
                ctx.stroke();
                // Cup inner glow
                ctx.fillStyle = 'rgba(217,70,239,0.15)';
                ctx.beginPath();
                ctx.ellipse(side * 52, -40, 10, 13, 0, 0, Math.PI * 2);
                ctx.fill();
            }

            // Eyes
            const blinkCycle = Math.sin(t * 0.5);
            const eyeH = blinkCycle > 0.95 ? 2 : 12;
            ctx.fillStyle = '#121212';
            ctx.beginPath();
            ctx.ellipse(-22, -15, 8, eyeH, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.ellipse(22, -15, 8, eyeH, 0, 0, Math.PI * 2);
            ctx.fill();
            // Eye shine
            if (eyeH > 2) {
                ctx.fillStyle = '#fff';
                ctx.beginPath();
                ctx.ellipse(-19, -19, 3, 3, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.beginPath();
                ctx.ellipse(25, -19, 3, 3, 0, 0, Math.PI * 2);
                ctx.fill();
            }

            // Nose
            ctx.fillStyle = '#f7b0b0';
            ctx.save();
            ctx.translate(0, 15);
            ctx.rotate(noseWiggle * (Math.PI / 180));
            ctx.beginPath();
            ctx.ellipse(0, 0, 12, 8, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            // Mouth
            ctx.strokeStyle = '#2b1f1b';
            ctx.lineWidth = 2;
            ctx.beginPath();
            if (emotion === 'happy' || emotion === 'excited') {
                ctx.arc(0, 20, 15, 0.1, Math.PI - 0.1);
            } else {
                ctx.arc(0, 25, 10, 0.3, Math.PI - 0.3);
            }
            ctx.stroke();

            // Whiskers
            ctx.strokeStyle = 'rgba(255,255,255,0.25)';
            ctx.lineWidth = 1.5;
            for (const side of [-1, 1]) {
                for (const angle of [-0.2, 0, 0.2]) {
                    ctx.beginPath();
                    ctx.moveTo(side * 25, 10);
                    ctx.lineTo(side * 70, 10 + angle * 80 + Math.sin(t * 4 + angle) * 3);
                    ctx.stroke();
                }
            }

            ctx.restore();

            animationRef.current = requestAnimationFrame(draw);
        };

        animationRef.current = requestAnimationFrame(draw);
        return () => {
            if (animationRef.current) cancelAnimationFrame(animationRef.current);
        };
    }, [emotion, animation]);

    return (
        <div style={{
            background: 'linear-gradient(135deg, rgba(15,10,25,0.95), rgba(25,15,40,0.95))',
            border: '1px solid rgba(217, 70, 239, 0.3)',
            borderRadius: '16px',
            padding: '16px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '10px',
            position: 'relative',
            overflow: 'hidden',
            boxShadow: '0 0 30px rgba(217, 70, 239, 0.12)',
        }}>
            {/* Background pulse */}
            <div style={{
                position: 'absolute',
                inset: 0,
                background: 'radial-gradient(circle at center, rgba(217,70,239,0.04) 0%, transparent 70%)',
                animation: 'ratPulse 3s ease-in-out infinite',
                pointerEvents: 'none',
            }} />

            {/* Header */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                width: '100%',
                zIndex: 1,
            }}>
                <h3 style={{
                    margin: 0,
                    fontSize: '13px',
                    fontWeight: 800,
                    textTransform: 'uppercase',
                    letterSpacing: '0.15em',
                    background: 'linear-gradient(90deg, #d946ef, #f59e0b)',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                }}>
                    🐀 DJ RAT
                </h3>
                {/* Beat dots */}
                <div style={{ display: 'flex', gap: '3px' }}>
                    {[0, 1, 2, 3].map(i => (
                        <div key={i} style={{
                            width: '3px',
                            height: i === beatBounce ? '14px' : '5px',
                            borderRadius: '2px',
                            background: i === beatBounce ? '#d946ef' : 'rgba(217,70,239,0.25)',
                            transition: 'height 0.15s ease',
                        }} />
                    ))}
                </div>
            </div>

            {/* Rat Canvas */}
            <canvas
                ref={canvasRef}
                width={260}
                height={200}
                style={{
                    borderRadius: '12px',
                    zIndex: 1,
                }}
            />

            {/* Speech bubble */}
            <div style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(217,70,239,0.15)',
                borderRadius: '12px',
                padding: '10px 14px',
                fontSize: '12px',
                color: '#e2e8f0',
                lineHeight: 1.4,
                width: '100%',
                zIndex: 1,
                minHeight: '20px',
            }}>
                {isThinking ? (
                    <span style={{ color: '#d946ef', fontStyle: 'italic' }}>🎵 Vibing...</span>
                ) : (
                    <span>{ratMessage}</span>
                )}
            </div>

            {/* Emotion + mood */}
            <div style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'center',
                zIndex: 1,
                width: '100%',
            }}>
                <span style={{ fontSize: '9px', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                    Mood:
                </span>
                <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    color: emotionColor(emotion),
                    textTransform: 'capitalize',
                }}>{emotion}</span>
            </div>

            {/* Chat input */}
            <div style={{
                display: 'flex',
                gap: '6px',
                width: '100%',
                zIndex: 1,
            }}>
                <input
                    type="text"
                    placeholder="Talk to DJ Rat..."
                    value={chatInput}
                    onChange={e => setChatInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleChat()}
                    style={{
                        flex: 1,
                        background: 'rgba(255,255,255,0.05)',
                        border: '1px solid rgba(217,70,239,0.15)',
                        borderRadius: '8px',
                        padding: '7px 10px',
                        color: '#fff',
                        fontSize: '11px',
                        outline: 'none',
                    }}
                />
                <button
                    onClick={handleChat}
                    style={{
                        background: 'linear-gradient(135deg, #d946ef, #9333ea)',
                        border: 'none',
                        borderRadius: '8px',
                        padding: '7px 12px',
                        color: '#fff',
                        fontSize: '10px',
                        fontWeight: 700,
                        cursor: 'pointer',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                    }}
                >
                    Send
                </button>
            </div>

            <style>{`
        @keyframes ratPulse {
          0%, 100% { opacity: 0.5; }
          50% { opacity: 1; }
        }
      `}</style>
        </div>
    );
}
