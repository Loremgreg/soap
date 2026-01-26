/**
 * i18n configuration for multi-language support (FR/DE/EN).
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import frCommon from './locales/fr/common.json';
import frAuth from './locales/fr/auth.json';
import frBilling from './locales/fr/billing.json';
import frErrors from './locales/fr/errors.json';
import frHome from './locales/fr/home.json';

import deCommon from './locales/de/common.json';
import deAuth from './locales/de/auth.json';
import deBilling from './locales/de/billing.json';
import deErrors from './locales/de/errors.json';
import deHome from './locales/de/home.json';

import enCommon from './locales/en/common.json';
import enAuth from './locales/en/auth.json';
import enBilling from './locales/en/billing.json';
import enErrors from './locales/en/errors.json';
import enHome from './locales/en/home.json';

// Resources object with all translations
const resources = {
  fr: {
    common: frCommon,
    auth: frAuth,
    billing: frBilling,
    errors: frErrors,
    home: frHome,
  },
  de: {
    common: deCommon,
    auth: deAuth,
    billing: deBilling,
    errors: deErrors,
    home: deHome,
  },
  en: {
    common: enCommon,
    auth: enAuth,
    billing: enBilling,
    errors: enErrors,
    home: enHome,
  },
};

/**
 * Supported languages in the app.
 */
export const supportedLanguages = ['fr', 'de', 'en'] as const;
export type SupportedLanguage = (typeof supportedLanguages)[number];

/**
 * Language display names for the language selector.
 */
export const languageNames: Record<SupportedLanguage, string> = {
  fr: 'Français',
  de: 'Deutsch',
  en: 'English',
};

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'fr',
    supportedLngs: supportedLanguages,
    defaultNS: 'common',
    ns: ['common', 'auth', 'billing', 'errors', 'home'],

    // Language detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      lookupLocalStorage: 'i18nextLng',
      caches: ['localStorage'],
    },

    interpolation: {
      escapeValue: false, // React already escapes
    },

    react: {
      useSuspense: false, // Disable suspense for simpler error handling
    },
  });

export default i18n;
