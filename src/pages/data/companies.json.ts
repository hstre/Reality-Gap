import type { APIRoute } from 'astro';
import type { Company } from '../../lib/rg';
import { getLatestObservation } from '../../lib/rg';
import slugsJson from '../../data/companies.index.json';

export const prerender = true;

export const GET: APIRoute = async () => {
  const slugs: string[] = slugsJson;

  const companies: Company[] = await Promise.all(
    slugs.map(slug =>
      import(`../../data/companies/${slug}.json`).then(m => m.default as Company)
    )
  );

  // Full dataset: all companies with all observations
  const payload = {
    meta: {
      description: 'Reality Gap (RG) dataset. Research use only. Data sourced via yfinance / Yahoo Finance. Not investment advice.',
      author: 'Hanns-Steffen Rentschler',
      generated: new Date().toISOString().slice(0, 10),
      companies: companies.length,
    },
    companies,
  };

  return new Response(JSON.stringify(payload, null, 2), {
    headers: {
      'Content-Type': 'application/json',
      'Content-Disposition': 'attachment; filename="reality-gap-data.json"',
    },
  });
};
