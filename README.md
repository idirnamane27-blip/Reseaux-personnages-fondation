# AMS-1 — Entités nommées dans le cycle de Fondation

Trois listes tirées des trois romans (pages impaires) : **L** (suites de mots à majuscule), **LP** (personnages),
**LL** (lieux et organisations). Aucun nom n'est écrit à la main.

## Arborescence

```
corpus/                       PDF des trois romans (pages impaires)
texte/                        texte brut extrait des PDF, page par page
texte_propre/                 texte nettoyé (numéros de page retirés, mots recollés)
ressources/
  antidictionnaire.txt        mots outils du français (principe 1 de LL)
  pronoms.txt                 pour repérer les verbes + pronom (« Dit-il ») (principe 1 de LL)
  articles.txt                sautés devant un candidat (« sur la Terre »)
  prepositions_lieu.txt       sur, vers, dans, depuis (indice préposition de LL)
  noms_communs.txt            noms communs de Lexique 3.83 (créé une fois par outils/creer_noms_communs.py)
outils/
  creer_noms_communs.py       télécharge Lexique 3.83, garde les mots dont la catégorie principale est NOM
src/
  extraction.py               PDF -> texte/
  nettoyage.py                texte/ -> texte_propre/
  liste_l.py                  tâche 1 : liste L des suites de mots à majuscule
  ressources.py               lecture des fichiers de ressources/
  corpus.py                   un seul parcours du corpus : fréquence, milieu de phrase, mot précédent
  majuscule_de_nom.py         principe 1 : la majuscule doit être celle d'un nom (départ des candidats de LL)
  lp2/                        tâche 2 : LP
    pipeline.py               enchaîne les étapes, écrit LP.txt, LP_formes.txt, LP_journal.txt
    majuscule.py              étape 1 : majuscule gardée en milieu de phrase
    titres.py                 règle A : titres calculés avec le dictionnaire
    dictionnaire.py           noms communs de Lexique (ressources/noms_communs.txt)
    exemples.py               étape 2 : personnes sûres et non-personnes sûres
    spacy_lieux.py            étape 2 : mots que spaCy voit dans des lieux (cache resultats/spacy_lp2/)
    modele.py                 étape 3 : bayésien naïf sur les voisins de chaque occurrence
    regroupement.py           étapes 4 et 5 : retrait des titres, une ligne par personnage, règle B
  ll/                         tâche 3 : LL
    pipeline.py               candidats, nettoyage, deux indices, décision OU ; écrit LL.txt, LL_journal.txt
    l1_candidats.py           candidats : passent le principe 1, moins les formes de LP
    nettoyage_ll.py           retire les titres calculés par LP2 et les gentilés
    l2_preposition.py         indice 1 : suit souvent sur / vers / dans / depuis
    l3_spacy.py               indice 2 : avis de spaCy (LOC + ORG + MISC > PER)
  stats.py                    statistiques du corpus et des trois listes -> rendu/statistiques.txt
  rendu.py                    copie L, LP, LL de resultats/ vers rendu/, avec une ligne d'en-tête
  kwic.py                     outil de vérification : une forme dans ses contextes (python -m src.kwic "Port" 5)
evaluation/
  evaluation.py               LP par personnage et par livre, LP par forme, LL -> resultats/evaluation.txt
  reference_personnes.txt     référence des noms de personnes
  personnages_reference.txt   la même, regroupée par personnage
  reference_lieux.txt         référence des lieux et organisations (définition en tête)
  tests_rejetes.txt           essais rejetés et limites connues, avec leurs chiffres
resultats/                    L.txt, L_sans_bruit.txt, LP.txt, LP_formes.txt, LP_journal.txt, LL_candidats.txt,
                              LL.txt, LL_journal.txt, evaluation.txt, caches spaCy (spacy_etiquettes.txt, spacy_lp2/)
rendu/                        L.txt, LP.txt, LL.txt, statistiques.txt, rapport.docx
```

## Tâche 2 : de L à LP (src/lp2/)

Tout est appris sur le texte traité, qui peut être un autre roman.

1. **Majuscule** : un mot de L est gardé s'il garde sa majuscule en milieu de phrase dans au moins 90 % des cas,
   s'il contient une minuscule et s'il apparaît au moins k fois pour 100 000 tokens (k = 1).
2. **Titres et exemples sûrs** :
   - un titre est un nom commun du dictionnaire (Lexique) placé au moins 3 fois devant un nom propre
     (« docteur Seldon »), ou une abréviation hors dictionnaire presque toujours suivie d'un point (« Mr. Fogg ») ;
   - personnes sûres : locuteurs d'incise au moins 2 fois (« , dit Seldon », « , dit le Mulet »), sauf les titres ;
     les verbes de parole sont appris sur les incises « dit-il », « demanda-t-elle » ;
   - non-personnes sûres : après sur/vers/dans/à/en dans au moins 20 % des cas, après un article dans au moins
     50 % des cas sans jamais parler, ou vues comme LOC par spaCy dans au moins 70 % des cas.
3. **Classifieur** : bayésien naïf sur le mot à gauche et le mot à droite de chaque occurrence, entraîné sur les
   exemples sûrs (un tour de bootstrapping) ; gardé si p(personne) >= 0,5 ; les traits jamais vus sont ignorés.
4. **Titres retirés** : « Docteur Seldon » devient « Seldon » ; un titre n'est jamais une ligne.
5. **Regroupement** : un nom complet (tous ses mots sont des personnes) fait une ligne ; un nom seul rejoint le
   seul nom complet qui le contient, sinon il est ambigu ; règle B : une ligne d'un seul mot qui est un nom commun
   (« Excellence ») est supprimée, sauf preuve de personne.

k et p ont été réglés sur Fondation et empire seul, puis testés une fois sur Fondation et Seconde Fondation.

## Tâche 3 : de L et LP à LL (src/ll/)

1. **Candidats** : ce qui passe le principe 1 (pas de mot outil, de lettre seule, de chiffre romain, de sigle,
   de verbe + pronom ; vu au moins une fois en milieu de phrase) et n'est pas une forme de LP.
2. **Nettoyage** : on retire les titres calculés par LP2 (« Commodore ») et les gentilés (« Korelliens » :
   suffixe -ien, -ais, -ois... dont le radical commence un autre candidat).
3. **Indice préposition** : le candidat suit sur / vers / dans / depuis dans au moins 10 % de ses occurrences.
4. **Indice spaCy** (`fr_core_news_md`) : LOC + ORG + MISC > PER ; comptes gardés dans spacy_etiquettes.txt.
5. **Décision** : LL = candidats avec l'indice préposition OU l'indice spaCy.

## Test de généralisation

LP2 a été lancée sans changement sur deux romans qui ne sont pas dans le projet :
`python -m src.lp2.pipeline <fichier.txt> --sortie <dossier>`.

- Jules Verne, *Le Tour du monde en quatre-vingts jours* : Project Gutenberg n° 800 (texte ebooksgratuits),
  de « Jules Verne » à « FIN », sans l'en-tête ni la licence Gutenberg.
- Guy de Maupassant, *Bel-Ami* : Project Gutenberg n° 57430 (*Œuvres complètes*, vol. 13, Louis Conard, 1910),
  de « BEL-AMI. » à « FIN », sans les notes ni la licence.

## Données (non incluses dans le dépôt)

Les romans sont sous droit d'auteur : ils ne sont pas publiés ici. Pour faire tourner le code, placer :

- `corpus_asimov_leaderboard/prelude_a_fondation/chapter_*.txt.preprocessed` et
  `corpus_asimov_leaderboard/les_cavernes_d_acier/chapter_*.txt.preprocessed` (corpus du leaderboard fourni
  sur la page du cours) : suffisent pour `python -m src.reseau.soumission` ;
- `corpus/*.pdf` (trilogie, pages impaires), puis `python -m src.extraction` et `python -m src.nettoyage` :
  nécessaires pour les listes L, LP, LL et pour l'évaluation locale du réseau.

## Installer

```
pip install -r requirements.txt
python -m spacy download fr_core_news_md
python -m outils.creer_noms_communs      # une seule fois : ressources/noms_communs.txt
```

## Tout relancer

```
python -m src.extraction
python -m src.nettoyage
python -m src.liste_l
python -m src.lp2.pipeline
python -m src.ll.pipeline
python -m src.stats
python -m src.rendu
python -m evaluation.evaluation
```

## Sujet 3 : réseaux de personnages (src/reseau/)

Corpus leaderboard dans `corpus_asimov_leaderboard/` (un fichier par chapitre ; `chapter_1` = ID `paf0`).

```
python -m src.reseau.soumission              # -> resultats/reseau/soumission.csv (à déposer sur Kaggle)
python -m src.reseau.soumission --sans-cache # relance spaCy (sinon resultats/reseau/mentions.json est réutilisé
                                             # tant que les textes, le modèle et ressources/titres.txt n'ont pas changé)
python -m src.reseau.soumission --sans-rappel # sans l'étape rappel.py (pour comparer)
python -m evaluation.evaluation_reseau        # évaluation locale -> resultats/reseau/evaluation_locale.txt
```

Le pipeline est dans `src/reseau/pipeline.py` (même code pour la soumission et l'évaluation) ; le cache spaCy
est dans `resultats/reseau/cache/<corpus>/`.

**Graphes par livre (trilogie)** : `python -m src.reseau.livres` puis `python -m src.reseau.figures` ->
`resultats/reseau/livres/` (un `.graphml` et un `.png` par roman, `mesures.txt` : degré, intermédiarité,
communautés). L'analyse qualitative est dans `resultats/reseau/livres/analyse.md`.

**Article** (4 pages, style Interspeech) : `article/` (`main.tex`, `mybib.bib`, figures en PDF), à compiler sur
Overleaf depuis le modèle « Interspeech Paper Kit » (voir `article/LISEZMOI.md`).

**Évaluation locale** : `evaluation/metrique_reseau.py` recode la métrique du sujet (section 3.3 : couplage
biparti, sim_p / sim_r pour les nœuds, Jaccard pour aligner les arêtes). Les références sont dans
`evaluation/annotations_reseau/` (consignes dans LISEZMOI.txt) : des blocs de 5 pages de la trilogie
(`chapitres_trilogie()`), pas des chapitres du leaderboard, que le sujet demande de ne pas annoter.
Le script donne le score par passage et liste les nœuds en trop, manqués et mélangés.

### Scores

| Version | Ajout | Kaggle | Local |
|---|---|---|---|
| v1 | spaCy PER + titres + alias par inclusion | 0.48210 | |
| v2 | filtre (minuscule, gentilés, lieux), bords d'entité, casse, titres seuls | 0.63420 | |
| v3 | rappel des noms validés dans tout le livre, alias au niveau du livre | 0.69532 | |
| v4 | surnoms (même nom de famille + prénoms proches, abréviations) | 0.72574 | 0.658 |
| v5 | locuteurs d'incise, article des surnoms (« le Mulet »), noms communs, titres | 0.74077 | 0.900 |
| v6 | + rejet des mots jamais vus avec une majuscule en milieu de phrase (retirée : le code produit v5) | 0.72747 | 0.966 |

Score local sur 4 passages annotés de la trilogie (optimiste pour v5 : règles corrigées en regardant ces passages).
Les soumissions sont archivées dans `resultats/reseau/soumissions/`.

1. **donnees.py** : lit les chapitres, recolle les traits d'union de fin de ligne, met le texte sur une ligne.
2. **ner.py** : entités PER de spaCy (`fr_core_news_md`), étendues au titre qui précède (`ressources/titres.txt`) :
   la référence annote « Dr Sarton » en entier.
3. **filtre.py** : corrige les bords d'entité (« L’Empereur », « Jéhu galopa », « VI Le Maire », et en début de
   phrase seulement « Grimace de Seldon ») puis, pour un nom d'un seul mot (titres à part), retire dans l'ordre :
   les gentilés (-ien, -ite) ; garde les **locuteurs** d'au moins 2 incises (« fit Mis », « dit le Mulet » ; verbes
   de parole appris sur « dit-il », « demanda-t-elle », moins `ressources/auxiliaires.txt`) ; retire les mots plus
   souvent en minuscule qu'avec une majuscule en milieu de phrase (« Vraiment ») ; les lieux (souvent après
   sur/vers/dans/depuis, « à », « de » ou un article) ; les noms communs de Lexique seuls (« Excellence ») —
   un titre prouve la personne (« R. Sammy »). L'article fait partie du nom quand le nom le suit souvent
   (« le Mulet », « le Premier Orateur »), comme dans les consignes d'annotation. Rejets : `resultats/reseau/rejets.txt`.
   Le vote LOC/PER de spaCy n'est pas utilisé : il voit « Seldon » LOC plus souvent que PER.
4. **rappel.py** : un nom validé une fois dans un livre est recherché partout dans ce livre (spaCy rate des
   occurrences) ; en cas de chevauchement, la mention la plus longue gagne. 1 775 -> 3 002 mentions.
5. **alias.py** : sans les titres et sans la casse, un nom long absorbe ceux qu'il contient ; un nom d'un mot
   rejoint le nom long le plus cité qui le contient (à égalité, ordre alphabétique) ; un titre seul
   (« Empereur ») rejoint le seul personnage qui porte ce titre, sinon il est retiré. Les groupes sont faits
   sur le livre entier puis restreints à chaque chapitre.
   Surnoms : règle A, deux noms complets de même nom de famille dont les prénoms se ressemblent fusionnent
   (« Lije Baley » -> « Elijah Baley », mais pas « Jessie Baley » / « Bentley Baley ») ; règle B, un mot seul
   qui commence comme un nom plus long et dont toutes les lettres s'y retrouvent dans l'ordre en est
   l'abréviation (« Ben » -> « Bentley »).
6. **graphe.py** : lien si deux mentions sont à 25 tokens ou moins ; poids = nombre de co-occurrences ;
   attribut `names` = alias séparés par « ; ».
