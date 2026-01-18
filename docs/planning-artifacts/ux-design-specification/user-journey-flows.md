# User Journey Flows

## Journey 1: First Time Recording (Onboarding)

**Contexte**: Greg ouvre SOAP Notice pour la première fois, sceptique mais prêt à tester.

**Objectif**: Réussir le premier enregistrement sans friction, comprendre l'interface, voir une note SOAP générée.

**Success criteria**:
- Recording démarre en < 5 secondes
- Interface claire, pas de confusion
- Note générée en < 30s
- Greg pense "ça marche vraiment!"

```mermaid
graph TD
    Start([Ouvre SOAP Notice<br/>Première fois]) --> CheckPerms{Permissions<br/>micro OK?}

    CheckPerms -->|Non| ReqPerms[Demande permission<br/>microphone]
    ReqPerms --> PermsGranted{Accordé?}
    PermsGranted -->|Non| ErrorPerms[Erreur: Permission refusée<br/>Message explicatif]
    ErrorPerms --> End1([Fin - Bloqué])

    PermsGranted -->|Oui| HomeScreen
    CheckPerms -->|Oui| HomeScreen[Écran Home<br/>Bouton Record centré<br/>Quota visible<br/>Tooltip consentement]

    HomeScreen --> UserReadsConsent{Clique<br/>consentement?}
    UserReadsConsent -->|Oui| ConsentModal[Modale consentement<br/>Script multilingue<br/>Bouton Got it]
    ConsentModal --> CloseModal[Ferme modale]
    CloseModal --> HomeScreen

    UserReadsConsent -->|Non| TapRecord
    HomeScreen --> TapRecord[Tap Record button]

    TapRecord --> CheckConnection{Connexion<br/>internet?}
    CheckConnection -->|Non| ErrorOffline[Erreur: Pas de connexion<br/>Recording impossible]
    ErrorOffline --> End2([Fin - Bloqué])

    CheckConnection -->|Oui| RecordingStart[Recording démarre<br/>Timer 00:00:00<br/>Bouton → Pause/Stop<br/>Wake lock activé<br/>Indicateur visuel pulsant]

    RecordingStart --> RecordingInProgress{Greg parle<br/>pendant anamnèse}
    RecordingInProgress -->|10 min| StillRecording[Timer 00:10:00<br/>Transcription live WebSocket]

    StillRecording --> TapStop[Tap Stop button]
    TapStop --> ProcessingStart[Recording arrêté<br/>Wake lock désactivé<br/>État: Processing...]

    ProcessingStart --> DeepgramTranscribe[Deepgram transcription<br/>Finalisation audio]
    DeepgramTranscribe --> MistralExtract[Mistral AI extraction<br/>Génération note SOAP]

    MistralExtract --> CheckTimeout{< 30s?}
    CheckTimeout -->|Non| ErrorTimeout[Erreur: Timeout<br/>Réessayer ou support]
    ErrorTimeout --> End3([Fin - Échec])

    CheckTimeout -->|Oui| NoteGenerated[Note SOAP affichée<br/>4 sections S/O/A/P<br/>Éditable<br/>Boutons Copy visibles]

    NoteGenerated --> FirstSuccess[Toast: Note générée!<br/>Greg voit contenu<br/>Quota -1 visite]
    FirstSuccess --> End4([Fin - Succès<br/>Adoption probable])
```

---

## Journey 2: Regular Recording Workflow (Core)

**Contexte**: Utilisateur habituel (a déjà fait 5-10 recordings), utilise l'app quotidiennement.

**Objectif**: Workflow ultra-rapide: Record → Stop → Copy en < 2 min total.

**Success criteria**:
- Démarrage en 1 tap
- Aucune friction
- Note précise sans hallucinations
- Copy réussie vers logiciel externe

```mermaid
graph TD
    Start([Ouvre app<br/>Utilisateur régulier]) --> HomeScreen[Écran Home<br/>Quota visible 23/50<br/>Bouton Record]

    HomeScreen --> QuickRecord[Tap Record<br/>1 tap, zéro friction]

    QuickRecord --> RecordingActive[Recording actif<br/>Timer démarre<br/>Wake lock ON<br/>Indicateur visuel]

    RecordingActive --> Anamnesis{Anamnèse<br/>en cours}
    Anamnesis -->|5-10 min| ContinueRecording[Timer actif<br/>Deepgram streaming<br/>Transcription live backend]

    ContinueRecording --> NeedPause{Besoin<br/>pause?}
    NeedPause -->|Oui| TapPause[Tap Pause button]
    TapPause --> Paused[État: Paused<br/>Timer arrêté<br/>Bouton Resume visible]
    Paused --> TapResume[Tap Resume]
    TapResume --> ContinueRecording

    NeedPause -->|Non| TapStop[Tap Stop button]
    TapStop --> Processing[Processing...<br/>Skeleton loader<br/>Progress indicator]

    Processing --> CheckQuota{Quota<br/>disponible?}
    CheckQuota -->|Non| ErrorQuota[Erreur: Quota épuisé<br/>Upsell modale<br/>Upgrade plan]
    ErrorQuota --> End1([Fin - Bloqué])

    CheckQuota -->|Oui| TranscribeExtract[Deepgram + Mistral<br/>Génération SOAP<br/>~15-30s]

    TranscribeExtract --> CheckQuality{Note<br/>cohérente?}
    CheckQuality -->|Hallucinations| ErrorQuality[Note incohérente<br/>Alerte utilisateur<br/>Vérification requise]
    ErrorQuality --> NoteDisplay

    CheckQuality -->|OK| NoteDisplay[Note SOAP affichée<br/>4 sections éditables<br/>Copy buttons visibles<br/>Quota -1]

    NoteDisplay --> UserVerifies{Vérifie<br/>contenu?}
    UserVerifies -->|Oui| GoToEdit[Voir Journey 3:<br/>Edit & Copy Note]

    UserVerifies -->|Non, direct| QuickCopy[Tap Copy All<br/>Note complète → clipboard]
    QuickCopy --> CopySuccess[Toast: Copied!<br/>Feedback visuel]
    CopySuccess --> PasteExternal[Paste dans logiciel<br/>externe cabinet]
    PasteExternal --> End2([Fin - Succès<br/>Workflow complet])
```

---

## Journey 3: Edit & Copy Note

**Contexte**: Note SOAP générée, utilisateur veut vérifier/corriger avant de copier.

**Objectif**: Éditer rapidement les sections nécessaires, copier (complète ou partielle).

**Success criteria**:
- Édition mobile fluide
- Auto-save transparent
- Copy flexible (complète ou par section)
- Pas de perte de modifications

```mermaid
graph TD
    Start([Note générée<br/>affichée]) --> NoteView[Vue note SOAP<br/>4 sections S/O/A/P<br/>Mode lecture]

    NoteView --> UserAction{Action<br/>utilisateur?}

    UserAction -->|Lire seulement| ReadSections[Scroll sections<br/>Vérification visuelle]
    ReadSections --> DecideCopy

    UserAction -->|Éditer| TapEdit[Tap sur section<br/>ou Edit button]
    TapEdit --> EditMode[Mode édition activé<br/>Keyboard visible<br/>Cursor dans textarea]

    EditMode --> UserEdits{Modifications?}
    UserEdits -->|Oui| TypeChanges[Tape corrections<br/>Auto-save toutes 2s<br/>Indicateur discret]
    TypeChanges --> AutoSave[Modifications sauvées<br/>localStorage/backend]
    AutoSave --> MoreEdits{Plus de<br/>changements?}
    MoreEdits -->|Oui| UserEdits
    MoreEdits -->|Non| EditComplete[Édition terminée<br/>Tap hors textarea]

    EditComplete --> DecideCopy
    UserEdits -->|Non| DecideCopy{Copier<br/>quoi?}

    DecideCopy -->|Note complète| CopyAll[Tap Copy All button<br/>Toutes sections → clipboard]
    CopyAll --> FormatCheck{Format<br/>settings?}
    FormatCheck -->|Paragraph| CopyParagraph[Format: Texte continu<br/>Sections séparées par titres]
    FormatCheck -->|Bullet Points| CopyBullets[Format: Bullet points<br/>Structure liste]
    CopyParagraph --> CopySuccess
    CopyBullets --> CopySuccess[Toast: Copied!<br/>Animation button<br/>Feedback visuel 2s]

    DecideCopy -->|Section individuelle| ChooseSection[Tap Copy button<br/>sur section spécifique<br/>Ex: Plan uniquement]
    ChooseSection --> CopySingleSection[Section → clipboard<br/>Format préservé]
    CopySingleSection --> CopySuccess

    CopySuccess --> PasteWhere{Coller<br/>où?}
    PasteWhere -->|App externe| SwitchApp[Switch vers logiciel<br/>cabinet/notes]
    SwitchApp --> Paste[Cmd/Ctrl+V<br/>Note collée<br/>Format OK]
    Paste --> End1([Fin - Succès])

    PasteWhere -->|Plus tard| SaveToHistory[Note sauvée<br/>Historique automatique<br/>Accessible plus tard]
    SaveToHistory --> End2([Fin - Succès])
```

---

## Journey 4: Access Note from History

**Contexte**: Utilisateur veut retrouver une note passée (d'hier, semaine dernière).

**Objectif**: Naviguer historique → Retrouver note → Rouvrir → Éditer/Copier.

**Success criteria**:
- Historique accessible en 1-2 taps
- Notes identifiables (date, patient, preview)
- Réouverture instantanée
- Édition/copy identique à note fraîche

```mermaid
graph TD
    Start([Home screen<br/>Besoin note passée]) --> TapHistory[Tap History<br/>Bottom nav ou menu]

    TapHistory --> HistoryList[Liste 10 notes<br/>Triées par date desc<br/>Preview texte<br/>Metadata visible]

    HistoryList --> UserScroll{Scroll<br/>liste?}
    UserScroll -->|Cherche note| ScrollDown[Scroll down<br/>Max 10 notes visibles]
    ScrollDown --> FindNote

    UserScroll -->|Non| FindNote{Trouve<br/>note?}
    FindNote -->|Non| NoNote[Note pas trouvée<br/>Peut-être supprimée<br/>Rolling 10 notes max]
    NoNote --> End1([Fin - Note perdue])

    FindNote -->|Oui| TapNote[Tap sur note card]
    TapNote --> NoteLoaded[Note rouverte<br/>Mode lecture<br/>Contenu complet affiché]

    NoteLoaded --> WhatToDo{Action<br/>souhaitée?}

    WhatToDo -->|Juste lire| ReadNote[Lecture seule<br/>Scroll sections]
    ReadNote --> ClosedNote[Retour History<br/>ou Home]
    ClosedNote --> End2([Fin - Lecture])

    WhatToDo -->|Éditer| EditOldNote[Mode édition<br/>Identique Journey 3]
    EditOldNote --> SaveChanges[Auto-save<br/>Modifications persistées]
    SaveChanges --> AfterEdit

    WhatToDo -->|Copier| CopyOldNote[Copy All ou section<br/>Identique Journey 3]
    CopyOldNote --> CopySuccess[Toast: Copied!<br/>Clipboard rempli]
    CopySuccess --> AfterEdit{Continuer?}

    AfterEdit -->|Oui| NoteLoaded
    AfterEdit -->|Non| CloseNote[Retour History/Home]
    CloseNote --> End3([Fin - Succès])
```

---

## Journey 5: Settings Configuration

**Contexte**: Utilisateur veut ajuster préférences (langue, format note, verbosity).

**Objectif**: Modifier settings → Sauvegarder → Appliquer aux prochaines notes.

**Success criteria**:
- Settings accessibles facilement
- Changements clairs et immédiats
- Pas de reload app nécessaire
- Defaults intelligents mémorisés

```mermaid
graph TD
    Start([Home screen<br/>ou anywhere]) --> OpenSettings[Tap Settings<br/>Bottom nav ou hamburger]

    OpenSettings --> SettingsScreen[Écran Settings<br/>Sections groupées]

    SettingsScreen --> ChooseSection{Quelle<br/>section?}

    ChooseSection -->|Langue| LanguageSection[Section: Recording Language<br/>Options: FR/DE/EN/Auto<br/>Défaut: Auto-detect]
    LanguageSection --> SelectLanguage[Tap langue souhaitée<br/>Radio buttons<br/>Feedback visuel]
    SelectLanguage --> LanguageSaved[Langue sauvée<br/>localStorage<br/>Appliqué prochains recordings]
    LanguageSaved --> BackToSettings

    ChooseSection -->|Format note| FormatSection[Section: Note Format<br/>Options: Paragraph/Bullet Points<br/>Défaut: Paragraph]
    FormatSection --> SelectFormat[Tap format souhaité<br/>Radio buttons]
    SelectFormat --> FormatSaved[Format sauvé<br/>Appliqué prochaines notes]
    FormatSaved --> BackToSettings

    ChooseSection -->|Verbosity| VerbositySection[Section: Note Verbosity<br/>Options: Concise/Medium<br/>Défaut: Medium]
    VerbositySection --> SelectVerbosity[Tap niveau souhaité<br/>Radio buttons]
    SelectVerbosity --> VerbositySaved[Verbosity sauvée<br/>Appliqué génération LLM]
    VerbositySaved --> BackToSettings[Retour Settings screen]

    BackToSettings --> MoreChanges{Plus de<br/>changements?}
    MoreChanges -->|Oui| ChooseSection
    MoreChanges -->|Non| CloseSettings[Tap Back ou Home<br/>Quitte Settings]

    CloseSettings --> SettingsApplied[Settings actifs<br/>Prochaine note utilisera<br/>nouvelles préférences]
    SettingsApplied --> End1([Fin - Succès])

    ChooseSection -->|Autre| OtherSettings[Sections futures:<br/>- Account/Subscription<br/>- Input device<br/>- Notifications<br/>- Help/Support]
    OtherSettings --> BackToSettings
```

---

## Journey Patterns

Après analyse des 5 parcours, voici les **patterns communs** à standardiser:

### Navigation Patterns

**Pattern 1: Bottom Navigation (Mobile)**
- **Usage**: Navigation principale Home / History / Settings
- **Pourquoi**: Thumb-friendly mobile, toujours accessible
- **Implémentation**: Bottom nav bar fixe, 3 items max

**Pattern 2: Modal/Sheet Overlay**
- **Usage**: Consentement patient, erreurs bloquantes, upsell quota
- **Pourquoi**: Capte attention sans navigation destructive
- **Implémentation**: shadcn `<Dialog>` ou `<Sheet>` (drawer mobile)

**Pattern 3: Back Navigation**
- **Usage**: Retour depuis note detail, historique, settings
- **Pourquoi**: Convention mobile, predictable
- **Implémentation**: Header back arrow ou swipe gesture

### Feedback Patterns

**Pattern 1: Toast Notifications**
- **Usage**: Copy success, auto-save confirmations, non-blocking info
- **Pourquoi**: Feedback immédiat sans bloquer workflow
- **Implémentation**: shadcn `<Toast>` en top-right (mobile) ou bottom-center

**Pattern 2: Inline Error Messages**
- **Usage**: Erreurs permissions, connexion, quota épuisé
- **Pourquoi**: Contexte clair, actionnable
- **Implémentation**: Alert banner sous action concernée

**Pattern 3: Loading States**
- **Usage**: Processing note (15-30s), transcription en cours
- **Pourquoi**: Manage expectations, reduce anxiety
- **Implémentation**: Skeleton loaders (shadcn `<Skeleton>`), progress spinners

### State Management Patterns

**Pattern 1: Persistent State (localStorage)**
- **Usage**: Settings (langue, format, verbosity), historique 10 notes
- **Pourquoi**: Pas de backend complexe pour MVP, rapide
- **Implémentation**: React hooks + localStorage sync

**Pattern 2: Optimistic UI**
- **Usage**: Auto-save édition, copy to clipboard
- **Pourquoi**: Feels instant, améliore perception perf
- **Implémentation**: Update UI immédiatement, sync async

**Pattern 3: Error Recovery**
- **Usage**: Timeout transcription, connexion perdue pendant recording
- **Pourquoi**: Ne jamais perdre travail utilisateur
- **Implémentation**: Retry automatique (3x), puis message actionnable

---

## Flow Optimization Principles

### 1. Minimize Friction to Value
- **Recording démarre en 1 tap** (pas de champs obligatoires)
- **Copy en 1 tap** (bouton visible, action immédiate)
- **Settings optionnels** (defaults intelligents, workflow fonctionne sans y toucher)

### 2. Progressive Disclosure
- **Home screen = essentials uniquement** (Record button, quota, timer)
- **Settings cachés** (bottom nav secondaire)
- **Advanced features post-MVP** (favoris, tags, search) si besoin

### 3. Clear Feedback Loops
- **États visuels évidents**: Idle / Recording / Processing / Ready
- **Timer toujours visible** pendant recording (anxiety reduction)
- **Progress indicators** pendant génération note (15-30s feels shorter)

### 4. Error Prevention > Error Handling
- **Check connexion avant recording** (évite frustration après 10 min)
- **Wake lock automatique** (évite interruption screen lock)
- **Auto-save édition** (évite perte modifications)

### 5. Mobile-First Optimizations
- **Touch targets larges** (min 44x44px boutons critiques)
- **Thumb zone priority** (Record button center-bottom, facile pouce)
- **Keyboard-aware** (édition note, textarea scroll visible au-dessus keyboard)
