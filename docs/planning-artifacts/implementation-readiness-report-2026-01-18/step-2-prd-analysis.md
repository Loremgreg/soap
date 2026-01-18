# Step 2: PRD Analysis

## Functional Requirements (FRs)

| ID | Requirement | Source |
|----|-------------|--------|
| FR1 | OAuth Google en 1 clic | Scope MVP |
| FR2 | Sélection plan (Starter 29€ ou Pro 49€) | Scope MVP |
| FR3 | Trial 7 jours (5 visites max) | Scope MVP |
| FR4 | Recording live avec indicateur simple | Scope MVP |
| FR5 | Stop → Transcription instantanée | Flux core |
| FR6 | Extraction SOAP via LLM < 30s | Flux core |
| FR7 | Affichage note SOAP structurée | Flux core |
| FR8 | Édition post-génération | Scope MVP |
| FR9 | Copier dans presse-papier | Flux core |
| FR10 | Sauvegarde note dans historique | Flux core |
| FR11 | Historique max 10 notes (rolling) | Scope MVP |
| FR12 | Notification avant suppression note ancienne | Comportements Critiques |
| FR13 | Paiement Stripe anniversary billing | Scope MVP |
| FR14 | Dashboard compteur visites | Scope MVP |
| FR15 | Blocage soft à quota atteint | Protection Économique |
| FR16 | Upsell +5/+10 visites | Protection Économique |
| FR17 | 3 langues interface (FR/DE/EN) | Scope MVP |
| FR18 | Scripts consentement patient | Scope MVP |
| FR19 | Note = langue app utilisateur | Comportements Critiques |
| FR20 | Suppression immédiate audio | Sécurité |
| FR21 | API suppression complète (RGPD) | Sécurité |
| FR22 | Audit trail par note | Domain Requirements |
| FR23 | Dashboard admin | User Journeys |
| FR24 | Monitoring Sentry | User Journeys |

**Total: 24 FRs**

## Non-Functional Requirements (NFRs)

| ID | Requirement | Criticité |
|----|-------------|-----------|
| NFR1 | Latence < 30s après Stop | 🔴 Critique |
| NFR2 | Satisfaction ≥ 4/5 | 🔴 Critique |
| NFR3 | 99% uptime | 🟡 Important |
| NFR4 | TLS 1.3 transit | 🔴 Critique |
| NFR5 | PostgreSQL chiffré repos | 🔴 Critique |
| NFR6 | Données EU uniquement | 🔴 Critique |
| NFR7 | Rate limit 10 uploads/h/user | 🔴 Critique |
| NFR8 | Max 10 min/audio | 🔴 Critique |
| NFR9 | 1 trial/email | 🔴 Critique |
| NFR10 | Monitoring usage temps réel | 🔴 Critique |
| NFR11 | Architecture LLM switchable | 🟡 Important |
| NFR12 | DPA tous providers | 🔴 Critique |
| NFR13 | Sentry + métriques latence | 🔴 Critique |

**Total: 13 NFRs**

## PRD Completeness: ✅ PASS

---
