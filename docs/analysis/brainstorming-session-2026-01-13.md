---
stepsCompleted: [1, 2, 3]
inputDocuments: []
session_topic: "Application de transcription audio pour physiothérapeutes - Note SOAP structurée"
session_goals: "Concevoir une architecture simple pour transcrire des anamnèses et extraire des notes cliniques structurées"
selected_approach: "ai-recommended"
techniques_used: ["Role Playing", "First Principles Thinking", "Constraint Mapping"]
ideas_generated: []
context_file: "project-context-template.md"
date: "2026-01-13"
facilitator: "Greg"
---

# Rapport de Session Brainstorming

**Projet :** SOAP Notice - Application de transcription pour physiothérapeutes
**Date :** 13 janvier 2026
**Facilitateur :** Mary (Business Analyst)
**Participant :** Greg

---

## 1. Résumé Exécutif

Cette session de brainstorming a permis de définir les contours d'une application clinique pour physiothérapeutes. L'objectif principal est de transformer des enregistrements audio d'anamnèses en notes cliniques structurées au format SOAP enrichi, en privilégiant une architecture simple et maintenable.

**Décision clé :** Passage du format ICF initial vers un template SOAP détaillé en 4 sections (Subjective, Objective, Clinical Reasoning, Management Plan).

---

## 2. Définition du Produit

### 2.1 Vision

Créer un outil clinique réel (pas un chatbot) qui :
- Écoute un enregistrement audio live d'une anamnèse de physiothérapie
- Transcrit automatiquement la parole via service cloud
- Structure les informations cliniques extraites au format SOAP

### 2.2 Feature Principale

**Input :** Enregistrement audio de session (< 10 minutes)
**Output :** Note de physiothérapie structurée, prête à copier-coller

### 2.3 Format de Note Cible

```
1. Subjective Assessment
   A. Chief Complaint (description exacte, onset, caractéristiques douleur)
   B. History of Present Condition (progression, facteurs modifiants, interventions)
   C. Functional Impact Assessment (ADL, travail/sport/loisirs)

2. Objective Assessment
   A. Observation (posture, local, analyse de la marche)
   B. Physical Examination (ROM, force, tests spéciaux, palpation, neuro)

3. Clinical Reasoning
   - Assessment (diagnostic, facteurs contributifs, précautions)
   - Outcome Measures (tests standardisés, scores baseline)

4. Management Plan
   A. Treatment Provided (thérapie manuelle, exercices, modalités, éducation)
   B. Home Program (exercices, auto-gestion)
   C. Follow-up Plan (calendrier, objectifs, critères de sortie)
```

---

## 3. Contraintes Identifiées

### 3.1 Contraintes Réglementaires (P0 - Critiques)

| Contrainte | Statut | Stratégie |
|------------|--------|-----------|
| RGPD - Données de santé (Art. 9) | ✅ Réelle | Cloud EU sécurisé, DPA avec providers |
| Secret médical | ✅ Réelle | Chiffrement, pas de transmission non sécurisée |
| Droit à l'effacement | ✅ Réelle | API de suppression des enregistrements |
| Localisation des données | ✅ Décidé | Serveurs EU uniquement |

### 3.2 Contraintes Techniques (P1 - Importantes)

| Contrainte | Statut | Stratégie |
|------------|--------|-----------|
| Qualité audio (bruit, accents) | ✅ Réelle | Deepgram EU (robuste au bruit) |
| Précision extraction entités | ✅ Réelle | Claude API + prompt structuré |
| Latence acceptable | ✅ Réelle | < 30s pour 10min audio (batch OK) |
| Vocabulaire médical | ✅ Réelle | Few-shot prompting avec exemples |

### 3.3 Contraintes Utilisateur (P1 - Importantes)

| Contrainte | Statut | Stratégie |
|------------|--------|-----------|
| Temps disponible du kiné | ✅ Réelle | Interface minimaliste, 1 clic |
| Adoption technologique | Variable | UX intuitive, pas de formation |
| Correction post-transcription | ✅ Réelle | Interface d'édition dans React |
| Intégration logiciel existant | MVP différé | Bouton "Copier" pour V1 |

### 3.4 Contraintes Projet

| Contrainte | Décision |
|------------|----------|
| Langage | Python (imposé) |
| Architecture | Simple, pas de sur-ingénierie |
| Philosophie | Outil clinique réel, pas de chatbot |
| Scope MVP | Flux linéaire : Record → Transcribe → Extract → Copy |

---

## 4. Décisions Architecturales

### 4.1 Stack Technique Validée

| Composant | Technologie | Justification |
|-----------|-------------|---------------|
| **Frontend** | Vite + React + TailwindCSS | Évolutif, maintenable, setup rapide |
| **Backend** | Python FastAPI | Choix utilisateur, async natif |
| **Speech-to-Text** | Deepgram EU | API cloud, localisation EU, robuste |
| **LLM Extraction** | Claude API | Excellent pour extraction structurée |
| **Base de données** | PostgreSQL EU | Multi-client ready, RGPD, backups |

### 4.2 Architecture Globale

```
┌─────────────────────────────────────────────────────────┐
│                        FRONTEND                         │
│              Vite + React + TailwindCSS                 │
│  - Enregistrement audio (MediaRecorder API)             │
│  - Affichage note structurée                            │
│  - Édition et copie                                     │
└─────────────────────────┬───────────────────────────────┘
                          │ API calls (REST)
                          ▼
┌─────────────────────────────────────────────────────────┐
│                        BACKEND                          │
│                    Python FastAPI                       │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Deepgram EU │  │ Claude API  │  │ PostgreSQL EU   │  │
│  │    (STT)    │  │(Extraction) │  │   (Stockage)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 4.3 Flux de Données MVP

```
1. [Utilisateur] Clique "Enregistrer" dans l'interface React
2. [Frontend] Capture audio via MediaRecorder API
3. [Utilisateur] Clique "Arrêter"
4. [Frontend] Envoie audio blob au backend FastAPI
5. [Backend] Envoie audio à Deepgram EU → reçoit transcription
6. [Backend] Envoie transcription + template à Claude API
7. [Claude] Extrait et structure en format SOAP
8. [Backend] Retourne note structurée au frontend
9. [Frontend] Affiche note, permet édition
10. [Utilisateur] Clique "Copier" → colle dans logiciel existant
```

### 4.4 Providers Cloud Recommandés (EU/RGPD)

| Service | Provider | Coût estimé |
|---------|----------|-------------|
| PostgreSQL | Supabase EU / Neon EU | Gratuit → 25€/mo |
| Hosting Backend | Railway / Scaleway | ~5-10€/mo |
| Hosting Frontend | Vercel / Netlify | Gratuit |

---

## 5. Insights Clés

### 5.1 Ce qui compte vraiment

1. **Le prompt LLM est le cœur du produit** - La qualité de l'extraction dépend entièrement du prompt structuré qui mappe vers les 4 sections SOAP

2. **Le STT n'est pas le défi principal** - Deepgram gère bien l'audio bruité et les accents ; le vrai travail est l'extraction sémantique

3. **L'UX doit être invisible** - Un kiné n'a pas le temps de comprendre une interface ; 1 bouton pour enregistrer, 1 pour copier

4. **Le format de sortie drive tout** - Le template SOAP détaillé guide la structure du prompt et les attentes de l'utilisateur

### 5.2 Risques Identifiés

| Risque | Probabilité | Mitigation |
|--------|-------------|------------|
| Extraction imprécise sur cas complexes | Moyenne | Few-shot examples, interface d'édition |
| Qualité audio insuffisante | Faible | Recommandations micro, pré-processing |
| Non-adoption par les kinés | Moyenne | Tests utilisateurs précoces |
| Coûts API qui explosent | Faible | Monitoring, limites par user |

### 5.3 Ce qui peut attendre (Post-MVP)

- Authentification multi-utilisateurs
- Historique des sessions par patient
- Export PDF formaté
- Intégration directe avec logiciels métier
- Fine-tuning du modèle sur données réelles
- Application mobile

---

## 6. Prochaines Étapes Recommandées

1. **Créer le Product Brief** - Formaliser la vision et le scope MVP
2. **Valider le prompt d'extraction** - Tester avec des transcriptions réelles
3. **Prototype backend** - FastAPI + Deepgram + Claude en local
4. **Interface minimale** - React avec 2 écrans (record + display)
5. **Test utilisateur** - Faire tester par 1-2 kinés réels

---

## 7. Annexes

### 7.1 Techniques de Brainstorming Utilisées

| Phase | Technique | Objectif |
|-------|-----------|----------|
| 1 | Role Playing | Comprendre perspectives stakeholders |
| 2 | First Principles Thinking | Déconstruire hypothèses, architecture minimale |
| 3 | Constraint Mapping | Identifier contraintes réelles vs imaginées |

### 7.2 Questions Résolues

- ✅ Format de note : SOAP enrichi
- ✅ Hébergement : Cloud EU sécurisé
- ✅ STT : API cloud (Deepgram EU)
- ✅ Durée session : < 10 minutes
- ✅ Intégration MVP : Copy-paste
- ✅ Frontend : React (Vite + Tailwind)
- ✅ Base de données : PostgreSQL EU

---

*Rapport généré lors de la session de brainstorming BMAD*
*Facilitatrice : Mary (Business Analyst)*
