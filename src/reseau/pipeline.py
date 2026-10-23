"""Principe : le même enchaînement d'étapes pour tout corpus découpé en chapitres.
Pourquoi : la soumission Kaggle et l'évaluation locale doivent mesurer exactement le même programme.
Exemple : extraire_reseaux(chapitres_leaderboard()) -> {"paf0": Graph, ...}, journal des rejets."""
from src.reseau.alias import groupes_du_chapitre, resoudre_alias
from src.reseau.filtre import Filtre
from src.reseau.graphe import construire_graphe
from src.reseau.ner import extraire_mentions
from src.reseau.rappel import Rappel, lexique_par_livre


def livre(identifiant):
    """« paf12 » -> « paf »."""
    return identifiant.rstrip("0123456789")


def analyser(chapitres, nom_corpus="leaderboard", cache=True, rappel=True, verbeux=True):
    """REN -> filtre -> rappel -> alias (par livre) ;
    renvoie ({ID: mentions gardées}, {livre: groupes de noms}, journal des rejets)."""
    mentions, _ = extraire_mentions(chapitres, nom_corpus, cache)
    filtre = Filtre([t for _, t in chapitres])
    journal = {}
    gardees = {i: filtre.filtrer(mentions[i], journal) for i, _ in chapitres}
    if rappel:
        outil, lexiques = Rappel(), lexique_par_livre(gardees)
        avant = sum(map(len, gardees.values()))
        gardees = {i: outil.completer(t, gardees[i], lexiques[livre(i)]) for i, t in chapitres}
        # les occurrences retrouvées par le rappel reçoivent aussi leur article (« du Mulet » non, « le Mulet » oui)
        for mentions_chapitre in gardees.values():
            for m in mentions_chapitre:
                filtre.avec_article(m)
        if verbeux:
            print(f"rappel : {avant} -> {sum(map(len, gardees.values()))} mentions")

    par_livre = {}
    for identifiant, mentions_chapitre in gardees.items():
        par_livre.setdefault(livre(identifiant), []).extend(mentions_chapitre)
    groupes_livre = {l: resoudre_alias(ms) for l, ms in par_livre.items()}
    return gardees, groupes_livre, journal


def extraire_reseaux(chapitres, nom_corpus="leaderboard", cache=True, rappel=True, verbeux=True):
    """REN -> filtre -> rappel -> alias (par livre) -> graphe ; renvoie ({ID: Graph}, journal des rejets)."""
    gardees, groupes_livre, journal = analyser(chapitres, nom_corpus, cache, rappel, verbeux)
    graphes = {}
    for identifiant, _ in chapitres:
        groupes = groupes_du_chapitre(gardees[identifiant], groupes_livre[livre(identifiant)])
        graphes[identifiant] = construire_graphe(gardees[identifiant], groupes)
    return graphes, journal
