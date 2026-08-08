import { useState } from "react";

interface Props {
  onSubmit: (url: string) => void;
  loading: boolean;
}

export default function RepoInput({ onSubmit, loading }: Props) {
  const [url, setUrl] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) onSubmit(url.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 w-full max-w-2xl">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://github.com/owner/repo"
        className="flex-1 bg-panel border border-white/10 rounded-lg px-4 py-3 text-sm
                   focus:outline-none focus:ring-2 focus:ring-accent"
      />
      <button
        type="submit"
        disabled={loading}
        className="bg-accent hover:opacity-90 disabled:opacity-50 transition
                   px-5 py-3 rounded-lg font-heading text-sm font-medium"
      >
        {loading ? "Analyzing..." : "Analyze"}
      </button>
    </form>
  );
}