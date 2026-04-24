interface ScoreGaugeProps {
  score: number;
  grade: string;
}

function gradeColor(grade: string): string {
  switch (grade) {
    case 'A': return '#16a34a';
    case 'B': return '#65a30d';
    case 'C': return '#ca8a04';
    case 'D': return '#ea580c';
    case 'F': return '#dc2626';
    default: return '#6b7280';
  }
}

export default function ScoreGauge({ score, grade }: ScoreGaugeProps) {
  const color = gradeColor(grade);
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-40 h-40">
        <svg viewBox="0 0 120 120" className="w-full h-full -rotate-90">
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke="#e5e1dc"
            strokeWidth="8"
          />
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold" style={{ color }}>{Math.round(score)}</span>
          <span className="text-sm text-[var(--color-muted)]">/ 100</span>
        </div>
      </div>
      <div
        className="text-2xl font-bold px-4 py-1 rounded-full text-white"
        style={{ backgroundColor: color }}
      >
        Grade: {grade}
      </div>
    </div>
  );
}
