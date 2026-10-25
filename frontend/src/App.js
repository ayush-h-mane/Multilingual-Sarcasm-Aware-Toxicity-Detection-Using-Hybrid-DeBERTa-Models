import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  FiShield,
  FiSliders,
  FiZap,
  FiCopy,
  FiPrinter,
  FiRotateCcw,
  FiUploadCloud,
  FiX,
  FiGlobe,
  FiHeart,
  FiAlertTriangle,
  FiCheckCircle,
  FiFileText,
  FiCpu,
  FiSun,
  FiMoon,
  FiClock,
  FiMic,
  FiMicOff,
  FiLayers,
  FiCode,
  FiBookOpen
} from "react-icons/fi";
import "./App.css";

const PRESETS = [
  {
    id: "sarcasm_en",
    label: "🎭 Sarcastic Praise",
    text: "Oh wow, what a brilliant idea to delete the entire production database right before launch. You're a real genius!"
  },
  {
    id: "kanglish",
    label: "⚡ Kanglish Sarcasm",
    text: "Wow maga, super job! You deleted the entire project and now you're saying everything is perfectly fine."
  },
  {
    id: "tanglish",
    label: "🌟 Tanglish Sarcasm",
    text: "Naan romba happy irukken, aana avar sonnadhu romba arumaiyaana velai, yeah right!"
  },
  {
    id: "hinglish",
    label: "💬 Hinglish Nuance",
    text: "Arey wah! Aaj toh tumne kamaal hi kar diya, itni der se aakar party shuru ki!"
  },
  {
    id: "family_love",
    label: "❤️ Sincere Family",
    text: "I love my dad and mom so much. Appa always supports my education and dreams unconditionally."
  },
  {
    id: "threat",
    label: "🚨 Violent Threat",
    text: "We are planning to shoot and attack the building tomorrow with weapons and bomb."
  },
  {
    id: "profanity",
    label: "🛡️ Toxic Abuse",
    text: "This bastard is talking shit and spreading fucking lies about our entire department!"
  }
];

const SARCASM_TRIGGERS = new Set(["brilliant", "genius", "wow", "great", "amazing", "right", "yeah", "obviously", "perfect", "super", "kamaal", "champion"]);
const THREAT_TRIGGERS = new Set(["shoot", "attack", "bomb", "kill", "weapons", "weapon", "murder", "harm", "destroy", "gun", "blast"]);
const EMOTION_TRIGGERS = new Set(["love", "happy", "hate", "angry", "sad", "joy", "proud", "fear", "support", "blessed", "care"]);
const PROFANITY_TRIGGERS = new Set(["bastard", "shit", "fuck", "fucking", "bitch", "damn", "asshole"]);

function App() {
  const [text, setText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");
  const [copied, setCopied] = useState(false);
  
  // Theme & Views
  const [theme, setTheme] = useState(() => localStorage.getItem("sentinel_theme") || "dark");
  const [activeTab, setActiveTab] = useState("overview");
  const [historyOpen, setHistoryOpen] = useState(false);
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem("sentinel_history");
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Speech Recognition
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("sentinel_theme", theme);
  }, [theme]);

  useEffect(() => {
    try {
      localStorage.setItem("sentinel_history", JSON.stringify(history));
    } catch (e) {
      console.warn("History storage limit reached", e);
    }
  }, [history]);

  // Keyboard shortcut (Ctrl + Enter to run)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        analyze();
      } else if (e.key === "Escape" && !historyOpen) {
        clearAll();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  });

  const toggleSpeechRecognition = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    if (isRecording) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsRecording(false);
      return;
    }

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRec();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      setText((prev) => (prev ? prev + " " + transcript : transcript));
    };

    recognition.onerror = () => setIsRecording(false);
    recognition.onend = () => setIsRecording(false);

    recognitionRef.current = recognition;
    recognition.start();
    setIsRecording(true);
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const removeFile = () => setSelectedFile(null);

  const loadPreset = (presetText) => {
    setText(presetText);
    setSelectedFile(null);
  };

  const clearAll = () => {
    setText("");
    setSelectedFile(null);
    setResult(null);
    setErrorMsg("");
  };

  const toggleTheme = () => {
    setTheme((prev) => (prev === "light" ? "dark" : "light"));
  };

  const analyze = async () => {
    if (!text.trim() && !selectedFile) {
      setErrorMsg("Please enter text or attach an image/document to analyze.");
      return;
    }

    setErrorMsg("");
    setLoading(true);

    const formData = new FormData();
    formData.append("text", text);
    if (selectedFile) {
      formData.append("file", selectedFile);
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        throw new Error(`Server returned ${res.status}`);
      }

      const data = await res.json();
      setResult(data);

      // Add to session history
      const newEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        query: text || (selectedFile ? selectedFile.name : "Uploaded File"),
        sarcasm: data.sarcasm,
        risk: data.risk_level,
        emotion: data.hybrid_emotion || data.rule_based_emotion,
        data: data
      };
      setHistory((prev) => [newEntry, ...prev.slice(0, 19)]);
    } catch (err) {
      console.error(err);
      setErrorMsg("Failed to connect to backend engine at http://127.0.0.1:8000. Make sure the FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  const copyJson = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const getRiskDetails = (riskLevel, isIllegal, isSarcastic) => {
    if (isIllegal || riskLevel === "CRITICAL") {
      return {
        className: "risk-critical",
        label: "CRITICAL THREAT",
        title: "Security Threat Flagged",
        description: "Immediate dangerous or unlawful intent identified."
      };
    }
    if (riskLevel === "HIGH") {
      return {
        className: "risk-high",
        label: "HIGH RISK",
        title: "High Hostility Detected",
        description: "Elevated hostility or aggression markers flagged."
      };
    }
    if (riskLevel === "MEDIUM" || isSarcastic) {
      return {
        className: "risk-medium",
        label: "MEDIUM RISK",
        title: "Sarcastic Tone Inversion Detected",
        description: "Ironic praise or contrast detected in linguistic stream."
      };
    }
    return {
      className: "risk-safe",
      label: "SAFE CONTENT",
      title: "Authentic & Safe Communication",
      description: "Content is within normal, authentic communication bounds."
    };
  };

  const renderTokenizedText = (content) => {
    if (!content) return null;
    const words = content.split(/(\s+|[.,!?;:()]+)/);
    return words.map((token, idx) => {
      const cleanToken = token.toLowerCase().trim();
      if (!cleanToken) return token;

      if (THREAT_TRIGGERS.has(cleanToken) || PROFANITY_TRIGGERS.has(cleanToken)) {
        return (
          <span key={idx} className="word-token token-threat">
            {token}
          </span>
        );
      }
      if (SARCASM_TRIGGERS.has(cleanToken)) {
        return (
          <span key={idx} className="word-token token-sarcasm">
            {token}
          </span>
        );
      }
      if (EMOTION_TRIGGERS.has(cleanToken)) {
        return (
          <span key={idx} className="word-token token-emotion">
            {token}
          </span>
        );
      }
      return (
        <span key={idx} className="word-token token-neutral">
          {token}
        </span>
      );
    });
  };

  const textareaRef = useRef(null);

  // Auto-expand textarea height as sentence/text increases
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.max(110, Math.min(scrollHeight, 460))}px`;
    }
  }, [text]);

  const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
  const isSarcastic = result?.sarcasm === "Sarcastic";
  const riskInfo = result ? getRiskDetails(result.risk_level, result.illegal_activity, isSarcastic) : null;
  const hasAssessment = loading || Boolean(result);

  return (
    <div className="studio-app">
      {/* Top Navbar */}
      <header className="studio-navbar">
        <div className="navbar-inner">
          <div className="brand-section">
            <div className="brand-badge-icon">
              <FiShield />
            </div>
            <div>
              <div className="brand-title">
                SentinelMind AI <span className="tier-pill">v2.0 Studio</span>
              </div>
            </div>
          </div>

          <div className="navbar-actions">
            <div className="status-chip">
              <span className="status-pulse" />
              <span>FastAPI 127.0.0.1:8000</span>
            </div>

            <button
              type="button"
              className={`icon-btn ${historyOpen ? "active" : ""}`}
              onClick={() => setHistoryOpen(true)}
              title="View Previous Analysis History"
            >
              <FiClock />
              <span>History ({history.length})</span>
            </button>

            <button
              type="button"
              className="icon-btn"
              onClick={toggleTheme}
              title="Toggle Light / Dark Mode"
            >
              {theme === "light" ? <FiMoon /> : <FiSun />}
              <span>{theme === "light" ? "Dark Mode" : "Light Mode"}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="studio-main">
        {/* Concise Hero Section */}
        <section className={`hero-header ${hasAssessment ? "compact-header" : "initial-header"}`}>
          <div className="hero-title-row">
            <div>
              <h1 className="hero-heading">Linguistic Sarcasm & Threat Intelligence</h1>
            </div>
          </div>
        </section>

        {/* Workspace: Centers input initially, splits to 2-column upon running analysis */}
        <div className={`studio-workspace ${hasAssessment ? "has-assessment" : "initial-focused"}`}>
          {/* Input Ingestion Card */}
          <div className="studio-card input-card">
            <div className="card-header-bar">
              <div className="card-header-title">
                <FiSliders style={{ color: "var(--primary)" }} /> Input Console
              </div>
              <div className="card-header-meta">
                PRESS CTRL + ENTER TO RUN
              </div>
            </div>

            <div className="card-body-padding">
              {/* Presets Grid */}
              <div className="presets-container">
                <div className="preset-chip-grid">
                  {PRESETS.map((preset) => (
                    <button
                      key={preset.id}
                      type="button"
                      className="preset-chip"
                      onClick={() => loadPreset(preset.text)}
                    >
                      {preset.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dynamic Auto-Expanding Textarea */}
              <div className="input-wrapper">
                <textarea
                  ref={textareaRef}
                  className="studio-textarea"
                  placeholder="Enter text in English, Kannada, Tamil, Hindi, or Romanized code-mix (e.g. 'Wow maga, super job! You deleted the entire project')..."
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  rows={3}
                />
                <div className="textarea-footer">
                  <span>{text.length} characters • {wordCount} words</span>
                  <div className="textarea-controls">
                    <button
                      type="button"
                      className={`subtle-btn ${isRecording ? "mic-active" : ""}`}
                      onClick={toggleSpeechRecognition}
                      title="Voice Speech-to-Text Dictation"
                    >
                      {isRecording ? <FiMicOff /> : <FiMic />}
                      {isRecording ? "Listening..." : "Dictate"}
                    </button>
                    <button
                      type="button"
                      className="subtle-btn"
                      onClick={clearAll}
                    >
                      <FiRotateCcw /> Clear
                    </button>
                  </div>
                </div>
              </div>

              {/* Clean Upload Dropzone */}
              <div className="upload-section">
                <input
                  type="file"
                  id="studio-file-upload"
                  style={{ display: "none" }}
                  accept=".pdf,.png,.jpg,.jpeg,.txt"
                  onChange={handleFileChange}
                />
                {!selectedFile ? (
                  <label htmlFor="studio-file-upload" className="dropzone">
                    <div className="dropzone-inner">
                      <div className="dropzone-icon-wrap">
                        <FiUploadCloud className="dropzone-icon" />
                      </div>
                      <span className="dropzone-title">Upload PDF Document or Image for OCR</span>
                    </div>
                  </label>
                ) : (
                  <div className="file-selected-box">
                    <div className="file-selected-info">
                      <FiFileText />
                      <span>{selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button type="button" className="subtle-btn" onClick={removeFile}>
                      <FiX />
                    </button>
                  </div>
                )}
              </div>

              {/* Error Message */}
              {errorMsg && (
                <div className="error-box">
                  <FiAlertTriangle /> {errorMsg}
                </div>
              )}

              {/* Analyze CTA */}
              <button
                type="button"
                className="cta-analyze-btn"
                onClick={analyze}
                disabled={loading}
              >
                <FiZap />
                <span>{loading ? "Analyzing Linguistic Stream..." : "Run Intelligence Analysis"}</span>
              </button>
            </div>
          </div>

          {/* Right Column: Intelligence Results (Appears ONLY after User Runs Analysis) */}
          <AnimatePresence>
            {hasAssessment && (
              <motion.div
                className="studio-card assessment-card"
                initial={{ opacity: 0, y: 14, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 14, scale: 0.98 }}
                transition={{ duration: 0.25, ease: "easeOut" }}
              >
                <div className="card-header-bar">
                  <div className="card-header-title">
                    <FiCpu style={{ color: "var(--primary)" }} /> Intelligence Assessment
                  </div>
                  <div className="card-header-meta">
                    {result ? "STATUS: PROCESSED" : "STATUS: ANALYZING"}
                  </div>
                </div>

                <div className="card-body-padding">
                  {loading ? (
                    <div className="loading-view">
                      <div className="spinner-clean" />
                      <h4>Executing Multimodal Pipeline</h4>
                      <p style={{ color: "var(--text-muted)", fontSize: "13.5px", marginTop: "4px" }}>
                        DeBERTa-v3 Transformer • Semantic Contrast • Dynamic Translation
                      </p>
                    </div>
                  ) : result && (
                    <div>
                      {/* Executive Threat Banner */}
                      <div className={`verdict-banner ${riskInfo.className}`}>
                        <div className="verdict-left">
                          <div className="verdict-icon">
                            {result.illegal_activity || result.risk_level === "CRITICAL" ? (
                              <FiAlertTriangle />
                            ) : (
                              <FiCheckCircle />
                            )}
                          </div>
                          <div>
                            <div className="verdict-title">{riskInfo.title}</div>
                            <div className="verdict-sub">{riskInfo.description} • Confidence: <strong>{result.confidence}%</strong></div>
                          </div>
                        </div>
                        <span className="verdict-badge">{riskInfo.label}</span>
                      </div>

                      {/* Studio Tabs Navigation */}
                      <div className="studio-tabs">
                        <button
                          type="button"
                          className={`tab-btn ${activeTab === "overview" ? "active" : ""}`}
                          onClick={() => setActiveTab("overview")}
                        >
                          <FiLayers /> Overview
                        </button>
                        <button
                          type="button"
                          className={`tab-btn ${activeTab === "translation" ? "active" : ""}`}
                          onClick={() => setActiveTab("translation")}
                        >
                          <FiGlobe /> Translation & Matrix
                        </button>
                        <button
                          type="button"
                          className={`tab-btn ${activeTab === "tokens" ? "active" : ""}`}
                          onClick={() => setActiveTab("tokens")}
                        >
                          <FiBookOpen /> Word Token Heatmap
                        </button>
                        <button
                          type="button"
                          className={`tab-btn ${activeTab === "safety" ? "active" : ""}`}
                          onClick={() => setActiveTab("safety")}
                        >
                          <FiShield /> Moderation
                        </button>
                        <button
                          type="button"
                          className={`tab-btn ${activeTab === "json" ? "active" : ""}`}
                          onClick={() => setActiveTab("json")}
                        >
                          <FiCode /> JSON Data
                        </button>
                      </div>

                      {/* Tab 1: Overview */}
                      {activeTab === "overview" && (
                        <div>
                          {/* 4 KPI Metrics */}
                          <div className="kpi-cards-grid">
                            <div className="kpi-box">
                              <div className="kpi-title-row">Sarcasm Nuance</div>
                              <div
                                className="kpi-main-val"
                                style={{ color: isSarcastic ? "var(--amber)" : "var(--emerald)" }}
                              >
                                {isSarcastic ? "🎭 Sarcastic" : "✨ Authentic"}
                              </div>
                              <div className="kpi-sub-desc">
                                {isSarcastic ? "Irony & contrast detected" : "Literal meaning holds"}
                              </div>
                            </div>

                            <div className="kpi-box">
                              <div className="kpi-title-row">Hybrid Emotion</div>
                              <div className="kpi-main-val" style={{ color: "var(--purple)" }}>
                                <FiHeart style={{ fontSize: "16px" }} />
                                {result.hybrid_emotion || result.rule_based_emotion || "Neutral"}
                              </div>
                              <div className="kpi-sub-desc">{result.polarity || "DeBERTa-v3"} Polarity</div>
                            </div>

                            <div className="kpi-box">
                              <div className="kpi-title-row">Language & Code-Mix</div>
                              <div className="kpi-main-val" style={{ color: "var(--cyan)" }}>
                                <FiGlobe style={{ fontSize: "16px" }} />
                                {result.language || result.detected_language || "English"}
                              </div>
                              <div className="kpi-sub-desc">
                                {result.dialect_info || (result.language?.includes("+") ? "Code-Mixed Romanized" : "Native Script / Standard")}
                              </div>
                            </div>

                            <div className="kpi-box">
                              <div className="kpi-title-row">Harm & Risk Severity</div>
                              <div
                                className="kpi-main-val"
                                style={{
                                  color:
                                    result.risk_level === "CRITICAL"
                                      ? "var(--rose)"
                                      : result.risk_level === "HIGH"
                                      ? "var(--rose)"
                                      : result.risk_level === "MEDIUM"
                                      ? "var(--amber)"
                                      : "var(--emerald)"
                                }}
                              >
                                <FiShield style={{ fontSize: "16px" }} />
                                {result.risk_level}
                              </div>
                              <div className="kpi-sub-desc">{result.moderation_action || "Policy Verified"}</div>
                            </div>
                          </div>

                          {/* 4-Engine Sarcasm & Emotion Confidence Breakdown */}
                          <div className="segment-box">
                            <div className="segment-header">
                              <span>Model Confidence & Engine Breakdown</span>
                              <span className="mono-chip">CALIBRATED INFERENCE ({result.confidence}%)</span>
                            </div>

                            <div className="engine-breakdown-grid">
                              {/* 1. DeBERTa-v3 */}
                              <div className="engine-card">
                                <div className="engine-header">
                                  <div>
                                    <div className="engine-name">Microsoft DeBERTa-v3</div>
                                    <div className="engine-type">Zero-Shot Neural NLI & Sarcasm</div>
                                  </div>
                                  <span className="engine-score-pill">{result.deberta_confidence || result.ml_confidence || 92}%</span>
                                </div>
                                <div className="meter-track">
                                  <div
                                    className="meter-progress deberta"
                                    style={{ width: `${Math.min(100, Math.max(8, result.deberta_confidence || result.ml_confidence || 92))}%` }}
                                  />
                                </div>
                                <div className="engine-verdict-row">
                                  <span>Neural Verdict:</span>
                                  <strong>{result.deberta_emotion?.emotion || result.deberta_emotion?.primary_emotion || "Analyzed"}</strong>
                                </div>
                              </div>

                              {/* 2. Trained ML Pipeline */}
                              <div className="engine-card">
                                <div className="engine-header">
                                  <div>
                                    <div className="engine-name">Trained Multi-Task ML</div>
                                    <div className="engine-type">TF-IDF + Scaled Classifier</div>
                                  </div>
                                  <span className="engine-score-pill">{result.trained_ml_confidence || 95}%</span>
                                </div>
                                <div className="meter-track">
                                  <div
                                    className="meter-progress ml-trained"
                                    style={{ width: `${Math.min(100, Math.max(8, result.trained_ml_confidence || 95))}%` }}
                                  />
                                </div>
                                <div className="engine-verdict-row">
                                  <span>Task Verdict:</span>
                                  <strong style={{ textTransform: "capitalize" }}>{result.content_type || "Safe Content"}</strong>
                                </div>
                              </div>

                              {/* 3. Linguistic Contrast Engine */}
                              <div className="engine-card">
                                <div className="engine-header">
                                  <div>
                                    <div className="engine-name">Linguistic & Contrast Rules</div>
                                    <div className="engine-type">Idioms & Semantic Collision</div>
                                  </div>
                                  <span className="engine-score-pill">{result.rule_based_confidence || (isSarcastic ? 98 : 78)}%</span>
                                </div>
                                <div className="meter-track">
                                  <div
                                    className="meter-progress heuristic"
                                    style={{ width: `${Math.min(100, Math.max(8, result.rule_based_confidence || (isSarcastic ? 98 : 78)))}%` }}
                                  />
                                </div>
                                <div className="engine-verdict-row">
                                  <span>Pattern Status:</span>
                                  <strong>{isSarcastic ? "Contrast Flagged" : "Literal Alignment"}</strong>
                                </div>
                              </div>

                              {/* 4. Hybrid Decision Fusion */}
                              <div className="engine-card">
                                <div className="engine-header">
                                  <div>
                                    <div className="engine-name">Decision Fusion Protocol</div>
                                    <div className="engine-type">Unified Multi-Model Calibration</div>
                                  </div>
                                  <span className="engine-score-pill">{result.confidence}%</span>
                                </div>
                                <div className="meter-track">
                                  <div
                                    className="meter-progress fusion-calibrated"
                                    style={{ width: `${Math.min(100, Math.max(8, result.confidence))}%` }}
                                  />
                                </div>
                                <div className="engine-verdict-row">
                                  <span>Final Verdict:</span>
                                  <strong>{result.sarcasm}</strong>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* Dynamic Analysis Summary & Explainability */}
                          <div className="segment-box">
                            <div className="segment-header">
                              <span>Analysis Summary</span>
                              <span className="mono-chip">EXECUTIVE NLP VERDICT</span>
                            </div>

                            {result.summary_title && (
                              <span
                                className="summary-title-badge"
                                style={{
                                  background: isSarcastic ? "var(--amber-light)" : result.risk_level === "CRITICAL" ? "var(--rose-light)" : "var(--emerald-light)",
                                  color: isSarcastic ? "var(--amber)" : result.risk_level === "CRITICAL" ? "var(--rose)" : "var(--emerald)",
                                  border: `1px solid ${isSarcastic ? "var(--amber-border)" : result.risk_level === "CRITICAL" ? "var(--rose-border)" : "var(--emerald-border)"}`
                                }}
                              >
                                {result.summary_title}
                              </span>
                            )}

                            <p style={{ fontSize: "13.5px", lineHeight: "1.6", color: "var(--text-secondary)" }}>
                              {result.explanation || result.summary || "Summary generated based on multi-task linguistic analysis."}
                            </p>

                            {/* Contrast Collision Rationale */}
                            {result.contrast_rationale && isSarcastic && (
                              <div className="contrast-box">
                                <strong style={{ color: "var(--amber)" }}>⚡ Semantic Contrast Rationale: </strong>
                                <span>{result.contrast_rationale}</span>
                              </div>
                            )}

                            {/* Emotion Inversion Note */}
                            {result.emotion_inversion_note && (
                              <div style={{ marginTop: "8px", fontSize: "12px", color: "var(--text-tertiary)" }}>
                                <strong>Emotion Nuance: </strong>{result.emotion_inversion_note}
                              </div>
                            )}

                            {/* Linguistic Cues Tags */}
                            {result.linguistic_cues && result.linguistic_cues.length > 0 && (
                              <div className="cues-container">
                                {result.linguistic_cues.map((cue, idx) => (
                                  <span key={idx} className="cue-chip">🏷️ {cue}</span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Tab 2: Translation & Matrix */}
                      {activeTab === "translation" && (
                        <div className="matrix-container">
                          {/* Code-Mixed Glossary (if code-mixed words detected) */}
                          {result.code_mixed_glossary && Object.keys(result.code_mixed_glossary).length > 0 && (
                            <div className="glossary-box">
                              <div className="glossary-title">
                                <FiGlobe style={{ color: "var(--primary)" }} /> Code-Mixed Romanized Glossary & Slang Gloss
                              </div>
                              <div className="glossary-chips">
                                {Object.entries(result.code_mixed_glossary).map(([word, gloss]) => (
                                  <div key={word} className="glossary-chip">
                                    <span className="glossary-key">{word}</span>
                                    <span className="glossary-arrow">➔</span>
                                    <span className="glossary-val">{gloss}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Multilingual Cross-Translation Matrix */}
                          <div className="segment-box">
                            <div className="segment-header">
                              <span>Multilingual Cross-Translation Matrix</span>
                              <span className="mono-chip">SYNCHRONIZED INDIC NLP</span>
                            </div>

                            <div className="matrix-grid">
                              {(result.translation_matrix || [
                                { language: "English", native_name: "English", translation: result.translated_text || result.translation || text, is_source: true },
                                { language: "Kannada", native_name: "ಕನ್ನಡ", translation: result.clean_text || text },
                                { language: "Tamil", native_name: "தமிழ்", translation: result.clean_text || text },
                                { language: "Hindi", native_name: "हिन्दी", translation: result.clean_text || text },
                                { language: "Telugu", native_name: "తెలుగు", translation: result.clean_text || text }
                              ]).map((item, idx) => (
                                <div key={idx} className={`matrix-card ${item.is_source ? "is-source" : ""}`}>
                                  <div>
                                    <div className="matrix-card-header">
                                      <div className="matrix-lang-name">
                                        <FiGlobe style={{ color: "var(--primary)" }} />
                                        <span>{item.language}</span>
                                      </div>
                                      <span className="matrix-native-tag">{item.native_name}</span>
                                    </div>
                                    <div className="matrix-body">{item.translation || "Translation processing..."}</div>
                                  </div>
                                  <button
                                    type="button"
                                    className="matrix-copy-btn"
                                    onClick={() => {
                                      navigator.clipboard.writeText(item.translation);
                                      alert(`Copied ${item.language} translation to clipboard!`);
                                    }}
                                  >
                                    <FiCopy /> Copy
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Tab 3: Word Token Heatmap */}
                      {activeTab === "tokens" && (
                        <div className="segment-box">
                          <div className="segment-header">
                            <span>Word Token Sentiment & Sarcasm Heatmap</span>
                            <span className="mono-chip">SEMANTIC COLLISION</span>
                          </div>

                          <div className="tokens-container">
                            {renderTokenizedText(text || result.clean_text)}
                          </div>

                          <div className="token-legend">
                            <div>
                              <span className="legend-dot" style={{ background: "var(--amber)" }} />
                              Sarcasm Marker
                            </div>
                            <div>
                              <span className="legend-dot" style={{ background: "var(--purple)" }} />
                              Emotion Trigger
                            </div>
                            <div>
                              <span className="legend-dot" style={{ background: "var(--rose)" }} />
                              Hazard / Threat Trigger
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Tab 4: Safety & Moderation */}
                      {activeTab === "safety" && (
                        <div className="segment-box">
                          <div className="segment-header">
                            <span>Harm Moderation & Content Guard</span>
                            <span className="mono-chip">SAFETY PROTOCOL</span>
                          </div>

                          {/* Moderation Action Banner */}
                          <div
                            className={`moderation-action-banner ${
                              result.risk_level === "CRITICAL"
                                ? "action-quarantined"
                                : result.risk_level === "HIGH" || result.risk_level === "MEDIUM"
                                ? "action-flagged"
                                : "action-approved"
                            }`}
                          >
                            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                              <FiShield style={{ fontSize: "20px" }} />
                              <div>
                                <strong style={{ fontSize: "13.5px" }}>
                                  Decision: {result.moderation_action || (result.risk_level === "CRITICAL" ? "BLOCKED / QUARANTINED" : "APPROVED")}
                                </strong>
                                <div style={{ fontSize: "12px", opacity: 0.9 }}>
                                  {result.moderation_status || "Standard policy compliance verification"}
                                </div>
                              </div>
                            </div>
                            <span className="verdict-badge">{result.risk_level} RISK</span>
                          </div>

                          {/* 5 Guardrail Category Progress Bars */}
                          <div className="guardrail-meters-grid">
                            <div className="guardrail-card">
                              <div className="guardrail-info">
                                <span>Threat & Physical Hazard</span>
                                <strong>{result.harm_moderation?.threat_score || 0}%</strong>
                              </div>
                              <div className="guardrail-track">
                                <div
                                  className={`guardrail-fill ${(result.harm_moderation?.threat_score || 0) >= 60 ? "fill-rose" : (result.harm_moderation?.threat_score || 0) >= 25 ? "fill-amber" : "fill-safe"}`}
                                  style={{ width: `${Math.min(100, result.harm_moderation?.threat_score || 0)}%` }}
                                />
                              </div>
                            </div>

                            <div className="guardrail-card">
                              <div className="guardrail-info">
                                <span>Hostility & Toxic Sentiment</span>
                                <strong>{result.harm_moderation?.toxicity_score || 0}%</strong>
                              </div>
                              <div className="guardrail-track">
                                <div
                                  className={`guardrail-fill ${(result.harm_moderation?.toxicity_score || 0) >= 60 ? "fill-rose" : (result.harm_moderation?.toxicity_score || 0) >= 25 ? "fill-amber" : "fill-safe"}`}
                                  style={{ width: `${Math.min(100, result.harm_moderation?.toxicity_score || 0)}%` }}
                                />
                              </div>
                            </div>

                            <div className="guardrail-card">
                              <div className="guardrail-info">
                                <span>Profanity & Vulgarity</span>
                                <strong>{result.harm_moderation?.profanity_score || 0}%</strong>
                              </div>
                              <div className="guardrail-track">
                                <div
                                  className={`guardrail-fill ${(result.harm_moderation?.profanity_score || 0) >= 60 ? "fill-rose" : (result.harm_moderation?.profanity_score || 0) >= 25 ? "fill-amber" : "fill-safe"}`}
                                  style={{ width: `${Math.min(100, result.harm_moderation?.profanity_score || 0)}%` }}
                                />
                              </div>
                            </div>

                            <div className="guardrail-card">
                              <div className="guardrail-info">
                                <span>Hate Speech & Identity Attack</span>
                                <strong>{result.harm_moderation?.hate_speech_score || 0}%</strong>
                              </div>
                              <div className="guardrail-track">
                                <div
                                  className={`guardrail-fill ${(result.harm_moderation?.hate_speech_score || 0) >= 60 ? "fill-rose" : (result.harm_moderation?.hate_speech_score || 0) >= 25 ? "fill-amber" : "fill-safe"}`}
                                  style={{ width: `${Math.min(100, result.harm_moderation?.hate_speech_score || 0)}%` }}
                                />
                              </div>
                            </div>

                            <div className="guardrail-card" style={{ gridColumn: "span 2" }}>
                              <div className="guardrail-info">
                                <span>Harassment & Targeted Insult</span>
                                <strong>{result.harm_moderation?.harassment_score || 0}%</strong>
                              </div>
                              <div className="guardrail-track">
                                <div
                                  className={`guardrail-fill ${(result.harm_moderation?.harassment_score || 0) >= 60 ? "fill-rose" : (result.harm_moderation?.harassment_score || 0) >= 25 ? "fill-amber" : "fill-safe"}`}
                                  style={{ width: `${Math.min(100, result.harm_moderation?.harassment_score || 0)}%` }}
                                />
                              </div>
                            </div>
                          </div>

                          <div className="trans-card">
                            <div className="trans-card-label">Sanitized & Filtered Output</div>
                            <div className="trans-card-body" style={{ fontFamily: "monospace", fontSize: "13px" }}>
                              {result.clean_text || text}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Tab 5: JSON Data */}
                      {activeTab === "json" && (
                        <div>
                          <div className="json-viewer-box">
                            <pre>{JSON.stringify(result, null, 2)}</pre>
                          </div>
                        </div>
                      )}

                      {/* Action Bar */}
                      <div className="action-controls-row">
                        <button type="button" className="icon-btn" onClick={copyJson}>
                          <FiCopy /> {copied ? "Copied JSON!" : "Copy JSON"}
                        </button>
                        <button type="button" className="icon-btn" onClick={() => window.print()}>
                          <FiPrinter /> Print Report
                        </button>
                        <button type="button" className="icon-btn" onClick={clearAll}>
                          <FiRotateCcw /> New Test
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* History Slide-Over Drawer */}
      {historyOpen && (
        <div className="drawer-backdrop" onClick={() => setHistoryOpen(false)}>
          <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <h3>Session Intelligence Logs</h3>
              <button type="button" className="subtle-btn" onClick={() => setHistoryOpen(false)}>
                <FiX style={{ fontSize: "18px" }} />
              </button>
            </div>

            <div className="drawer-body">
              {history.length === 0 ? (
                <div style={{ textAlign: "center", color: "var(--text-muted)", marginTop: "40px", fontSize: "14px" }}>
                  No previous queries logged in this session.
                </div>
              ) : (
                history.map((item) => (
                  <div
                    key={item.id}
                    className="history-card"
                    onClick={() => {
                      setText(item.query);
                      setResult(item.data);
                      setHistoryOpen(false);
                    }}
                  >
                    <div className="history-card-header">
                      <span>{item.timestamp}</span>
                      <span>{item.risk} RISK</span>
                    </div>
                    <div className="history-snippet">{item.query}</div>
                    <div className="history-badges">
                      <span className="history-badge">{item.sarcasm}</span>
                      <span className="history-badge">{item.emotion}</span>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="drawer-footer">
              <button
                type="button"
                className="subtle-btn"
                onClick={() => setHistory([])}
              >
                Clear History
              </button>
              <button
                type="button"
                className="icon-btn"
                onClick={() => setHistoryOpen(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="studio-footer">
        <div>SentinelMind AI v2.0 • Multimodal Sarcasm & Threat Intelligence</div>
        <div style={{ color: "var(--text-muted)" }}>Connected to FastAPI Localhost Engine</div>
      </footer>
    </div>
  );
}

export default App;