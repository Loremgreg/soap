# Scope Produit

## MVP - Minimum Viable Product

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
- ✅ **Notification suppression** : Alerte + confirmation avant suppression de la note la plus ancienne (quand limite atteinte)
- ✅ **Langue note = langue app** : La note générée est TOUJOURS dans la langue de l'app utilisateur, pas dans la langue de la transcription

**Exclu du MVP :**
- ❌ Historique illimité ou archivage long terme
- ❌ Organisation par patient (recherche, filtres, tags)
- ❌ Transcription live visible pendant enregistrement
- ❌ Export PDF
- ❌ Intégrations logiciels métier
- ❌ Multi-utilisateurs par cabinet
- ❌ Espagnol (langue 4)

## Growth Features (Post-MVP)

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

## Vision (Futur)

- Application mobile native (iOS/Android)
- Fine-tuning modèle sur données réelles anonymisées
- Intégration directe HL7/FHIR
- Reconnaissance vocale offline
