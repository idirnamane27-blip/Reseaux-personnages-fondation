"""Étape 2 (aide) : spaCy dit quels mots il voit dans des lieux.
Pourquoi : son modèle a appris sur d'autres textes qu'une ville ou un pays est un lieu ; on ne lui demande que cela.
Exemple : « Bombay » est dans une entité LOC 55 fois sur 61 -> exemple sûr de non-personne.
Les comptes sont gardés par fichier dans resultats/spacy_lp2/ : spaCy ne lit chaque livre qu'une fois."""
import time
from collections import Counter

from src.liste_l import DOSSIER_RESULTATS, decouper_mots

MODELE = "fr_core_news_md"
DOSSIER_CACHE = DOSSIER_RESULTATS / "spacy_lp2"


def compter_fichier(textes):
    """Counter des (mot, étiquette) : chaque mot de chaque entité trouvée par spaCy."""
    import spacy   # chargé seulement si le cache manque
    nlp = spacy.load(MODELE, enable=["ner"])
    nlp.max_length = max(nlp.max_length, max(len(t) for t in textes) + 1)
    compte = Counter()
    for doc in nlp.pipe(textes):
        for entite in doc.ents:
            compte.update((mot, entite.label_) for mot in decouper_mots(entite.text.replace("’", "'")))
    return compte


def etiquettes(textes_par_fichier):
    """Counter des (mot, étiquette) sur tous les fichiers, relu du cache quand il existe."""
    DOSSIER_CACHE.mkdir(parents=True, exist_ok=True)
    total = Counter()
    for chemin, textes in textes_par_fichier.items():
        cache = DOSSIER_CACHE / chemin.name
        if not cache.exists():
            debut = time.perf_counter()
            compte = compter_fichier(textes)
            cache.write_text("".join(f"{m}\t{e}\t{n}\n" for (m, e), n in compte.items()), encoding="utf-8")
            print(f"spaCy sur {chemin.name} : {time.perf_counter() - debut:.1f} s")
        for ligne in cache.read_text(encoding="utf-8").splitlines():
            mot, etiquette, n = ligne.split("\t")
            total[mot, etiquette] += int(n)
    return total
