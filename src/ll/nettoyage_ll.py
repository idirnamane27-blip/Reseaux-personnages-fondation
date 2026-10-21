"""Nettoyage des candidats de LL : les titres et les gentilés ne sont pas des lieux.
Pourquoi : un titre calculé par LP2 (« Commodore », « Plan ») précède des noms sans en être un ; un gentilé
(« Kalganiens ») désigne les habitants d'un lieu, pas le lieu. Ces deux règles ne retirent aucun vrai lieu.
Exemple : « Seigneur » (titre) et « Korelliens » (radical « Korell », début du candidat « Korell ») sont retirés."""
import re

from src.liste_l import decouper_mots
from src.lp2.dictionnaire import charger_noms_communs
from src.lp2.majuscule import majuscules
from src.lp2.pipeline import K, construire_L, lire_textes
from src.lp2.titres import est_titre, titres
from src.nettoyage import DOSSIER_PROPRE

GENTILE = re.compile(r"^(.{4,}?)(iens|ienne|iennes|ien|aises|aise|ais|oises|oise|ois)$")


def titres_LP2():
    """Titres calculés par LP2 (règle A), avec son code et ses réglages, sur le corpus."""
    pages = [decouper_mots(t) for v in lire_textes(sorted(DOSSIER_PROPRE.glob("*.txt"))).values() for t in v]
    nb_tokens = sum(1 for mots in pages for m in mots if m[0].isalnum())
    noms_propres, fiches = majuscules(construire_L(pages), pages, nb_tokens, K)
    return titres(pages, set(noms_propres), charger_noms_communs())


def est_gentile(c, candidats):
    """Un mot en -ien(s), -ienne(s), -ais(e)(s), -ois(e)(s) dont le radical (4 lettres ou plus) commence
    un autre candidat qui n'est pas lui-même un gentilé."""
    trouve = GENTILE.match(c) if " " not in c else None
    return bool(trouve) and any(a != c and a.startswith(trouve.group(1)) and not GENTILE.match(a) for a in candidats)


def nettoyer(candidats):
    """Renvoie les candidats gardés et {candidat retiré: « titre » ou « gentilé »}."""
    titres_appris = titres_LP2()
    retires = {}
    for c in candidats:
        if " " not in c and est_titre(c, titres_appris):
            retires[c] = "titre"
        elif est_gentile(c, candidats):
            retires[c] = "gentilé"
    return [c for c in candidats if c not in retires], retires
