import { useEffect, useMemo, useRef, useState } from "react";

type ChatItem = {
  role: "user" | "assistant" | "status" | "error";
  text: string;
  timestamp: string;
};

type AssistantPayload = {
  message: string;
  emotion: string;
  intensity: string;
  animation: string | null;
};

type UncAIItem = {
  id: string;
  source: string;
  sender: string;
  subject: string;
  content: string;
};

type UncAIStats = {
  total: number;
  correct: number;
  incorrect: number;
  accuracy: number;
  current_streak: number;
  best_streak: number;
  avg_reasoning_score: number | null;
  by_type: Record<string, { total: number; correct: number; accuracy: number }>;
};

type UncAIResult = {
  correct: boolean;
  actual_is_scam: boolean;
  scam_type: string | null;
  feedback: string;
  reveal: {
    id: string;
    source: string;
    sender: string;
    subject: string;
    content: string;
    scam_type: string | null;
    is_scam: boolean;
    tactics: string[];
    severity: number;
    red_flags: string[];
  };
  reasoning: {
    score: number | null;
    feedback: string | null;
    red_flags_mentioned: string[];
  };
  stats: UncAIStats;
};

type SpeechRecognitionResultLike = {
  isFinal: boolean;
  0: {
    transcript: string;
  };
};

type SpeechRecognitionEventLike = {
  results: {
    0?: SpeechRecognitionResultLike;
  };
};

type SpeechRecognitionLike = {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};

type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

type WindowWithSpeechRecognition = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor;
  webkitSpeechRecognition?: SpeechRecognitionConstructor;
};

const DEFAULT_WS_URL =
  (import.meta as ImportMeta & { env?: { VITE_WS_URL?: string } }).env?.VITE_WS_URL ||
  "ws://localhost:8000/ws";

const DEFAULT_API_URL =
  (import.meta as ImportMeta & { env?: { VITE_API_URL?: string } }).env?.VITE_API_URL ||
  "http://localhost:8000";

export default function App() {
  const [connected, setConnected] = useState(false);
  const [chatLog, setChatLog] = useState<ChatItem[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [assistantState, setAssistantState] = useState<AssistantPayload>({
    message: "",
    emotion: "neutral",
    intensity: "medium",
    animation: null
  });
  const [frameData, setFrameData] = useState<string | null>(null);
  const [frameSize, setFrameSize] = useState({ width: 520, height: 360 });
  const [hasFrames, setHasFrames] = useState(false);
  const [uncaiItem, setUncaiItem] = useState<UncAIItem | null>(null);
  const [uncaiResult, setUncaiResult] = useState<UncAIResult | null>(null);
  const [uncaiStats, setUncaiStats] = useState<UncAIStats | null>(null);
  const [uncaiExplanation, setUncaiExplanation] = useState("");
  const [uncaiStatus, setUncaiStatus] = useState<string | null>(null);
  const [uncaiBusy, setUncaiBusy] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationRef = useRef<number | null>(null);

  const wsUrl = useMemo(() => DEFAULT_WS_URL, []);
  const apiBase = useMemo(() => DEFAULT_API_URL, []);
  const uncaiUserId = "default";

  useEffect(() => {
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.addEventListener("open", () => {
      setConnected(true);
      appendLog("status", `Connected to ${wsUrl}`);
    });

    ws.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "assistant") {
          setAssistantState({
            message: data.message || "",
            emotion: data.emotion || "neutral",
            intensity: data.intensity || "medium",
            animation: data.animation || null
          });
          appendLog("assistant", data.message || "");
        } else if (data.type === "frame") {
          if (typeof data.data === "string") {
            setFrameData(data.data);
            setHasFrames(true);
          }
          if (typeof data.width === "number" && typeof data.height === "number") {
            setFrameSize({ width: data.width, height: data.height });
          }
        } else if (data.type === "status") {
          appendLog("status", data.message || "status");
        } else if (data.type === "error") {
          appendLog("error", data.message || "error");
        }
      } catch (err) {
        appendLog("error", "Failed to parse server message.");
      }
    });

    ws.addEventListener("close", () => {
      setConnected(false);
      appendLog("status", "Disconnected from server.");
    });

    return () => {
      ws.close();
    };
  }, [wsUrl]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${apiBase}/api/uncai/stats?user_id=${uncaiUserId}`);
        if (!response.ok) {
          return;
        }
        const data = await response.json();
        if (data?.success && data?.stats) {
          setUncaiStats(data.stats as UncAIStats);
        }
      } catch (err) {
        return;
      }
    };
    fetchStats();
  }, [apiBase]);

  useEffect(() => {
    const SpeechRecognitionImpl =
      (window as WindowWithSpeechRecognition).SpeechRecognition ||
      (window as WindowWithSpeechRecognition).webkitSpeechRecognition;

    if (!SpeechRecognitionImpl) {
      appendLog("error", "SpeechRecognition is not supported in this browser.");
      return;
    }

    const recognition = new SpeechRecognitionImpl();
    recognition.lang = "en-US";
    recognition.interimResults = true;
    recognition.continuous = false;

    recognition.onresult = (event) => {
      const result = event.results[0];
      if (!result) {
        return;
      }
      const transcript = result[0].transcript.trim();
      setInputValue(transcript);
      if (result.isFinal) {
        sendMessage(transcript);
        setIsListening(false);
      }
    };

    recognition.onerror = () => {
      setIsListening(false);
      appendLog("error", "Speech recognition error.");
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
  }, []);

  useEffect(() => {
    if (hasFrames) {
      return;
    }
    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    const draw = (time: number) => {
      const t = time / 1000;
      const { emotion, animation } = assistantState;

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = "#1b1a1f";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2 - 20;
      const bob = Math.sin(t * 2.0) * 6;
      const wiggle = animation ? Math.sin(t * 10.0) * 8 : 0;
      const noseWiggle = animation ? Math.sin(t * 16.0) * 6 : 0;

      ctx.save();
      ctx.translate(centerX, centerY + bob);
      ctx.rotate(wiggle * (Math.PI / 180));

      ctx.fillStyle = emotionColor(emotion);
      ctx.beginPath();
      ctx.ellipse(0, 0, 120, 100, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#2b1f1b";
      ctx.beginPath();
      ctx.ellipse(-60, -80, 35, 25, -0.3, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(60, -80, 35, 25, 0.3, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#121212";
      ctx.beginPath();
      ctx.ellipse(-35, -20, 10, 16, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(35, -20, 10, 16, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = "#f7b0b0";
      ctx.save();
      ctx.translate(0, 30);
      ctx.rotate(noseWiggle * (Math.PI / 180));
      ctx.beginPath();
      ctx.ellipse(0, 0, 18, 12, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      ctx.restore();

      animationRef.current = requestAnimationFrame(draw);
    };

    animationRef.current = requestAnimationFrame(draw);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [assistantState, hasFrames]);

  useEffect(() => {
    if (!frameData) {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) {
      return;
    }

    if (canvas.width !== frameSize.width || canvas.height !== frameSize.height) {
      canvas.width = frameSize.width;
      canvas.height = frameSize.height;
    }

    const ctx = canvas.getContext("2d");
    if (!ctx) {
      return;
    }

    const img = new Image();
    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    };
    img.src = `data:image/png;base64,${frameData}`;
  }, [frameData, frameSize]);

  const appendLog = (role: ChatItem["role"], text: string) => {
    if (!text) {
      return;
    }
    const timestamp = new Date().toLocaleTimeString();
    setChatLog((prev) => [...prev, { role, text, timestamp }]);
  };

  const sendMessage = (text: string) => {
    if (!text.trim()) {
      return;
    }

    appendLog("user", text);
    setInputValue("");

    wsRef.current?.send(
      JSON.stringify({
        type: "user_text",
        text
      })
    );
  };

  const toggleListening = () => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      return;
    }

    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  const startPractice = async () => {
    setUncaiBusy(true);
    setUncaiStatus(null);
    try {
      const response = await fetch(`${apiBase}/api/uncai/practice`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const data = await response.json();
      if (!data?.success) {
        setUncaiStatus(data?.error || "No practice items available.");
        setUncaiItem(null);
        return;
      }
      setUncaiItem(data.item as UncAIItem);
      setUncaiResult(null);
      setUncaiExplanation("");
    } catch (err) {
      setUncaiStatus("Failed to load a practice item.");
    } finally {
      setUncaiBusy(false);
    }
  };

  const submitPractice = async (answer: "scam" | "legit") => {
    if (!uncaiItem) {
      return;
    }
    setUncaiBusy(true);
    setUncaiStatus(null);
    try {
      const response = await fetch(`${apiBase}/api/uncai/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          item_id: uncaiItem.id,
          answer,
          explanation: uncaiExplanation,
          user_id: uncaiUserId
        })
      });
      const data = await response.json();
      if (!data?.success) {
        setUncaiStatus(data?.error || "Failed to submit your answer.");
        return;
      }
      setUncaiResult(data as UncAIResult);
      if (data?.stats) {
        setUncaiStats(data.stats as UncAIStats);
      }
    } catch (err) {
      setUncaiStatus("Failed to submit your answer.");
    } finally {
      setUncaiBusy(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Rat Assistant</h1>
          <p className="subtitle">
            Voice-first chat with animated emotion cues.
          </p>
        </div>
        <div className={connected ? "status connected" : "status"}>
          {connected ? "Connected" : "Disconnected"}
        </div>
      </header>

      <section className="stage">
        <canvas ref={canvasRef} width={520} height={360} />
        <div className="controls">
          <div className="input-row">
            <input
              type="text"
              placeholder="Type a message or use the mic"
              value={inputValue}
              onChange={(event) => setInputValue(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  sendMessage(inputValue);
                }
              }}
            />
            <button onClick={() => sendMessage(inputValue)}>Send</button>
          </div>
          <div className="input-row">
            <button className={isListening ? "mic active" : "mic"} onClick={toggleListening}>
              {isListening ? "Listening..." : "Use Microphone"}
            </button>
            <span className="hint">
              {isListening ? "Speak now" : "Press to start speech-to-text"}
            </span>
          </div>
        </div>
      </section>

      <section className="chat">
        <h2>Chat Log</h2>
        <div className="chat-log">
          {chatLog.map((item, index) => (
            <div key={`${item.role}-${index}`} className={`chat-item ${item.role}`}>
              <div className="meta">
                <span>{item.role}</span>
                <span>{item.timestamp}</span>
              </div>
              <p>{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="uncai">
        <div className="uncai-header">
          <div>
            <h2>UncAI Training Lab</h2>
            <p className="subtitle">
              Practice spotting scams and see how your instincts improve.
            </p>
          </div>
          <button className="uncai-cta" onClick={startPractice} disabled={uncaiBusy}>
            {uncaiItem ? "New Scenario" : "Start Training"}
          </button>
        </div>

        {uncaiStatus ? <div className="uncai-status">{uncaiStatus}</div> : null}

        <div className="uncai-grid">
          <div className="uncai-card">
            <div className="uncai-card-header">
              <span className="uncai-label">Scenario</span>
              <span className="uncai-chip">
                {uncaiItem?.source === "glasses" ? "Real-World" : "Digital"}
              </span>
            </div>

            {uncaiItem ? (
              <>
                <h3 className="uncai-subject">{uncaiItem.subject}</h3>
                <p className="uncai-from">From: {uncaiItem.sender}</p>
                <div className="uncai-content">{uncaiItem.content}</div>

                <label className="uncai-label" htmlFor="uncai-explanation">
                  Your reasoning (optional)
                </label>
                <textarea
                  id="uncai-explanation"
                  value={uncaiExplanation}
                  onChange={(event) => setUncaiExplanation(event.target.value)}
                  placeholder="Call out the red flags you notice."
                  rows={4}
                />

                <div className="uncai-actions">
                  <button
                    className="uncai-button danger"
                    onClick={() => submitPractice("scam")}
                    disabled={uncaiBusy}
                  >
                    Mark as Scam
                  </button>
                  <button
                    className="uncai-button"
                    onClick={() => submitPractice("legit")}
                    disabled={uncaiBusy}
                  >
                    Mark as Legit
                  </button>
                </div>
              </>
            ) : (
              <div className="uncai-empty">
                <p>Click "Start Training" to get your first scenario.</p>
              </div>
            )}

            {uncaiResult ? (
              <div className={`uncai-result ${uncaiResult.correct ? "good" : "bad"}`}>
                <h4>{uncaiResult.correct ? "Correct" : "Incorrect"}</h4>
                <p>{uncaiResult.feedback}</p>
                <div className="uncai-reveal">
                  <span className="uncai-label">Reveal</span>
                  <div className="uncai-reveal-grid">
                    <div>
                      <div className="uncai-pill">
                        Type: {uncaiResult.reveal.scam_type || "legit"}
                      </div>
                      <div className="uncai-pill">
                        Severity: {uncaiResult.reveal.severity}
                      </div>
                    </div>
                    <div>
                      <div className="uncai-label">Red flags</div>
                      <ul>
                        {uncaiResult.reveal.red_flags.map((flag, index) => (
                          <li key={`${flag}-${index}`}>{flag}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
                {uncaiResult.reasoning.score !== null ? (
                  <div className="uncai-reasoning">
                    <span className="uncai-label">Reasoning score</span>
                    <div className="uncai-pill">
                      {uncaiResult.reasoning.score} / 100
                    </div>
                    {uncaiResult.reasoning.feedback ? (
                      <p>{uncaiResult.reasoning.feedback}</p>
                    ) : null}
                  </div>
                ) : null}
              </div>
            ) : null}
          </div>

          <div className="uncai-card stats">
            <div className="uncai-card-header">
              <span className="uncai-label">Performance</span>
              <span className="uncai-chip">UncAI Report</span>
            </div>

            {uncaiStats ? (
              <>
                <div className="uncai-metrics">
                  <div>
                    <span className="uncai-label">Accuracy</span>
                    <strong>{uncaiStats.accuracy}%</strong>
                  </div>
                  <div>
                    <span className="uncai-label">Total</span>
                    <strong>{uncaiStats.total}</strong>
                  </div>
                  <div>
                    <span className="uncai-label">Best streak</span>
                    <strong>{uncaiStats.best_streak}</strong>
                  </div>
                </div>

                <div className="uncai-metrics">
                  <div>
                    <span className="uncai-label">Correct</span>
                    <strong>{uncaiStats.correct}</strong>
                  </div>
                  <div>
                    <span className="uncai-label">Incorrect</span>
                    <strong>{uncaiStats.incorrect}</strong>
                  </div>
                  <div>
                    <span className="uncai-label">Reasoning avg</span>
                    <strong>
                      {uncaiStats.avg_reasoning_score === null
                        ? "-"
                        : uncaiStats.avg_reasoning_score}
                    </strong>
                  </div>
                </div>

                <div className="uncai-bytype">
                  <span className="uncai-label">By scam type</span>
                  <ul>
                    {Object.entries(uncaiStats.by_type).map(([key, bucket]) => (
                      <li key={key}>
                        <span>{key}</span>
                        <span>
                          {bucket.correct}/{bucket.total} ({bucket.accuracy}%)
                        </span>
                      </li>
                    ))}
                    {Object.keys(uncaiStats.by_type).length === 0 ? (
                      <li className="muted">No scam-type stats yet.</li>
                    ) : null}
                  </ul>
                </div>
              </>
            ) : (
              <div className="uncai-empty">
                <p>Complete a scenario to start tracking performance.</p>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}

function emotionColor(emotion: string) {
  switch (emotion) {
    case "happy":
      return "#d8923a";
    case "excited":
      return "#f5a524";
    case "sad":
      return "#7b6b8f";
    case "surprised":
      return "#c97c5d";
    case "concerned":
      return "#8d6e63";
    case "thinking":
      return "#b08259";
    default:
      return "#9b6b3c";
  }
}
