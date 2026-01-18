# Domain-Specific Requirements

## Classification Réglementaire

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

## Conformité RGPD - Données de Santé (Art. 9)

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

## Audit Trail & Métadonnées

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

## Risques Domaine Healthcare & Mitigations

| Risque | Probabilité | Impact | Mitigation MVP |
|--------|-------------|--------|----------------|
| **Transcription imprécise → erreur clinique** | Moyenne | Critique | Édition post-génération obligatoire + disclaimer responsabilité |
| **Fuite de données de santé** | Faible | Critique | Chiffrement bout-en-bout + providers EU RGPD-compliant + DPA |
| **Hallucination LLM → information fausse** | Faible | Élevé | User satisfaction ≥ 4/5 + feedback loop + édition accessible |
| **Classification dispositif médical future** | Faible | Moyen | Veille réglementaire + pas de features diagnostiques MVP |
| **Non-conformité RGPD** | Faible | Critique | Architecture 100% EU + DPA tous providers + audit annuel |
| **Responsabilité juridique fondateur** | Faible | Critique | CGU claires + assurance RC pro + legal counsel |

---

## Intégrations & Interopérabilité (Post-MVP)

**MVP :** Aucune intégration directe. Copy-paste manuel vers logiciels métier existants.

**Growth Phase (Phase 2-3) :**
- Intégrations possibles : Kinvent, Thérasoft, Deskimo (logiciels kinés EU)
- Protocoles : API REST, HL7 FHIR si applicable
- Prérequis : Accords partenariats + certifications éventuelles

---

## Validation Qualité Terrain

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

