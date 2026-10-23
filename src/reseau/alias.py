"""Principe : deux noms désignent le même personnage si, sans leurs titres, l'un est contenu dans l'autre.
Pourquoi : « Seldon », « Hari Seldon » et « docteur Seldon » partagent le cœur « Seldon ».
Exemple : {Hari, Hari Seldon, docteur Seldon, Dors} -> {Hari, Hari Seldon, docteur Seldon}, {Dors}.
Les groupes sont faits sur le livre entier puis restreints à chaque chapitre : « Lije » rejoint Baley
même dans un chapitre où « Lije Baley » n'apparaît pas en entier."""
from collections import Counter

from src.ressources import charger_liste


def coeur(nom, titres):
    """Mots du nom sans les titres, en minuscules : « Dr Han Fastolfe » -> ("han", "fastolfe") ; () pour un titre seul."""
    return tuple(m.lower() for m in nom.split() if m.lower() not in titres)


def prenoms_proches(a, b):
    """« Lije » et « Elijah » : les 3 premières lettres de l'un sont au début de l'autre, ou juste après sa
    première lettre. Seulement utilisé quand le nom de famille est le même (règle A)."""
    court, long_ = sorted((a, b), key=len)
    return len(court) >= 3 and court != long_ and long_.find(court[:3]) in (0, 1)


def est_abreviation(court, long_):
    """« Ben » pour « Bentley » : mêmes deux premières lettres, et toutes les lettres du court dans l'ordre (règle B) ;
    « Mis » n'abrège pas « Meirus »."""
    if len(court) < 3 or len(court) >= len(long_) or court[:2] != long_[:2]:
        return False
    reste = iter(long_)
    return all(lettre in reste for lettre in court)


def resoudre_alias(mentions):
    """Liste de groupes de noms (ensembles), du personnage le plus cité au moins cité.
    Un nom d'un seul mot rejoint le nom long le plus cité qui le contient.
    Un titre seul (« Empereur ») rejoint le seul groupe où ce titre précède un nom, sinon il est retiré."""
    titres = charger_liste("titres.txt")
    noms_communs = charger_liste("noms_communs.txt")
    freq = Counter(m.texte for m in mentions)
    coeurs = {nom: coeur(nom, titres) for nom in freq}
    freq_coeur = Counter()
    for nom, n in freq.items():
        if coeurs[nom]:
            freq_coeur[coeurs[nom]] += n

    # 1. les cœurs longs : on fusionne ceux qui sont contenus dans un plus long (« Hari Seldon » ⊂ « Hari Seldon Junior »)
    longs = sorted({c for c in freq_coeur if len(c) > 1}, key=lambda c: (-len(c), -freq_coeur[c], c))
    representant = {}
    for c in longs:
        parent = next((r for r in representant.values() if set(c) <= set(r)), None)
        representant[c] = parent or c
    poids = Counter()
    for c, r in representant.items():
        poids[r] += freq_coeur[c]

    # 1b. règle A : même nom de famille et prénoms proches (« Lije Baley » -> « Elijah Baley ») ;
    # « Jessie Baley » et « Bentley Baley » restent séparés
    for r in sorted(poids, key=lambda r: (poids[r], r)):
        cible = max((x for x in poids if x != r and len(x) == len(r) == 2 and x[-1] == r[-1]
                     and prenoms_proches(x[0], r[0]) and poids[x] >= poids[r]),
                    key=lambda x: (poids[x], x), default=None)
        if cible:
            for c in representant:
                if representant[c] == r:
                    representant[c] = cible
            poids[cible] += poids.pop(r)

    # 2. les cœurs d'un mot : rattachés au nom long le plus cité qui contient ce mot
    for c in freq_coeur:
        if len(c) == 1:
            # on passe par tous les noms longs, même absorbés (« Lije » ⊂ « Lije Baley » -> « Elijah Baley »)
            candidats = {representant[x] for x in longs if c[0] in x}
            # à égalité (« Randa » : Kiangtow Randa ou Lisung Randa ?), ordre alphabétique pour être reproductible
            representant[c] = max(candidats, key=lambda r: (poids[r], r)) if candidats else c

    # 2b. règle B : un mot seul sans nom long est l'abréviation d'un autre nom (« Ben » -> « Bentley »)
    for c in sorted(freq_coeur, key=lambda c: (freq_coeur[c], c)):
        if len(c) == 1 and representant[c] == c:
            # la cible est un nom propre, pas un mot du dictionnaire : « Mis » n'abrège pas « Ministre »
            cibles = {representant[x] for x in freq_coeur if x != c and representant[x] != c
                      and any(est_abreviation(c[0], mot) and mot not in noms_communs for mot in x)}
            if cibles:
                representant[c] = max(cibles, key=lambda r: (freq_coeur[r] + poids[r], r))

    groupes = {}
    for nom in freq:
        if coeurs[nom]:
            groupes.setdefault(representant[coeurs[nom]], set()).add(nom)

    # 3. les titres seuls
    for nom in freq:
        if not coeurs[nom]:
            titre = nom.lower()
            porteurs = [r for r, noms in groupes.items() if any(n.lower().startswith(titre + " ") for n in noms)]
            if len(porteurs) == 1:
                groupes[porteurs[0]].add(nom)

    total = {r: sum(freq[n] for n in noms) for r, noms in groupes.items()}
    return [groupes[r] for r in sorted(groupes, key=lambda r: (-total[r], r))]


def groupes_du_chapitre(mentions, groupes_livre):
    """Groupes du livre restreints aux noms présents dans le chapitre.
    Les noms écartés au niveau du livre (titres seuls sans porteur, comme « Sire ») n'ont pas de nœud."""
    presents = {m.texte for m in mentions}
    return [g & presents for g in groupes_livre if g & presents]
