import { useCallback, useRef, useState } from "react";

interface Props {
  onFile: (file: File) => void;
  disabled?: boolean;
}

export default function DropZone({ onFile, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (file && file.name.toLowerCase().endsWith(".csv")) {
        onFile(file);
      }
    },
    [onFile],
  );

  return (
    <div
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        if (!disabled) handleFiles(e.dataTransfer.files);
      }}
      className={`grid cursor-pointer place-items-center rounded-lg border-2 border-dashed p-10 text-center transition-colors ${
        dragOver
          ? "border-accent bg-accent/10"
          : "border-ink-line bg-ink-soft hover:border-accent/50"
      } ${disabled ? "pointer-events-none opacity-60" : ""}`}
    >
      <div>
        <div className="text-3xl">⇪</div>
        <p className="mt-3 text-sm text-slate-200">
          Drop a CSV here, or click to browse
        </p>
        <p className="mt-1 text-xs text-ink-mute">
          Must contain the 20 CICIDS feature columns · max 50 MB
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        className="hidden"
        onChange={(e) => handleFiles(e.target.files)}
      />
    </div>
  );
}
