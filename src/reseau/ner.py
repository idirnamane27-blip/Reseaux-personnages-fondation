"""Principe : les apparitions de personnages sont les entités PER de spaCy, étendues au titre qui les précède.
Pourquoi : la référence annote « Dr Sarton » en entier, spaCy ne voit souvent que « Sarton ».
Exemple : « parla au docteur Seldon » -> Mention("docteur Seldon", debut=3, fin=5)."""
import hashlib
import json
from collections import Counter
from dataclasses import dataclass, asdict

import spacy

from src.extraction import RACINE
from src.ressources import charger_liste

MODELE = "fr_core_news_md"
VERSION_CACHE = "2"  # à changer quand le contenu des mentions change (v2 : champ precedent)
DOSSIER_CACHE = RACINE / "resultats" / "reseau" / "cache"  # un sous-dossier par corpus (leaderboard, trilogie)
PONCTUATION = " «»\"'’—–-,.;:!?()[]…"


@dataclass
class Mention:
    texte: str
    debut: int  # index du premier token
    fin: int    # index après le dernier token
    precedent: str = ""  # token juste avant : début de phrase ? article (« le Mulet ») ?


def nettoyer(texte):
    """Retire la ponctuation collée aux bords ; garde le point des titres abrégés (« R. Daneel »)."""
    return texte.strip(PONCTUATION.replace(".", "")).rstrip(PONCTUATION).strip()


def mentions_du_doc(doc, titres):
    mentions = []
    for ent in doc.ents:
        if ent.label_ != "PER":
            continue
        debut = ent.start
        # titre juste avant, éventuellement abrégé avec un point séparé : « R . Daneel »
        if debut >= 2 and doc[debut - 1].text == "." and (doc[debut - 2].text.lower() + ".") in titres:
            debut -= 2
        elif debut >= 1 and doc[debut - 1].text.lower() in titres:
            debut -= 1
        texte = nettoyer(doc[debut:ent.end].text)
        # un nom commence par une majuscule ou par un titre (« docteur Seldon »)
        if len(texte) < 2 or not (texte[0].isupper() or debut < ent.start):
            continue
        mentions.append(Mention(texte, debut, ent.end, doc[debut - 1].text if debut else ""))
    return mentions


def compter_etiquettes(doc, etiquettes):
    """Pour chaque texte d'entité, combien de fois spaCy l'a vu PER, LOC, ORG, MISC (sert au filtre des lieux)."""
    for ent in doc.ents:
        etiquettes.setdefault(nettoyer(ent.text), Counter())[ent.label_] += 1


def lire_etiquettes(dossier):
    donnees = json.loads((dossier / "etiquettes.json").read_text(encoding="utf-8"))
    return {texte: Counter(c) for texte, c in donnees.items()}


def empreinte(chapitres):
    contenu = VERSION_CACHE + MODELE + "".join(i + t for i, t in chapitres) + (RACINE / "ressources" / "titres.txt").read_text()
    return hashlib.md5(contenu.encode("utf-8")).hexdigest()


def extraire_mentions(chapitres, nom_corpus="leaderboard", cache=True):
    """({ID: [Mention, ...]}, {texte: Counter(étiquettes)}) ; gardés dans resultats/reseau/cache/<corpus>/,
    et recalculés dès que les textes, le modèle ou la liste des titres changent (empreinte.txt)."""
    dossier = DOSSIER_CACHE / nom_corpus
    fichiers = [dossier / n for n in ("mentions.json", "etiquettes.json", "empreinte.txt")]
    if cache and all(f.exists() for f in fichiers) and fichiers[2].read_text() == empreinte(chapitres):
        donnees = json.loads(fichiers[0].read_text(encoding="utf-8"))
        return {i: [Mention(**m) for m in ms] for i, ms in donnees.items()}, lire_etiquettes(dossier)
    titres = charger_liste("titres.txt")
    nlp = spacy.load(MODELE, exclude=["parser", "lemmatizer", "morphologizer", "attribute_ruler"])
    nlp.max_length = 2_000_000
    resultat, etiquettes = {}, {}
    for (identifiant, _), doc in zip(chapitres, nlp.pipe(t for _, t in chapitres)):
        resultat[identifiant] = mentions_du_doc(doc, titres)
        compter_etiquettes(doc, etiquettes)
        print(f"{identifiant}: {len(resultat[identifiant])} mentions")
    dossier.mkdir(parents=True, exist_ok=True)
    fichiers[0].write_text(json.dumps({i: [asdict(m) for m in ms] for i, ms in resultat.items()},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
    fichiers[1].write_text(json.dumps(etiquettes, ensure_ascii=False, indent=1), encoding="utf-8")
    fichiers[2].write_text(empreinte(chapitres))
    return resultat, etiquettes
