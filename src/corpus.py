"""Principe : on parcourt le corpus une seule fois et on note, pour chaque forme de L, ce que LL regarde.
Pourquoi : LL juge un candidat d'après ses occurrences ; les relever une fois évite de relire le corpus.
Exemple : « sur la planète Terminus » -> Terminus : milieu de phrase ; « sur la Terre » -> précédent « sur »."""
from collections import Counter

from src.liste_l import N_MAX, decouper_mots
from src.nettoyage import DOSSIER_PROPRE, lire_pages
from src.ressources import charger_liste

# Après ces signes, la majuscule peut être celle d'un début de phrase ou de réplique
FIN_DE_PHRASE = {".", "!", "?", '"', "-", ":", ";", "(", "…"}


def toutes_les_pages():
    """Renvoie la liste des mots de chaque page du corpus."""
    return [decouper_mots(texte)
            for chemin in sorted(DOSSIER_PROPRE.glob("*.txt"))
            for texte in lire_pages(chemin)]


def formes_en(mots, i):
    """Renvoie les (forme, nombre de tokens) qui commencent en i, écrites comme dans L."""
    formes = [(" ".join(mots[i:i + n]), n) for n in range(1, N_MAX + 1) if i + n <= len(mots)]
    # L écrit « Mur d'Hélicon » sans espace après l'apostrophe
    if i + 2 < len(mots) and mots[i + 1] in ("d'", "d’"):
        formes.append((f"{mots[i]} {mots[i + 1]}{mots[i + 2]}", 3))
    return formes


def en_milieu_de_phrase(mots, i):
    """Vrai si l'occurrence en position i n'ouvre ni la page ni une phrase."""
    return i > 0 and mots[i - 1] not in FIN_DE_PHRASE and not mots[i - 1].endswith(".")


def mot_precedent(mots, i, articles):
    """Mot avant la position i, en sautant les articles : dans « sur la Terre », c'est « sur » qui compte."""
    j = i - 1
    while j >= 0 and mots[j].lower().rstrip("'’") in articles:
        j -= 1
    return mots[j].lower() if j >= 0 else ""


def analyser_corpus(L):
    """Renvoie {"candidats": {forme: fiche}} ; fiche = n, fréquence, occurrences en milieu de phrase, mots précédents."""
    articles = charger_liste("articles.txt")
    fiches = {c: {"n": n, "frequence": 0, "milieu": 0, "precedents": Counter()} for c, n, f in L}
    for mots in toutes_les_pages():
        for i in range(len(mots)):
            for forme, n in formes_en(mots, i):
                if forme in fiches:
                    fiche = fiches[forme]
                    fiche["frequence"] += 1
                    fiche["milieu"] += en_milieu_de_phrase(mots, i)
                    fiche["precedents"][mot_precedent(mots, i, articles)] += 1
    return {"candidats": fiches}
