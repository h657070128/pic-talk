/**
 * Tests for the main Home page component (app/page.tsx).
 *
 * Covers:
 *  - Initial rendering and task fetching
 *  - Recording flow (start/stop)
 *  - Error handling for API failures
 *  - Conditional UI rendering based on state
 *  - Next Image button
 */
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import Home from "../app/page";

/* ==================== Mocks ==================== */

const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock MediaRecorder
const mockStop = jest.fn();
const mockStart = jest.fn();
let capturedOndataavailable: ((e: any) => void) | null = null;
let capturedOnstop: (() => void) | null = null;

class MockMediaRecorder {
  ondataavailable: ((e: any) => void) | null = null;
  onstop: (() => void) | null = null;

  start() {
    mockStart();
  }
  stop() {
    mockStop();
    if (this.ondataavailable) {
      this.ondataavailable({ data: new Blob(["audio"], { type: "audio/wav" }) });
    }
    if (this.onstop) {
      this.onstop();
    }
  }
}

(global as any).MediaRecorder = MockMediaRecorder;

// Mock getUserMedia
const mockTrackStop = jest.fn();
const mockGetUserMedia = jest.fn();

Object.defineProperty(global.navigator, "mediaDevices", {
  value: { getUserMedia: mockGetUserMedia },
  writable: true,
  configurable: true,
});

// Mock alert
const mockAlert = jest.fn();
global.alert = mockAlert;

/* ==================== Fixtures ==================== */

const sampleTask = {
  id: 1,
  semantic_plan: '{"scene": "park"}',
  image_url: "https://example.com/test-image.png",
  standard_answer: "A child plays in the park.",
  difficulty: "beginner",
  created_at: "2024-01-01T00:00:00",
};

const sampleResult = {
  id: 10,
  asr_text: "child playing in park",
  relevance_score: 85,
  fluency_score: 70,
  ai_feedback: {
    relevance_score: 85,
    fluency_score: 70,
    summary: "Good attempt at describing the image.",
    strengths: ["Identified main subject"],
    issues: ["Missing details"],
    suggestions: ["Add more adjectives"],
  },
  created_at: "2024-01-02T00:00:00",
};

function setupFetchTaskSuccess() {
  mockFetch.mockResolvedValue({
    ok: true,
    json: async () => sampleTask,
  });
}

function setupFetchTaskFailure() {
  mockFetch.mockResolvedValue({
    ok: false,
    status: 500,
  });
}

/* ==================== Tests ==================== */

beforeEach(() => {
  jest.clearAllMocks();
});

describe("Home Page", () => {
  describe("Initial rendering", () => {
    it("renders the page title", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });
      expect(screen.getByText(/Pic-Talk/)).toBeTruthy();
    });

    it("fetches a task on mount", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          "http://127.0.0.1:8000/api/image/get_random_task"
        );
      });
    });

    it("displays the task image after loading", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        const img = screen.getByAltText("practice") as HTMLImageElement;
        expect(img).toBeTruthy();
        expect(img.src).toBe(sampleTask.image_url);
      });
    });

    it("displays difficulty level", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText(/beginner/i)).toBeTruthy();
      });
    });
  });

  describe("Buttons", () => {
    it("shows Start Recording and Next Image buttons", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText(/Start Recording/)).toBeTruthy();
        expect(screen.getByText(/Next Image/)).toBeTruthy();
      });
    });
  });

  describe("Next Image", () => {
    it("fetches new task when Next Image is clicked", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(1);
      });

      await act(async () => {
        fireEvent.click(screen.getByText(/Next Image/));
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe("Recording", () => {
    it("switches to Stop Recording button when recording starts", async () => {
      setupFetchTaskSuccess();
      const mockStream = {
        getTracks: () => [{ stop: mockTrackStop }],
      };
      mockGetUserMedia.mockResolvedValue(mockStream);

      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText(/Start Recording/)).toBeTruthy();
      });

      await act(async () => {
        fireEvent.click(screen.getByText(/Start Recording/));
      });

      await waitFor(() => {
        expect(screen.getByText(/Stop Recording/)).toBeTruthy();
      });
      expect(mockGetUserMedia).toHaveBeenCalledWith({ audio: true });
    });

    it("shows alert when microphone permission is denied", async () => {
      setupFetchTaskSuccess();
      mockGetUserMedia.mockRejectedValue(new Error("Permission denied"));

      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.getByText(/Start Recording/)).toBeTruthy();
      });

      await act(async () => {
        fireEvent.click(screen.getByText(/Start Recording/));
      });

      await waitFor(() => {
        expect(mockAlert).toHaveBeenCalledWith("Microphone permission denied");
      });
    });
  });

  describe("Error handling", () => {
    it("shows alert on fetch task failure", async () => {
      setupFetchTaskFailure();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(mockAlert).toHaveBeenCalledWith("Failed to load task");
      });
    });

    it("shows alert on network error", async () => {
      mockFetch.mockRejectedValue(new Error("Network error"));
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(mockAlert).toHaveBeenCalledWith("Failed to load task");
      });
    });
  });

  describe("Feedback display", () => {
    it("does not show feedback section initially", async () => {
      setupFetchTaskSuccess();
      await act(async () => {
        render(<Home />);
      });

      await waitFor(() => {
        expect(screen.queryByText(/AI Feedback/)).toBeNull();
        expect(screen.queryByText(/ASR text/)).toBeNull();
      });
    });
  });
});
