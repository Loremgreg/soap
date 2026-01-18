# Project Context Analysis

## Requirements Overview

**Functional Requirements:**
L'application SOAP Notice présente un flux linéaire mais techniquement exigeant :
1. **Authentification** : OAuth Google (session management simple)
2. **Recording** : Capture audio jusqu'à 10 minutes avec Wake Lock API
3. **Transcription temps réel** : WebSocket streaming vers Deepgram nova-3
4. **Extraction SOAP** : Appel Mistral AI post-transcription (< 30s)
5. **Édition/Copie** : Interface mobile-first avec auto-save
6. **Historique limité** : Max 10 notes avec suppression rolling
7. **Gestion quotas** : Compteur temps réel avec upsell intégré
8. **Paiement** : Stripe avec anniversary billing

**Non-Functional Requirements:**
- **Performance** : Latence totale < 30s après Stop (critique)
- **Disponibilité** : 99% uptime cible
- **Sécurité** : RGPD Art. 9 compliance, TLS 1.3, chiffrement repos
- **Rétention** : Audio = 0 jours, Notes = max 10 rolling
- **Localisation données** : 100% EU (providers, hébergement, DB)

**Scale & Complexity:**
- Domaine principal : Full-stack PWA mobile-first
- Niveau de complexité : Moyen-Haut
- Composants architecturaux estimés : 8-10 modules

## Technical Constraints & Dependencies

| Contrainte | Détail |
|------------|--------|
| **LLM Provider** | Mistral AI (MVP) avec abstraction switchable vers Azure OpenAI |
| **STT Provider** | Deepgram nova-3, WebSocket streaming obligatoire |
| **Database** | PostgreSQL EU (Neon recommandé - serverless, scale-to-zero, migration facile) |
| **Backend** | Python FastAPI (async, WebSocket natif) |
| **Frontend** | Vite + React + TailwindCSS + shadcn/ui |
| **Paiement** | Stripe (webhooks, anniversary billing) |
| **Auth** | Google OAuth 2.0 |

## Database Provider Decision

**Choix : Neon (PostgreSQL Serverless)**

Justification :
- **Scale-to-zero** : Coût proche de 0€ pendant développement/faible usage
- **PostgreSQL standard** : Aucun vendor lock-in, migration triviale vers self-hosted
- **EU Data Residency** : Région Frankfurt disponible (RGPD compliant)
- **Connection pooling intégré** : Compatible FastAPI async
- **Branching** : Clone DB en 1 seconde pour tests/staging

Migration future vers self-hosted si nécessaire :
- `pg_dump` pour export complet
- Changement de `DATABASE_URL` dans `.env`
- Temps estimé : 30-60 minutes

## Cross-Cutting Concerns Identified

1. **Sécurité & Conformité RGPD** - Chiffrement, DPA providers, audit trail
2. **Gestion d'erreurs robuste** - Retry logic, fallbacks, user feedback
3. **Observabilité** - Sentry, métriques latence, monitoring quotas
4. **Internationalisation** - UI (FR/DE/EN), scripts consentement, notes multilingues
5. **État temps réel** - WebSocket status, quota counter, recording state
