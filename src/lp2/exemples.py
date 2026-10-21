"""Étape 2 : exemples sûrs, trouvés seuls dans le texte.
Pourquoi : le classifieur de l'étape 3 apprend sur des mots dont on est sûr ; le texte en donne de deux sortes :
ceux qui parlent (personnes) et ceux qu'on situe, qu'on détermine ou que spaCy voit comme lieux (non-personnes).
Exemple : « , dit Seldon », « , murmura la Dame » -> personnes ; « à Bombay » -> non-personne ; « l'Empire » -> non-personne ;
un mot qui parle au moins une fois en incise n'est jamais une non-personne par la seule règle de l'article."""
import re
from collections import Counter

MIN_INCISES = 3   # un verbe vu moins de 3 fois en incise peut être un hasard
AVANT_INCISE = {",", "!", "?", "…", "."}
# « dit-il », « dit-elle », « demanda-t-il » ; une incise s'écrit en minuscule (« Est-il » ouvre une question)
INCISE = re.compile(r"^([a-zà-ÿ]\w*?)(?:-t)?-(?:il|elle)$")
MIN_LOCUTEUR = 2       # deux incises : une seule pourrait être une erreur de découpage
PART_PREPOSITION = 0.2  # un lieu suit sur/vers/dans/à/en au moins une fois sur cinq
PART_ARTICLE = 0.5      # un nom commun à majuscule (« la Galaxie ») a le plus souvent un article
PART_LOC = 0.7          # spaCy voit le mot dans un lieu au moins 7 fois sur 10
PREPOSITIONS = {"sur", "vers", "dans", "à", "en"}
ARTICLES = {"le", "la", "les", "l'", "l’", "un", "une", "des"}


def verbes_de_parole(pages):
    """Verbes V tels que « V-il », « V-elle », « V-t-il » ou « V-t-elle » suivent au moins 3 fois , ! ? … ou ."""
    incises = Counter()
    for mots in pages:
        for i in range(1, len(mots)):
            trouve = INCISE.match(mots[i])
            if trouve and mots[i - 1] in AVANT_INCISE:
                incises[trouve.group(1)] += 1
    return {verbe for verbe, n in incises.items() if n >= MIN_INCISES}


def mot_avant(mots, i, sauter_articles):
    """Mot avant la position i ; « sur la Terre » : en sautant les articles, c'est « sur »."""
    j = i - 1
    while sauter_articles and j >= 0 and mots[j].lower() in ARTICLES:
        j -= 1
    return mots[j].lower() if j >= 0 else ""


def exemples(pages, candidats, etiquettes, verbes, titres_appris):
    """Renvoie (personnes, non_personnes, comptes) ; etiquettes = Counter (mot, étiquette spaCy).
    Un titre (« dit le Maire ») n'est jamais un locuteur sûr : il annonce une personne, il n'en est pas une."""
    candidats = set(candidats)
    locuteur, preposition, article, frequence = Counter(), Counter(), Counter(), Counter()
    for mots in pages:
        for i, mot in enumerate(mots):
            if mot not in candidats:
                continue
            frequence[mot] += 1
            # « , dit Seldon » ou « , dit le Mulet » : un verbe de parole en incise, un article possible, le locuteur
            j = i - 2 if i >= 1 and mots[i - 1].lower() in ARTICLES else i - 1
            locuteur[mot] += (j >= 1 and mots[j] in verbes and mots[j - 1] in AVANT_INCISE
                              and mot.lower() not in titres_appris)
            preposition[mot] += mot_avant(mots, i, True) in PREPOSITIONS
            article[mot] += mot_avant(mots, i, False) in ARTICLES
    part = lambda compte, c: compte[c] / frequence[c] if frequence[c] else 0
    par_preposition = {c for c in candidats if part(preposition, c) >= PART_PREPOSITION}
    par_article = {c for c in candidats if part(article, c) >= PART_ARTICLE and not locuteur[c]}
    par_spacy = {c for c in candidats if frequence[c] and etiquettes[c, "LOC"] / frequence[c] >= PART_LOC}
    personnes = {c for c in candidats if locuteur[c] >= MIN_LOCUTEUR}
    non_personnes = par_preposition | par_article | par_spacy
    les_deux = personnes & non_personnes
    comptes = {"locuteur": locuteur, "preposition": par_preposition, "article": par_article, "spacy": par_spacy,
               "article mais locuteur": {c for c in candidats if part(article, c) >= PART_ARTICLE and locuteur[c]},
               "les deux": les_deux}
    return personnes - les_deux, non_personnes - les_deux, comptes
