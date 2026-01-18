# User Journeys

## Journey 1 : Greg le Kiné - Découverte Trial

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

## Journey 2 : Greg le Kiné - Usage Quotidien (Mois 2)

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

## Journey 3 : Greg le Kiné Power User - Dépassement Quota

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

## Journey 4 : Greg le Founder - Monitoring & Support

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

## Journey Requirements Summary

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
