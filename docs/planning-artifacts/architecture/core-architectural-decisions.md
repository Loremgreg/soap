# Core Architectural Decisions

## Data Architecture

| Décision | Choix | Justification |
|----------|-------|---------------|
| **ORM** | SQLAlchemy 2.0 async | Standard Python, type-safe, async natif |
| **Migrations** | Alembic | Auto-génère migrations depuis modèles, rollback facile |
| **Cache** | Pas de cache MVP | < 100 users, complexité non justifiée |

## Configuration Rules

**Principe : Configuration-driven, pas de changement de code pour modifier les paramètres business.**

Les paramètres suivants sont stockés dans la table `plans` et modifiables sans déploiement :

| Paramètre | Description | Exemple valeurs |
|-----------|-------------|-----------------|
| `max_notes_retention` | Nombre max de notes conservées par user | 10 |
| `max_recording_minutes` | Durée max d'un enregistrement | 10 |
| `quota_monthly` | Nombre de visites par mois | 20, 50 |
| `price_monthly` | Prix mensuel en centimes | 2900, 4900 |

**Implémentation :**
```python
# Les limites sont lues depuis la DB, jamais hardcodées
user_plan = await get_user_plan(user_id)
if recording_duration > user_plan.max_recording_minutes * 60:
    raise AudioTooLongError()
```

**Avantages :**
- Ajout de nouveaux plans sans déploiement
- A/B testing de pricing possible
- Ajustement des limites en production instantané

## Authentication & Security

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Session** | JWT | Stateless, scalable, standard API |
| **Librairie OAuth** | Authlib | Standard Python, bien documenté |
| **Stockage token** | Cookie httpOnly | Protégé XSS, envoi automatique |

## API & Communication

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Versioning** | `/api/v1/` préfixe URL | Évolutivité sans breaking changes |
| **Format erreurs** | JSON structuré + codes HTTP | Standard, facile à parser côté frontend |
| **Rate limiting** | slowapi | Protection abus, simple à intégrer FastAPI |
| **WebSocket audio** | Backend proxy vers Deepgram | Sécurité (clé API cachée), contrôle quotas |

**Format d'erreur standardisé :**
```json
{
  "error": {
    "code": "QUOTA_EXCEEDED",
    "message": "Quota mensuel atteint",
    "details": { "current": 50, "limit": 50 }
  }
}
```

## Frontend Architecture

| Décision | Choix | Justification |
|----------|-------|---------------|
| **State Management** | Zustand + TanStack Query | Zustand = état local léger, TanStack Query = données serveur avec cache |
| **Routing** | TanStack Router | Cohérence avec TanStack Query, type-safe |
| **Formulaires** | React Hook Form | Performant (pas de re-render), validation intégrée |
| **Capture Audio** | Web Audio API native | 0 dépendance, suffisant pour streaming |

## Infrastructure & Deployment

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Hébergement Frontend** | Vercel | Gratuit, CDN global, auto-deploy GitHub |
| **Hébergement Backend** | Railway | ~5€/mois, région EU, supporte WebSocket |
| **CI/CD** | Intégré Vercel/Railway | Push GitHub → Deploy automatique |
| **Environnements** | Variables d'env Vercel/Railway | Séparation dev/prod, secrets sécurisés |
| **Monitoring** | Sentry | Gratuit, alertes erreurs, stack traces |

## Cost Analysis MVP

| Service | Coût/mois |
|---------|-----------|
| Vercel (Frontend) | 0€ |
| Railway (Backend) | ~5€ |
| Neon (Database) | 0€ |
| Sentry (Monitoring) | 0€ |
| **Total** | **~5€/mois** |
