"""Départ : les candidats à LL sont les noms propres de L qui ne sont pas des personnes.
Pourquoi : le principe 1 (src/majuscule_de_nom.py) retire les majuscules qui ne sont pas des noms ;
ce que LP a pris est une personne.
Exemple : « Terminus » passe le principe 1 et n'est pas dans LP -> candidat ; « Seldon » est dans LP -> écarté."""
from src.liste_l import DOSSIER_RESULTATS, lire_L
from src.majuscule_de_nom import principe_1_majuscule_de_nom


def ecrire_candidats(candidats, analyse):
    fiches = analyse["candidats"]
    with open(DOSSIER_RESULTATS / "LL_candidats.txt", "w", encoding="utf-8") as f:
        for c in candidats:
            f.write(f"{c}\t{fiches[c]['n']}\t{fiches[c]['frequence']}\n")


def candidats_LL(L, analyse):
    """Candidats qui passent le principe 1, moins toutes les formes de LP (LP_formes.txt) ; écrit LL_candidats.txt."""
    LP = {c for c, n, f in lire_L("LP_formes.txt")}
    candidats = [c for c in principe_1_majuscule_de_nom(L, analyse) if c not in LP]
    ecrire_candidats(candidats, analyse)
    return candidats
