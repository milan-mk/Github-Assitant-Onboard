interface Props {
  files: string[];
  highlighted: string[];
}

export default function FileTree({ files, highlighted }: Props) {
  return (
    <div className="bg-panel border border-white/10 rounded-lg p-4 h-full overflow-y-auto">
      <h3 className="font-heading text-sm text-white/60 mb-3 uppercase tracking-wide">
        File tree ({files.length})
      </h3>
      <ul className="space-y-1 text-sm font-mono">
        {files.map((f) => (
          <li
            key={f}
            className={highlighted.includes(f) ? "text-accent font-medium" : "text-white/70"}
          >
            {f}
          </li>
        ))}
      </ul>
    </div>
  );
}