# Sécurité & Contraintes Économiques

## Sécurité des Données (RGPD Art. 9)

| Mesure | Implémentation |
|--------|----------------|
| Chiffrement transit | TLS 1.3 |
| Chiffrement repos | PostgreSQL chiffré (EU) |
| Localisation données | Serveurs EU uniquement |
| Rétention audio | **0 jours** (suppression immédiate post-transcription) |
| Rétention notes | **Max 10 dernières notes** (suppression rolling avec notification) |
| Droit à l'oubli | API de suppression complète |
| Consentement patient | Script verbal (FR/DE/EN) fourni dans app |

## Protection Économique (Abus API)

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
