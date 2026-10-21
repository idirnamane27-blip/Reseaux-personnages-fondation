"""Tâche 1 : construit la liste L des n-grammes de mots commençant par une majuscule,
plus les formes « Maj de Maj », « Maj du Maj » et « Maj d'Maj »."""
import re
from collections import Counter

from src.extraction import RACINE
from src.nettoyage import DOSSIER_PROPRE, lire_pages

DOSSIER_RESULTATS = RACINE / "resultats"
N_MAX = 3

# Dans l'ordre : une élision (l', qu'), un mot avec ses traits d'union, un signe seul.
MOT = re.compile(r"\w+['’](?=\w)|\w+(?:-\w+)*|[^\w\s]")


def decouper_mots(texte):
    """Découpe un texte en mots et en signes de ponctuation."""
    return MOT.findall(texte)


def est_majuscule(mot):
    """Vrai pour un mot qui commence par une majuscule (hors élision comme « L' »)."""
    return mot[0].isupper() and not mot.endswith(("'", "’"))


def candidats(mots):
    """Renvoie les n-grammes (n de 1 à N_MAX) de mots consécutifs à majuscule."""
    resultat = []
    suite = []
    for mot in mots + [""]:  # le mot vide final termine la dernière suite
        if mot and est_majuscule(mot):
            suite.append(mot)
            continue
        for debut in range(len(suite)):
            for n in range(1, N_MAX + 1):
                if debut + n <= len(suite):
                    resultat.append(" ".join(suite[debut:debut + n]))
        suite = []
    return resultat + formes_de(mots)


def formes_de(mots):
    """Renvoie les formes « Maj de Maj », « Maj du Maj » et « Maj d'Maj » (Plan de Seldon)."""
    resultat = []
    for i in range(len(mots) - 2):
        premier, lien, dernier = mots[i:i + 3]
        if not (est_majuscule(premier) and est_majuscule(dernier)):
            continue
        if lien in ("de", "du"):
            resultat.append(f"{premier} {lien} {dernier}")
        elif lien in ("d'", "d’"):
            resultat.append(f"{premier} {lien}{dernier}")
    return resultat


def lire_L(nom="L.txt"):
    """Renvoie la liste des (candidat, n, fréquence) d'un fichier au format de L.txt."""
    resultat = []
    with open(DOSSIER_RESULTATS / nom, encoding="utf-8") as f:
        for ligne in f:
            candidat, n, frequence = ligne.rstrip("\n").split("\t")[:3]
            resultat.append((candidat, int(n), int(frequence)))
    return resultat


def main():
    DOSSIER_RESULTATS.mkdir(exist_ok=True)
    fichiers = sorted(DOSSIER_PROPRE.glob("*.txt"))

    if not fichiers:
        print("Aucun texte trouvé dans", DOSSIER_PROPRE)
        return

    compteur = Counter()
    for chemin in fichiers:
        for texte in lire_pages(chemin):
            compteur.update(candidats(decouper_mots(texte)))

    with open(DOSSIER_RESULTATS / "L.txt", "w", encoding="utf-8") as f:
        for candidat, frequence in compteur.most_common():
            f.write(f"{candidat}\t{candidat.count(' ') + 1}\t{frequence}\n")

    print(f"{len(compteur)} candidats écrits dans {DOSSIER_RESULTATS / 'L.txt'}")


if __name__ == "__main__":
    main()
