"""Étape 5 : une ligne par personnage.
Pourquoi : un personnage est appelé par son nom complet ou par un seul de ses noms ; il ne doit compter qu'une fois.
Exemple : « Bayta » n'est contenu que dans « Bayta Darell » -> rattaché ; « Darell » est dans « Bayta Darell » et
« Toran Darell » -> ambigu, pas de ligne ; deux noms complets ne fusionnent jamais.
Règle B : une ligne d'un seul mot qui est un nom commun du dictionnaire (« Papa », « Excellence ») est supprimée,
sauf si le mot a une preuve de personne (« , dit le Mulet »)."""
from src.lp2.titres import est_titre, sans_titre


def regrouper(L, personnes, titres_appris, est_nom_commun, locuteur):
    """Renvoie [(personnage, fréquence totale, formes)] et ce que l'étape a fait (pour le journal)."""
    frequences = {forme: f for forme, n, f in L}
    noms = {p for p in personnes if not est_titre(p, titres_appris)}   # un titre seul n'est jamais une ligne
    groupes = {}   # nom sans titre -> formes de L qui l'écrivent (« Seldon » -> Seldon, Docteur Seldon)
    for forme, n, f in L:
        reste = sans_titre(forme, titres_appris)
        if reste in frequences and all(mot in noms for mot in reste.split()):
            groupes.setdefault(reste, []).append(forme)
    complets = [nom for nom in groupes if " " in nom]
    personnages = {c: list(groupes[c]) for c in complets}
    rattaches, ambigus = {}, {}
    for nom in sorted(nom for nom in groupes if " " not in nom):
        contenants = [c for c in complets if nom in c.split()]
        if len(contenants) == 1:
            personnages[contenants[0]] += groupes[nom]
            rattaches[nom] = contenants[0]
        elif contenants:
            ambigus[nom] = contenants
        else:
            personnages[nom] = groupes[nom]
    regle_b = {nom: locuteur[nom] for nom in personnages if " " not in nom and est_nom_commun(nom)}
    lignes = []
    for nom, formes in personnages.items():
        if nom in regle_b and not regle_b[nom]:
            continue
        formes = sorted(set(formes), key=lambda x: (x != nom, -frequences[x], x))
        lignes.append((nom, sum(frequences[x] for x in formes), formes))
    lignes.sort(key=lambda l: (-l[1], l[0]))
    titres_retires = {forme: nom for nom, formes in groupes.items() for forme in formes if forme != nom}
    return lignes, {"complets": complets, "rattachés": rattaches, "ambigus": ambigus,
                    "titres retirés": titres_retires, "règle B": regle_b}
