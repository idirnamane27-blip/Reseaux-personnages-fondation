# Article (4 pages, style Interspeech)

Fichiers à importer dans un projet Overleaf créé depuis le modèle
[Interspeech Paper Kit](https://www.overleaf.com/latex/templates/interspeech-paper-kit/svqkgcpdbxfg)
(le modèle fournit `Interspeech.cls` et le style de bibliographie) :

- `main.tex` : l'article ;
- `mybib.bib` : la bibliographie ;
- `figures/fon.pdf`, `figures/fee.pdf`, `figures/sdf.pdf` : à mettre dans un dossier `figures` du projet.

Dans Overleaf : *Menu* > *Main document* = `main.tex`, puis *Recompile*.

Les figures sont produites par `python -m src.reseau.livres` puis `python -m src.reseau.figures`
(copies de `resultats/reseau/livres/*_article.pdf`, au format d'une colonne).
