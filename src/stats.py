"""Principe : décrire le corpus et les trois listes, pour chaque livre et au total.
Pourquoi : la taille d'un livre et la richesse de son vocabulaire aident à lire les scores de L, LP et LL.
Exemple : python -m src.stats -> rendu/statistiques.txt (pages, tokens, types, hapax, 20 mots fréquents, tailles des listes)."""
from collections import Counter

from src.corpus import formes_en
from src.extraction import RACINE
from src.liste_l import DOSSIER_RESULTATS, decouper_mots, lire_L
from src.nettoyage import DOSSIER_PROPRE, lire_pages

FICHIER_STATS = RACINE / "rendu" / "statistiques.txt"
NB_FREQUENTS = 20


def lire_LP():
    """[formes de chaque personnage] de LP.txt (personnage TAB fréquence TAB formes séparées par « | »)."""
    lignes = (DOSSIER_RESULTATS / "LP.txt").read_text(encoding="utf-8").splitlines()
    return [l.split("\t")[2].split(" | ") for l in lignes]


def compter_livre(pages, formes):
    """Nombre de pages, Counter des mots (en minuscules, sans ponctuation), Counter des formes cherchées."""
    mots_du_livre, formes_vues = Counter(), Counter()
    for texte in pages:
        mots = decouper_mots(texte)
        mots_du_livre.update(m.lower() for m in mots if m[0].isalnum())
        for i in range(len(mots)):
            formes_vues.update(f for f, n in formes_en(mots, i) if f in formes)
    return len(pages), mots_du_livre, formes_vues


def bloc(titre, nb_pages, mots, formes_vues, L, LP, LL):
    tokens, types = sum(mots.values()), len(mots)
    hapax = sum(1 for n in mots.values() if n == 1)
    return [f"=== {titre}",
            f"pages             : {nb_pages}",
            f"tokens            : {tokens}",
            f"types             : {types}",
            f"ratio types/tokens: {types / tokens:.3f}",
            f"hapax             : {hapax} ({hapax / types:.0%} des types)",
            f"{NB_FREQUENTS} mots les plus fréquents : "
            + ", ".join(f"{m} ({n})" for m, n in mots.most_common(NB_FREQUENTS)),
            f"taille de L       : {sum(1 for f in L if formes_vues[f])} formes",
            f"taille de LP      : {sum(1 for formes in LP if any(formes_vues[f] for f in formes))} personnages",
            f"taille de LL      : {sum(1 for f in LL if formes_vues[f])} lieux", ""]


def main():
    L = [c for c, n, f in lire_L("L.txt")]
    LL = [c for c, n, f in lire_L("LL.txt")]
    LP = lire_LP()
    formes = set(L) | set(LL) | {f for p in LP for f in p}
    lignes = ["# Statistiques du corpus (pages impaires) et des listes L, LP, LL, par livre et au total "
              "(python -m src.stats)", ""]
    total_pages, total_mots, total_formes = 0, Counter(), Counter()
    for chemin in sorted(DOSSIER_PROPRE.glob("*.txt")):
        nb_pages, mots, formes_vues = compter_livre(lire_pages(chemin), formes)
        lignes += bloc(chemin.stem.replace("_impaires", ""), nb_pages, mots, formes_vues, L, LP, LL)
        total_pages += nb_pages
        total_mots += mots
        total_formes += formes_vues
    lignes += bloc("Total", total_pages, total_mots, total_formes, L, LP, LL)
    texte = "\n".join(lignes)
    FICHIER_STATS.write_text(texte, encoding="utf-8", newline="\n")
    print(texte)


if __name__ == "__main__":
    main()
