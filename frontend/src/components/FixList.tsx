import { useState } from 'react';
import type { Fix } from '../types';

function priorityBadge(priority: string) {
  const colors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-gray-100 text-gray-700',
  };
  return (
    <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${colors[priority] ?? colors.low}`}>
      {priority}
    </span>
  );
}

function effortBadge(effort: string) {
  return (
    <span className="text-xs text-[var(--color-muted)] border border-[var(--color-border)] px-2 py-0.5 rounded-full">
      {effort} effort
    </span>
  );
}

interface Props {
  fixes: Fix[];
}

export default function FixList({ fixes }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (fixes.length === 0) {
    return (
      <div className="text-center text-[var(--color-muted)] py-8">
        No fixes needed — your site is well optimised for AI agents!
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {fixes.map((fix, i) => (
        <div
          key={fix.id}
          className="border border-[var(--color-border)] rounded-lg bg-white animate-fade-in-up"
          style={{ animationDelay: `${i * 60}ms` }}
        >
          <button
            className="w-full text-left p-4 flex items-center gap-3 cursor-pointer"
            onClick={() => setExpanded(expanded === fix.id ? null : fix.id)}
          >
            <span className="text-lg font-bold text-[var(--color-terra)] w-6">
              {i + 1}
            </span>
            <div className="flex-1 min-w-0">
              <div className="font-medium">{fix.title}</div>
              <div className="flex items-center gap-2 mt-1">
                {priorityBadge(fix.priority)}
                {effortBadge(fix.effort)}
                <span className="text-xs text-green-700 font-medium">
                  +{fix.score_lift} pts
                </span>
              </div>
            </div>
            <span className="text-[var(--color-muted)] text-xl">
              {expanded === fix.id ? '\u2212' : '+'}
            </span>
          </button>
          {expanded === fix.id && (
            <div className="px-4 pb-4 border-t border-[var(--color-border)] pt-3">
              <p className="text-sm text-[var(--color-muted)] mb-3">{fix.description}</p>
              {fix.code_snippet && (
                <pre className="bg-gray-50 border border-gray-200 rounded-md p-3 text-xs overflow-x-auto">
                  <code>{fix.code_snippet}</code>
                </pre>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
