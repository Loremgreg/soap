# Component Strategy

## shadcn/ui Components (Foundation)

Composants utilisés **directement** depuis shadcn/ui:

| Composant | Usage dans SOAP Notice |
|-----------|------------------------|
| `Button` | Actions principales, Copy buttons |
| `Card` | Conteneur note SOAP, note history cards |
| `Textarea` | Édition sections SOAP |
| `Dialog` | Modale consentement, erreurs, upsell |
| `Sheet` | Drawer mobile pour menus |
| `Toast` | Feedback copy success, auto-save |
| `Select` | Sélecteur langue |
| `Badge` | Tags, labels |
| `Skeleton` | Loading states |
| `Separator` | Divisions visuelles |

## Custom Components (À Créer)

Composants **spécifiques** à SOAP Notice (basés sur shadcn/ui):

### 1. RecordButton
- **Purpose**: Démarrer/Pause/Stop l'enregistrement audio
- **States**: `idle` | `recording` | `paused` | `processing`
- **Size**: Large (80x80px min), touch-optimized
- **Visual**: Pulse animation pendant recording, icon microphone

### 2. Timer
- **Purpose**: Afficher durée enregistrement en cours
- **Format**: `HH:MM:SS`
- **States**: `running` | `paused` | `stopped`
- **Size**: Grande typographie, lisible à distance

### 3. QuotaWidget
- **Purpose**: Afficher visites restantes en permanence
- **Format**: `"23/50 visites restantes"`
- **States**: `normal` (vert) | `warning` (orange, < 10) | `critical` (rouge, < 5) | `empty` (quota épuisé)
- **Position**: Header sticky ou floating

### 4. SOAPEditor
- **Purpose**: Afficher/Éditer les 4 sections de la note SOAP
- **Sections**: Subjective | Objective | Assessment | Plan
- **Features**:
  - Chaque section éditable (textarea)
  - Bouton Copy individuel par section
  - Auto-save avec indicateur discret
  - Mode lecture vs édition

### 5. SectionCopyButton
- **Purpose**: Copier une section individuelle vers clipboard
- **States**: `idle` | `copied` (feedback 2s)
- **Feedback**: Toast + animation bouton

### 6. CopyAllButton
- **Purpose**: Copier note SOAP complète
- **States**: `idle` | `copied`
- **Position**: Bottom de la note, toujours visible

### 7. NoteHistoryCard
- **Purpose**: Afficher une note dans la liste historique
- **Content**: Date, preview texte (truncated), metadata
- **Actions**: Tap → ouvre note complète

### 8. ConsentDialog
- **Purpose**: Afficher script consentement patient
- **Content**: Texte multilingue (FR/DE/EN), illustration
- **Actions**: Bouton "Got it!" pour fermer

### 9. LanguageSelector
- **Purpose**: Choisir langue d'enregistrement
- **Options**: FR 🇫🇷 | DE 🇩🇪 | EN 🇬🇧 | Auto 🌐
- **Persistence**: localStorage

### 10. BottomNav
- **Purpose**: Navigation principale mobile
- **Items**: Home (Record) | History | Settings
- **Style**: Fixe en bas, 3 items max
