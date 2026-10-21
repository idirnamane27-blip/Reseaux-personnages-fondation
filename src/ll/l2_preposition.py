"""Indice 1 : un lieu suit souvent une préposition de lieu.
Pourquoi : on va « sur Terminus », « vers Kalgan », on vit « dans l'Empire ».
Exemple : Terminus suit sur/vers/dans/depuis dans plus de 10 % de ses occurrences -> indice vrai."""
from src.ressources import charger_liste

SEUIL_LIEU = 0.1         # part d'occurrences après sur/vers/dans/depuis à partir de laquelle on a un lieu
PREPOSITIONS_LIEU = charger_liste("prepositions_lieu.txt")


def part_de_prepositions(c, analyse):
    """Part des occurrences du candidat qui suivent une préposition de lieu (articles sautés)."""
    fiche = analyse["candidats"][c]
    return sum(fiche["precedents"][p] for p in PREPOSITIONS_LIEU) / fiche["frequence"]


def est_un_lieu(c, analyse):
    return part_de_prepositions(c, analyse) >= SEUIL_LIEU


def indice_preposition(candidats, analyse):
    """Ensemble des candidats qui suivent assez souvent une préposition de lieu."""
    return {c for c in candidats if est_un_lieu(c, analyse)}
