"""Principe : toutes les connaissances sur la langue sont dans des fichiers, pas dans le code.
Pourquoi : on peut lire, corriger ou remplacer une liste sans toucher au programme.
Exemple : charger_liste("articles.txt") -> {"le", "la", "les", "l"}."""
from src.extraction import RACINE

DOSSIER_RESSOURCES = RACINE / "ressources"


def lire_lignes(nom_fichier):
    """Lignes utiles en minuscules : les lignes vides et les commentaires # sont ignorés."""
    lignes = (DOSSIER_RESSOURCES / nom_fichier).read_text(encoding="utf-8").splitlines()
    return [l.strip().lower() for l in lignes if l.strip() and not l.startswith("#")]


def charger_liste(nom_fichier):
    """Renvoie l'ensemble des mots d'un fichier à un mot par ligne."""
    return set(lire_lignes(nom_fichier))
