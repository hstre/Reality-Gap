import type { APIRoute } from 'astro';
import type { Company } from '../../lib/rg';
import { getLatestObservation } from '../../lib/rg';
import slugsJson from '../../data/companies.index.json';

export const prerender = true;

function esc(v: string | number | null | undefined): string {
  if (v === null || v === undefined) return '';
  const s = String(v);
  return s.includes(',') || s.includes('"') || s.includes('\n')
    ? `"${s.replace(/"/g, '""')}"` : s;
}

export const GET: APIRoute = async () => {
  const slugs: string[] = slugsJson;

  const companies: Company[] = await Promise.all(
    slugs.map(slug =>
      import(`../../data/companies/${slug}.json`).then(m => m.default as Company)
    )
  );

  const header = [
    'ticker', 'company', 'sector', 'index', 'country', 'currency',
    'period', 'rg8', 'rg10', 'rg12', 'trend',
    'marketCap_bn', 'tangibleEquity_bn', 'smoothedEarnings_bn',
    'fundamentalBaseRG10_bn', 'netIncome_bn',
  ].join(',');

  const rows = companies.map(c => {
    const obs = getLatestObservation(c) as any;
    return [
      esc(c.ticker),
      esc(c.company),
      esc(c.sector),
      esc(c.index),
      esc(c.country),
      esc(c.currency),
      esc(obs?.periodLabel),
      esc(obs?.rg8),
      esc(obs?.rg10),
      esc(obs?.rg12),
      esc(obs?.trend),
      esc(obs?.marketCap),
      esc(obs?.tangibleEquity),
      esc(obs?.smoothedEarnings),
      esc(obs?.fundamentalBaseRG10),
      esc(obs?.netIncome),
    ].join(',');
  });

  const csv = [header, ...rows].join('\r\n');

  return new Response(csv, {
    headers: {
      'Content-Type': 'text/csv; charset=utf-8',
      'Content-Disposition': 'attachment; filename="reality-gap-data.csv"',
    },
  });
};
