"use client";
import "./spinner.css";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";

/* ================= 接口类型定义 ================= */

interface Task {
  id: number;
  semantic_plan: string;
  image_url: string;
  standard_answer: string;
  difficulty: string;
  created_at: string;
}

interface AIFeedback {
  issues: string[];
  summary: string;
  strengths: string[];
  suggestions: string[];
  fluency_score: number;
  relevance_score: number;
}

interface PracticeResult {
  id: number;
  asr_text: string;
  relevance_score: number;
  fluency_score: number;
  ai_feedback: AIFeedback;
  created_at: string;
}

/* ================= 主组件 ================= */

export default function Home() {
  const [task, setTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [analyzing, setAnalyzing] = useState<boolean>(false);

  const [recording, setRecording] = useState<boolean>(false);
  const [mediaRecorder, setMediaRecorder] =
    useState<MediaRecorder | null>(null);

  const [result, setResult] = useState<PracticeResult | null>(null);

  const audioStreamRef = useRef<MediaStream | null>(null);

  /* ================= 拉取题目 ================= */

  const fetchTask = async () => {
    setAnalyzing(true);
    setResult(null);

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/api/image/get_random_task"
      );

      if (!res.ok) {
        throw new Error("Fetch task failed");
      }

      const data: Task = await res.json();

      setTask(data);
    } catch (err) {
      console.error(err);
      alert("Failed to load task");
    }

    setAnalyzing(false);
  };

  /* ================= 初始化 ================= */

  useEffect(() => {
    fetchTask();
  }, []);

  /* ================= 开始录音 ================= */

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      audioStreamRef.current = stream;

      const recorder = new MediaRecorder(stream);

      const chunks: BlobPart[] = [];

      recorder.ondataavailable = (e: BlobEvent) => {
        if (e.data.size > 0) {
          chunks.push(e.data);
        }
      };

      recorder.onstop = () => {
        uploadAudio(chunks);
      };

      recorder.start();

      setMediaRecorder(recorder);
      setRecording(true);
    } catch (err) {
      console.error(err);
      alert("Microphone permission denied");
    }
  };

  /* ================= 停止录音 ================= */

  const stopRecording = () => {
    if (!mediaRecorder) return;

    mediaRecorder.stop();

    audioStreamRef.current?.getTracks().forEach((t) => t.stop());

    setRecording(false);
  };

  /* ================= 上传音频 ================= */

  const uploadAudio = async (chunks: BlobPart[]) => {
    if (!task) return;

    setLoading(true);

    const blob = new Blob(chunks, { type: "audio/wav" });

    const file = new File([blob], "recording.wav", {
      type: "audio/wav",
    });

    const formData = new FormData();

    formData.append("audio_file", file);
    formData.append("task_id", String(task.id));

    try {
      const res = await fetch(
        "http://127.0.0.1:8000/api/user-practice/evaluate",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data: PracticeResult = await res.json();

      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }

    setLoading(false);
  };

  /* ================= UI ================= */

  return (
    <>
      {analyzing && (
        <div style={styles.overlay}>
          <div style={styles.spinnerBox}>
            <div style={styles.spinner}></div>
            <p>Analyzing your speech...</p>
          </div>
        </div>
      )}
      <main style={styles.container}>
        <div style={styles.header}>
          <h1>🗣 Pic-Talk</h1>
          <Link href="/history" style={styles.historyLink}>
            📊 Practice History
          </Link>
        </div>

        {loading && <p>Loading...</p>}

        {/* 图片 */}
        {task && (
          <div style={styles.card}>
            <img
              src={task.image_url}
              alt="practice"
              style={styles.image}
            />

            <p>Difficulty: {task.difficulty}</p>
          </div>
        )}

        {/* 控制按钮 */}
        <div style={styles.controls}>
          {!recording ? (
            <button onClick={startRecording} style={styles.btn}>
              🎤 Start Recording
            </button>
          ) : (
            <button onClick={stopRecording} style={styles.btnStop}>
              ⏹ Stop Recording
            </button>
          )}

          <button onClick={fetchTask} style={styles.btnNext}>
            🔄 Next Image
          </button>
        </div>

        {/* ASR text */}
        {result && result.asr_text && (
          <div style={styles.feedback}>
            <h2>📊 ASR text</h2>

            <p>
              {result.asr_text}
            </p>
          </div>
        )}

        {/* AI 反馈 */}
        {result && result.ai_feedback && (
          <div style={styles.feedback}>
            <h2>📊 AI Feedback</h2>

            <p>
              <b>Relevance:</b>{" "}
              {result.ai_feedback.relevance_score}
            </p>

            <p>
              <b>Fluency:</b>{" "}
              {result.ai_feedback.fluency_score}
            </p>

            <h3>✅ Strengths</h3>
            <ul>
              {result.ai_feedback.strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>

            <h3>⚠ Issues</h3>
            <ul>
              {result.ai_feedback.issues.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>

            <h3>💡 Suggestions</h3>
            <ul>
              {result.ai_feedback.suggestions.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>

            <h3>📝 Summary</h3>
            <p>{result.ai_feedback.summary}</p>
          </div>
        )}
      </main>
    </>
  );
}

/* ================= 样式 ================= */

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: "800px",
    margin: "auto",
    padding: "20px",
    fontFamily: "Arial",
    textAlign: "center",
  },

  header: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "16px",
    flexWrap: "wrap" as const,
    marginBottom: "8px",
  },

  historyLink: {
    fontSize: "14px",
    color: "#2196f3",
    textDecoration: "none",
    fontWeight: 500,
    padding: "6px 14px",
    border: "1px solid #2196f3",
    borderRadius: "20px",
  },

  card: {
    marginBottom: "20px",
  },

  image: {
    width: "100%",
    maxHeight: "400px",
    objectFit: "contain",
    borderRadius: "8px",
    border: "1px solid #ddd",
  },

  controls: {
    margin: "20px 0",
  },

  btn: {
    padding: "10px 20px",
    margin: "10px",
    fontSize: "16px",
    background: "#4caf50",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },

  btnStop: {
    padding: "10px 20px",
    margin: "10px",
    fontSize: "16px",
    background: "#f44336",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },

  btnNext: {
    padding: "10px 20px",
    margin: "10px",
    fontSize: "16px",
    background: "#2196f3",
    color: "white",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },

  feedback: {
    marginTop: "30px",
    padding: "20px",
    border: "1px solid #ddd",
    borderRadius: "8px",
    textAlign: "left",
  },

  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0,0,0,0.4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 9999,
  },
  
  spinnerBox: {
    background: "white",
    padding: "40px 50px",
    borderRadius: "12px",
    textAlign: "center",
    boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
  },
  
  spinner: {
    width: "50px",
    height: "50px",
    border: "6px solid #ddd",
    borderTop: "6px solid #2196f3",
    borderRadius: "50%",
    margin: "0 auto 20px",
    animation: "spin 1s linear infinite",
  },
  
};
