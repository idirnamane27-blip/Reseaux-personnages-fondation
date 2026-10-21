"""Étape 2 bis (règle A) : un titre est un nom commun du dictionnaire placé devant un nom propre.
Pourquoi : « Docteur Seldon », « capitaine Pritcher », « Mr. Fogg » : le titre n'est pas le nom ; on le retire
avant le regroupement pour que « Docteur Seldon » rejoigne « Seldon ». Aucune liste de titres n'est écrite :
le dictionnaire dit si le mot est un nom commun, le texte dit s'il précède des noms propres.
Exemple : « docteur » (nom commun) devant Seldon, Darell, Kleise -> titre ; « Mr » (absent du dictionnaire,
toujours suivi d'un point) devant Fogg, Fix -> abréviation-titre."""
from collections import Counter, defaultdict

MIN_DEVANT_NOM = 3   # trois occurrences devant un nom propre : pas un hasard de construction
PART_POINT = 0.9     # une abréviation (« Mr ») est presque toujours suivie d'un point


def titres(pages, noms_propres, est_nom_commun):
    """{titre en minuscule: (sorte, occurrences devant un nom propre, noms propres suivis)}."""
    total, point, devant = Counter(), Counter(), Counter()
    suivis = defaultdict(set)
    for mots in pages:
        for i, mot in enumerate(mots):
            if not mot[0].isalpha():
                continue
            cle = mot.lower()
            total[cle] += 1
            suivant = mots[i + 1] if i + 1 < len(mots) else ""
            point[cle] += suivant == "."
            # le point n'est sauté que pour une abréviation, ce qu'on ne sait qu'à la fin : on note les deux cas
            apres_point = mots[i + 2] if suivant == "." and i + 2 < len(mots) else ""
            for nom, cas in ((suivant, "direct"), (apres_point, "point")):
                if nom in noms_propres:
                    devant[cle, cas] += 1
                    suivis[cle, cas].add(nom)
    resultat = {}
    for cle in total:
        if est_nom_commun(cle) and devant[cle, "direct"] >= MIN_DEVANT_NOM:
            resultat[cle] = ("nom commun", devant[cle, "direct"], sorted(suivis[cle, "direct"]))
        elif (not est_nom_commun(cle) and point[cle] >= PART_POINT * total[cle]
              and devant[cle, "point"] >= MIN_DEVANT_NOM):
            resultat[cle] = ("abréviation", devant[cle, "point"], sorted(suivis[cle, "point"]))
    return resultat


def est_titre(mot, titres_appris):
    return mot.lower() in titres_appris


def sans_titre(forme, titres_appris):
    """« Docteur Han Pritcher » -> « Han Pritcher » : retire les titres en tête de la forme."""
    mots = forme.split()
    while len(mots) > 1 and est_titre(mots[0], titres_appris):
        mots = mots[1:]
    return " ".join(mots)
