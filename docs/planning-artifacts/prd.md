---
stepsCompleted: ['step-01-init', 'step-02-discovery', 'step-03-success', 'step-04-journeys', 'step-05-domain']
inputDocuments:
  - docs/planning-artifacts/product-brief-soap-notice-2026-01-14.md
  - docs/analysis/brainstorming-session-2026-01-13.md
  - docs/templates/physiotherapy-note-template.md
documentCounts:
  briefs: 1
  research: 0
  brainstorming: 1
  projectDocs: 0
  templates: 1
workflowType: 'prd'
projectType: 'greenfield'
date: 2026-01-14
classification:
  projectType: web_app
  domain: healthcare
  complexity: high
  projectContext: greenfield
---

# Product Requirements Document - SOAP Notice

**Auteur:** Greg
**Date:** 14 janvier 2026

## Critères de Succès

### Succès Utilisateur

**Gain de temps mesurable :**
- **5-8 minutes économisées** par nouvelle note patient
- ~35-56 min/semaine pour un kiné standard (7 nouveaux patients)
- **~4 heures/mois** récupérées sur la documentation

**Expérience cible :**
- Onboarding ultra-rapide : connexion Google en 1 clic
- Flux ultra-simple : Record → Transcribe → SOAP → Copy
- Trial 7 jours (5 visites) pour valider sans risque
- **Note structurée prête < 30 secondes après clic sur Stop**

**Consentement patient :**
- Script verbal fourni dans l'app (FR/DE/EN)
- Exemple FR : *"Pour optimiser la qualité de nos échanges, je vais enregistrer notre conversation afin de préparer votre note clinique. Si vous préférez que je ne l'enregistre pas, dites-le moi sans problème."*

**Moment "aha!" :** Le kiné voit sa note SOAP complète apparaître en moins de 30 secondes après avoir arrêté l'enregistrement, alors qu'il n'a fait que parler naturellement.

### Succès Business

| Horizon | Objectif | Métrique |
|---------|----------|----------|
| **3 mois** | Validation marché | 20 users payants |
| **3 mois** | Revenue | 580-980€ MRR (mix plans) |
| **3 mois** | Conversion trial | ≥ 30% trial → payant |
| **12 mois** | Croissance | À définir post-MVP |

**Modèle économique - 2 plans :**

| Plan | Prix | Visites/mois | Ratio | Volume discount |
|------|------|--------------|-------|-----------------|
| **Starter** | 29€/mois | 20 visites | 1,45€/visite | - |
| **Pro** | 49€/mois | 50 visites | 0,98€/visite | **33% économie** vs Starter |

**Upsell (tous plans) :** +5 visites = +5€ | +10 visites = +10€

**Trial :** 7 jours gratuits (5 visites max)

**Paiement :** Stripe avec anniversary billing (cycle basé sur date d'inscription)

**Cible :** Kinés indépendants + cabinets (1-3 praticiens)

**Opportunité Growth Phase :** Plan Enterprise 79€/100 visites pour power users

### Succès Technique

| Critère | Cible | Criticité | Notes |
|---------|-------|-----------|-------|
| Latence génération | **< 30s après Stop** | 🔴 Critique | Streaming live pendant consultation |
| Qualité perçue | **User satisfaction ≥ 4/5** | 🔴 Critique | Mesurée via early adopters |
| Langues MVP | FR, DE, EN | 🔴 Critique | Tester avec users dans chaque langue |
| Conformité RGPD | Données EU, chiffrement | 🔴 Critique | Consentement verbal documenté |
| Disponibilité | 99% uptime | 🟡 Important | - |
| Authentification | OAuth Google | 🔴 Critique MVP | Anniversary billing Stripe |
| Gestion quotas | Temps réel, fiable | 🔴 Critique MVP | Hard reset mensuel par user |
| Monitoring | Sentry + latence metrics | 🔴 Critique MVP | Validation 30s en prod |

**Architecture flux technique :**
1. Record live → Audio stream vers Deepgram (transcription temps réel)
2. Stop → Transcription complète disponible instantanément
3. Extraction Claude API → 15-20s
4. Note SOAP affichée → Total < 30s après Stop

### Résultats Mesurables

**Après 3 mois :**
- ✅ 20 utilisateurs payants actifs
- ✅ Taux de conversion trial ≥ 30%
- ✅ Temps génération < 30s après Stop (mesuré via monitoring)
- ✅ Satisfaction qualité note ≥ 4/5
- ✅ Zéro incident sécurité/RGPD
- ✅ 580-980€ MRR généré (mix Starter/Pro)

## Sécurité & Contraintes Économiques

### Sécurité des Données (RGPD Art. 9)

| Mesure | Implémentation |
|--------|----------------|
| Chiffrement transit | TLS 1.3 |
| Chiffrement repos | PostgreSQL chiffré (EU) |
| Localisation données | Serveurs EU uniquement |
| Rétention audio | **0 jours** (suppression immédiate post-transcription) |
| Rétention notes | **Max 10 dernières notes** (suppression rolling) |
| Droit à l'oubli | API de suppression complète |
| Consentement patient | Script verbal (FR/DE/EN) fourni dans app |

### Protection Économique (Abus API)

| Risque | Garde-fou MVP |
|--------|---------------|
| **Sur-consommation** | Hard limit : 10 min max/audio |
| **Dépassement quota** | Blocage soft + proposition upsell |
| **Spam uploads** | Rate limiting : max 10 uploads/heure/user |
| **Trial abuse** | 1 trial/email (vérification Google OAuth) |
| **Coûts incontrôlés** | Monitoring usage temps réel par user |

**Quotas par plan :**
- **Trial (7j)** : 5 visites max
- **Starter (29€/mois)** : 20 visites/mois (200 min max)
- **Pro (49€/mois)** : 50 visites/mois (500 min max)
- **Upsell on-demand** : +5 visites (+5€) ou +10 visites (+10€)

**Billing cycle :** Anniversary billing (ex: inscription le 25 → facturation le 25 de chaque mois, géré nativement par Stripe)

**Comportement dépassement :**
1. User atteint son quota (20/20 ou 50/50)
2. Blocage upload avec message : "Quota atteint pour ce mois"
3. Proposition upsell : "Acheter +5 ou +10 visites supplémentaires ?"
4. Si refus : déblocage automatique à l'anniversary date suivante

**Économie unitaire validée :**
- Coût API par visite : ~0,05-0,06€
- Marge brute Starter : 96%
- Marge brute Pro : 94%

## Scope Produit

### MVP - Minimum Viable Product

**Flux core :**
1. Connexion OAuth Google (1 clic)
2. Sélection plan (Starter 29€ ou Pro 49€) + trial 7j
3. **Record live** (indicateur simple, pas de transcription visible)
4. **Stop** → Transcription instantanément disponible
5. Extraction SOAP (Claude API, < 30s)
6. Afficher + éditer
7. Copier dans presse-papier
8. **Note sauvegardée dans historique (max 10)**

**Inclus dans MVP :**
- ✅ **Authentification** : OAuth Google uniquement
- ✅ **Paiement** : Stripe (Starter 29€ ou Pro 49€, anniversary billing)
- ✅ **Trial** : 7 jours gratuits (5 visites max)
- ✅ **Quotas** : 20 ou 50 visites/mois selon plan + upsell (+5 ou +10)
- ✅ **3 langues** : Français, Allemand, Anglais
- ✅ **Consentement** : Scripts verbaux FR/DE/EN dans tooltip
- ✅ **Interface web responsive**
- ✅ **Recording live** : Indicateur simple (pas de transcription visible)
- ✅ **Édition post-transcription**
- ✅ **Monitoring** : Sentry + métriques latence
- ✅ **Dashboard** : compteur visites restantes + **historique 10 dernières notes**
- ✅ **Historique limité** : 10 dernières notes avec suppression rolling

**Exclu du MVP :**
- ❌ Historique illimité ou archivage long terme
- ❌ Organisation par patient (recherche, filtres, tags)
- ❌ Transcription live visible pendant enregistrement
- ❌ Export PDF
- ❌ Intégrations logiciels métier
- ❌ Multi-utilisateurs par cabinet
- ❌ Espagnol (langue 4)

### Growth Features (Post-MVP)

**Phase 2 (mois 4-6) :**
- Espagnol (4ème langue)
- Plan Enterprise (79€/100 visites) pour power users
- **Historique étendu avec recherche/filtres** (organisation par patient, dates, tags)
- **Archivage optionnel** (conservation > 10 notes sur demande user)
- Export PDF formaté
- Plans multi-utilisateurs (cabinets)

**Phase 3 (mois 7-12) :**
- Intégrations API logiciels métier
- Facturation équipe/cabinet
- Tableau de bord analytics usage
- Transcription live visible (option UX avancée)

### Vision (Futur)

- Application mobile native (iOS/Android)
- Fine-tuning modèle sur données réelles anonymisées
- Intégration directe HL7/FHIR
- Reconnaissance vocale offline

## User Journeys

### Journey 1 : Greg le Kiné - Découverte Trial

**Persona : Greg**
- Kiné indépendant, cabinet solo
- 7 nouveaux patients/semaine, documentation chronophage
- A entendu parler d'IA pour automatiser les notes
- Sceptique mais curieux

**Opening Scene (Jour 1 - Lundi matin, 8h45) :**

Greg arrive au cabinet, 4 patients programmés aujourd'hui. Il a 15 minutes avant le premier. Il ouvre SOAP Notice sur son laptop.

"OAuth Google - OK, ça c'est rapide." Trial 7 jours, 5 visites. "Parfait, je teste sur mes nouveaux patients cette semaine."

**Premier patient (9h00) :**

Mme Dupont, 52 ans, douleur lombaire. Greg lit le script de consentement : "Pour optimiser la qualité de nos échanges, je vais enregistrer notre conversation..." Elle acquiesce.

Il clique **Record**. Indicateur rouge visible. Il mène son anamnèse normalement, oublie presque qu'il enregistre.

10 minutes plus tard, fin de l'examen physique. Il clique **Stop**.

*"Note en cours de génération..."*

Il fait entrer Mme Dupont dans la salle de traitement. 20 secondes plus tard, notification : "Note prête."

**Climax (9h25 - Entre deux patients) :**

Greg ouvre la note. Structure SOAP complète :
- Subjective : Douleur L4-L5, irradiation jambe droite, depuis 5 jours...
- Objective : ROM lombaire limité, test Lasègue positif...
- Clinical Reasoning : Probable hernie discale...
- Management Plan : Traitement

Il relit. 95% correct. Il édite 2 petits détails (un chiffre, une formulation).

**Copier → Coller dans son logiciel métier.**

**Temps total économisé : 6 minutes.**

**Resolution :**

*"Putain, ça marche. Vraiment."*

Greg utilise ses 4 visites restantes dans la semaine. À chaque fois, même résultat : note en < 30s, qualité excellente, 5-6 min gagnées.

Vendredi soir, il souscrit au plan Pro (49€/mois). Il envoie le lien à 3 collègues.

---

### Journey 2 : Greg le Kiné - Usage Quotidien (Mois 2)

**Situation :** Greg est maintenant abonné Pro (50 visites/mois). SOAP Notice fait partie de sa routine.

**Routine typique (Mardi après-midi) :**

14h00 - Patient 1 : Record → Stop → Note générée → Copie
14h45 - Patient 2 : Record → Stop → Note générée → Copie
15h30 - Patient 3 : Record → Stop → Note générée → Copie

**Flow automatique.** Il n'y pense même plus. C'est comme respirer.

**Incident (Mercredi matin) :**

Patient parle très vite, accent prononcé. Greg clique Stop. Note générée... mais la transcription a manqué 2 phrases clés.

Il édite manuellement (1 min). Puis copie.

*"OK, pas parfait, mais quand même mieux que tout retaper."*

**Dashboard :** 23/50 visites utilisées. "Nickel, je suis large."

---

### Journey 3 : Greg le Kiné Power User - Dépassement Quota

**Situation (Semaine 3 du mois) :**

Greg a une semaine chargée : 12 nouveaux patients au lieu de 7 habituels (collègue malade, il prend ses patients).

Dashboard : **48/50 visites.**

Jeudi matin, il génère sa 50ème note. Message apparaît :

*"Quota atteint pour ce mois. Renouvellement le 15 du mois. Besoin de plus de visites ?"*

**[Acheter +5 visites (5€)] [Acheter +10 visites (10€)]**

Greg clique **+10 visites**. Stripe débite 10€. Quota passe à 60/60.

*"Parfait, je finis ma semaine tranquille."*

**Réflexion :** *"Si ça continue comme ça, je vais passer au plan Enterprise..."*

---

### Journey 4 : Greg le Founder - Monitoring & Support

**Opening Scene (Samedi matin, 10h) :**

Greg ouvre son laptop, pas en tant que kiné, mais en tant que créateur de SOAP Notice.

Dashboard admin :
- 23 users actifs (dont 18 payants)
- 342 visites générées cette semaine
- MRR : 847€
- 2 tickets support ouverts

**Support Ticket 1 :**

*"Bonjour, ma note est incomplète, la section Objective est vide."*

Greg ouvre Sentry. Logs : L'audio était trop court (2 min), le patient n'a presque rien dit pendant l'examen physique.

Il répond : *"Bonjour, l'enregistrement était court et le patient peu bavard pendant l'examen. Essayez de décrire à voix haute ce que vous observez pendant la palpation/ROM."*

**Support Ticket 2 :**

*"L'app ne génère rien depuis 10 min."*

Greg check Sentry : Deepgram timeout. Il redémarre le worker FastAPI. Problème résolu en 3 min.

**Monitoring latence :**

Temps moyen génération : 24s (✅ < 30s).
99e percentile : 38s (⚠️ légèrement au-dessus).

*Note mentale : "Investiguer les cas > 30s la semaine prochaine."*

**Décision produit :**

Greg voit que 3 users ont acheté +10 visites 2 fois ce mois.

*"Signal clair : Ces gens-là ont besoin du plan Enterprise. Je le lance dans 2 mois."*

**Resolution :**

Greg ferme son laptop. 18 payants, ça fait 847€ MRR. Objectif 3 mois : 20 users / 580-980€ → **Il est sur la bonne trajectoire.**

Il retourne à son cabinet. Lundi, il est kiné. Le weekend, il est founder.

---

### Journey Requirements Summary

Ces 4 journeys révèlent les capabilities suivantes :

**Core Product (Journeys 1-3) :**
- OAuth Google onboarding
- Trial 7j / 5 visites
- Recording live avec indicateur
- Génération note < 30s
- Édition post-transcription
- Dashboard visites restantes
- Historique 10 dernières notes
- Upsell quota (+5/+10 visites)
- Script consentement patient (FR/DE/EN)

**Admin/Founder (Journey 4) :**
- Dashboard admin (users, MRR, visites)
- Monitoring latence (Sentry)
- Support tickets (voir logs user)
- Métriques business (conversion, usage)

## Domain-Specific Requirements

### Classification Réglementaire

**Statut dispositif médical (EU MDR 2017/745) :**
- SOAP Notice est un **outil de documentation clinique**, non un dispositif médical
- Pas d'objectif médical direct (pas de diagnostic, traitement, ou prévention)
- Comparable à un dictaphone + assistant de saisie
- **Hors scope réglementation dispositifs médicaux**

**Important :** Si des fonctionnalités de suggestion diagnostique ou détection automatique de pathologies sont ajoutées à l'avenir, une réévaluation réglementaire sera nécessaire (classification probable Classe I ou IIa).

**Responsabilité professionnelle :**
- Le professionnel de santé reste **seul responsable légalement** du contenu de la note clinique
- L'édition post-génération est encouragée et accessible
- Le système ne fait aucune suggestion diagnostique ou thérapeutique
- Disclaimer implicite intégré dans les CGU

**Accès aux données :**
- Seul le kiné accède aux notes via l'application
- Le patient obtient sa note via le dossier officiel du professionnel (circuit standard)
- Pas d'accès patient direct via SOAP Notice

---

### Conformité RGPD - Données de Santé (Art. 9)

**Architecture conforme EU :**

| Composant | Provider | Localisation | Conformité |
|-----------|----------|--------------|------------|
| **LLM Extraction** | **Mistral AI** | 🇫🇷 France | ✅ RGPD natif |
| **STT** | Deepgram EU | 🇪🇺 EU data residency | ✅ DPA requis |
| **Database** | PostgreSQL | 🇪🇺 EU (Supabase/Neon) | ✅ RGPD natif |
| **Hosting Backend** | Railway/Render | 🇪🇺 EU region | ✅ Configurable |

**Stratégie LLM :**
- **MVP :** Mistral Large 2 (France, conformité RGPD garantie)
- **Evolution :** Architecture switchable vers Azure OpenAI (EU) si besoin
- **Interdit :** Claude API (US), OpenAI direct (US) sans garanties EU

**Architecture LLM Switchable :**
```python
# Configuration via variable d'environnement
LLM_PROVIDER=mistral  # ou azure_openai

# Abstraction permettant le switch sans refonte
class BaseLLMClient(ABC):
    @abstractmethod
    async def extract_soap_note(transcript, template) -> str
```

**Chiffrement et sécurité :**
- TLS 1.3 en transit
- PostgreSQL chiffré au repos
- Clés API stockées dans secrets management (pas en clair)

**Rétention et suppression :**
- Audio : **0 jours** (suppression immédiate post-transcription)
- Transcriptions : **Max 10 notes** (suppression rolling automatique)
- Métadonnées : Conservées avec les notes
- Droit à l'oubli : Suppression complète sur demande user

**Consentement patient :**
- Consentement **verbal** recueilli par le professionnel
- Scripts fournis dans l'app (FR/DE/EN)
- Pas de stockage du consentement dans l'app (responsabilité du professionnel)

**DPA (Data Processing Agreements) requis :**
- ✅ Mistral AI (à obtenir)
- ✅ Deepgram (vérifier option EU + DPA)
- ✅ PostgreSQL provider (Supabase/Neon fournissent DPA standard)

---

### Audit Trail & Métadonnées

**Traçabilité complète pour chaque note générée :**

```json
{
  "note_id": "uuid",
  "user_id": "uuid",
  "created_at": "2026-01-15T09:23:45Z",
  "language": "fr",
  "audio_duration_seconds": 612,
  "transcription_provider": "deepgram",
  "llm_provider": "mistral",
  "llm_model": "mistral-large-2",
  "original_content": "...",
  "edited_content": "...",
  "edit_count": 2,
  "last_edited_at": "2026-01-15T09:25:12Z",
  "copied_at": "2026-01-15T09:25:30Z"
}
```

**Usages de l'audit trail :**
- Support technique (investigation problèmes qualité)
- Défense en cas de litige (preuve de génération + édition)
- Métriques qualité (taux d'édition, sections modifiées)
- Amélioration continue (feedback loop)

**Rétention métadonnées :**
- Conservées avec la note (suppression synchronisée)
- Agrégations anonymisées conservées pour analytics (opt-in)

---

### Risques Domaine Healthcare & Mitigations

| Risque | Probabilité | Impact | Mitigation MVP |
|--------|-------------|--------|----------------|
| **Transcription imprécise → erreur clinique** | Moyenne | Critique | Édition post-génération obligatoire + disclaimer responsabilité |
| **Fuite de données de santé** | Faible | Critique | Chiffrement bout-en-bout + providers EU RGPD-compliant + DPA |
| **Hallucination LLM → information fausse** | Faible | Élevé | User satisfaction ≥ 4/5 + feedback loop + édition accessible |
| **Classification dispositif médical future** | Faible | Moyen | Veille réglementaire + pas de features diagnostiques MVP |
| **Non-conformité RGPD** | Faible | Critique | Architecture 100% EU + DPA tous providers + audit annuel |
| **Responsabilité juridique fondateur** | Faible | Critique | CGU claires + assurance RC pro + legal counsel |

---

### Intégrations & Interopérabilité (Post-MVP)

**MVP :** Aucune intégration directe. Copy-paste manuel vers logiciels métier existants.

**Growth Phase (Phase 2-3) :**
- Intégrations possibles : Kinvent, Thérasoft, Deskimo (logiciels kinés EU)
- Protocoles : API REST, HL7 FHIR si applicable
- Prérequis : Accords partenariats + certifications éventuelles

---

### Validation Qualité Terrain

**Avant lancement MVP public :**

1. **Test Mistral Large 2 sur 10 cas réels** (Greg + 2-3 early adopters)
   - Critère succès : ≥ 8/10 notes satisfaisantes (≥ 4/5)
   - Si < 8/10 → Switch vers Azure OpenAI (EU)

2. **Test multilingue** (FR/DE/EN)
   - Validation précision Deepgram + Mistral sur chaque langue
   - Critère succès : Qualité équivalente sur les 3 langues

3. **Stress test latence**
   - 10 enregistrements simultanés
   - Validation < 30s après Stop maintenu

**Critères de validation domaine :**
- ✅ Conformité RGPD validée (legal counsel)
- ✅ DPA signés avec tous providers
- ✅ Audit trail fonctionnel
- ✅ Qualité notes ≥ 4/5 sur échantillon test
- ✅ Architecture switchable LLM testée

