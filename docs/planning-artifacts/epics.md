---
status: complete
stepsCompleted: ['step-01-validate-prerequisites', 'step-02-design-epics', 'step-03-create-stories', 'step-04-final-validation']
inputDocuments:
  - docs/planning-artifacts/prd.md
  - docs/planning-artifacts/architecture.md
  - docs/planning-artifacts/ux-design-specification.md
  - project-context.md
---

# SOAP Notice - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for SOAP Notice, decomposing the requirements from the PRD, UX Design, and Architecture into implementable stories.

## Requirements Inventory

### Functional Requirements

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

### Non-Functional Requirements

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

### Additional Requirements

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

### FR Coverage Map

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

## Epic List

### Epic 1: Authentification & Onboarding
L'utilisateur peut créer un compte, choisir son plan et démarrer son essai gratuit.

**FRs couverts:** FR1, FR2, FR3
**Valeur livrée:** Se connecter avec Google, choisir Starter/Pro, accéder au trial 7 jours avec 5 visites.

---

### Epic 2: Enregistrement Audio
L'utilisateur peut enregistrer l'audio de ses consultations de manière fiable sur mobile.

**FRs couverts:** FR4, FR5, FR6, FR7, FR26, FR27
**Valeur livrée:** Démarrer un recording, voir le timer, écran reste allumé, arrêter après max 10 min, interface mobile PWA avec bottom navigation.

---

### Epic 3: Génération Note SOAP
L'utilisateur reçoit une note clinique structurée automatiquement à partir de son enregistrement.

**FRs couverts:** FR8, FR9
**Valeur livrée:** Voir sa note SOAP générée en < 30s avec 4 sections (Subjective/Objective/Assessment/Plan).

---

### Epic 4: Édition & Copie de Notes
L'utilisateur peut éditer, affiner et exporter ses notes vers son logiciel métier.

**FRs couverts:** FR10, FR11, FR12, FR13
**Valeur livrée:** Éditer chaque section SOAP, auto-save automatique, copier note complète ou sections individuelles.

---

### Epic 5: Historique des Notes
L'utilisateur peut accéder et gérer ses notes précédentes.

**FRs couverts:** FR14, FR15
**Valeur livrée:** Voir les 10 dernières notes, les rouvrir, les éditer, les copier.

---

### Epic 6: Support Multilingue & Settings
L'utilisateur peut configurer l'application dans sa langue préférée et accéder aux scripts de consentement.

**FRs couverts:** FR16, FR17, FR18, FR28
**Valeur livrée:** Choisir FR/DE/EN/Auto-detect, lire le script consentement patient, ajuster ses préférences dans Settings.

---

### Epic 7: Gestion Quotas & Facturation
L'utilisateur peut surveiller son utilisation, acheter des visites supplémentaires et gérer son abonnement.

**FRs couverts:** FR19, FR20, FR21, FR22, FR23, FR24, FR25
**Valeur livrée:** Voir compteur visites restantes, alertes quota, acheter upsell +5/+10, payer via Stripe, protection rate limiting.

---

### Epic 8: Administration & Conformité RGPD
Le fondateur peut monitorer la plateforme et les utilisateurs peuvent exercer leur droit à l'oubli.

**FRs couverts:** FR29, FR30
**Valeur livrée:** Dashboard admin avec métriques business/techniques, API de suppression complète de compte (RGPD).

---

## Stories

### Epic 1: Authentification & Onboarding

#### Story 1.1: Project Setup & Infrastructure

As a developer,
I want a fully configured project with frontend, backend, and database infrastructure,
So that I can start implementing user-facing features on a solid foundation.

**Acceptance Criteria:**

**Given** a new development environment
**When** the project is cloned and dependencies installed
**Then** the frontend dev server starts on localhost:5173 with Vite + React + TypeScript
**And** shadcn/ui is configured with base components (Button, Card, Toast, Dialog)
**And** TailwindCSS is configured with mobile-first breakpoints (320px, 768px, 1024px)
**And** TanStack Router is configured with type-safe routes

**Given** the backend project structure
**When** the FastAPI server starts
**Then** it runs on localhost:8000 with async support
**And** SQLAlchemy 2.0 async is configured with Pydantic v2 schemas
**And** Alembic migrations are initialized
**And** CORS is configured for frontend origin

**Given** the database configuration
**When** connecting to Neon PostgreSQL
**Then** the connection uses EU region (Frankfurt)
**And** SSL/TLS is enforced
**And** connection pooling is configured

**Given** the deployment configuration
**When** code is pushed to main branch
**Then** frontend auto-deploys to Vercel
**And** backend auto-deploys to Railway EU region
**And** environment variables are properly configured

---

#### Story 1.2: OAuth Google Login

As a physiotherapist,
I want to login with my Google account in one click,
So that I can access the app quickly without creating another password.

**Acceptance Criteria:**

**Given** I am on the login page (unauthenticated)
**When** I click the "Continue with Google" button
**Then** I am redirected to Google OAuth consent screen
**And** the button is large (min 44x44px touch target) and clearly visible

**Given** I complete Google OAuth successfully
**When** I am redirected back to the app
**Then** a JWT is created and stored in httpOnly cookie
**And** a user record is created in the database (if first login)
**And** I am redirected to the plan selection page (if new user) or home (if returning user)

**Given** I am already logged in
**When** I open the app
**Then** I am automatically authenticated via the httpOnly cookie
**And** I see the home screen directly

**Given** the Google OAuth fails or is cancelled
**When** I am redirected back to the app
**Then** I see an error message explaining the issue
**And** I can retry the login

**Given** the user table schema
**When** a new user logs in
**Then** the users table is created with: id, google_id, email, name, avatar_url, created_at, updated_at

---

#### Story 1.3: Plan Selection & Trial Activation

As a new user,
I want to choose my subscription plan and start a free trial,
So that I can test the app before committing to a paid subscription.

**Acceptance Criteria:**

**Given** I am a new user after first Google login
**When** I land on the plan selection page
**Then** I see two plan options clearly displayed:
- **Starter** : 29€/mois, 20 visites/mois
- **Pro** : 49€/mois, 50 visites/mois
**And** both plans show "Essai gratuit 7 jours" badge
**And** the interface is mobile-optimized

**Given** I select a plan (Starter or Pro)
**When** I click "Démarrer l'essai gratuit"
**Then** a subscription record is created with status "trial"
**And** trial_ends_at is set to now + 7 days
**And** my quota is set to 10 visits (trial limit)
**And** I am redirected to the home screen

**Given** the subscription table schema
**When** a trial is activated
**Then** the subscriptions table is created with: id, user_id, plan (starter/pro), status (trial/active/cancelled), quota_remaining, quota_total, trial_ends_at, current_period_start, current_period_end, stripe_customer_id (nullable), stripe_subscription_id (nullable), created_at, updated_at

**Given** I am a returning user with existing subscription
**When** I open the app
**Then** I skip plan selection and go directly to home

**Given** my trial period expires
**When** I open the app
**Then** I see a message prompting me to subscribe
**And** I cannot record until I subscribe or add payment

**Given** the plans configuration table
**When** the system needs plan limits
**Then** the plans table exists with: id, name, price_monthly, quota_monthly, max_recording_minutes, is_active, created_at, updated_at
**And** plan limits (quota, recording duration) are fetched from this table, not hardcoded
**And** frontend retrieves limits via API for easy configurability

---

### Epic 2: Enregistrement Audio

#### Story 2.1: Mobile PWA Shell & Navigation

As a physiotherapist,
I want a mobile-optimized interface with clear navigation,
So that I can use the app efficiently during consultations on my phone or tablet.

**Acceptance Criteria:**

**Given** I open the app on a mobile device
**When** the home screen loads
**Then** I see a mobile-first layout optimized for portrait orientation
**And** a bottom navigation bar with 3 items: Home (icon microphone), History (icon list), Settings (icon gear)
**And** touch targets are minimum 44x44px

**Given** I am on any screen
**When** I tap a bottom nav item
**Then** I navigate to that screen without full page reload
**And** the active nav item is visually highlighted

**Given** the PWA configuration
**When** I add the app to my home screen (Add to Home Screen)
**Then** the app icon and name are displayed correctly
**And** the app opens in standalone mode (no browser chrome)
**And** the manifest.json is properly configured

**Given** I am on the Home screen
**When** the page renders
**Then** the QuotaWidget is visible in the header showing "X/Y visites restantes"
**And** the Record button is prominently centered

---

#### Story 2.2: Audio Recording Interface

As a physiotherapist,
I want to start, pause, and stop audio recording with clear visual feedback,
So that I can reliably capture patient consultations without worrying about the screen locking.

**Acceptance Criteria:**

**Given** I am on the Home screen (not recording)
**When** I see the Record button
**Then** it is large (min 80x80px), centered, with microphone icon
**And** it shows "Record" or microphone icon in idle state

**Given** I have not granted microphone permission
**When** I tap the Record button
**Then** the browser requests microphone permission
**And** if denied, I see an error message explaining how to enable it

**Given** I have microphone permission and internet connection
**When** I tap the Record button
**Then** recording starts immediately
**And** the button changes to show Stop icon (and optionally Pause)
**And** a pulse animation indicates active recording
**And** the Timer starts at 00:00:00 and increments every second
**And** Wake Lock is activated (screen won't lock)

**Given** I am recording
**When** I tap Pause
**Then** recording pauses, timer stops
**And** button shows Resume option
**And** Wake Lock remains active

**Given** I am recording and approach 10 minutes
**When** the timer reaches 09:30
**Then** I see a warning that recording will stop at 10:00

**Given** I am recording
**When** the timer reaches max recording limit (from plans table)
**Then** recording automatically stops
**And** I see a message "Limite atteinte"

**Given** I am recording
**When** I tap Stop
**Then** recording stops
**And** Wake Lock is deactivated
**And** UI transitions to "Processing..." state
**And** audio data is sent to backend

**Given** I lose internet connection while recording
**When** the connection is lost
**Then** I see a warning indicator
**And** recording continues locally
**And** audio will be sent when connection restores (or error on stop)

---

#### Story 2.3: Deepgram Streaming Integration

As a system,
I want to transcribe audio in real-time using Deepgram WebSocket streaming,
So that the transcription is ready immediately when recording stops.

**Acceptance Criteria:**

**Given** a user starts recording
**When** the frontend sends audio chunks to backend
**Then** backend opens a WebSocket connection to Deepgram nova-3
**And** audio is streamed in real-time for transcription
**And** transcription results are accumulated server-side

**Given** the backend receives audio data
**When** processing the stream
**Then** the audio format is validated (WebM/Opus or supported format)
**And** chunked audio is forwarded to Deepgram

**Given** Deepgram returns transcription results
**When** final results are received
**Then** they are stored temporarily for SOAP extraction
**And** audio file is NOT persisted (RGPD: 0 day retention)

**Given** the user stops recording
**When** the final transcription is complete
**Then** the full transcript text is available for the next step (SOAP extraction)
**And** response time from Stop to transcript ready is tracked (target < 5s)

**Given** Deepgram connection fails
**When** an error occurs
**Then** the error is logged to Sentry
**And** user sees an error message with retry option
**And** no partial data is lost if possible

**Given** the recordings table schema
**When** a recording is processed
**Then** the recordings table is created with: id, user_id, duration_seconds, language_detected, transcript_text, created_at
**And** audio binary is NOT stored (deleted immediately after transcription)

---

### Epic 3: Génération Note SOAP

#### Story 3.1: SOAP Note Extraction with Mistral AI

As a physiotherapist,
I want my recorded consultation to be automatically structured into a SOAP note,
So that I save time on documentation and get a professional clinical format.

**Acceptance Criteria:**

**Given** a completed transcription from Deepgram
**When** the backend processes the transcript
**Then** the transcript is sent to Mistral AI (mistral-large-2) with a structured prompt
**And** the prompt instructs extraction into 4 sections: Subjective, Objective, Assessment, Plan
**And** the response is parsed into structured JSON format

**Given** the SOAP note structure template
**When** the prompt is constructed
**Then** it references the structure defined in docs/templates/physiotherapy-note-template.md
**And** the output follows the 4-section format: Subjective, Objective, Clinical Reasoning, Plan

**Given** the Mistral API call
**When** generating the SOAP note
**Then** the total time from Stop button to note displayed is < 30 seconds
**And** latency is logged to metrics for monitoring (NFR11)

**Given** the LLM abstraction layer
**When** Mistral AI is called
**Then** the implementation uses an abstraction that can be switched to Azure OpenAI
**And** the switch requires only configuration change, not code change

**Given** the SOAP note structure
**When** the note is generated
**Then** each section contains:
- **Subjective (S)**: Patient's reported symptoms, history, complaints, functional impact
- **Objective (O)**: Observable findings, measurements, physical examination results
- **Assessment (A)**: Clinical reasoning, diagnosis, contributing factors
- **Plan (P)**: Treatment provided, home program, follow-up plan

**Given** the transcript is in any language (FR/DE/EN/ES/other)
**When** the note is generated
**Then** the note is ALWAYS in the user's app language setting (not the transcript language)
**And** medical terminology is appropriate for the output language
**And** the LLM handles transcription-to-note language translation if needed

**Given** the notes table schema
**When** a note is generated
**Then** the notes table is created with: id, user_id, recording_id, subjective, objective, assessment, plan, language, format (paragraph/bullets), verbosity (concise/medium), created_at, updated_at

**Given** Mistral API fails or times out
**When** an error occurs
**Then** the error is logged to Sentry
**And** user sees a clear error message
**And** retry option is available
**And** the transcript is not lost (can retry extraction)

---

#### Story 3.2: Note Display with Loading States

As a physiotherapist,
I want to see my generated SOAP note with clear loading feedback,
So that I know the system is working and can quickly review my note.

**Acceptance Criteria:**

**Given** I have just stopped a recording
**When** the note is being generated
**Then** I see a skeleton loader for each SOAP section (4 animated placeholders)
**And** a progress message "Génération de la note en cours..."
**And** the UI remains responsive

**Given** the note generation completes successfully
**When** the note is ready
**Then** the skeleton loaders are replaced with actual content
**And** each section (S/O/A/P) is clearly labeled and visually distinct
**And** a success toast appears briefly "Note générée !"

**Given** I view the generated note
**When** the note displays
**Then** I see all 4 sections in order: Subjective, Objective, Assessment, Plan
**And** each section has its label visible (S, O, A, P or full names)
**And** the content is readable with appropriate typography
**And** the layout is optimized for mobile (single column, scrollable)

**Given** the note generation time
**When** I'm waiting
**Then** if > 15 seconds elapsed, I see "Cela prend plus de temps que prévu..."
**And** if > 25 seconds, I see "Presque terminé..."
**And** if > 30 seconds without result, I see an error with retry option

**Given** the quota system
**When** a note is successfully generated
**Then** the user's quota_remaining is decremented by 1
**And** the QuotaWidget updates in real-time

---

### Epic 4: Édition & Copie de Notes

#### Story 4.1: SOAP Note Editor

As a physiotherapist,
I want to edit each section of my generated SOAP note,
So that I can correct any errors and add details before copying to my patient management system.

**Acceptance Criteria:**

**Given** a generated SOAP note is displayed
**When** I view the note
**Then** each section (S/O/A/P) is displayed in an editable textarea
**And** sections are clearly labeled and visually separated
**And** the interface is optimized for mobile editing

**Given** I tap on a section to edit
**When** the section becomes active
**Then** the textarea receives focus
**And** the mobile keyboard appears
**And** the view scrolls so the active section is visible above the keyboard

**Given** I am editing a section
**When** I type changes
**Then** modifications are auto-saved every 2 seconds
**And** a discrete indicator shows "Sauvegardé" after each save
**And** no explicit "Save" button is required

**Given** I am editing and lose connection
**When** auto-save fails
**Then** changes are preserved locally
**And** I see a warning "Connexion perdue - modifications locales"
**And** sync resumes when connection restores

**Given** I want to expand/collapse sections
**When** I tap a section header
**Then** the section expands or collapses (optional feature for long notes)
**And** collapsed sections show a preview of content

**Given** the note update API
**When** auto-save triggers
**Then** only the modified section is sent to backend (PATCH)
**And** updated_at timestamp is refreshed

---

#### Story 4.2: Copy to Clipboard

As a physiotherapist,
I want to copy my note (complete or by section) to my clipboard,
So that I can paste it into my patient management software with one tap.

**Acceptance Criteria:**

**Given** I am viewing a SOAP note
**When** I look at the bottom of the note
**Then** I see a prominent "Copier la note" button (Copy All)
**And** the button has a large touch target (min 44x44px)

**Given** I tap "Copier la note"
**When** the copy action executes
**Then** the complete note is copied to clipboard
**And** format includes all 4 sections with headers (S/O/A/P)
**And** a toast appears "Note copiée !" for 2 seconds
**And** the button briefly shows a checkmark animation

**Given** I want to copy only one section
**When** I view a specific section (e.g., Plan)
**Then** I see a small "Copy" icon/button next to the section header
**And** tapping it copies only that section's content

**Given** I tap a section's Copy button
**When** the copy action executes
**Then** only that section is copied to clipboard
**And** the section header is included (e.g., "Plan: ...")
**And** a toast appears "Section copiée !"

**Given** the clipboard format
**When** content is copied
**Then** the text is plain text (no HTML)
**And** line breaks and formatting are preserved
**And** the format matches user preference (paragraph or bullet points from settings)

**Given** clipboard API is not available (rare browsers)
**When** copy fails
**Then** user sees "Sélectionnez et copiez manuellement"
**And** text is highlighted for easy manual selection

---

### Epic 5: Historique des Notes

#### Story 5.1: Note History List

As a physiotherapist,
I want to see a list of my recent notes,
So that I can quickly find and access a previous consultation.

**Acceptance Criteria:**

**Given** I tap "History" in the bottom navigation
**When** the history screen loads
**Then** I see a list of my notes sorted by date (newest first)
**And** the maximum number of notes is determined by my plan's max_notes_retention setting
**And** the list is scrollable on mobile

**Given** the user's language preference (FR/DE/EN)
**When** any UI text is displayed
**Then** all labels, buttons, and messages are displayed in the selected language

**Given** I view the history list
**When** I look at each note card
**Then** I see:
- Date and time of creation
- Language indicator (FR/DE/EN)
- Preview of Subjective section (first ~50 characters, truncated)
**And** each card is tappable

**Given** I have reached my plan's max_notes_retention limit
**When** a new note is about to be saved
**Then** I see a warning message informing me that the oldest note will be deleted
**And** I can confirm to proceed or cancel
**And** if confirmed, the oldest note is deleted and the new one is saved

**Given** I have no notes yet
**When** I view history
**Then** I see an empty state message
**And** a call-to-action to record first consultation

**Given** the notes list API
**When** the history loads
**Then** only metadata is fetched initially (not full content)
**And** loading is fast (< 1 second)

**Given** the plans table configuration
**When** the system checks retention limits
**Then** max_notes_retention is read from the plans table (not hardcoded)
**And** changing the limit requires only a database update, not code changes

---

#### Story 5.2: Note Detail & Actions

As a physiotherapist,
I want to open a previous note and perform actions on it,
So that I can review, edit, or copy past consultations.

**Acceptance Criteria:**

**Given** I am on the history list
**When** I tap on a note card
**Then** the full note opens in detail view
**And** all 4 sections (S/O/A/P) are displayed
**And** I see a back button to return to history

**Given** I am viewing a past note
**When** the note displays
**Then** the note is in read mode by default
**And** I see edit and copy action buttons
**And** the date/time of the note is visible in the header
**And** all text is in the user's selected language

**Given** I tap the edit button on a past note
**When** edit mode activates
**Then** the note becomes editable (same as Story 4.1)
**And** auto-save works the same way
**And** I can return to read mode or history

**Given** I tap the copy button on a past note
**When** the copy action executes
**Then** the complete note is copied to clipboard (same as Story 4.2)
**And** toast confirms the copy action

**Given** I am viewing a note and want to go back
**When** I tap the back button or swipe back
**Then** I return to the history list
**And** any unsaved edits are auto-saved before navigation

---

### Epic 6: Support Multilingue & Settings

#### Story 6.1: Settings Screen & Language Selection

As a physiotherapist,
I want to configure my language preference and other settings,
So that the app works in my preferred language and matches my workflow.

**Acceptance Criteria:**

**Given** I tap "Settings" in the bottom navigation
**When** the settings screen loads
**Then** I see grouped settings sections
**And** the interface is clean and mobile-optimized

**Given** I view the language settings section
**When** the section displays
**Then** I see options: Français, Deutsch, English, Auto-detect
**And** my current selection is highlighted
**And** "Auto-detect" is the default for new users

**Given** I select a language option (FR/DE/EN)
**When** I tap on a language
**Then** my preference is saved immediately (no save button needed)
**And** the UI updates to the selected language without app reload
**And** future SOAP notes will be generated in this language (regardless of spoken language)

**Given** I select "Auto-detect"
**When** I record a consultation
**Then** Deepgram detects the spoken language automatically
**And** the detected language is used for the SOAP note output

**Given** the language behavior
**When** a recording is in a different language than my app setting
**Then** the transcript is in the spoken language
**And** the SOAP note is generated in my app's configured language
**And** the LLM handles translation during extraction

**Given** the settings persistence
**When** I change a setting
**Then** it is saved to localStorage and synced to backend
**And** settings persist across sessions and devices (if logged in)

**Given** additional settings (future-ready)
**When** I view the settings screen
**Then** I see placeholders or sections for:
- Note format preference (Paragraph / Bullet points)
- Note verbosity (Concise / Medium)
- Account & Subscription (link to Epic 7)
**And** these are configurable if implemented, or show current defaults

---

#### Story 6.2: Patient Consent Scripts

As a physiotherapist,
I want to access patient consent scripts in multiple languages,
So that I can inform my patients about the recording before starting.

**Acceptance Criteria:**

**Given** I am on the Home screen
**When** I look near the Record button
**Then** I see a discrete info icon or link for patient consent
**And** the link is visible but not intrusive

**Given** I tap on the consent info
**When** the consent dialog opens
**Then** I see the consent script in my currently selected language
**And** the dialog is a modal/sheet overlay (not a new page)
**And** I can dismiss it easily

**Given** the consent script content
**When** I read the script
**Then** it explains:
- Audio will be recorded for documentation purposes
- Audio is transcribed and immediately deleted (not stored)
- The note is for clinical documentation only
- Patient can request data deletion
**And** the text is professionally written in FR/DE/EN

**Given** I want to read the script in a different language
**When** I am in the consent dialog
**Then** I see language tabs or selector (FR/DE/EN)
**And** I can switch to show the script in patient's language
**And** this is independent of my app language setting

**Given** the consent scripts storage
**When** the app loads
**Then** consent scripts are stored in a configuration (not hardcoded)
**And** updating script text requires only config/DB change, not code deployment

---

### Epic 7: Gestion Quotas & Facturation

#### Story 7.1: Quota Dashboard & Alerts

As a physiotherapist,
I want to always see my remaining visits and receive alerts when running low,
So that I'm never surprised by quota exhaustion during a busy day.

**Acceptance Criteria:**

**Given** I am logged in and on any screen
**When** the header displays
**Then** I see the QuotaWidget showing "X/Y visites restantes"
**And** it is always visible (sticky header)
**And** X = remaining visits, Y = total for current period

**Given** my quota status
**When** the QuotaWidget renders
**Then** it shows color-coded status:
- Green: > 10 visits remaining
- Orange: 5-10 visits remaining
- Red: < 5 visits remaining
- Gray/blocked: 0 visits remaining

**Given** my quota drops below 5 visits
**When** this threshold is crossed
**Then** I see a toast notification warning me
**And** the warning appears once per session (not repeatedly)

**Given** my quota reaches 0
**When** I try to start a recording
**Then** recording is blocked
**And** I see a clear message explaining quota exhaustion
**And** I see options to upgrade plan or buy more visits

**Given** a new billing period starts
**When** the period resets (anniversary billing)
**Then** my quota resets to plan's monthly allocation
**And** QuotaWidget updates immediately

---

#### Story 7.2: Stripe Subscription & Payment

As a user whose trial is ending,
I want to activate my paid subscription with Stripe,
So that I can continue using the service without interruption.

**Acceptance Criteria:**

**Given** my trial is about to expire (< 3 days remaining)
**When** I open the app
**Then** I see a banner reminding me to activate subscription
**And** the banner includes days remaining and CTA button

**Given** I tap to activate my subscription or access subscription settings
**When** the payment flow starts
**Then** I am redirected to Stripe Checkout (hosted page)
**And** my selected plan (Starter/Pro from trial) is pre-selected
**And** price is clearly displayed (29€/mois or 49€/mois)

**Given** I complete Stripe payment successfully
**When** the webhook confirms payment
**Then** my subscription status changes from "trial" to "active"
**And** my quota is set to plan's full monthly allocation (20 or 50)
**And** anniversary billing cycle starts from this date
**And** I see a confirmation message

**Given** Stripe payment fails
**When** the error occurs
**Then** I see a clear error message
**And** I can retry or use a different payment method
**And** my trial continues until expiration (if still valid)

**Given** I want to change my plan
**When** I access subscription settings
**Then** I see my current plan and option to upgrade/downgrade
**And** changes take effect at next billing cycle

**Given** I want to cancel my subscription
**When** I request cancellation
**Then** I see confirmation of what I will lose
**And** subscription remains active until current period ends
**And** no refund for partial period (standard SaaS policy)

---

#### Story 7.3: Upsell & Additional Visits

As a physiotherapist who has exhausted my quota mid-month,
I want to buy additional visits without waiting for the next billing cycle,
So that I can continue documenting consultations immediately.

**Acceptance Criteria:**

**Given** my quota is low or exhausted
**When** I see the upsell prompt (or access via settings)
**Then** I see two options:
- +5 visits for 5€
- +10 visits for 10€
**And** prices are clearly displayed

**Given** I select an upsell option
**When** I tap to purchase
**Then** I am redirected to Stripe Checkout for one-time payment
**And** the product is clearly labeled

**Given** the upsell payment succeeds
**When** the webhook confirms
**Then** my quota_remaining increases by purchased amount (5 or 10)
**And** QuotaWidget updates immediately
**And** I see confirmation toast
**And** these visits do NOT roll over to next month (use it or lose it)

**Given** the upsell payment fails
**When** the error occurs
**Then** I see error message and can retry
**And** my quota remains unchanged

**Given** I have purchased upsell visits
**When** the billing period resets
**Then** unused upsell visits are lost
**And** quota resets to plan's base allocation

---

#### Story 7.4: Rate Limiting & Protection

As a system administrator,
I want to protect the platform from abuse with rate limiting,
So that resources are fairly distributed and costs are controlled.

**Acceptance Criteria:**

**Given** a user is making API requests
**When** they exceed 10 recording submissions per hour
**Then** subsequent requests are rejected with HTTP 429
**And** user sees message explaining to retry in X minutes
**And** the limit resets after the hour window

**Given** the rate limit implementation
**When** tracking requests
**Then** limits are per-user (not per-IP)
**And** limits are enforced at backend API level
**And** legitimate usage (< 10/hour) is never affected

**Given** the audio duration limit
**When** recording reaches max_recording_minutes (from plans table)
**Then** frontend automatically stops the recording (as per Story 2.2)
**And** the captured audio is processed normally through the pipeline
**And** backend validates duration as a safety check only (in case frontend is bypassed)

**Given** suspicious activity patterns (future enhancement)
**When** detected
**Then** alerts are sent to admin via Sentry
**And** manual review can be triggered

---

### Epic 8: Administration & Conformité RGPD

#### Story 8.1: Admin Dashboard

As the founder/admin,
I want a dashboard showing key business and technical metrics,
So that I can monitor the health of the platform and make informed decisions.

**Acceptance Criteria:**

**Given** I am authenticated as an admin user
**When** I access the admin dashboard (separate route /admin)
**Then** I see a protected page requiring admin role
**And** regular users cannot access this route

**Given** I view the admin dashboard
**When** the metrics load
**Then** I see:
- Total users (registered)
- Active users (used app in last 30 days)
- Paying users (active subscription)
- Trial users (in trial period)
- MRR (Monthly Recurring Revenue) calculated from active subscriptions
- Total visits generated this month
**And** metrics refresh on page load (no real-time updates needed MVP)

**Given** I view usage metrics
**When** the dashboard displays
**Then** I see:
- Visits generated today / this week / this month
- Average latency (Stop → Note displayed) from last 24h
- 99th percentile latency
- Error count from Sentry (link to Sentry dashboard)

**Given** I want to investigate a user issue
**When** I search for a user by email
**Then** I see their profile: email, plan, quota remaining, subscription status
**And** I see their recent notes metadata (date, duration, language - NOT content)
**And** I can trigger account deletion if requested (RGPD)

**Given** the admin dashboard security
**When** implementing access control
**Then** admin role is determined by a flag in users table (is_admin boolean)
**And** initially only Greg's account has is_admin=true
**And** admin routes are protected at API level (not just frontend)

**Given** the audit trail metrics (aggregated)
**When** I view quality metrics
**Then** I see:
- Average edit count per note (indicates LLM quality)
- Notes with 0 edits vs 1+ edits percentage
- Average audio duration
**And** these are aggregated statistics, not per-user details

---

#### Story 8.2: API Suppression Compte (Droit à l'Oubli RGPD)

As a user,
I want to delete my account and all associated data,
So that I can exercise my RGPD right to be forgotten.

**Acceptance Criteria:**

**Given** I am logged in and in Settings
**When** I scroll to the bottom of the page
**Then** I see a "Supprimer mon compte" link/button
**And** it is clearly visible but not prominent (destructive action)

**Given** I tap "Supprimer mon compte"
**When** the confirmation dialog appears
**Then** I see a clear warning explaining:
- All my notes will be permanently deleted
- My subscription will be cancelled (no refund for current period)
- This action cannot be undone
**And** I must type "SUPPRIMER" (or equivalent) to confirm
**And** I see [Annuler] and [Supprimer définitivement] buttons

**Given** I confirm account deletion
**When** the deletion process runs
**Then** the API endpoint `DELETE /api/v1/users/me` is called
**And** all my data is deleted:
  - All notes (notes table)
  - All recordings metadata (recordings table)
  - Subscription record (subscriptions table)
  - User record (users table)
**And** Stripe subscription is cancelled via API (if active)
**And** my session/JWT is invalidated
**And** I am redirected to a "Compte supprimé" confirmation page
**And** I am logged out

**Given** the deletion is complete
**When** I try to log in again with the same Google account
**Then** I am treated as a new user (fresh start)
**And** no trace of previous data exists

**Given** the admin wants to delete a user (RGPD request via email)
**When** the admin uses the admin dashboard
**Then** the admin can trigger the same deletion process for any user
**And** an audit log entry is created (admin_id, deleted_user_email, timestamp)

**Given** the deletion API implementation
**When** DELETE /api/v1/users/me is called
**Then** deletion is performed in a transaction (all or nothing)
**And** if any step fails, the transaction is rolled back
**And** appropriate error message is returned

---

