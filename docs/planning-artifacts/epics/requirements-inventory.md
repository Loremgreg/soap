# Requirements Inventory

## Functional Requirements

**Authentification & Onboarding:**
- FR1: OAuth Google authentification (connexion en 1 clic)
- FR2: Sélection de plan (Starter 29€/mois ou Pro 49€/mois) avec trial 7 jours
- FR3: Trial gratuit 7 jours limité à 10 visites maximum

**Recording & Transcription:**
- FR4: Recording live avec indicateur visuel simple (pas de transcription visible pendant)
- FR5: Durée maximum d'enregistrement : 10 minutes
- FR6: Wake Lock API pour empêcher verrouillage écran pendant recording
- FR7: Stop déclenche la transcription instantanément disponible (Deepgram WebSocket streaming)

**Extraction SOAP:**
- FR8: Extraction SOAP via Mistral AI en < 30 secondes après Stop
- FR9: Note structurée en 4 sections : Subjective, Objective, Assessment (Clinical Reasoning), Plan

**Édition & Copie:**
- FR10: Affichage et édition de la note SOAP post-génération
- FR11: Auto-save des modifications (toutes les 2 secondes)
- FR12: Copier note complète dans presse-papier (1 bouton)
- FR13: Copier sections individuelles (S/O/A/P) dans presse-papier

**Historique:**
- FR14: Note sauvegardée dans historique (max 10 notes avec suppression rolling)
- FR15: Accès à l'historique des 10 dernières notes

**Multilingue:**
- FR16: Support 3 langues : Français, Allemand, Anglais
- FR17: Détection automatique de langue disponible (option Auto)
- FR18: Scripts de consentement patient disponibles (FR/DE/EN) dans tooltip

**Quotas & Paiement:**
- FR19: Dashboard avec compteur visites restantes en temps réel
- FR20: Quotas par plan : Trial (5), Starter (20/mois), Pro (50/mois)
- FR21: Upsell on-demand : +5 visites (+5€) ou +10 visites (+10€)
- FR22: Blocage upload avec message quand quota atteint + proposition upsell
- FR23: Stripe payment avec anniversary billing (cycle basé sur date d'inscription)

**Protection & Limites:**
- FR24: Rate limiting : max 10 uploads/heure/user
- FR25: Hard limit audio : 10 minutes maximum par enregistrement

**Interface:**
- FR26: Interface web responsive mobile-first (PWA)
- FR27: Bottom navigation : Home (Record) / History / Settings
- FR28: Sélecteur de langue visible dans Settings

**Administration & Conformité:**
- FR29: Dashboard admin avec métriques business (users, MRR, visites) et techniques (latence, erreurs)
- FR30: API suppression compte complète (droit à l'oubli RGPD Art. 17)

## Non-Functional Requirements

**Performance:**
- NFR1: Latence totale génération note < 30 secondes après Stop (CRITIQUE)
- NFR2: Qualité perçue : User satisfaction ≥ 4/5

**Disponibilité:**
- NFR3: 99% uptime cible

**Sécurité & Conformité RGPD (Art. 9):**
- NFR4: Chiffrement transit TLS 1.3
- NFR5: Chiffrement repos PostgreSQL (données EU uniquement)
- NFR6: Localisation données : Serveurs EU uniquement (Neon Frankfurt, Railway EU)
- NFR7: Rétention audio : 0 jours (suppression immédiate post-transcription)
- NFR8: Rétention notes : Max 10 dernières notes (suppression rolling)
- NFR9: Droit à l'oubli : API de suppression complète sur demande

**Monitoring:**
- NFR10: Sentry pour erreurs et alertes
- NFR11: Métriques latence pour validation < 30s en production

**Accessibilité:**
- NFR12: Touch targets minimum 44x44px (iOS guidelines)
- NFR13: Support navigateurs : iOS Safari 14+, Chrome 90+, Firefox 88+

## Additional Requirements

**From Architecture - Starter/Setup:**
- ARCH1: Frontend setup avec Vite + React + TypeScript + TailwindCSS + shadcn/ui
- ARCH2: Backend setup avec Python FastAPI (async) + SQLAlchemy 2.0 + Pydantic v2
- ARCH3: Database Neon (PostgreSQL Serverless EU - Frankfurt)
- ARCH4: Alembic pour migrations DB
- ARCH5: Authlib + JWT + httpOnly Cookie pour authentification

**From Architecture - State Management:**
- ARCH6: Zustand pour état local (isRecording, etc.)
- ARCH7: TanStack Query pour données serveur avec cache
- ARCH8: TanStack Router pour routing type-safe
- ARCH9: React Hook Form pour formulaires

**From Architecture - External Services:**
- ARCH10: Deepgram nova-3 WebSocket streaming pour STT
- ARCH11: Mistral AI (mistral-large-2) avec abstraction switchable vers Azure OpenAI
- ARCH12: Stripe pour paiements + webhooks
- ARCH13: Google OAuth 2.0 pour authentification

**From Architecture - Infrastructure:**
- ARCH14: Hébergement Frontend : Vercel (gratuit)
- ARCH15: Hébergement Backend : Railway (EU region, ~5€/mois)
- ARCH16: CI/CD intégré Vercel/Railway (push GitHub → deploy auto)

**From UX Design:**
- UX1: Mobile-first PWA (portrait prioritaire)
- UX2: Wake Lock API pendant recording
- UX3: Web Audio API pour capture microphone
- UX4: Clipboard API pour copy
- UX5: Bottom navigation (Home/History/Settings)
- UX6: Progressive disclosure (settings cachés par défaut)
- UX7: QuotaWidget toujours visible (sticky header)
- UX8: RecordButton large (80x80px min), centré, pulse animation pendant recording
- UX9: Timer visible pendant recording (HH:MM:SS)
- UX10: SOAPEditor avec 4 sections éditables + boutons Copy individuels
- UX11: Toast notifications pour feedback (Copy success, auto-save)
- UX12: Skeleton loaders pendant génération note
- UX13: ConsentDialog avec scripts multilingues

## FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1 | Epic 1 | OAuth Google |
| FR2 | Epic 1 | Sélection plan Starter/Pro |
| FR3 | Epic 1 | Trial 7 jours |
| FR4 | Epic 2 | Recording live avec indicateur |
| FR5 | Epic 2 | Limite 10 min max |
| FR6 | Epic 2 | Wake Lock API |
| FR7 | Epic 2 | Transcription Deepgram |
| FR8 | Epic 3 | Extraction Mistral < 30s |
| FR9 | Epic 3 | Structure 4 sections SOAP |
| FR10 | Epic 4 | Affichage et édition |
| FR11 | Epic 4 | Auto-save |
| FR12 | Epic 4 | Copy note complète |
| FR13 | Epic 4 | Copy sections individuelles |
| FR14 | Epic 5 | Historique max 10 notes |
| FR15 | Epic 5 | Accès historique |
| FR16 | Epic 6 | Support FR/DE/EN |
| FR17 | Epic 6 | Auto-detect langue |
| FR18 | Epic 6 | Scripts consentement |
| FR19 | Epic 7 | Dashboard quota |
| FR20 | Epic 7 | Quotas par plan |
| FR21 | Epic 7 | Upsell +5/+10 visites |
| FR22 | Epic 7 | Blocage quota + message |
| FR23 | Epic 7 | Stripe anniversary billing |
| FR24 | Epic 7 | Rate limiting |
| FR25 | Epic 7 | Hard limit audio |
| FR26 | Epic 2 | PWA responsive |
| FR27 | Epic 2 | Bottom navigation |
| FR28 | Epic 6 | Language selector |
| FR29 | Epic 8 | Dashboard admin (users, MRR, métriques) |
| FR30 | Epic 8 | API suppression compte (droit à l'oubli RGPD) |

---
