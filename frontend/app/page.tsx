"use client";

import { useEffect, useRef, useState } from "react";

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

/* ================= 辅助组件 ================= */

function ScoreBar({ label, score }: { label: string; score: number }) {
  const pct = Math.min(100, Math.max(0, score));
  const color =
    pct >= 80
      ? "bg-emerald-500"
      : pct >= 60
        ? "bg-amber-500"
        : "bg-rose-500";

  return (
    <div className="flex items-center gap-3">
      <span className="w-24 shrink-0 text-sm font-medium text-slate-600 dark:text-slate-300">
        {label}
      </span>
      <div className="relative h-3 flex-1 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
        <div
          className={`absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-10 text-right text-sm font-semibold tabular-nums">
        {score}
      </span>
    </div>
  );
}

function DifficultyBadge({ level }: { level: string }) {
  const styles: Record<string, string> = {
    beginner:
      "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
    intermediate:
      "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
    advanced:
      "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300",
  };
  const cls = styles[level.toLowerCase()] ?? styles.beginner;

  return (
    <span
      className={`inline-block rounded-full px-3 py-0.5 text-xs font-semibold uppercase tracking-wide ${cls}`}
    >
      {level}
    </span>
  );
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
      {/* Analyzing overlay */}
      {analyzing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="rounded-2xl bg-white px-10 py-8 text-center shadow-2xl dark:bg-slate-800">
            <div
              className="mx-auto mb-4 h-12 w-12 rounded-full border-4 border-slate-200 border-t-indigo-500 dark:border-slate-600 dark:border-t-indigo-400"
              style={{ animation: "spin 0.8s linear infinite" }}
            />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
              Loading task...
            </p>
          </div>
        </div>
      )}

      {/* Upload/evaluate loading overlay */}
      {loading && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="rounded-2xl bg-white px-10 py-8 text-center shadow-2xl dark:bg-slate-800">
            <div
              className="mx-auto mb-4 h-12 w-12 rounded-full border-4 border-slate-200 border-t-indigo-500 dark:border-slate-600 dark:border-t-indigo-400"
              style={{ animation: "spin 0.8s linear infinite" }}
            />
            <p className="text-sm font-medium text-slate-600 dark:text-slate-300">
              Analyzing your speech...
            </p>
          </div>
        </div>
      )}

      <main className="mx-auto max-w-2xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <header className="mb-10 text-center">
          <h1 className="bg-gradient-to-r from-indigo-600 to-violet-500 bg-clip-text text-4xl font-extrabold tracking-tight text-transparent sm:text-5xl">
            Pic-Talk
          </h1>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
            Describe what you see &mdash; practice English with AI feedback
          </p>
        </header>

        {/* Image card */}
        {task && (
          <section
            className="mb-8 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800"
            style={{ animation: "fade-in 0.4s ease-out" }}
          >
            <div className="relative">
              <img
                src={task.image_url}
                alt="Practice image"
                className="h-72 w-full object-cover sm:h-96"
              />
              <div className="absolute bottom-3 left-3">
                <DifficultyBadge level={task.difficulty} />
              </div>
            </div>
          </section>
        )}

        {/* Controls */}
        <div className="mb-10 flex flex-wrap items-center justify-center gap-4">
          {!recording ? (
            <button
              onClick={startRecording}
              className="group relative inline-flex items-center gap-2 rounded-full bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-indigo-700 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 active:scale-95"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 0 0-6 0v6a3 3 0 0 0 3 3Z" />
                <path d="M17 11a1 1 0 0 0-2 0 3 3 0 0 1-6 0 1 1 0 0 0-2 0 5 5 0 0 0 4 4.9V18H9a1 1 0 1 0 0 2h6a1 1 0 1 0 0-2h-2v-2.1A5 5 0 0 0 17 11Z" />
              </svg>
              Start Recording
            </button>
          ) : (
            <button
              onClick={stopRecording}
              className="relative inline-flex items-center gap-2 rounded-full bg-rose-600 px-6 py-3 text-sm font-semibold text-white shadow-md transition hover:bg-rose-700 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-rose-400 focus:ring-offset-2 active:scale-95"
            >
              {/* Pulse ring */}
              <span
                className="absolute -inset-1 rounded-full bg-rose-400"
                style={{ animation: "pulse-ring 1.2s ease-out infinite" }}
              />
              <span className="relative flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
                Stop Recording
              </span>
            </button>
          )}

          <button
            onClick={fetchTask}
            className="inline-flex items-center gap-2 rounded-full border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:shadow focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 active:scale-95 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M21 12a9 9 0 1 1-6.22-8.56" />
              <polyline points="21 3 21 9 15 9" />
            </svg>
            Next Image
          </button>
        </div>

        {/* ASR text */}
        {result && result.asr_text && (
          <section
            className="mb-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            style={{ animation: "fade-in 0.4s ease-out" }}
          >
            <h2 className="mb-3 flex items-center gap-2 text-lg font-bold text-slate-800 dark:text-slate-100">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-indigo-500"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2Z" />
              </svg>
              Your Speech
            </h2>
            <p className="leading-relaxed text-slate-600 dark:text-slate-300">
              {result.asr_text}
            </p>
          </section>
        )}

        {/* AI Feedback */}
        {result && result.ai_feedback && (
          <section
            className="mb-10 space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            style={{ animation: "fade-in 0.5s ease-out" }}
          >
            <h2 className="flex items-center gap-2 text-lg font-bold text-slate-800 dark:text-slate-100">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-indigo-500"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 20h9" />
                <path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854Z" />
              </svg>
              AI Feedback
            </h2>

            {/* Scores */}
            <div className="space-y-3">
              <ScoreBar
                label="Relevance"
                score={result.ai_feedback.relevance_score}
              />
              <ScoreBar
                label="Fluency"
                score={result.ai_feedback.fluency_score}
              />
            </div>

            {/* Strengths */}
            {result.ai_feedback.strengths.length > 0 && (
              <div>
                <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <circle cx="12" cy="12" r="10" />
                    <path d="m9 12 2 2 4-4" />
                  </svg>
                  Strengths
                </h3>
                <ul className="space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
                  {result.ai_feedback.strengths.map((s, i) => (
                    <li key={i} className="list-disc">
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Issues */}
            {result.ai_feedback.issues.length > 0 && (
              <div>
                <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-amber-600 dark:text-amber-400">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                    <path d="M12 9v4" />
                    <path d="M12 17h.01" />
                  </svg>
                  Issues
                </h3>
                <ul className="space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
                  {result.ai_feedback.issues.map((s, i) => (
                    <li key={i} className="list-disc">
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {result.ai_feedback.suggestions.length > 0 && (
              <div>
                <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-indigo-600 dark:text-indigo-400">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-4 w-4"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
                    <path d="M9 18h6" />
                    <path d="M10 22h4" />
                  </svg>
                  Suggestions
                </h3>
                <ul className="space-y-1 pl-5 text-sm text-slate-600 dark:text-slate-300">
                  {result.ai_feedback.suggestions.map((s, i) => (
                    <li key={i} className="list-disc">
                      {s}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Summary */}
            {result.ai_feedback.summary && (
              <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-700/50">
                <h3 className="mb-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
                  Summary
                </h3>
                <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                  {result.ai_feedback.summary}
                </p>
              </div>
            )}
          </section>
        )}
      </main>
    </>
  );
}
