"""Principe 1 : la majuscule doit être celle d'un nom (point de départ des candidats de LL).
Pourquoi : en français, une majuscule vient soit d'un nom propre, soit du début d'une phrase ; seule la première nous intéresse.
Exemple : « Mais » (mot outil), « Dit-il » (verbe + pronom), « Tenez » (toujours en tête de phrase) sont retirés ; « Seldon » reste."""
import re

from src.liste_l import DOSSIER_RESULTATS
from src.ressources import charger_liste

CHIFFRE_ROMAIN = re.compile(r"^[IVXLC]+$")


def mot_sans_nom(mot, pronoms):
    """Lettre seule, chiffre romain (chapitres), sigle en capitales ou verbe + pronom (« Dit-il »)."""
    return (len(mot) == 1 or CHIFFRE_ROMAIN.match(mot) or mot.isupper()
            or ("-" in mot and mot.rsplit("-", 1)[1].lower() in pronoms))


def est_bruit(candidat, antidictionnaire, pronoms):
    """Vrai si le candidat n'est fait que de mots outils ou contient un mot qui n'est pas un nom."""
    mots = candidat.split()
    return (all(mot.lower() in antidictionnaire for mot in mots)
            or any(mot_sans_nom(mot, pronoms) for mot in mots))


def ecrire_sans_bruit(candidats, analyse):
    """Écrit L_sans_bruit.txt."""
    fiches = analyse["candidats"]
    with open(DOSSIER_RESULTATS / "L_sans_bruit.txt", "w", encoding="utf-8") as f:
        for c in candidats:
            f.write(f"{c}\t{fiches[c]['n']}\t{fiches[c]['frequence']}\n")


def principe_1_majuscule_de_nom(L, analyse):
    """Retire le bruit, écrit L_sans_bruit.txt, puis retire ce qui n'est jamais en milieu de phrase."""
    antidictionnaire = charger_liste("antidictionnaire.txt")
    pronoms = charger_liste("pronoms.txt")
    sans_bruit = [c for c, n, f in L if not est_bruit(c, antidictionnaire, pronoms)]
    ecrire_sans_bruit(sans_bruit, analyse)
    # Un nom propre garde sa majuscule partout ; un mot vu seulement en tête de phrase n'en est pas un
    return [c for c in sans_bruit if analyse["candidats"][c]["milieu"] > 0]
