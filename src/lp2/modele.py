"""Étape 3 : un classifieur bayésien naïf juge chaque candidat d'après ses voisins.
Pourquoi : une personne et un lieu n'ont pas les mêmes voisins (« dit Seldon », « Seldon sourit » / « sur Terminus ») ;
appris sur les exemples sûrs, le modèle juge aussi les candidats qui n'ont jamais parlé.
Exemple : « Riose » n'est jamais locuteur assez souvent, mais ses voisins ressemblent à ceux des personnes."""
import math
from collections import Counter

P_BOOTSTRAP = 0.9   # un candidat aussi sûr devient un exemple pour le second tour


def occurrences(pages, candidats):
    """{candidat: [traits de chaque occurrence]} ; traits = mot à gauche et mot à droite, en minuscule."""
    traits = {c: [] for c in candidats}
    for mots in pages:
        for i, mot in enumerate(mots):
            if mot in traits:
                gauche = mots[i - 1].lower() if i > 0 else ""
                droite = mots[i + 1].lower() if i + 1 < len(mots) else ""
                traits[mot].append(("G:" + gauche, "D:" + droite))
    return traits


def entrainer(traits, personnes, non_personnes):
    """Comptes des traits par classe (1 = personne, 0 = non-personne)."""
    comptes = {1: Counter(), 0: Counter()}
    for classe, mots in ((1, personnes), (0, non_personnes)):
        for mot in mots:
            for occurrence in traits[mot]:
                comptes[classe].update(occurrence)
    return comptes


def probabilite(occurrences_mot, comptes):
    """Moyenne sur les occurrences de P(personne | traits) ; classes a priori égales, lissage de Laplace.
    Un trait jamais vu à l'entraînement est ignoré : il ne dit rien, mais le lissage le ferait pencher
    vers la classe qui a le moins de traits."""
    vocabulaire = len(set(comptes[1]) | set(comptes[0]))
    totaux = {c: sum(comptes[c].values()) + vocabulaire for c in (0, 1)}
    probas = []
    for occurrence in occurrences_mot:
        connus = [t for t in occurrence if comptes[0][t] or comptes[1][t]]
        score = {c: sum(math.log((comptes[c][t] + 1) / totaux[c]) for t in connus) for c in (0, 1)}
        probas.append(1 / (1 + math.exp(score[0] - score[1])))
    return sum(probas) / len(probas) if probas else 0


def classer(pages, candidats, personnes, non_personnes, seuil):
    """Renvoie les personnes retenues, {candidat: p} et les mots ajoutés aux exemples au second tour."""
    traits = occurrences(pages, candidats)
    comptes = entrainer(traits, personnes, non_personnes)
    p = {c: probabilite(traits[c], comptes) for c in candidats}
    ajoutes = {c for c in candidats if p[c] > P_BOOTSTRAP} - personnes - non_personnes
    comptes = entrainer(traits, personnes | ajoutes, non_personnes)
    p = {c: probabilite(traits[c], comptes) for c in candidats}
    return {c for c in candidats if p[c] >= seuil}, p, ajoutes
