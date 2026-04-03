// Types
export interface Observation {
  periodKey: string;    // e.g. "2026_q1"
  periodLabel: string;  // e.g. "Q1 2026"
  rg8: number | null;
  rg10: number | null;
  rg12: number | null;
  trend: '++' | '+' | '=' | '-' | '--' | null;
  marketCap?: number;
  bookEquity?: number;
  netIncome?: number;
  fundamentalBaseApprox?: number;
  note?: string;
}

export interface Company {
  company: string;
  ticker: string;
  slug: string;
  sector: string;
  currency: string;
  description?: string;
  observations: Observation[];
}

/**
 * Parse periodKey "2026_q1" -> sortable number (e.g. 20261)
 */
export function parsePeriodKey(key: string): number {
  const match = key.match(/^(\d{4})_q(\d)$/i);
  if (!match) return 0;
  return parseInt(match[1]!) * 10 + parseInt(match[2]!);
}

/**
 * Get latest observation by sorting periodKey descending
 */
export function getLatestObservation(company: Company): Observation | null {
  if (!company.observations || company.observations.length === 0) return null;
  const sorted = [...company.observations].sort(
    (a, b) => parsePeriodKey(b.periodKey) - parsePeriodKey(a.periodKey)
  );
  return sorted[0] ?? null;
}

/**
 * Format RG display label: "RG10 Q1 2026"
 */
export function formatRGLabel(variant: 8 | 10 | 12, periodLabel: string): string {
  return `RG${variant} ${periodLabel}`;
}

/**
 * Format number for display (market cap in billions, e.g. "$1,353B")
 */
export function formatMarketCap(value: number | undefined): string {
  if (value === undefined || value === null) return '—';
  return `$${value.toLocaleString('en-US')}B`;
}

/**
 * Format RG value with 1 decimal, or "—" if null/undefined
 */
export function formatRG(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return value.toFixed(1);
}

/**
 * Get trend label in English
 */
export function getTrendLabel(trend: string | null | undefined): string {
  switch (trend) {
    case '++': return 'Strongly Increasing';
    case '+':  return 'Increasing';
    case '=':  return 'Stable';
    case '-':  return 'Declining';
    case '--': return 'Strongly Declining';
    default:   return '—';
  }
}
