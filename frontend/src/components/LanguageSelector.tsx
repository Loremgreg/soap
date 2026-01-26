/**
 * Language selector component for switching between FR/DE/EN.
 */

import { useTranslation } from 'react-i18next';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { supportedLanguages, languageNames, type SupportedLanguage } from '@/i18n/config';

/**
 * Dropdown component for selecting the app language.
 *
 * Features:
 * - Displays current language
 * - Shows all supported languages (FR/DE/EN)
 * - Persists selection to localStorage via i18next
 * - Mobile-friendly with 44px min touch target
 */
export function LanguageSelector() {
  const { i18n } = useTranslation();

  const currentLanguage = (i18n.language?.substring(0, 2) || 'fr') as SupportedLanguage;

  const handleLanguageChange = (value: string) => {
    i18n.changeLanguage(value);
  };

  return (
    <Select value={currentLanguage} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-[120px] min-h-[44px]">
        <SelectValue>
          {languageNames[currentLanguage] || languageNames.fr}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {supportedLanguages.map((lang) => (
          <SelectItem key={lang} value={lang} className="min-h-[44px]">
            {languageNames[lang]}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
