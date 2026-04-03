/**
 * Format a number with fixed decimal places and locale-aware thousands separators.
 */
export function formatNumber(
  value: number | null | undefined,
  decimals = 2,
  locale = 'en-US'
): string {
  if (value === null || value === undefined) return '—';
  return value.toLocaleString(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Format a number as a percentage string (e.g. 0.123 -> "12.3%").
 * Multiplies by 100 unless `alreadyPercent` is true.
 */
export function formatPercent(
  value: number | null | undefined,
  decimals = 1,
  alreadyPercent = false,
  locale = 'en-US'
): string {
  if (value === null || value === undefined) return '—';
  const pct = alreadyPercent ? value : value * 100;
  return (
    pct.toLocaleString(locale, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }) + '%'
  );
}

/**
 * Format a currency amount in billions.
 */
export function formatBillions(
  value: number | null | undefined,
  currency = 'USD',
  locale = 'en-US'
): string {
  if (value === null || value === undefined) return '—';
  const symbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : currency === 'KRW' ? '₩' : currency + ' ';
  return `${symbol}${value.toLocaleString(locale, { minimumFractionDigits: 0, maximumFractionDigits: 1 })}B`;
}
