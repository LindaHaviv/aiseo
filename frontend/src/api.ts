import type { ScanResponse } from './types';

const API_BASE = import.meta.env.VITE_API_BASE ?? '';

export async function scanUrl(url: string): Promise<ScanResponse> {
  const resp = await fetch(`${API_BASE}/api/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(text || `Scan failed (HTTP ${resp.status})`);
  }
  return resp.json();
}
