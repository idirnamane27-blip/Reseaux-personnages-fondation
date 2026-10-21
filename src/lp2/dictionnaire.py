"""Le dictionnaire de la langue : les noms communs de Lexique 3 (ressources/noms_communs.txt).
Pourquoi : un mot du dictionnaire (« docteur », « mulet ») n'est un nom de personne que si le texte le prouve.
Exemple : « Docteur » est un nom commun ; « Seldon » n'en est pas un ; « Mais » non plus (conjonction d'abord)."""
from src.ressources import charger_liste


def charger_noms_communs():
    """Fonction mot -> vrai si le mot, en minuscule, est un nom commun."""
    noms = charger_liste("noms_communs.txt")
    return lambda mot: mot.lower() in noms
