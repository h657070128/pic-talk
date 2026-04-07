"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

/* ================= Types ================= */

interface AIFeedback {
  issues: string[];
  summary: string;
  strengths: string[];
  suggestions: string[];
  fluency_score: number;
  relevance_score: number;
}

interface HistoryRecord {
  id: number;
  task_id: number;
  user_id: number | null;
  user_audio_url: string | null;
  asr_text: string;
  ai_feedback: AIFeedback | string;
  relevance_score: number | null;
  fluency_score: number | null;
  created_at: string;
  image_url: string | null;
  difficulty: string | null;
}

interface HistoryResponse {
  records: HistoryRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface TrendPoint {
  relevance_score: number;
  fluency_score: number;
  created_at: string;
}

interface Stats {
  total_sessions: number;
  avg_relevance_score: number;
  avg_fluency_score: number;
  best_relevance_score: number;
  best_fluency_score: number;
  score_trend: TrendPoint[];
  current_streak: number;
}

/* ================= SVG Line Chart ================= */

function ScoreChart({ trend }: { trend: TrendPoint[] }) {
  if (trend.length < 2) {
    return (
      <div style={styles.chartEmpty}>
        <p>Need at least 2 sessions to show a trend chart.</p>
      </div>
    );
  }

  const W = 600;
  const H = 200;
  const PAD_X = 40;
  const PAD_Y = 20;
  const chartW = W - PAD_X * 2;
  const chartH = H - PAD_Y * 2;

  const maxScore = 100;
  const minScore = 0;

  const toX = (i: number) => PAD_X + (i / (trend.length - 1)) * chartW;
  const toY = (score: number) =>
    PAD_Y + chartH - ((score - minScore) / (maxScore - minScore)) * chartH;

  const relPoints = trend.map((p, i) => `${toX(i)},${toY(p.relevance_score)}`).join(" ");
  const fluPoints = trend.map((p, i) => `${toX(i)},${toY(p.fluency_score)}`).join(" ");

  const yTicks = [0, 25, 50, 75, 100];

  return (
    <div style={styles.chartContainer}>
      <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, height: "auto" }}>
        {/* Grid lines */}
        {yTicks.map((tick) => (
          <g key={tick}>
            <line
              x1={PAD_X}
              y1={toY(tick)}
              x2={W - PAD_X}
              y2={toY(tick)}
              stroke="#e0e0e0"
              strokeDasharray="4 4"
            />
            <text x={PAD_X - 5} y={toY(tick) + 4} textAnchor="end" fontSize="10" fill="#888">
              {tick}
            </text>
          </g>
        ))}

        {/* Relevance line */}
        <polyline fill="none" stroke="#4caf50" strokeWidth="2.5" points={relPoints} />
        {trend.map((p, i) => (
          <circle key={`r-${i}`} cx={toX(i)} cy={toY(p.relevance_score)} r="3" fill="#4caf50" />
        ))}

        {/* Fluency line */}
        <polyline fill="none" stroke="#2196f3" strokeWidth="2.5" points={fluPoints} />
        {trend.map((p, i) => (
          <circle key={`f-${i}`} cx={toX(i)} cy={toY(p.fluency_score)} r="3" fill="#2196f3" />
        ))}
      </svg>

      <div style={styles.legend}>
        <span style={{ ...styles.legendDot, background: "#4caf50" }} /> Relevance
        <span style={{ ...styles.legendDot, background: "#2196f3", marginLeft: 16 }} /> Fluency
      </div>
    </div>
  );
}

/* ================= Session Card ================= */

function SessionCard({ record }: { record: HistoryRecord }) {
  const [expanded, setExpanded] = useState(false);

  const feedback: AIFeedback | null =
    typeof record.ai_feedback === "string"
      ? (() => { try { return JSON.parse(record.ai_feedback); } catch { return null; } })()
      : record.ai_feedback;

  const snippet = record.asr_text
    ? record.asr_text.length > 120
      ? record.asr_text.slice(0, 120) + "..."
      : record.asr_text
    : "No transcription";

  const dateStr = record.created_at
    ? new Date(record.created_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  return (
    <div style={styles.sessionCard} onClick={() => setExpanded(!expanded)}>
      <div style={styles.sessionHeader}>
        {record.image_url && (
          <img src={record.image_url} alt="task" style={styles.thumbnail} />
        )}
        <div style={styles.sessionInfo}>
          <div style={styles.sessionDate}>{dateStr}</div>
          {record.difficulty && (
            <span style={styles.difficultyBadge}>{record.difficulty}</span>
          )}
          <div style={styles.sessionScores}>
            <span style={styles.scoreRel}>
              Relevance: {record.relevance_score ?? "-"}
            </span>
            <span style={styles.scoreFlu}>
              Fluency: {record.fluency_score ?? "-"}
            </span>
          </div>
          <div style={styles.sessionSnippet}>{snippet}</div>
        </div>
        <div style={styles.expandIcon}>{expanded ? "\u25B2" : "\u25BC"}</div>
      </div>

      {expanded && feedback && (
        <div style={styles.feedbackExpanded}>
          <div style={styles.feedbackSection}>
            <h4 style={styles.feedbackH4}>Strengths</h4>
            <ul>
              {feedback.strengths?.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div style={styles.feedbackSection}>
            <h4 style={styles.feedbackH4}>Issues</h4>
            <ul>
              {feedback.issues?.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div style={styles.feedbackSection}>
            <h4 style={styles.feedbackH4}>Suggestions</h4>
            <ul>
              {feedback.suggestions?.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          {feedback.summary && (
            <div style={styles.feedbackSection}>
              <h4 style={styles.feedbackH4}>Summary</h4>
              <p>{feedback.summary}</p>
            </div>
          )}
          <div style={styles.feedbackSection}>
            <h4 style={styles.feedbackH4}>Full Transcription</h4>
            <p style={styles.fullTranscription}>{record.asr_text}</p>
          </div>
        </div>
      )}
    </div>
  );
}

/* ================= Main History Page ================= */

export default function HistoryPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      try {
        const [statsRes, historyRes] = await Promise.all([
          fetch("http://127.0.0.1:8000/api/user-practice/stats"),
          fetch(
            `http://127.0.0.1:8000/api/user-practice/history?page=${page}&page_size=10`
          ),
        ]);
        if (cancelled) return;
        if (statsRes.ok) {
          setStats(await statsRes.json());
        }
        if (historyRes.ok) {
          setHistory(await historyRes.json());
        }
      } catch (err) {
        console.error("Failed to load data:", err);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadData();
    return () => {
      cancelled = true;
    };
  }, [page]);

  const goToPage = (p: number) => {
    setLoading(true);
    setPage(p);
  };

  return (
    <main style={styles.container}>
      {/* Navigation */}
      <div style={styles.nav}>
        <Link href="/" style={styles.navLink}>
          &larr; Back to Practice
        </Link>
        <h1 style={styles.title}>Practice History & Progress</h1>
      </div>

      {loading && <p>Loading...</p>}

      {/* Summary Stats Bar */}
      {stats && (
        <div style={styles.statsBar}>
          <div style={styles.statBox}>
            <div style={styles.statValue}>{stats.total_sessions}</div>
            <div style={styles.statLabel}>Total Sessions</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statValue}>{stats.avg_relevance_score}</div>
            <div style={styles.statLabel}>Avg Relevance</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statValue}>{stats.avg_fluency_score}</div>
            <div style={styles.statLabel}>Avg Fluency</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statValue}>{stats.best_relevance_score}</div>
            <div style={styles.statLabel}>Best Relevance</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statValue}>{stats.best_fluency_score}</div>
            <div style={styles.statLabel}>Best Fluency</div>
          </div>
          <div style={styles.statBox}>
            <div style={styles.statValue}>
              {stats.current_streak} day{stats.current_streak !== 1 ? "s" : ""}
            </div>
            <div style={styles.statLabel}>Streak</div>
          </div>
        </div>
      )}

      {/* Progress Chart */}
      {stats && stats.score_trend.length > 0 && (
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Score Trend</h2>
          <ScoreChart trend={stats.score_trend} />
        </div>
      )}

      {/* Session List */}
      {history && (
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>
            Sessions ({history.total} total)
          </h2>

          {history.records.length === 0 ? (
            <p style={styles.empty}>No practice sessions yet. Start practicing!</p>
          ) : (
            <>
              {history.records.map((rec) => (
                <SessionCard key={rec.id} record={rec} />
              ))}

              {/* Pagination */}
              {history.total_pages > 1 && (
                <div style={styles.pagination}>
                  <button
                    style={styles.pageBtn}
                    disabled={page <= 1}
                    onClick={() => goToPage(page - 1)}
                  >
                    Previous
                  </button>
                  <span style={styles.pageInfo}>
                    Page {history.page} of {history.total_pages}
                  </span>
                  <button
                    style={styles.pageBtn}
                    disabled={page >= history.total_pages}
                    onClick={() => goToPage(page + 1)}
                  >
                    Next
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </main>
  );
}

/* ================= Styles ================= */

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: 800,
    margin: "auto",
    padding: 20,
    fontFamily: "Arial, sans-serif",
  },
  nav: {
    marginBottom: 24,
  },
  navLink: {
    color: "#2196f3",
    textDecoration: "none",
    fontSize: 14,
    fontWeight: 500,
  },
  title: {
    margin: "8px 0 0",
    fontSize: 24,
  },
  /* Stats bar */
  statsBar: {
    display: "flex",
    flexWrap: "wrap",
    gap: 12,
    marginBottom: 24,
  },
  statBox: {
    flex: "1 1 120px",
    background: "#f5f5f5",
    borderRadius: 8,
    padding: "14px 12px",
    textAlign: "center",
  },
  statValue: {
    fontSize: 22,
    fontWeight: 700,
    color: "#333",
  },
  statLabel: {
    fontSize: 12,
    color: "#777",
    marginTop: 4,
  },
  /* Chart */
  section: {
    marginBottom: 28,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 12,
  },
  chartContainer: {
    background: "#fafafa",
    borderRadius: 8,
    padding: 16,
    border: "1px solid #e0e0e0",
  },
  chartEmpty: {
    textAlign: "center",
    color: "#999",
    padding: 20,
  },
  legend: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    fontSize: 13,
    marginTop: 8,
    color: "#555",
  },
  legendDot: {
    display: "inline-block",
    width: 10,
    height: 10,
    borderRadius: "50%",
  },
  /* Session cards */
  sessionCard: {
    border: "1px solid #e0e0e0",
    borderRadius: 8,
    marginBottom: 12,
    padding: 14,
    cursor: "pointer",
    transition: "box-shadow 0.15s",
  },
  sessionHeader: {
    display: "flex",
    alignItems: "flex-start",
    gap: 14,
  },
  thumbnail: {
    width: 80,
    height: 60,
    objectFit: "cover",
    borderRadius: 6,
    border: "1px solid #ddd",
    flexShrink: 0,
  },
  sessionInfo: {
    flex: 1,
    minWidth: 0,
  },
  sessionDate: {
    fontSize: 13,
    color: "#777",
    marginBottom: 2,
  },
  difficultyBadge: {
    display: "inline-block",
    background: "#e3f2fd",
    color: "#1565c0",
    fontSize: 11,
    padding: "2px 8px",
    borderRadius: 10,
    marginBottom: 4,
  },
  sessionScores: {
    display: "flex",
    gap: 14,
    marginBottom: 4,
    fontSize: 14,
  },
  scoreRel: {
    color: "#4caf50",
    fontWeight: 600,
  },
  scoreFlu: {
    color: "#2196f3",
    fontWeight: 600,
  },
  sessionSnippet: {
    fontSize: 13,
    color: "#555",
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap" as const,
  },
  expandIcon: {
    fontSize: 12,
    color: "#999",
    flexShrink: 0,
    marginTop: 4,
  },
  /* Expanded feedback */
  feedbackExpanded: {
    marginTop: 14,
    borderTop: "1px solid #eee",
    paddingTop: 12,
    textAlign: "left",
  },
  feedbackSection: {
    marginBottom: 10,
  },
  feedbackH4: {
    margin: "0 0 4px",
    fontSize: 14,
    fontWeight: 600,
  },
  fullTranscription: {
    background: "#f9f9f9",
    padding: 10,
    borderRadius: 6,
    fontSize: 13,
    lineHeight: 1.5,
  },
  /* Pagination */
  pagination: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    marginTop: 16,
  },
  pageBtn: {
    padding: "8px 16px",
    fontSize: 14,
    background: "#2196f3",
    color: "white",
    border: "none",
    borderRadius: 5,
    cursor: "pointer",
  },
  pageInfo: {
    fontSize: 14,
    color: "#555",
  },
  empty: {
    textAlign: "center",
    color: "#999",
    padding: 40,
  },
};
