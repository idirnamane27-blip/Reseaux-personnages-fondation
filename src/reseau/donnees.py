"""Principe : un chapitre du corpus leaderboard = un texte d'une seule ligne, avec son ID Kaggle.
Pourquoi : les fichiers sont coupés à la largeur de page ; une phrase coupée gênerait la REN.
Exemple : prelude_a_fondation/chapter_1.txt.preprocessed -> ("paf0", "Mathématicien CLÉON Ier— ...").
La trilogie (texte_propre/, une page impaire sur deux) est coupée en blocs de 5 pages : ("fon0", pages 1 à 5)."""
import re

from src.extraction import RACINE

DOSSIER_LEADERBOARD = RACINE / "corpus_asimov_leaderboard"
LIVRES = [("prelude_a_fondation", "paf"), ("les_cavernes_d_acier", "lca")]
TRILOGIE = [("Fondation_impaires.txt", "fon"), ("Fondation_et_empire_impaires.txt", "fee"),
            ("Seconde_Fondation_impaires.txt", "sdf")]
PAGES_PAR_BLOC = 5


def normaliser(texte):
    """Recolle les traits d'union de fin de ligne (« eux-\\nmêmes ») puis met tout sur une ligne.
    La signature des citations de Prélude (« ENCYCLOPAEDIA GALACTICA2 ») devient une fin de phrase :
    sinon spaCy la colle au nom qui suit (« GALACTICA Seldon »)."""
    texte = re.sub(r"ENCYCLOP\w* GALACTICA\d*", ".", texte)
    texte = re.sub(r"-\n\s*", "-", texte)
    return re.sub(r"\s+", " ", texte).strip()


def chapitres_leaderboard():
    """Liste des (ID, texte) dans l'ordre : paf0..paf18 puis lca0..lca17.
    Les fichiers sont numérotés à partir de 1, les ID Kaggle à partir de 0."""
    resultat = []
    for dossier, code in LIVRES:
        fichiers = (DOSSIER_LEADERBOARD / dossier).glob("chapter_*.txt.preprocessed")
        for fichier in sorted(fichiers, key=lambda f: int(f.name.split("_")[1].split(".")[0])):
            numero = int(fichier.name.split("_")[1].split(".")[0])
            resultat.append((f"{code}{numero - 1}", normaliser(fichier.read_text(encoding="utf-8"))))
    return resultat


def chapitres_trilogie():
    """Liste des (ID, texte) des blocs de 5 pages de la trilogie : fon0, fon1, ..., fee0, ..., sdf0, ..."""
    from src.nettoyage import DOSSIER_PROPRE, lire_pages
    resultat = []
    for fichier, code in TRILOGIE:
        pages = lire_pages(DOSSIER_PROPRE / fichier)
        for k in range(0, len(pages), PAGES_PAR_BLOC):
            resultat.append((f"{code}{k // PAGES_PAR_BLOC}", normaliser(" ".join(pages[k:k + PAGES_PAR_BLOC]))))
    return resultat
