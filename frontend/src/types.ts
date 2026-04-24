export interface CheckResult {
  id: string;
  name: string;
  category: string;
  status: 'pass' | 'fail' | 'warn' | 'skip';
  message: string;
  score: number;
  weight: number;
}

export interface Fix {
  id: string;
  check_id: string;
  title: string;
  description: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  effort: 'easy' | 'medium' | 'hard';
  score_lift: number;
  code_snippet: string | null;
}

export interface CategoryScore {
  name: string;
  score: number;
  max_score: number;
  checks: CheckResult[];
}

export interface ScanResponse {
  url: string;
  score: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  categories: CategoryScore[];
  fixes: Fix[];
  scanned_at: string;
}
