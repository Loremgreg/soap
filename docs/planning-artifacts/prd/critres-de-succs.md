# Critères de Succès

## Succès Utilisateur

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

## Succès Business

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

## Succès Technique

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

## Résultats Mesurables

**Après 3 mois :**
- ✅ 20 utilisateurs payants actifs
- ✅ Taux de conversion trial ≥ 30%
- ✅ Temps génération < 30s après Stop (mesuré via monitoring)
- ✅ Satisfaction qualité note ≥ 4/5
- ✅ Zéro incident sécurité/RGPD
- ✅ 580-980€ MRR généré (mix Starter/Pro)
