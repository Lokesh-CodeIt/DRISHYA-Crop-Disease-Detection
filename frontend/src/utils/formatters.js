/**
 * formatters.js - DRISHYA Multilingual Formatting & Condition Mapping Layer
 *
 * Implements:
 * 1. BCP-47 locale-aware date, time, and number formatting (Intl API)
 * 2. Stable ML class display name mapping (preserves backend class_to_idx)
 */

export const LOCALE_CONFIG = {
  en: { code: 'en', label: 'English', bcp47: 'en-IN' },
  hi: { code: 'hi', label: 'हिन्दी', bcp47: 'hi-IN' },
  mr: { code: 'mr', label: 'मराठी', bcp47: 'mr-IN' },
};

/**
 * Returns BCP-47 locale tag for standard Intl formatting
 */
export function getBcp47Locale(langCode = 'en') {
  return LOCALE_CONFIG[langCode]?.bcp47 || 'en-IN';
}

/**
 * Formats a date using Intl.DateTimeFormat
 * @param {Date|string|number} date
 * @param {string} langCode - 'en', 'hi', or 'mr'
 * @param {Intl.DateTimeFormatOptions} options
 */
export function formatDate(date, langCode = 'en', options = {}) {
  if (!date) return '';
  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d.getTime())) return '';

  const defaultOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...options,
  };

  try {
    return new Intl.DateTimeFormat(getBcp47Locale(langCode), defaultOptions).format(d);
  } catch (e) {
    return d.toLocaleDateString();
  }
}

/**
 * Formats a time string (e.g. 10:30 AM)
 */
export function formatTime(date, langCode = 'en') {
  if (!date) return '';
  const d = date instanceof Date ? date : new Date(date);
  if (isNaN(d.getTime())) return '';

  try {
    return new Intl.DateTimeFormat(getBcp47Locale(langCode), {
      hour: '2-digit',
      minute: '2-digit',
    }).format(d);
  } catch (e) {
    return d.toLocaleTimeString();
  }
}

/**
 * Formats numbers according to Indian locale standard
 */
export function formatNumber(number, langCode = 'en', options = {}) {
  if (number === null || number === undefined || isNaN(number)) return '';
  try {
    return new Intl.NumberFormat(getBcp47Locale(langCode), options).format(number);
  } catch (e) {
    return String(number);
  }
}

/**
 * Normalizes ML model raw class labels into stable i18n condition keys
 * Examples:
 *   ('turmeric', 'Dry Leaf') -> 'condition.turmeric.dry_leaf'
 *   ('citrus', 'Citrus Canker') -> 'condition.citrus.citrus_canker'
 *   ('citrus', 'Swallowtail Larval Herbivory (Deficiency)') -> 'condition.citrus.swallowtail_larval_herbivory'
 */
export function mapConditionToKey(crop, rawClassName) {
  if (!crop || !rawClassName) return '';

  const cleanCrop = crop.toLowerCase().trim();
  let normalizedClass = rawClassName
    .toLowerCase()
    .replace(/\s*\(.*?\)\s*/g, '') // remove parenthetical suffixes like (Deficiency)
    .replace(/[^a-z0-9]+/g, '_')   // replace non-alphanumeric with underscore
    .replace(/^_+|_+$/g, '');       // trim leading/trailing underscores

  return `condition.${cleanCrop}.${normalizedClass}`;
}

/**
 * Translates an ML condition name using the mapping layer without altering model outputs
 * Falls back to raw class name if key is missing or unmapped
 * @param {string} crop
 * @param {string} rawClassName
 * @param {Function} t - i18next translation function
 */
export function getConditionDisplayName(crop, rawClassName, t) {
  if (!rawClassName) return '';
  if (!t || typeof t !== 'function') return rawClassName;

  const key = mapConditionToKey(crop, rawClassName);
  if (!key) return rawClassName;

  const translated = t(key, { defaultValue: rawClassName });
  return translated || rawClassName;
}
