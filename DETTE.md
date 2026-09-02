# Dette d'exactitude réglementaire / métier

Constats trouvés en cours de travail, volontairement NON corrigés au moment
où ils ont été trouvés (hors périmètre du chantier en cours à ce moment-là),
consignés ici pour ne pas être perdus. À traiter en bloc, après le socle de
clauses (`backend/bands.py`, `backend/composer.py`, `backend/clauses/`) et
la rédaction des clauses elles-mêmes.

## 0. ÉVOLUTION PRIORITAIRE — donner un contenu propre à la section Positionnement

- **Contexte** : la comparaison à une référence sectorielle inventée a été
  retirée (chantier du 2026-09-02). La section « Positionnement » affiche
  désormais un classement **interne** des trois piliers — vrai, mais proche
  d'un doublon du tableau de bord de la page 2.
- **La vraie valeur d'un outil de suivi pluriannuel** : comparer l'entreprise
  **à elle-même**, exercice après exercice. La donnée existe déjà
  (`score_history` sur `ESGRequest`, déjà utilisée par la page trajectoire).
- **À faire** : reconstruire la section sur cette comparaison temporelle
  (évolution par pilier, écart au précédent exercice, tendance). Sourcé,
  vrai, et sans doublon. Limite connue : rien à afficher au premier
  exercice — prévoir le repli sur le classement interne actuel.

## 1. `accident_frequency_rate` — barème non recalibré

- **Où** : `backend/esg_calculator.py:132-135` (score), recopié tel quel
  dans `backend/bands.py` (`SEUILS["accident_frequency_rate"]`).
- **Constat** : le barème de score (1 / 3 / 5 / 8 / 15) n'a jamais été
  recalibré vers des valeurs réalistes. La moyenne nationale CNAM tourne
  autour de 20 (ordre de grandeur cité en session, à vérifier contre la
  source CNAM réelle avant correction — ne pas la recopier telle quelle sans
  vérification).
- **Décision pour ce chantier** : `bands.py` s'aligne sciemment sur le
  barème existant, même faux, pour ne pas introduire une divergence
  score/texte le jour où on corrige. La correction devra toucher les DEUX
  endroits **dans le même commit** : `esg_calculator.py` et `bands.py`.

## 1bis. `SECTOR_CARBON_THRESHOLDS` — grille sectorielle non sourcée

- **Où** : `backend/esg_calculator.py:21-40` — 15 familles sectorielles ×
  5 seuils d'intensité carbone (t CO₂e / M€ CA), écrits à la main. Seul
  « sourçage » : le commentaire « une industrie lourde n'est pas jugée sur
  la grille des services ».
- **DISTINCTION IMPORTANTE avec le benchmark ESG supprimé le 2026-09-02** :
  la variation sectorielle de l'intensité carbone est un **vrai fait
  métier**, contrairement à une « moyenne ESG par secteur » qui, elle,
  n'avait aucun fondement. Cette grille ne rend donc pas le rapport faux,
  seulement **imprécis**.
- **Ce qui rend le sujet sérieux malgré tout** : (i) les valeurs ne sont
  adossées à aucune source publiée ; (ii) cette grille pilote le **SCORE**,
  pas seulement le texte — elle influence la note lettrée du livrable ;
  (iii) depuis le chantier clauses, une clause affirme « L'intensité
  carbone est conforme à ce qu'on observe dans son secteur », ce qui
  transforme la grille en affirmation de comparaison sectorielle.
- **À faire** : adosser les seuils à une source réelle et citable (ADEME /
  Base Carbone, intensités sectorielles publiées, ou équivalent), et citer
  cette source dans la note méthodologique. **Même niveau de priorité que
  le TF1 (point 1)** : à traiter dans le chantier « exactitude du scoring »,
  avec le barème accidents et `corruption_cases`.

## 2. `corruption_cases` — absent du score

- **Où** : `backend/esg_calculator.py`, fonction `calculate_governance_score`
  (lignes 155-200). Le champ `corruption_cases` n'y apparaît jamais.
- **Constat** : un cas de corruption déclaré ne fait bouger ni le score de
  gouvernance, ni la note globale. Seul le texte (`content_generator.py:
  790-791`) le mentionne, et uniquement dans le cas `== 0` ("zéro cas de
  corruption enregistré") — rien n'est dit si `> 0`.
- **Anormal pour un indicateur ESG** : à corriger (formule de pénalité à
  ajouter au score, et libellé à écrire pour le cas `> 0`), sujet distinct
  du socle de clauses.

## 3. `female_board_percent` — attribution légale à vérifier

- **Où** : `backend/content_generator.py:777` : `"conforme loi Rixain
  (≥40%)"` pour le seuil de 40% au **conseil d'administration**.
- **Constat (non vérifié, à confirmer contre le texte des lois)** : de
  mémoire, le quota de 40% au conseil d'administration relève de la loi
  Copé-Zimmermann (2011) ; la loi Rixain (2021) porte sur les comités
  exécutifs / comités de direction, avec une trajectoire vers 40% à horizon
  2029-2030 — pas sur le conseil d'administration lui-même.
- **Décision pour ce chantier** : `backend/bands.py` n'inscrit **aucune**
  entrée `CIBLES` pour `female_board_percent` tant que l'attribution légale
  n'est pas vérifiée contre le texte réel des deux lois.

## 4. `female_employees_percent` — "objectif légal 40%" sans fondement identifié

- **Où** : `backend/content_generator.py:741-744` : gap calculé par rapport
  à un "objectif légal 40%" sur l'effectif total de l'entreprise (pas le
  conseil, pas le CODIR).
- **Constat** : aucun fondement légal identifié pour un quota de 40% sur
  l'effectif total en droit français. À vérifier ou à retirer du texte.
- **Décision pour ce chantier** : `backend/bands.py` n'inscrit **aucune**
  entrée `CIBLES` pour `female_employees_percent`.

## 5. Séparateur de milliers anglais dans un texte français

- **Où** : `backend/content_generator.py` (ancien générateur, format `,`
  — ex. ligne 708 : `f"{env.energy_consumption_mwh:,.0f} MWh consommés"`)
  et, par alignement volontaire, `backend/composer.py._formater_valeur()`.
- **Constat** : les nombres sortent en `12,000` (séparateur anglais) dans
  un texte français, où l'usage est `12 000`.
- **Décision pour ce chantier** : le composer **reproduit sciemment** le
  format de l'ancien générateur. Corriger seulement le composer ferait
  cohabiter `12 000` (sections déjà migrées) et `12,000` (sections encore
  sur l'ancien générateur) dans un même rapport, ce qui se verrait.
- **À faire** : passer tout le système en `12 000` **d'un seul coup**,
  ancien générateur + composer, avec un test de non-régression sur le
  rendu. Ne pas le faire section par section.

## 6. `include_benchmarks` : drapeau défini mais jamais lu

- **Où** : `backend/models.py:245` définit `include_benchmarks: bool = True`.
- **Constat** : aucun générateur ne teste ce drapeau (`grep` : 2 occurrences
  en tout, le modèle et un test). La section correspondante s'affiche donc
  toujours, même si le consultant la désactive dans le formulaire.
- **Décision** : non traité pendant le chantier « référence sectorielle »
  — le drapeau perd en partie son objet maintenant que la comparaison
  externe a disparu. À réévaluer : soit le câbler sur la section
  Positionnement, soit le retirer du modèle et du formulaire.

---

*Ce fichier est un registre, pas un plan d'action daté. Le retirer d'une
ligne seulement quand la vérification a été faite ET la correction
appliquée aux deux endroits concernés (score + bands le cas échéant).*
