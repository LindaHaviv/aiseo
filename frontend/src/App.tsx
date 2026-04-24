import { useState } from 'react';
import { scanUrl } from './api';
import type { ScanResponse } from './types';
import ScanForm from './components/ScanForm';
import ScoreGauge from './components/ScoreGauge';
import CategoryCard from './components/CategoryCard';
import FixList from './components/FixList';

export default function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleScan(url: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await scanUrl(url);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-[var(--color-border)] bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
               style={{ backgroundColor: 'var(--color-terra)' }}>
            AI
          </div>
          <h1 className="text-xl font-bold tracking-tight">AISEO</h1>
          <span className="text-sm text-[var(--color-muted)] hidden sm:inline">
            AI Agent SEO Score
          </span>
        </div>
      </header>

      {/* Hero / Input */}
      <section className="max-w-5xl mx-auto px-6 pt-16 pb-12 text-center">
        {!result && !loading && (
          <>
            <p className="text-xs font-semibold tracking-widest uppercase text-[var(--color-terra)] mb-3">
              SEO for AI
            </p>
            <h2 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
              Is your site visible to AI agents?
            </h2>
            <p className="text-lg text-[var(--color-muted)] mb-10 max-w-xl mx-auto">
              Paste any URL. Get a score, grade, and actionable fix list for how well
              AI models can find, read, and cite your content.
            </p>
          </>
        )}
        <div className="flex justify-center">
          <ScanForm onScan={handleScan} loading={loading} />
        </div>
        {error && (
          <div className="mt-6 text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3 max-w-2xl mx-auto text-sm">
            {error}
          </div>
        )}
      </section>

      {/* Loading state */}
      {loading && (
        <section className="max-w-5xl mx-auto px-6 pb-12">
          <div className="flex flex-col items-center gap-4 py-12">
            <div className="w-16 h-16 rounded-full border-4 border-[var(--color-terra)] border-t-transparent animate-spin" />
            <p className="text-[var(--color-muted)]">
              Scanning for AI agent accessibility...
            </p>
          </div>
        </section>
      )}

      {/* Results */}
      {result && (
        <section className="max-w-5xl mx-auto px-6 pb-20">
          {/* Score */}
          <div className="flex flex-col items-center mb-12 animate-fade-in-up">
            <p className="text-sm text-[var(--color-muted)] mb-4">
              Results for <span className="font-medium text-[var(--color-ink)]">{result.url}</span>
            </p>
            <ScoreGauge score={result.score} grade={result.grade} />
          </div>

          {/* Categories */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold mb-6">Category Breakdown</h2>
            <div className="grid gap-4 md:grid-cols-2">
              {result.categories.map((cat) => (
                <CategoryCard key={cat.name} category={cat} />
              ))}
            </div>
          </div>

          {/* Fixes */}
          <div>
            <h2 className="text-2xl font-bold mb-2">Fix List</h2>
            <p className="text-[var(--color-muted)] mb-6">
              Prioritised recommendations to boost your AI visibility score.
            </p>
            <FixList fixes={result.fixes} />
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-[var(--color-border)] py-6 text-center text-sm text-[var(--color-muted)]">
        AISEO &mdash; Built to make your site discoverable by AI agents
      </footer>
    </div>
  );
}
