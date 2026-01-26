# Story 1.4: Internationalisation (FR/DE/EN)

Status: done

## Story

As a user,
I want to use the app in my preferred language (French, German, or English),
So that I can understand all UI elements and messages.

## Acceptance Criteria

### AC1: Language Selection
**Given** I am on any page of the app
**When** I click on the language selector
**Then** I can choose between French, German, and English
**And** my choice is persisted in localStorage
**And** the app UI updates immediately without page reload

### AC2: All UI Text Translated
**Given** I have selected a language
**When** I navigate through the app
**Then** all UI text is displayed in my selected language
**Including**: buttons, labels, headings, descriptions, error messages, toasts

### AC3: Default Language Detection
**Given** I open the app for the first time
**When** the app loads
**Then** it detects my browser's preferred language
**And** defaults to French if browser language is not FR/DE/EN

### AC4: Date/Number Formatting
**Given** I have selected a language
**When** dates or numbers are displayed
**Then** they are formatted according to the locale (e.g., 29,00 € vs €29.00)

### AC5: API Error Messages
**Given** the backend returns an error
**When** the error is displayed to the user
**Then** the error message is in the user's selected language

## Tasks / Subtasks

### Task 1: Frontend - i18n Setup (AC: 1, 3)
- [ ] 1.1 Install react-i18next and i18next dependencies
- [ ] 1.2 Create `frontend/src/i18n/config.ts` with i18next configuration
- [ ] 1.3 Create `frontend/src/i18n/locales/` folder structure (fr/, de/, en/)
- [ ] 1.4 Configure language detection (browser, localStorage)
- [ ] 1.5 Wrap App with I18nextProvider in main.tsx
- [ ] 1.6 Write tests for i18n configuration

### Task 2: Frontend - Translation Files (AC: 2)
- [ ] 2.1 Create `fr/common.json` - Common UI elements (buttons, labels)
- [ ] 2.2 Create `fr/auth.json` - Login page, OAuth messages
- [ ] 2.3 Create `fr/billing.json` - Plans, subscriptions, trial
- [ ] 2.4 Create `fr/errors.json` - Error messages
- [ ] 2.5 Duplicate to `de/` folder with German translations
- [ ] 2.6 Duplicate to `en/` folder with English translations

### Task 3: Frontend - Language Selector Component (AC: 1)
- [ ] 3.1 Create `frontend/src/components/LanguageSelector.tsx` component
- [ ] 3.2 Add dropdown with flag icons or language codes (FR/DE/EN)
- [ ] 3.3 Persist selection to localStorage
- [ ] 3.4 Add to app header/navbar (visible on all pages)
- [ ] 3.5 Style with TailwindCSS (mobile-friendly, min 44x44px touch target)

### Task 4: Frontend - Migrate Auth Components (AC: 2)
- [ ] 4.1 Update `LoginPage.tsx` - Replace hardcoded FR text with t() calls
- [ ] 4.2 Update `GoogleLoginButton.tsx` - Translate button text
- [ ] 4.3 Update `ProtectedRoute.tsx` - Translate loading states
- [ ] 4.4 Update auth-related toasts in `useAuth.ts`

### Task 5: Frontend - Migrate Billing Components (AC: 2)
- [ ] 5.1 Update `plan-selection.tsx` - All headings, descriptions
- [ ] 5.2 Update `PlanCard.tsx` - Plan details, button text
- [ ] 5.3 Update `PlanSelector.tsx` - Error states, empty states
- [ ] 5.4 Update `TrialBadge.tsx` - Badge text
- [ ] 5.5 Update `TrialExpiredModal.tsx` - Modal content
- [ ] 5.6 Update `useSubscription.ts` - Toast messages

### Task 6: Frontend - Migrate Home & Common (AC: 2)
- [ ] 6.1 Update `index.tsx` (home) - All text content
- [ ] 6.2 Update any shared UI components with text
- [ ] 6.3 Update toast notifications throughout app

### Task 7: Frontend - Date/Number Formatting (AC: 4)
- [ ] 7.1 Create `frontend/src/lib/formatters.ts` with locale-aware formatters
- [ ] 7.2 Implement `formatPrice(cents, locale)` - Currency formatting
- [ ] 7.3 Implement `formatDate(date, locale)` - Date formatting
- [ ] 7.4 Update `PlanCard.tsx` to use formatPrice
- [ ] 7.5 Update any date displays to use formatDate

### Task 8: Testing & Validation (AC: 1, 2, 3, 4, 5)
- [ ] 8.1 Test language switching in all 3 languages
- [ ] 8.2 Test browser language detection
- [ ] 8.3 Test localStorage persistence across sessions
- [ ] 8.4 Test all pages render correctly in each language
- [ ] 8.5 Visual review - ensure no text overflow or layout issues

## Technical Context

### Dependencies to Add
```bash
npm install react-i18next i18next i18next-browser-languagedetector i18next-http-backend
```

### i18n Configuration Pattern
```typescript
// frontend/src/i18n/config.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'fr',
    supportedLngs: ['fr', 'de', 'en'],
    defaultNS: 'common',
    interpolation: {
      escapeValue: false,
    },
  });
```

### Translation Usage Pattern
```tsx
// Before (hardcoded):
<h1>Bienvenue, {name}!</h1>

// After (i18n):
import { useTranslation } from 'react-i18next';
const { t } = useTranslation('billing');
<h1>{t('planSelection.welcome', { name })}</h1>
```

### Folder Structure
```
frontend/src/i18n/
├── config.ts
└── locales/
    ├── fr/
    │   ├── common.json
    │   ├── auth.json
    │   ├── billing.json
    │   └── errors.json
    ├── de/
    │   └── ... (same structure)
    └── en/
        └── ... (same structure)
```

## Dev Agent Record

### Implementation Notes
(To be filled during implementation)

### Decisions Made
- Using react-i18next as the i18n library (standard for React apps)
- Namespace per feature (auth, billing, common) for code splitting
- Browser language detection with French fallback
- localStorage for user preference persistence

### File List

**Frontend - New Files:**
- `frontend/src/i18n/config.ts`
- `frontend/src/i18n/locales/fr/common.json`
- `frontend/src/i18n/locales/fr/auth.json`
- `frontend/src/i18n/locales/fr/billing.json`
- `frontend/src/i18n/locales/fr/errors.json`
- `frontend/src/i18n/locales/de/common.json`
- `frontend/src/i18n/locales/de/auth.json`
- `frontend/src/i18n/locales/de/billing.json`
- `frontend/src/i18n/locales/de/errors.json`
- `frontend/src/i18n/locales/en/common.json`
- `frontend/src/i18n/locales/en/auth.json`
- `frontend/src/i18n/locales/en/billing.json`
- `frontend/src/i18n/locales/en/errors.json`
- `frontend/src/components/LanguageSelector.tsx`
- `frontend/src/lib/formatters.ts`

**Frontend - Modified Files:**
- `frontend/src/main.tsx` - Add I18nextProvider
- `frontend/src/routes/plan-selection.tsx` - Replace hardcoded text
- `frontend/src/routes/index.tsx` - Replace hardcoded text
- `frontend/src/features/auth/pages/LoginPage.tsx` - Replace hardcoded text
- `frontend/src/features/auth/components/GoogleLoginButton.tsx` - Replace hardcoded text
- `frontend/src/features/auth/hooks/useAuth.ts` - Translate toasts
- `frontend/src/features/billing/components/PlanCard.tsx` - Replace hardcoded text
- `frontend/src/features/billing/components/PlanSelector.tsx` - Replace hardcoded text
- `frontend/src/features/billing/components/TrialBadge.tsx` - Replace hardcoded text
- `frontend/src/features/billing/components/TrialExpiredModal.tsx` - Replace hardcoded text
- `frontend/src/features/billing/hooks/useSubscription.ts` - Translate toasts

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-26 | Story created to fulfill MVP requirement for 3 languages (FR/DE/EN) | Dev Agent (Claude Opus 4.5) |
