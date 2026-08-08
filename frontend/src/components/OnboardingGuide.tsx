import ReactMarkdown from "react-markdown";

interface Props {
  guide: string;
}

export default function OnboardingGuide({ guide }: Props) {
  return (
    <div className="bg-panel border border-white/10 rounded-lg p-6 h-full overflow-y-auto prose prose-invert prose-sm max-w-none">
      <ReactMarkdown>{guide}</ReactMarkdown>
    </div>
  );
}