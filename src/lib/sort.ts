import type { Company, Observation } from './rg';
import { getLatestObservation, parsePeriodKey } from './rg';

/**
 * Generic sort helper — sorts array by a key extractor, ascending or descending.
 */
export function sortBy<T>(
  arr: T[],
  keyFn: (item: T) => number | string | null | undefined,
  direction: 'asc' | 'desc' = 'asc'
): T[] {
  return [...arr].sort((a, b) => {
    const va = keyFn(a) ?? (direction === 'asc' ? Infinity : -Infinity);
    const vb = keyFn(b) ?? (direction === 'asc' ? Infinity : -Infinity);
    if (va < vb) return direction === 'asc' ? -1 : 1;
    if (va > vb) return direction === 'asc' ? 1 : -1;
    return 0;
  });
}

/**
 * Sort companies by their latest RG10 value, descending (highest first).
 * Companies with no RG10 value are placed at the end.
 */
export function sortByRG10Desc(companies: Company[]): Company[] {
  return sortBy(
    companies,
    (c) => {
      const obs = getLatestObservation(c);
      return obs?.rg10 ?? null;
    },
    'desc'
  );
}

/**
 * Sort companies alphabetically by sector, then by company name.
 */
export function sortBySector(companies: Company[]): Company[] {
  return [...companies].sort((a, b) => {
    const sectorCmp = a.sector.localeCompare(b.sector);
    if (sectorCmp !== 0) return sectorCmp;
    return a.company.localeCompare(b.company);
  });
}

/**
 * Sort observations by periodKey descending (latest first).
 */
export function sortObservationsDesc(observations: Observation[]): Observation[] {
  return [...observations].sort(
    (a, b) => parsePeriodKey(b.periodKey) - parsePeriodKey(a.periodKey)
  );
}
