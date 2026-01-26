/**
 * Locale-aware formatting utilities for prices, dates, and numbers.
 */

/**
 * Maps i18n language codes to Intl locale codes.
 */
const localeMap: Record<string, string> = {
  fr: 'fr-FR',
  de: 'de-DE',
  en: 'en-US',
};

/**
 * Gets the Intl locale code from i18n language.
 *
 * @param language - i18n language code (fr, de, en)
 * @returns Intl locale code
 */
function getLocale(language: string): string {
  return localeMap[language] || localeMap.fr;
}

/**
 * Formats a price from cents to locale-aware currency string.
 *
 * @param cents - Price in cents (e.g., 2900 = 29€)
 * @param language - i18n language code
 * @returns Formatted price string (e.g., "29,00 €" or "€29.00")
 *
 * @example
 * formatPrice(2900, 'fr') // "29,00 €"
 * formatPrice(2900, 'en') // "€29.00"
 * formatPrice(2900, 'de') // "29,00 €"
 */
export function formatPrice(cents: number, language: string): string {
  const euros = cents / 100;
  const locale = getLocale(language);

  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: 'EUR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(euros);
}

/**
 * Formats a date to locale-aware string.
 *
 * @param date - Date to format (Date object or ISO string)
 * @param language - i18n language code
 * @param options - Intl.DateTimeFormat options
 * @returns Formatted date string
 *
 * @example
 * formatDate(new Date(), 'fr') // "26 janvier 2026"
 * formatDate(new Date(), 'en') // "January 26, 2026"
 */
export function formatDate(
  date: Date | string,
  language: string,
  options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const locale = getLocale(language);

  return new Intl.DateTimeFormat(locale, options).format(dateObj);
}

/**
 * Formats a number to locale-aware string.
 *
 * @param value - Number to format
 * @param language - i18n language code
 * @returns Formatted number string
 *
 * @example
 * formatNumber(1234.56, 'fr') // "1 234,56"
 * formatNumber(1234.56, 'en') // "1,234.56"
 */
export function formatNumber(value: number, language: string): string {
  const locale = getLocale(language);
  return new Intl.NumberFormat(locale).format(value);
}
