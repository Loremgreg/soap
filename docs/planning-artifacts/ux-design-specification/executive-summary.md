# Executive Summary

## Project Vision

SOAP Notice est une application **mobile-first** (smartphone/tablette) conçue pour physiothérapeutes indépendants et cabinets 1-3 praticiens. L'objectif: transformer des enregistrements audio d'anamnèses en notes SOAP structurées en **< 30 secondes**, avec un workflow d'une simplicité radicale.

**Philosophie UX**: Moins c'est plus. Pas de features superflues, pas de complexité. Record → Stop → Copy. C'est tout.

## Target Users

**Persona principal: Greg le Kiné**

- **Contexte**: Kiné indépendant, 7+ nouveaux patients/semaine, perd 5-8 min/note sur documentation manuelle
- **Motivation**: Récupérer ~4h/mois pour se concentrer sur les soins, pas l'admin
- **Tech profil**: Utilisateur smartphone quotidien, sceptique sur l'IA mais pragmatique ("si ça marche, j'adopte")
- **Device**: Smartphone/tablette pendant consultation (patient présent)
- **Environnement**: Cabinet de physiothérapie, environnement parfois bruyant, mains pas toujours libres

**Pain points actuels**:
- Documentation post-consultation prend trop de temps
- Risque d'oubli d'informations importantes
- Frustration de "perdre du temps" sur de l'admin au lieu de soigner

**Job to be done**:
*"Quand je termine une anamnèse, je veux une note SOAP complète et structurée instantanément, pour que je puisse passer au traitement sans perdre 5-8 minutes à écrire."*

## Key Design Challenges

### Challenge 1: Mobile-First Constraints
**Contexte**: Smartphone/tablette = espace écran limité, navigation touch, keyboard mobile
**Impact UX**: Impossible de reprendre le layout desktop 2-colonnes de Claire. Nécessite architecture navigation mobile native (bottom nav ou hamburger).

### Challenge 2: Recording Stability Mobile
**Contexte**: Enregistrements jusqu'à 10 min, risque de verrouillage écran ou interruption
**Impact UX**: Besoin de wake lock, indicateurs persistants, gestion erreurs robuste.

### Challenge 3: Text Editing Mobile
**Contexte**: Note SOAP = 4 sections structurées, édition post-génération obligatoire
**Impact UX**: Interface d'édition mobile optimisée, sections collapsibles, auto-save, keyboard adapté.

### Challenge 4: Multilingue EU
**Contexte**: FR/DE/EN supportés (+ détection auto), scripts consentement multilingues
**Impact UX**: Sélecteur langue visible, traductions professionnelles, détection automatique intelligente.

## Design Opportunities

### Opportunity 1: Radical Mobile Simplicity
**Vision**: Créer l'app de transcription clinique **la plus simple** du marché mobile.
**Approche**: Progressive disclosure - workflow core en 2 taps (Record → Stop), settings avancés accessibles mais cachés par défaut.

### Opportunity 2: Quota Awareness as Feature
**Vision**: Transformer le quota (contrainte business) en feature UX motivante.
**Approche**: Widget "X/50 visites restantes" toujours visible, célébration du gain de temps ("Vous avez économisé 6 min!"), upsell contextuel.

### Opportunity 3: Mobile-Native Interactions
**Vision**: Exploiter les affordances mobile (haptic, gestures, notifications).
**Approche**: Haptic feedback sur actions critiques, swipe gestures pour navigation historique, notification persistante pendant recording.

### Opportunity 4: Trust Through Transparency
**Vision**: L'édition post-génération n'est pas un bug, c'est une feature (responsabilité légale).
**Approche**: Encourager explicitement l'édition, montrer les changements utilisateur, ne jamais surfer sur "100% automatique".
