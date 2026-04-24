import type { CategoryScore } from '../types';

function statusIcon(status: string) {
  switch (status) {
    case 'pass': return <span className="text-green-600">&#10003;</span>;
    case 'fail': return <span className="text-red-600">&#10007;</span>;
    case 'warn': return <span className="text-amber-500">&#9888;</span>;
    default:     return <span className="text-gray-400">&mdash;</span>;
  }
}

interface Props {
  category: CategoryScore;
}

export default function CategoryCard({ category }: Props) {
  return (
    <div className="border border-[var(--color-border)] rounded-lg bg-white p-5 animate-fade-in-up">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-lg">{category.name}</h3>
        <span className="text-sm font-medium text-[var(--color-muted)]">
          {Math.round(category.score)} / {category.max_score}
        </span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 mb-4">
        <div
          className="h-2 rounded-full transition-all duration-700"
          style={{
            width: `${(category.score / category.max_score) * 100}%`,
            backgroundColor: category.score >= 80 ? '#16a34a'
              : category.score >= 60 ? '#ca8a04' : '#dc2626',
          }}
        />
      </div>
      <ul className="space-y-2">
        {category.checks.map((check) => (
          <li key={check.id} className="flex items-start gap-2 text-sm">
            <span className="mt-0.5 flex-shrink-0">{statusIcon(check.status)}</span>
            <div>
              <span className="font-medium">{check.name}</span>
              <span className="text-[var(--color-muted)] ml-1">— {check.message}</span>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
