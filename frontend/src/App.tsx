import { useState } from "react";
import RepoInput from "./components/RepoInput";
import FileTree from "./components/FileTree";
import OnboardingGuide from "./components/OnboardingGuide";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface AnalysisResult {
  repo: string;
  file_count: number;
  file_tree: string[];
  key_files_analyzed: string[];
  onboarding_guide: string;
}

function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleAnalyze = async (repoUrl: string) => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_URL}/analyze-repo`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to analyze repo");
      }
      const data: AnalysisResult = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center px-6 py-12">
      <h1 className="font-heading text-3xl font-bold mb-2 text-center">
        GitHub <span className="text-accent">Onboarding</span> Assistant
      </h1>
      <p className="text-white/60 text-sm mb-8 text-center max-w-lg">
        Paste any public GitHub repo URL and get an AI-generated guide to help
        you understand the project and start contributing faster.
      </p>

      <RepoInput onSubmit={handleAnalyze} loading={loading} />

      {error && <p className="text-red-400 text-sm mt-4 max-w-2xl text-center">{error}</p>}

      {result && (
        <div className="w-full max-w-6xl mt-10 grid grid-cols-1 md:grid-cols-2 gap-6 h-[600px]">
          <FileTree files={result.file_tree} highlighted={result.key_files_analyzed} />
          <OnboardingGuide guide={result.onboarding_guide} />
        </div>
      )}
    </div>
  );
}

export default App;