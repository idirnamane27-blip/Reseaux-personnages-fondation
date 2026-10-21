"""Étape 1 : un nom propre garde sa majuscule au milieu des phrases.
Pourquoi : en tête de phrase tout mot prend une majuscule ; ailleurs, seul un nom propre la garde (presque) toujours.
Exemple : « Seldon » n'est jamais écrit « seldon » (taux 1,0, gardé) ; « Mais » s'écrit « mais » en milieu de phrase (retiré)."""
from collections import Counter

TAUX_MIN = 0.9   # 10 % de minuscules : une faute d'OCR ou un emploi rare, pas un mot courant


def debut_de_phrase(mots, i):
    """Vrai si la position i ouvre la page, une phrase ou une réplique (après un signe autre que la virgule)."""
    return i == 0 or (not mots[i - 1][0].isalnum() and mots[i - 1] != ",")


def compter_hors_debut(pages):
    """Counter des mots tels qu'ils sont écrits, hors début de phrase."""
    compte = Counter()
    for mots in pages:
        compte.update(mot for i, mot in enumerate(mots) if not debut_de_phrase(mots, i))
    return compte


def seuil_frequence(nb_tokens, k):
    """k apparitions pour 100 000 tokens."""
    return k * nb_tokens / 100000


def majuscules(L, pages, nb_tokens, k):
    """Renvoie les mots retenus et {mot: (taux_maj, fréquence, motif de rejet ou "")} pour le journal."""
    hors_debut = compter_hors_debut(pages)
    seuil = seuil_frequence(nb_tokens, k)
    fiches = {}
    for forme, n, frequence in L:
        if n != 1:
            continue
        total = hors_debut[forme] + hors_debut[forme.lower()]
        taux = hors_debut[forme] / total if total else 0
        if forme == forme.upper():
            motif = "sans minuscule"   # lettre seule, sigle, chiffre romain : « O », « II », « PDQ »
        elif not total:
            motif = "jamais en milieu de phrase"
        elif taux < TAUX_MIN:
            motif = "minuscule"
        elif frequence < seuil:
            motif = "rare"
        else:
            motif = ""
        fiches[forme] = (taux, frequence, motif)
    return [m for m, (t, f, motif) in fiches.items() if not motif], fiches
