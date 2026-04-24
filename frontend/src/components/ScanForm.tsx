import { useState, type FormEvent } from 'react';

interface Props {
  onScan: (url: string) => void;
  loading: boolean;
}

export default function ScanForm({ onScan, loading }: Props) {
  const [url, setUrl] = useState('');

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = url.trim();
    if (!trimmed) return;
    onScan(trimmed);
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 w-full max-w-2xl">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Enter any URL (e.g. example.com)"
        className="flex-1 px-4 py-3 rounded-lg border border-[var(--color-border)] bg-white text-base focus:outline-none focus:ring-2 focus:ring-[var(--color-terra)] focus:border-transparent"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading || !url.trim()}
        className="px-6 py-3 rounded-lg font-semibold text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        style={{ backgroundColor: 'var(--color-terra)' }}
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <span className="animate-scan-pulse">Scanning</span>
            <span className="animate-spin inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
          </span>
        ) : (
          'Scan'
        )}
      </button>
    </form>
  );
}
