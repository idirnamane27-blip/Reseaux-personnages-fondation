"""Principe : un nom validé une fois dans un livre est recherché partout dans ce livre.
Pourquoi : spaCy rate des occurrences d'un nom qu'il a reconnu ailleurs ; chaque occurrence ratée
peut faire perdre un personnage (rappel des nœuds) ou un lien (rappel des arêtes).
Exemple : « Hummin » reconnu au chapitre 5 -> retrouvé aussi dans les phrases du chapitre 7 où spaCy l'a raté."""
from collections import Counter

import spacy
from spacy.matcher import PhraseMatcher

from src.reseau.ner import MODELE, Mention, nettoyer
from src.ressources import charger_liste


def lexique_par_livre(mentions_gardees):
    """{code livre: Counter(nom)} à partir des mentions qui ont passé le filtre ; le code est « paf » dans « paf12 »."""
    lexiques = {}
    for identifiant, mentions in mentions_gardees.items():
        livre = identifiant.rstrip("0123456789")
        lexiques.setdefault(livre, Counter()).update(m.texte for m in mentions)
    return lexiques


class Rappel:
    def __init__(self):
        # seul le tokenizer sert : les positions doivent être les mêmes que celles des entités spaCy
        self.nlp = spacy.load(MODELE, exclude=["tok2vec", "morphologizer", "parser", "attribute_ruler",
                                               "lemmatizer", "ner"])
        self.nlp.max_length = 2_000_000
        self.titres = charger_liste("titres.txt")

    def completer(self, texte, mentions, lexique):
        """Mentions de spaCy + toutes les occurrences des noms du lexique ; en cas de chevauchement,
        la plus longue gagne (« Hari Seldon » plutôt que « Seldon »), puis celle de spaCy."""
        doc = self.nlp(texte)
        matcher = PhraseMatcher(self.nlp.vocab)
        # les titres seuls ne sont pas recherchés : « Empereur » désigne qui on veut selon le chapitre
        noms = [n for n in lexique if any(m.lower() not in self.titres for m in n.split())]
        matcher.add("NOM", list(self.nlp.tokenizer.pipe(noms)))
        trouvees = []
        for _, debut, fin in matcher(doc):
            if debut >= 1 and doc[debut - 1].text.lower() in self.titres and doc[debut - 1].text[0].isupper():
                debut -= 1  # « Docteur Seldon » en début de phrase ; en minuscule, le titre est déjà dans le lexique
            trouvees.append(Mention(nettoyer(doc[debut:fin].text), debut, fin, doc[debut - 1].text if debut else ""))

        candidates = sorted(mentions + trouvees, key=lambda m: (-(m.fin - m.debut), m not in mentions))
        occupe, resultat = set(), []
        for m in candidates:
            positions = set(range(m.debut, m.fin))
            if not positions & occupe:
                occupe |= positions
                resultat.append(m)
        return sorted(resultat, key=lambda m: m.debut)
