# Checklist avant de passer un nouveau marché en VBB

*Tirée de l'investigation PK (switch du 2 sept. 2026) et de la revue pré-lancement Inde. Chaque point renvoie à
l'erreur ou au piège qu'il évite. À dérouler dans l'ordre : un point bloquant non résolu = pas de switch.*

Légende : **[B]** bloquant, **[R]** recommandé.

---

## 1. Mesure : savoir compter les réservations avant de changer quoi que ce soit

- [ ] **[B] Source de vérité choisie et écrite.** Adobe eVar84 (réservations créditées au jour du clic) ou le
  registre Floodlight `QR_Booking` (`FROM conversion`, une ligne par transaction). En PK les deux concordent
  (89 vs 89).
- [ ] **[B] Ne jamais utiliser "Bookings (FL)" / "Revenue (FL)".** Ces métriques additionnent `QR_Booking` et le tag
  Google `Booking`, donc deux systèmes. C'est l'origine des "68 % de réservations sans revenu" en PK.
- [ ] **[B] `QR_Booking` all_conversions réservé aux comparaisons.** Le cross-device modélisé le gonfle : 3,5x le
  registre en PK, 9,8x sur le régional. Ces conversions arrivent tard, donc les 2 à 3 dernières semaines sont
  toujours sous-estimées. C'est ce qui a créé la fausse "casse" de CA et MY.
- [ ] **[R] Extraction Adobe eVar84 en place pour le marché**, avec un historique d'au moins 12 mois pour la
  saisonnalité.
- [ ] **[R] Parseur de noms de campagne testé sur les deux conventions** (pipe `Google|XX|Dest|...` et legacy
  `_XX-Country-...`). Un parseur pipe seul a perdu 71 % de la dépense 2025 en PK.

## 2. Signal de valeur : ce que le bidder va réellement optimiser

- [ ] **[B] Composition de l'objectif du portefeuille connue.** Quelles actions sont primaires, avec quelle valeur.
  Repérer les actions de test (ex. `Flight Search (TEST Sept2026)`, valeur 0).
- [ ] **[B] Choix rule-based vs ML justifié.** En PK, les valeurs rule-based (`QR_FlightSearch_VBB`) surévaluent
  le UK alors que les valeurs ML (`QR_FlightSearch_VBB_ML`) sont calibrées. Les ML sont à privilégier si le marché
  y est éligible.
- [ ] **[B] Calibration par groupe de destinations.** Pour chaque groupe (UK, long-courrier, régional, GCC, etc.),
  calculer sur les 3 derniers mois :
  `valeur de recherche par clic / revenu de réservation par clic` (script : `scripts/pk_value_per_search.py`).
  - Un groupe sur-noté de plus de 30 % par rapport aux autres est à risque.
  - En PK : UK 5,0 vs long-courrier 3,8 vs régional 2,9.
- [ ] **[B] Segments à forte valeur et peu de réservations.** En Inde, GCC et Moyen-Orient font 169k clics pour
  5 transactions en 8 semaines, alors que le signal de valeur les note haut.
- [ ] **[R] Sens de la recherche.** La valeur est-elle rattachée à la route recherchée, ou à l'origine du
  client ? Une recherche "Londres vers Lahore" faite depuis une campagne PK n'a pas la même valeur.

## 3. Configuration de la stratégie

- [ ] **[B] Un ROAS cible ou un plafond de CPC défini.** Aucun des 4 marchés switchés (PK, SA, CA, MY) n'en avait.
  Le pic de CPC de la phase d'apprentissage est alors sans limite.
- [ ] **[B] Budget compris.**
  - Budget partagé ou non, et montant.
  - Part de la perte d'impression liée au budget.
  - Un budget partagé limitant laisse le bidder choisir qui perd. En PK, avant le switch, il a coupé de lui-même
    les campagnes pays GB.
- [ ] **[B] Liste des campagnes du portefeuille exportée**, avec ID, nom, destination, budget et stratégie actuelle.
  C'est la liste de retour arrière prête à l'emploi (voir `docs/analysis/13_uk_switchback_campaigns.csv`).
- [ ] **[B] Automatisations identifiées et gelées.** En PK, un script Google Ads et un outil interne réécrivent les
  budgets presque tous les jours, et les listes de négatifs partagées sont recréées tous les quelques jours
  (round 7). Lister tout script ou outil qui touche aux budgets, enchères ou négatifs, connaître son objectif, et
  l'exclure des campagnes du test.
- [ ] **[R] Lire la configuration via l'API Google Ads, pas seulement SA360.** SA360 ne voit ni les termes de
  recherche, ni `change_status` (90 jours), ni `change_event` (30 jours), ni les listes de négatifs partagées.
- [ ] **[R] Snapshot de la configuration complète avant le switch** : stratégies, budgets, enchères, ciblage
  géographique, modificateurs, audiences. L'API SA360 ne donne que les valeurs actuelles, pas l'historique, et
  n'expose pas `change_event`. Sans snapshot, on ne peut pas reconstruire l'état d'avant.

## 4. Calendrier : un seul changement à la fois

- [ ] **[B] Aucun autre changement majeur 3 semaines avant et 3 semaines après** : coupe de budget, restructuration
  ou modifications massives de campagnes, nouveaux mots-clés.
  - En PK, la coupe du 20 août tombe 13 jours avant le switch ; toute comparaison avant/après les mélange.
  - En Inde, 646 modifications de campagnes ont eu lieu les 13-15 et 22-23 sept. sans explication.
- [ ] **[B] Modifications récentes listées et expliquées** (`last_modified_time` des campagnes, groupes d'annonces
  et mots-clés sur les 6 dernières semaines).
- [ ] **[R] Saisonnalité vérifiée sur l'année précédente**, mêmes semaines, par groupe de destinations. Attention :
  le périmètre et les noms de campagnes peuvent avoir changé d'une année sur l'autre.
- [ ] **[R] Pas de switch juste avant un pic** (fêtes, vacances scolaires, Hajj et Umrah, etc.) : la période
  d'apprentissage tomberait dessus.

## 5. Termes de recherche et marque

- [ ] **[B] Rapport des termes de recherche des 3 derniers mois**, classé par :
  - sens : aller, retour inversé, pays tiers, générique ;
  - agences et OTA ;
  - concurrents ;
  - présence du mot marque.

  Script : `scripts/india_search_terms.py`.
- [ ] **[R] Pièges de codes vérifiés à la main.** Exemple : AUS = Austin, pas l'Australie.
- [ ] **[R] Fuite de la marque vers le non-brand mesurée.** Requêtes "qatar" achetées en non-brand, CPC brand.
  Le CPC brand a monté en sept. 2026 aussi en Inde, qui n'avait pas switché : la marque n'est donc pas un témoin
  propre.

## 6. Base de référence et puissance statistique

- [ ] **[B] Réservations par $ et par clic, par groupe de destinations, sur 8 à 12 semaines** (Adobe ou registre).
  Donner des nombres, pas seulement des taux.
- [ ] **[B] Calcul du volume attendu.** Combien de réservations par semaine par groupe ? Sous 5 par semaine, un
  groupe ne sera pas lisible avant/après. En PK, la perte GB repose sur 0 réservation observée contre 4,5 attendues.
- [ ] **[B] Seuils de volume (round 8).** Pour lire une baisse de 30 % (puissance 80 %, 5 % bilatéral), il faut
  environ 150 réservations dans le bras témoin, plus 2 semaines d'apprentissage et 2 semaines de queue.
  - Moins de 5 réservations par semaine (registre) : pas de test, décision sur garde-fous.
  - De 5 à 15 par semaine : test au niveau du compte seulement.
  - Plus de 15 par semaine : lecture possible sur les 2 ou 3 plus gros groupes.

  Ces durées sont un minimum : les campagnes ne sont pas indépendantes.
  Détail : `docs/analysis/14_ROUND8_PAIRING_REVIEW.md`.
- [ ] **[B] Critère de succès et règle de retour arrière écrits avant le switch.** Exemple : "réservations Adobe
  par $ du groupe X inférieures de plus de 40 % à la base pendant 3 semaines après apprentissage, alors retour sur
  ce groupe".
- [ ] **[R] Comparer par $, pas par clic.** En PK, l'"amélioration" par clic hors UK venait de clics moins chers ;
  par $ il n'y avait pas d'effet net.

## 7. Plan de test

- [ ] **[B] Un groupe témoin.** Il faut un témoin pour attribuer un effet au switch. Par ordre de préférence :
  1. Split **50/50** de campagnes appariées (même groupe de destinations, dépense proche), et non un holdout à
     20 % : à 20 %, il faut 1,4 fois plus de semaines pour la même réponse.
  2. Expérience Google Ads (split de campagnes).
  3. Marché comparable non switché, en dernier recours.

  Ne pas utiliser le résultat d'un marché "apparié" comme prior : les résultats des marchés lancés dépendent de la
  fenêtre et de la mesure (SA vaut +20 % sur le round 6, -21 % en commandes Adobe par $).

  La marque ne convient pas comme témoin, et ne doit pas l'être (c'était le témoin du Causal Impact PK).
- [ ] **[R] Switch progressif.** Commencer par les groupes bien calibrés et garder sur l'ancienne stratégie les
  groupes à risque identifiés aux sections 2 et 5.
- [ ] **[R] Position Google Flights (GFS) vérifiée** sur les routes principales : rang, part la moins chère, écart
  de prix. Les tables ne contiennent pas les concurrents, ce qui limite la lecture.

## 8. Après le switch : suivi

- [ ] **[B] Tableau de bord hebdomadaire par groupe de destinations** : coût, clics, CPC, réservations Adobe par
  jour de clic, réservations par $, revenu par $.
- [ ] **[B] Garde-fou par destination, pas seulement au total.** En PK, le total a tenu grâce à la marque, alors
  que la Grande-Bretagne tombait à 0.
- [ ] **[R] Lecture à J+21 minimum**, en excluant les 2 premières semaines d'apprentissage pour l'efficacité et les
  2 à 3 dernières semaines pour les conversions modélisées.
- [ ] **[R] Pas d'autre changement pendant la lecture** (voir section 4).

---

## Résumé : les 10 bloquants

| # | Check | Erreur évitée (PK / Inde) |
|---|---|---|
| 1 | Source de réservations : Adobe ou registre, jamais "Bookings (FL)" | 68 % de "réservations sans revenu" fictives |
| 2 | Composition de l'objectif du portefeuille connue | Action TEST à valeur 0, signal inconnu en Inde |
| 3 | Valeurs ML, ou rule-based calibrées par destination | UK surévalué (5,0 vs 2,9) |
| 4 | ROAS cible ou plafond de CPC | Pic de CPC sans limite |
| 5 | Budget et perte d'impression liée au budget compris | Campagnes GB coupées par le bidder |
| 6 | Snapshot de configuration et liste de retour arrière | API sans historique |
| 7 | Aucun autre changement à ±3 semaines | Coupe du 20 août, 646 modifications en Inde |
| 8 | Termes de recherche classés, segments à risque isolés | GCC, sens inversé, Austin |
| 9 | Base par $ et volume attendu par groupe | Effet UK sur 4,5 réservations attendues |
| 10 | Critère de succès, retour arrière et groupe témoin écrits avant | Marque utilisée comme témoin |
