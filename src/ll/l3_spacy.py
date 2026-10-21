"""Indice 2 : spaCy donne son avis sur chaque candidat (personne, lieu, organisation, divers).
Pourquoi : son modèle a appris ailleurs ce que nos indices ne voient pas ; il juge seulement nos candidats, sans en ajouter.
Exemple : « Trantor » étiqueté 40 fois LOC et 2 fois PER -> indice vrai ; « Fondation » compte aussi, via MISC."""
import time
from collections import Counter

import spacy

from src.liste_l import DOSSIER_RESULTATS
from src.nettoyage import DOSSIER_PROPRE, lire_pages

MODELE = "fr_core_news_md"
ETIQUETTES = ["PER", "LOC", "ORG", "MISC"]
# Comptes de spaCy gardés d'une exécution à l'autre (candidats de LL)
FICHIER_ETIQUETTES = DOSSIER_RESULTATS / "spacy_etiquettes.txt"


def normaliser(texte):
    """« d’Anacréon » -> « d'Anacréon » : L et spaCy doivent écrire l'apostrophe de la même façon."""
    return texte.replace("’", "'")


def compter_etiquettes(candidats):
    """Lance spaCy une fois sur tout le corpus, page par page ; renvoie {candidat: Counter des étiquettes}."""
    nlp = spacy.load(MODELE, enable=["ner"])   # le NER a son propre tok2vec : le reste est inutile
    par_ecriture = {normaliser(c): c for c in candidats}
    comptes = {c: Counter() for c in candidats}
    pages = [page for chemin in sorted(DOSSIER_PROPRE.glob("*.txt")) for page in lire_pages(chemin)]
    for doc in nlp.pipe(pages):
        for entite in doc.ents:
            candidat = par_ecriture.get(normaliser(entite.text))
            if candidat:
                comptes[candidat][entite.label_] += 1
    return comptes


def ecrire_etiquettes(comptes):
    with open(FICHIER_ETIQUETTES, "w", encoding="utf-8") as f:
        for c, compte in comptes.items():
            f.write(c + "".join(f"\t{compte[e]}" for e in ETIQUETTES) + "\n")


def lire_etiquettes(candidats):
    """Relit spacy_etiquettes.txt ; un candidat absent du fichier n'a aucune étiquette."""
    comptes = {c: Counter() for c in candidats}
    for ligne in FICHIER_ETIQUETTES.read_text(encoding="utf-8").splitlines():
        c, *nombres = ligne.split("\t")
        if c in comptes:
            comptes[c] = Counter(dict(zip(ETIQUETTES, map(int, nombres))))
    return comptes


def etiquettes_spacy(candidats):
    """Comptes d'étiquettes : relus s'ils couvrent tous les candidats, sinon calculés par spaCy puis enregistrés."""
    if FICHIER_ETIQUETTES.exists():
        connus = {l.split("\t")[0] for l in FICHIER_ETIQUETTES.read_text(encoding="utf-8").splitlines()}
        if connus >= set(candidats):
            return lire_etiquettes(candidats)
    debut = time.perf_counter()
    comptes = compter_etiquettes(candidats)
    print(f"spaCy : {time.perf_counter() - debut:.1f} s")
    ecrire_etiquettes(comptes)
    return comptes


def indice_spacy(candidats):
    """Candidats que spaCy voit plus souvent comme lieu, organisation ou divers que comme personne."""
    comptes = etiquettes_spacy(candidats)
    return {c for c in candidats
            if comptes[c]["LOC"] + comptes[c]["ORG"] + comptes[c]["MISC"] > comptes[c]["PER"]}
