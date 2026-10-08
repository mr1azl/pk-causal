# Protocole d'appariement: lancer un marché en VBB en s'appuyant sur un marché déjà lancé

13 marchés profilés sur la même fenêtre et la même méthode. Lancés: PK, SA, CA,
MY, mesurés **avant** leur switch du 2 septembre (16 juillet au 1er septembre).
Candidats: FR, ES, IT, PL, JP, KR, BR, OM, AE, mesurés sur leur état actuel,
qui est par définition un état pré-switch (16 juillet au 7 octobre).

Écrit le 8 octobre 2026. Complète la checklist, ne la remplace pas: la checklist
dit quoi vérifier, ce document dit **quel marché prendre comme référence et si
le test pourra seulement conclure**.

---

## Le résultat qui change l'ordre des priorités

La checklist traite la calibration comme le point central. Le profilage dit
autre chose: **la contrainte qui mord d'abord est le volume de réservations, pas
la calibration.**

Pour détecter une baisse de 30 % du taux de réservation, à 80 % de puissance et
5 % bilatéral, il faut **150 réservations dans le bras témoin**. En ajoutant
2 semaines d'apprentissage à exclure et 2 semaines de queue de conversion
(round 7c: une fenêtre de 14 jours ne voit que 88,5 % de ses réservations):

| marché | lancé | résa/sem | semaines pour conclure | verdict |
|---|---|---|---|---|
| CA | oui | 63,7 | **9** | lisible en un trimestre |
| SA | oui | 22,5 | **17** | lisible en deux trimestres |
| MY | oui | 19,5 | 19 | lisible en deux trimestres |
| **AE** | non | **19,0** | **20** | **lisible en deux trimestres** |
| PK | oui | 16,2 | 22 | un an, impossible par groupe |
| **OM** | non | 12,6 | 28 | un an, impossible par groupe |
| **FR** | non | 12,3 | 28 | un an, impossible par groupe |
| **ES** | non | 8,7 | 38 | un an, impossible par groupe |
| **BR** | non | 5,2 | 62 | **non testable** |
| **IT** | non | 4,7 | 68 | **non testable** |
| **PL** | non | 3,3 | 95 | **non testable** |
| **KR** | non | 1,7 | 180 | **non testable** |
| **JP** | non | 1,1 | 276 | **non testable** |

**Cinq des neuf candidats ne peuvent pas produire de résultat lisible au niveau
du compte**, encore moins par groupe de destinations. Le Japon demanderait cinq
ans. Ce n'est pas un argument pour ne pas lancer, c'est un argument pour **ne
pas prétendre mesurer** et pour décider autrement: par analogie avec un marché
apparié, avec des garde-fous opérationnels, pas par un test.

**Et le holdout à 20 % de la checklist Inde est sous-dimensionné.** Un bras
témoin plus petit a besoin de moins d'événements mais les collecte plus
lentement, et le second effet l'emporte: **il faut 1,4 fois plus de semaines
qu'un split 50/50** pour la même réponse. Si on teste, c'est 50/50.

---

## Les appariements

Distance euclidienne sur six dimensions standardisées sur les 13 marchés:
dispersion de CPC, rank lost, budget lost, impression share, recherches par
réservation, part cross-device. Les deux ratios sont comparés en logs.

**Exclu volontairement: la calibration de valeur par destination.** Le round 7d
a montré que PK avait la plus faible dispersion des quatre marchés et le pire
résultat. Elle ne prédit pas, l'inclure serait de la fausse précision.

| candidat | plus proche | prior | d1 | 2e | d2 | ratio | lecture |
|---|---|---|---|---|---|---|---|
| **AE** | **SA** | **+20%** | 1,28 | MY | 2,54 | **1,99** | **appariement net** |
| **OM** | **SA** | **+20%** | 2,14 | MY | 3,92 | **1,83** | **appariement net** |
| KR | SA | +20% | 2,15 | CA | 3,15 | 1,47 | faible, garder les deux |
| ES | SA | +20% | 2,50 | MY | 3,59 | 1,44 | faible, garder les deux |
| FR | SA | +20% | 2,04 | MY | 2,58 | 1,27 | faible, garder les deux |
| BR | PK | **-63%** | 3,34 | SA | 3,82 | 1,14 | ambigu, pas de prior |
| PL | SA | +20% | 3,05 | PK | 3,44 | 1,13 | ambigu, pas de prior |
| IT | MY | -29% | 2,87 | SA | 3,00 | 1,05 | ambigu, pas de prior |
| JP | SA | +20% | 3,01 | MY | 3,06 | 1,01 | ambigu, pas de prior |

Un appariement n'est utilisable que si le marché le plus proche est nettement
plus proche que le suivant. **Deux le sont: AE et OM, tous deux vers SA**, le
seul marché qui soit sorti gagnant du switch.

---

## Les profils, pour lire les appariements

| marché | résultat | CPC | p10 | p90 | **dispersion** | rank lost | budget lost | IS | rech/résa | cross-device |
|---|---|---|---|---|---|---|---|---|---|---|
| **SA** | **+20%** | 0,31 | 0,23 | 0,46 | **2,0** | 54% | 11% | 36% | 421 | 26% |
| CA | -26% | 1,15 | 0,42 | 2,06 | 4,8 | 72% | 6% | 22% | 348 | 23% |
| MY | -29% | 0,45 | 0,37 | 0,56 | 1,5 | 69% | 12% | 20% | 368 | 42% |
| **PK** | **-63%** | 0,32 | 0,18 | 1,63 | **9,2** | **31%** | 12% | **57%** | **1190** | **68%** |
| AE | | 0,42 | 0,35 | 0,55 | 1,6 | 50% | 11% | 39% | **191** | 22% |
| OM | | 0,34 | 0,24 | 0,50 | 2,1 | 36% | 11% | 53% | 264 | 32% |
| FR | | 0,48 | 0,31 | 1,23 | **4,0** | 59% | 13% | 29% | 991 | 34% |
| ES | | 0,34 | 0,28 | 0,47 | 1,7 | 40% | 16% | 44% | 880 | 38% |
| IT | | 0,35 | 0,25 | 0,68 | 2,7 | 61% | 13% | 27% | 1955 | 62% |
| BR | | 0,27 | 0,20 | 0,41 | 2,0 | 34% | 17% | 49% | 1323 | 67% |
| PL | | 0,27 | 0,22 | 0,36 | 1,7 | 39% | 14% | 47% | 1417 | 64% |
| KR | | 0,50 | 0,24 | 1,08 | **4,5** | 48% | 12% | 40% | 300 | 0% |
| JP | | 0,48 | 0,31 | 0,61 | 2,0 | 56% | 20% | 25% | 534 | 15% |

**Aucune dimension n'est monotone avec le résultat sur les quatre marchés
lancés.** Je l'ai testé et je le dis plutôt que de fabriquer un prédicteur sur
quatre points. Ce qu'on voit, c'est que **PK est extrême sur cinq dimensions à
la fois** et que PK est le résultat extrême: dispersion 9,2 contre 1,5 à 4,8,
rank lost 31 % contre 54 à 72, impression share 57 % contre 20 à 36,
1 190 recherches par réservation contre 348 à 421, 68 % de cross-device contre
23 à 42.

Le protocole n'est donc pas "prédire le résultat". C'est **repérer les candidats
qui ressemblent à PK là où PK était extrême, et dimensionner le test pour qu'il
puisse répondre**.

---

## Le protocole, dans l'ordre

### Étape 1. Puissance avant tout
Compter les réservations du registre `QR_Booking` par semaine sur 8 semaines.
Sous **5 par semaine, ne pas monter de test**: décider par analogie et
surveiller. Entre 5 et 15, test possible mais au niveau du compte seulement, pas
par groupe de destinations. Au-dessus de 15, un test par groupe devient
envisageable sur les deux ou trois plus gros groupes.

### Étape 2. Apparier
Calculer les six dimensions, standardiser contre le panel des 13, prendre la
distance au marché lancé le plus proche. **Exiger un ratio d1 sur d2 d'au moins
1,5** pour utiliser le prior. En dessous, il n'y a pas de référence utilisable
et il faut traiter le lancement comme un premier cas.

### Étape 3. Lire les quatre signaux de risque PK
Non pas comme un score, mais comme quatre questions à poser une par une:

1. **Dispersion de CPC au-dessus de 4.** Un plafond de CPC unique ne peut pas
   convenir à la fois au décile bas et au décile haut. C'est le mécanisme du
   round 7, celui qui a tué le UK en PK. **Concerne FR (4,0) et KR (4,5).**
2. **Rank lost sous 35 %.** Peu à gagner en montant, donc le bidder monte le
   prix sans acheter de volume. **Concerne BR (34 %) et OM (36 %).**
3. **Plus de 800 recherches par réservation.** Le signal de valeur est alors
   très dilué et le test très long. **Concerne IT, PL, BR, FR, ES.**
4. **Cross-device au-dessus de 55 %.** Le tableau de bord ne comptera pas des
   transactions. **Concerne IT (62 %), PL (64 %), BR (67 %).**

### Étape 4. Décider la forme du lancement
- Appariement net **et** puissance suffisante: test 50/50 par groupe, prior du
  marché apparié comme hypothèse.
- Appariement net, puissance insuffisante: lancement par analogie, garde-fous
  du marché apparié, pas de test.
- Pas d'appariement: ne pas lancer tant qu'un marché comparable n'a pas été
  lancé et lu.

### Étape 5. Les garde-fous, dans tous les cas
Du round 7c: lire à J+14 minimum sur des données vieilles d'au moins 14 jours,
jamais sur 7. Du round 3: surveiller budget lost et rank lost ensemble, un rank
lost qui tombe à zéro avec un budget lost qui monte est la signature de PK. Du
round 7: ne jamais poser un plafond de CPC unique sur un compte dont la
dispersion dépasse 3, le poser par groupe.

---

## Les neuf candidats, un par un

**AE, à lancer en premier.** Appariement le plus net du panel vers SA, le seul
succès, ratio 1,99. 19 réservations par semaine, lisible en 20 semaines. Profil
sain partout: dispersion 1,6, rank lost 50 %, **191 recherches par réservation,
le meilleur des 13 marchés**, cross-device 22 %. Aucun des quatre signaux PK.
C'est le lancement qui apprendra le plus pour le moins de risque.

**OM, en second.** Appariement net vers SA, ratio 1,83. Mais **rank lost à 36 %**,
le deuxième plus bas des candidats, donc le signal 2 est allumé: poser un
plafond de CPC avant de switcher. 28 semaines pour conclure, donc test au niveau
du compte seulement.

**FR, prudence.** Appariement faible vers SA, et **dispersion 4,0**, la deuxième
plus élevée du panel après KR. Le p90 est à 1,23 contre un p10 à 0,31. C'est la
configuration qui a fait que le plafond de PK a sauvé deux tiers du compte et
tué l'autre tiers. Si FR est lancé, **plafonds par groupe de destinations, pas
un plafond de compte**, et 991 recherches par réservation veut dire 28 semaines
de lecture.

**ES, possible mais lent.** Appariement faible vers SA, profil sans signal
allumé sauf la dilution (880 recherches par réservation). 38 semaines.

**KR, non.** Appariement faible vers SA mais **dispersion 4,5, la plus élevée du
panel**, et 1,7 réservation par semaine. 180 semaines pour conclure. Le
cross-device à 0 % est lui-même suspect et mérite une vérification de tagging
avant toute autre chose.

**JP, non.** 1,1 réservation par semaine, 276 semaines, aucun appariement
utilisable (ratio 1,01). Décider par analogie ou ne pas décider.

**IT, non.** Aucun appariement utilisable (ratio 1,05), **1 955 recherches par
réservation, le pire du panel**, cross-device 62 %, 68 semaines. Trois signaux
sur quatre allumés.

**PL, non.** Ratio 1,13, 1 417 recherches par réservation, cross-device 64 %,
95 semaines.

**BR, non, et pour une raison de plus.** C'est **le seul candidat dont le voisin
le plus proche est PK**, le marché qui s'est effondré. L'appariement est ambigu
(ratio 1,14) donc je n'en fais pas une prédiction, mais combiné à un rank lost
de 34 %, un cross-device de 67 % et 62 semaines de lecture, il n'y a aucune
raison de commencer par là.

---

## Et SA, puisque tu l'as déjà activé

SA est la référence du panel et il vaut la peine de dire pourquoi, parce que
c'est ce qu'on cherche à reproduire.

Au moment du switch SA avait **rank lost 54 %**, c'est-à-dire beaucoup à gagner
en montant les enchères, donc une hausse de CPC achetait du volume au lieu de
brûler le budget. Son CPC est monté 2,1 fois contre 6,6 pour PK. Sa dispersion
interne était de 2,0, donc le compte entier réagit à peu près pareil à un même
réglage. 421 recherches par réservation et 26 % de cross-device, les deux dans
la moitié saine du panel.

**Mais SA n'avait pas non plus de ROAS cible ni de plafond de CPC.** Son +20 %
n'est pas le produit d'une bonne configuration, c'est le produit d'une structure
de marché qui pardonnait la configuration. C'est une nuance qui compte avant de
répliquer: ce qu'il faut copier de SA, c'est le profil de marché, pas le
paramétrage.

---

## Limites

- Quatre marchés lancés, dont un seul résultat catastrophique. Aucun des
  prédicteurs ici n'est validé statistiquement et je ne les présente pas comme
  tels.
- Les résultats PK -63, SA +20, CA -26, MY -29 viennent du round 6, mesurés en
  réservations par 1 000 recherches, 20 sept au 5 oct contre 13 juin au 19 août.
  Le round 6 a aussi montré que ces chiffres bougent beaucoup selon la fenêtre:
  sur la fenêtre du readiness report, CA ressort à +17 %.
- Les profils candidats sont sur 12 semaines, les profils lancés sur 6,9
  semaines pré-switch. Les ratios sont robustes à ça, les volumes absolus non.
- Le registre `QR_Booking` ne couvre que 8 semaines ici, donc les réservations
  par semaine ont une marge réelle sur les petits marchés. JP repose sur 9
  transactions, KR sur 13.
- Les comptes retenus sont les comptes Google non-brand les plus dépensiers de
  chaque marché. FR, ES, IT, JP, KR, BR ont tous un compte en langue locale
  quasi vide à côté du compte EN, qui n'est pas analysé ici.
