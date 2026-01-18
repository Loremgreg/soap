# Design System Foundation

## Design System Choice

**Choix: Tailwind CSS + shadcn/ui**

SOAP Notice utilisera **Tailwind CSS** comme framework CSS utility-first, complété par **[shadcn/ui](https://ui.shadcn.com/)** pour les composants UI.

shadcn/ui est une collection de composants React réutilisables, accessibles et customisables construits avec:
- **Radix UI** (primitives headless pour accessibilité)
- **Tailwind CSS** (styling utility-first)
- **Copy-paste architecture** (composants dans votre codebase, pas npm dependency)

**Composants clés disponibles:**
- Button, Dialog, Dropdown Menu, Toast
- Form controls (Input, Textarea, Select, Checkbox)
- Navigation (Tabs, Sheet/Drawer)
- Feedback (Alert, Progress, Skeleton)
- Data display (Card, Badge, Separator)

## Rationale for Selection

### Pourquoi shadcn/ui pour SOAP Notice?

**1. Pas de designer dans l'équipe**
- Composants **pré-stylés professionnels** prêts à l'emploi
- Design cohérent sans compétences design avancées
- Focus développeur sur la logique métier (transcription, LLM) plutôt que sur CSS

**2. Mobile-First PWA Requirements**
- Composants **optimisés responsive** out-of-the-box
- Touch-friendly par défaut
- Patterns d'accessibilité mobile (focus management, keyboard navigation)

**3. Rapidité de développement MVP**
- Copy-paste components = **setup en minutes**
- Pas de learning curve complexe (si vous connaissez React + Tailwind)
- Documentation exhaustive avec exemples

**4. Customisation totale**
- Code dans votre projet = **100% contrôle**
- Pas de "black box" npm package à débugger
- Modification facile pour besoins spécifiques (ex: bouton Record custom)

**5. Accessibilité (A11y) built-in**
- Radix UI garantit **WCAG compliance**
- Gestion clavier/screen readers native
- Important pour outil médical professionnel

**6. Performance**
- Léger (pas de runtime JavaScript lourd)
- Tree-shakeable (seulement ce que vous utilisez)
- Compatible avec Vite (fast HMR)

**7. Écosystème et maintenance**
- Très populaire (communauté active)
- Fréquemment mis à jour
- Nombreux exemples et templates disponibles

## Implementation Approach

### Setup Initial

```bash
# Installation des dépendances
npx shadcn-ui@latest init
```

Configuration Tailwind existante détectée automatiquement.

### Architecture de Composants

```
src/
├── components/
│   ├── ui/              # shadcn/ui components (copy-paste)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── toast.tsx
│   │   └── ...
│   ├── recording/       # Composants métier SOAP Notice
│   │   ├── RecordButton.tsx
│   │   ├── Timer.tsx
│   │   ├── QuotaWidget.tsx
│   │   └── ...
│   └── soap-note/
│       ├── SOAPEditor.tsx
│       ├── SectionCopy.tsx
│       └── ...
```

**Workflow:**
1. Ajoutez composants shadcn/ui **au besoin** avec `npx shadcn-ui@latest add button`
2. Composants copiés dans `src/components/ui/`
3. Importez et customisez dans vos composants métier

**Composants shadcn/ui prioritaires pour MVP:**
- `button` - Boutons Record/Stop/Pause/Copy
- `card` - Conteneur de note SOAP
- `textarea` - Édition des sections SOAP
- `toast` - Feedback "Copied!" après copy
- `dialog` - Modale consentement patient
- `select` - Sélecteur langue (FR/DE/EN)
- `badge` - Quota widget ("23/50 visites")
- `skeleton` - Loading state pendant génération note

## Customization Strategy

### 1. Design Tokens (Tailwind Config)

**Palette couleurs adaptée au médical:**
- **Primary**: Vert professionnel (confiance, santé) - à définir step 8
- **Neutral/Gray**: Pour texte et backgrounds
- **Success**: Feedback positif (note générée)
- **Warning**: Alertes quota (< 5 visites)
- **Error**: États d'erreur (connexion perdue, timeout)

**Typography:**
- Font lisible mobile (système -apple-system, Roboto, ou Inter)
- Sizes responsive (base 16px mobile, scale fluide)

**Spacing & Sizing:**
- Touch targets: minimum 44x44px (iOS guidelines)
- Padding généreux pour mobile
- Breakpoints: `sm: 640px` (phone landscape), `md: 768px` (tablet)

### 2. Composants Customisés

**RecordButton (Ultra Custom):**
- Basé sur shadcn `<Button>` mais avec:
  - **États visuels clairs**: Idle / Recording (pulse animation) / Paused / Stopped
  - **Large touch target** (80x80px minimum)
  - **Icon + Label** (microphone icon)
  - **Feedback visuel fort** (border glow pendant recording)

**SOAPEditor (Custom Composition):**
- Basé sur shadcn `<Card>` + `<Textarea>`
- **4 sections éditables** (S / O / A / P)
- **Copy button** par section (shadcn `<Button>` variant)
- **Auto-save** indicator discret
- **Sections collapsibles** (optionnel, si note longue)

**QuotaWidget:**
- Basé sur shadcn `<Badge>`
- **Always visible** (sticky header ou floating)
- **Color-coded**: Green (> 10 visites) / Orange (5-10) / Red (< 5)

**LanguageSelector:**
- Basé sur shadcn `<Select>`
- **Flags icons** (FR 🇫🇷 / DE 🇩🇪 / EN 🇬🇧 / Auto 🌐)
- Accessible via Settings

### 3. Responsive Patterns

**Mobile-First Approach:**
- Design pour 320px (iPhone SE) d'abord
- Progressive enhancement pour tablet/desktop
- **Portrait prioritaire**, landscape secondaire

**Layout Strategy:**
- **Mobile**: Single column, bottom navigation
- **Tablet**: Possibilité 2 colonnes pour édition note (portrait = 1 col)

### 4. Accessibilité Enhancements

shadcn/ui garantit accessibilité de base (Radix UI), mais ajouts SOAP Notice:

- **Focus visible** clair (outlines Tailwind ring)
- **Skip links** ("Skip to note", "Skip to history")
- **ARIA labels** explicites sur boutons icon-only
- **Screen reader announcements** pour changements d'état (recording started, note generated)
- **Keyboard shortcuts** (optionnel): Space = Record/Stop, Cmd/Ctrl+C = Copy

### 5. Theming & Brand

**Pas de branding complexe pour MVP:**
- Palette simple et professionnelle (vert médical + neutrals)
- Logo simple (texte "SOAP Notice" suffisant pour MVP)
- Focus sur **clarté et efficacité** plutôt que sur branding fancy

**Dark mode?**
- **Pas pour MVP** (ajout post-launch si demandé)
- shadcn/ui supporte dark mode nativement si besoin futur
