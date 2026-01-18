# Core User Experience

## Defining Experience

L'expérience centrale de **SOAP Notice** se concentre sur un workflow ultra-linéaire et sans friction:

**Record → Stop → Note SOAP générée → Copy**

**L'action la plus fréquente**: "Enregistrer une nouvelle visite" - Cette action doit être **instantanément accessible** dès l'ouverture de l'application, sans aucune friction préalable.

**L'interaction critique à réussir**:
1. **Recording stable et fiable** - L'enregistrement audio ne doit jamais être interrompu (wake lock, feedback visuel clair, gestion d'erreurs robuste)
2. **Génération de note SOAP sans hallucinations** - La qualité de transcription (Deepgram) et d'extraction structurée (Mistral) doit être irréprochable pour maintenir la confiance utilisateur

L'utilisateur cible (Greg le Kiné) utilise l'application **pendant la consultation** avec le patient présent, sur **smartphone ou tablette**. L'interface n'a pas besoin d'être discrète - l'app est assumée comme outil clinique.

## Platform Strategy

**Type d'application**: Progressive Web App (PWA)
- Accessible depuis Safari, Chrome, Firefox (pas d'installation App Store/Play Store requise)
- Installation optionnelle sur home screen (Add to Home Screen)
- Cross-platform par nature (iOS, Android, desktop si nécessaire)

**Orientations supportées**:
- **Portrait** (prioritaire) - Usage smartphone en main
- **Landscape** (secondaire) - Usage tablette posée sur bureau

**Connectivité requise**:
- **Connexion internet obligatoire** pour la transcription en temps réel (Deepgram WebSocket streaming)
- Pas de mode offline pour le MVP (complexité non justifiée)

**Device capabilities exploitées**:
- ✅ **Wake Lock API** - Empêche le verrouillage automatique de l'écran pendant l'enregistrement (critique pour recordings de 5-10 min)
- ✅ **Web Audio API** - Accès microphone avec sélection input device
- ✅ **Clipboard API** - Copy to clipboard (note complète ou sections individuelles)
- ✅ **Notifications API** - Uniquement pour alertes quota (pas de notification persistante pendant recording)
- ❌ **Haptic feedback** - Pas de vibration tactile, uniquement feedback visuel

**Contraintes techniques**:
- Support minimum: iOS Safari 14+, Chrome 90+, Firefox 88+
- Responsive breakpoints: 320px (mobile) → 768px (tablet) → 1024px+ (desktop fallback)
- Performance: Génération de note < 30 secondes pour 10 min d'audio

## Effortless Interactions

Les interactions suivantes doivent être **ultra-fluides et sans friction**:

### 1. Start Recording (1 tap)
- Bouton **Record** large, centré, ultra-accessible dès l'ouverture de l'app
- Aucun champ obligatoire avant de démarrer (pas de Patient Name, pas de settings forcés)
- Feedback visuel immédiat: bouton change d'état, timer démarre, indicateur recording visible

### 2. Copy Flexibility (Pattern Claire)
- **Copy Note complète**: 1 bouton global en bas de la note ("Copy Note" ou "Copy All")
- **Copy sections individuelles**: Chaque section SOAP (Subjective / Objective / Assessment / Plan) a son propre bouton "Copy"
- Format clipboard préservé (markdown ou plaintext selon besoins)
- Feedback visuel après copy: toast "Copied!" ou animation bouton

### 3. Quota Awareness
- Widget quota **toujours visible** en permanence: "23/50 visites restantes"
- Pas de surprise "quota épuisé" en plein milieu d'une journée de consultations
- Alerte proactive quand < 5 visites restantes

### 4. Language Switching
- Sélecteur de langue **visible et accessible** (FR / DE / EN / Auto-detect)
- Changement de langue ne nécessite pas de reload app
- Script consentement patient disponible dans toutes les langues

## Critical Success Moments

### Moment 1: First Recording (Onboarding)
**Contexte**: Première utilisation, utilisateur teste l'app avec scepticisme ("est-ce que ça marche vraiment?")

**Success conditions**:
- Recording démarre en **< 5 secondes** après ouverture de l'app
- Interface claire, aucune confusion sur "quoi faire"
- Feedback visuel immédiat (timer visible, indicateur recording)
- Pas de bugs micro, pas d'erreurs permissions

**Failure risks**: Settings compliqués, confusion UI, bugs accès microphone, interface desktop-thinking sur mobile

---

### Moment 2: Note Generation (The Magic)
**Contexte**: Recording terminé (Stop pressé), attente de la note SOAP générée

**Success conditions**:
- Note apparaît en **< 30 secondes** (idéalement < 15s)
- Structurée correctement en 4 sections SOAP (Subjective / Objective / Assessment / Plan)
- Contenu pertinent, pas d'hallucinations, transcription précise
- Note immédiatement éditable

**Failure risks**: Timeout, note mal structurée, transcription incohérente, informations inventées (hallucinations LLM), pas d'indicateur de progression

---

### Moment 3: First Edit (Trust Building)
**Contexte**: Utilisateur ouvre la note générée pour vérifier et corriger

**Success conditions**:
- Interface d'édition **mobile-optimized** (grandes zones touch, keyboard adapté)
- Sections clairement séparées et identifiables (S / O / A / P)
- Auto-save automatique (pas de risque de perte)
- Scroll fluide, sections collapsibles si nécessaire

**Failure risks**: Édition mobile maladroite, keyboard bloque la vue, perte de modifications, interface lente

---

### Moment 4: Copy to External System
**Contexte**: Utilisateur veut copier la note (complète ou partielle) dans son logiciel de gestion cabinet

**Success conditions**:
- **1 tap** → note copiée dans clipboard → paste direct dans autre app
- Format préservé (markdown ou plaintext propre)
- Option de copier **section individuelle** (ex: uniquement le "P" - Plan) si besoin spécifique

**Failure risks**: Copy partiel, formatage cassé, perte de structure, boutons Copy non visibles

## Experience Principles

Ces principes guident toutes les décisions UX pour **SOAP Notice**:

### Principe 1: Zero Friction Recording
*"Démarrer un enregistrement ne doit jamais prendre plus de 1 tap. Aucun champ obligatoire, aucun settings préalable, aucune friction. Le bouton Record est roi."*

**Implications**:
- Bouton Record ultra-accessible (center screen, large touch target)
- Settings (Format, Verbosity, Langue) mémorisés et optionnels
- Pas de modale "Entrez le nom du patient" avant recording
- Feedback visuel immédiat au tap (pas de délai de réponse)

---

### Principe 2: Trust Through Quality
*"La note SOAP générée doit être précise et éditable. On ne promet jamais '100% automatique sans vérification'. On assume et encourage l'édition post-génération comme une feature, pas un bug."*

**Implications**:
- Interface d'édition optimisée et accessible (pas cachée)
- Encouragement explicite à vérifier/éditer la note
- Pas de message marketing du type "Parfait, rien à changer!"
- Transparence sur le processus (Transcription → Extraction → Édition)

---

### Principe 3: Copy Flexibility
*"L'utilisateur peut copier la note entière OU des sections individuelles (S/O/A/P) selon son besoin du moment. Le format clipboard est propre et préservé."*

**Implications**:
- Bouton "Copy All" global toujours visible
- Chaque section SOAP a son bouton "Copy" individuel
- Format markdown/plaintext propre (pas de HTML brisé)
- Feedback visuel après copy (toast ou animation)

---

### Principe 4: Mobile-First Stability
*"Le recording doit être rock-solid sur mobile: wake lock actif, feedback visuel clair, gestion d'erreurs robuste, aucune interruption possible."*

**Implications**:
- Wake Lock API activé pendant recording (écran ne verrouille pas)
- Feedback visuel constant (timer, indicateur pulsant, état clairement visible)
- Gestion erreurs: microphone permission, connexion perdue, quota épuisé
- Pas de haptic feedback (vibration) - uniquement visuel

---

### Principe 5: Progressive Disclosure
*"Le workflow core (Record → Stop → Copy) est immédiatement accessible et compréhensible. Les settings avancés (Format, Verbosity, Langue) sont accessibles mais pas intrusifs."*

**Implications**:
- Écran principal = Record button + Timer + Quota widget
- Settings dans navigation secondaire (hamburger ou bottom nav)
- Defaults intelligents (Format: Paragraph, Verbosity: Medium, Langue: Auto-detect)
- Utilisateur débutant réussit sans toucher aux settings
- Utilisateur avancé peut ajuster selon ses préférences
