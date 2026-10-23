# Réseaux de personnages par livre : analyse qualitative

Graphes produits par `python -m src.reseau.livres` puis `python -m src.reseau.figures` (fichiers `fon`, `fee`,
`sdf` en `.graphml` et `.png` dans ce dossier ; mesures complètes dans `mesures.txt`).

## Méthode

Chaque roman de la trilogie est coupé en blocs de 5 pages et passe par le pipeline utilisé pour le leaderboard
(REN spaCy étendue aux titres, filtre, rappel des noms validés dans le livre, résolution d'alias et de surnoms au
niveau du livre). Un nœud est un groupe d'alias, et le poids d'une arête est le nombre de co-occurrences à 25 tokens
ou moins, additionnées sur tous les blocs. Les communautés sont calculées par optimisation gloutonne de la modularité,
avec les poids. L'intermédiarité utilise la distance 1/poids.

**Limite du corpus.** Nous n'avons que les pages impaires des trois romans : la moitié du texte manque, et deux pages
consécutives du fichier ne se suivent pas dans le livre. Les poids sont donc environ deux fois trop faibles, et
certaines co-occurrences relient la fin d'une page à une page qui ne la suit pas.

| Roman | Personnages | Liens | Densité | Composante principale | Plus central (degré, intermédiarité) |
|---|---|---|---|---|---|
| Fondation | 64 | 101 | 0,050 | 53 | Salvor Hardin (26 ; 0,49) |
| Fondation et Empire | 47 | 111 | 0,103 | 40 | le Mulet (20 ; 0,30) |
| Seconde Fondation | 49 | 87 | 0,074 | 33 | A. Darell, en fait le docteur Toran Darell (12 ; 0,15) |

## Fondation : un roman à épisodes

*Fondation* est un recueil de cinq nouvelles séparées par des sauts de plusieurs décennies : Les Psychohistoriens
(Seldon, Gaal Dornick), Les Encyclopédistes et Les Maires (Salvor Hardin), Les Marchands (Limmar Ponyets, Eskel
Gorov), Les Princes marchands (Hober Mallow). Le graphe retrouve cette structure. Les quatre plus grandes communautés
correspondent aux épisodes :

1. **Hardin** (Pirenne, Wienis, Lee, Sermak, Lepold Ier, Verisof, Dorwin, Rodric) : les deux nouvelles dont il est le
   héros forment une seule communauté, puisque le même personnage fait le lien entre elles ;
2. **Mallow** (Twer, Jael, Sutt, Jord Parma, Onum Barr, Asper Argo) : Les Princes marchands ;
3. **Seldon et Gaal Dornick** : Les Psychohistoriens ;
4. **Les Marchands** (Gorov, Ponyets, Pherl, le Grand Maître).

C'est le roman le moins dense (0,050) : les épisodes partagent peu de personnages. Hardin a la plus forte
intermédiarité (0,49), car il est présent dans deux nouvelles. **Hari Seldon** (0,36) est presque au niveau de Mallow
(0,38) alors qu'il est mort après la première partie : ses apparitions enregistrées dans le caveau et les références au Plan le relient à
chaque époque. Il y joue le rôle de fil conducteur du cycle, et le graphe le montre bien.

**Erreurs visibles.** Ponyets, héros des Marchands, n'a qu'une mention : on y fait surtout référence par « le
Marchand », qui forme un nœud à part (25 mentions). « Ponyets » seul n'est jamais reconnu par spaCy, et le rappel ne
cherche que les noms complets déjà validés. « le Grand » (pour « le Grand Maître ») et « Grand Prêtre » sont des
fonctions plus que des personnes. « Cassandre Seldon » est un surnom ironique donné à Seldon pendant son procès, et
reste séparé de lui. « Achille », dans la communauté de Seldon, vient de l'expression « talon d'Achille ».

## Fondation et Empire : deux parties, un pont

Le roman a deux parties : Le Général (Bel Riose, Ducem Barr, Lathan Devers, Brodrig, l'empereur Cléon II) et Le Mulet
(Bayta, Toran, Magnifico, Ebling Mis, Han Pritcher). Les deux grandes communautés recouvrent exactement ces deux
parties. Une troisième, **Seldon, Randu, Indbur**, correspond à la crise de l'ouverture du caveau sur Terminus.

C'est le graphe le plus dense (0,103), car la seconde partie est un huis clos entre quatre personnages qui voyagent
ensemble (Bayta, Toran, Magnifico, Mis). Le **Mulet** est le personnage le plus central (degré 20, intermédiarité
0,30) bien qu'il n'apparaisse presque jamais en personne avant la fin : on parle de lui sans cesse. Cela montre la
différence entre co-occurrence et interaction. Hari Seldon (0,27) et Bel Riose (0,26) font le pont entre les deux
parties.

**Erreur révélatrice.** **Magnifico** et **le Mulet** sont deux nœuds reliés par 7 co-occurrences. Or Magnifico, le
bouffon, *est* le Mulet, et le lecteur ne l'apprend qu'à la dernière page. Aucune méthode fondée sur les noms ne
peut fusionner ces deux nœuds. Pour le lecteur qui découvre le livre, le graphe est d'ailleurs fidèle : deux
personnages distincts. « le Marchand » (Devers) et « Majesté Impériale » (Cléon II) restent séparés de leur porteur,
car ce sont des formules d'adresse sans nom propre à côté.

## Seconde Fondation : la confusion des Darell et des titres

Le roman a deux parties : la recherche de la Seconde Fondation par le Mulet (Bail Channis, Han Pritcher, le Premier
Orateur), puis, soixante ans plus tard, par un groupe de Terminus (le docteur Toran Darell, Pelleas Anthor, Homir
Munn, Semic, Turbor) et par Arcadia Darell, l'adolescente qui part seule vers Kalgan et Trantor (Callia, le Premier
Citoyen Stettin, Preem Palver). Les trois communautés retrouvent ces trois fils de l'intrigue.

C'est ici que les erreurs de résolution d'alias sont les plus parlantes :

- **Les Darell.** Le docteur Darell, sa fille Arcadia et ses ancêtres Bayta et Toran Darell (héros du livre
  précédent, cités) portent le même nom. « Darell » seul est rattaché au nom long le plus cité qui le contient,
  « A. Darell », la signature d'Arcadia sur un devoir. Le nœud regroupe en fait le docteur Darell, mais il porte le
  libellé de sa fille, qui forme son propre nœud « Arcadia ». Un nom de famille partagé par une famille entière ne
  peut pas être résolu par inclusion de noms.
- **« Premier Citoyen »** est le titre du Mulet dans la première partie, et celui de Stettin, seigneur de Kalgan,
  dans la seconde. Les deux sont fusionnés en un seul nœud, ce qui relie à tort les deux époques.
- **le Premier Orateur et Preem Palver** sont deux nœuds, alors que la fin révèle que le paysan Palver est le Premier
  Orateur : c'est le même cas que Magnifico et le Mulet.
- **« Arkady »**, le surnom d'Arcadia, forme un nœud séparé. La règle des abréviations demande que toutes les
  lettres du surnom se retrouvent dans l'ordre dans le nom, et le « k » d'Arkady n'est pas dans « Arcadia ».

## Bilan

Sur les trois romans, les communautés retrouvent la structure en parties de l'intrigue et les personnages les plus
centraux sont les héros attendus (Hardin, Mallow, Bayta, le Mulet, Darell). Hari Seldon apparaît dans les trois
réseaux comme un pont entre les époques, ce qui correspond à son rôle de fil conducteur du cycle.

Les erreurs restantes se rangent en trois familles :

1. **Rappel insuffisant des noms de famille seuls** (Ponyets) ;
2. **Résolution d'alias par les noms** : elle échoue quand plusieurs personnes partagent un nom de famille (les
   Darell) ou un titre (Premier Citoyen), et ne peut pas réunir une identité cachée (Magnifico et le Mulet, Palver
   et le Premier Orateur) ;
3. **Formules d'adresse et fonctions** sans nom propre (« le Marchand », « Majesté Impériale », « le Grand ») ;
4. **Mots de début de réplique** pris pour des noms : impératifs (« Calmez », « Terminez », « Retirez »),
   onomatopées (« Hmmm »). Une règle qui rejette les mots jamais vus avec une majuscule en milieu de phrase les
   supprime (score local 0,900 -> 0,966), mais elle a fait baisser le score Kaggle (0,74077 -> 0,72747) alors
   qu'elle ne retirait que 17 nœuds de ce type ; nous ne l'avons pas gardée.

La co-occurrence mesure qu'un personnage est *mentionné* avec un autre, pas qu'ils interagissent : le Mulet est
central dans *Fondation et Empire* parce qu'on parle de lui, pas parce qu'il est présent.
