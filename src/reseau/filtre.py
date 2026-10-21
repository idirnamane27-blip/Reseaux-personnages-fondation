"""Principe : on retire les mentions qui ne sont pas des personnages, avec des indices appris sur le corpus.
Pourquoi : spaCy prend pour des personnes des mots en début de réplique (« Vraiment »), des lieux (« Trantor »)
et des gentilés (« Spaciens ») ; chaque nœud en trop fait baisser la précision.
Exemple : « Voyons » est plus souvent en minuscule qu'avec une majuscule en milieu de phrase -> bruit ;
« Trantor » suit souvent « sur » -> lieu ; « fit Mis » -> Mis est une personne sûre, malgré le participe « mis ».
Le vote de spaCy (LOC contre PER) n'est pas utilisé : fr_core_news_md voit « Seldon » LOC 300 fois sur 530."""
import re
from collections import Counter

from src.ressources import charger_liste

# un mot est un lieu si une de ces parts de ses occurrences est atteinte (réglées sur le corpus leaderboard :
# lieux à 0,25-0,50, personnages à 0,05 au plus pour « à », 0,17 au plus pour « de »)
SEUIL_LIEU = 0.1      # après sur/vers/dans/depuis, articles sautés (« sur Trantor »), comme pour LL
SEUIL_A = 0.15        # juste après « à » (« à Billibotton »)
SEUIL_DE = 0.5        # juste après « de » (« secteur de Streeling »)
SEUIL_ARTICLE = 0.5   # juste après le/la/les/au/aux/du/des (« au Sacratorium »)
MIN_OCCURRENCES = 4   # en dessous, les parts ne veulent rien dire
MIN_LOCUTEUR = 2      # locuteur d'au moins 2 incises (« dit le Mulet ») -> personne sûre
SEUIL_SURNOM = 0.3    # part après le/la à partir de laquelle l'article fait partie du nom (« le Mulet »)
ARTICLES_CONTRACTES = {"au", "aux", "du", "des"}
SUFFIXES_GENTILES = ("ien", "iens", "ienne", "iennes", "ite", "ites")
ELISIONS = re.compile(r"^[LlDd][’']")
ROMAIN = re.compile(r"^[IVXLC]+$")
TOKEN = re.compile(r"[\w’'-]+|[^\w\s]")
INCISE = re.compile(r"^(\w+)-(?:t-)?(?:il|elle)$")  # « dit-il », « demanda-t-elle »
AVANT_INCISE = {",", "?", "!", "…", "»", '"'}       # « ..., demanda-t-il » ; pas « Existe-t-il » en début de phrase


def debut_de_phrase(precedent):
    return not precedent or (not precedent[0].isalnum() and precedent != ",")


class Filtre:
    def __init__(self, textes):
        self.titres = charger_liste("titres.txt")
        self.prepositions = charger_liste("prepositions_lieu.txt")
        self.articles = charger_liste("articles.txt")
        self.noms_communs = charger_liste("noms_communs.txt")
        self.minuscules = Counter()
        self.milieu = Counter()       # mot à majuscule précédé d'un mot ou d'une virgule
        self.occurrences = Counter()
        self.apres_preposition = Counter()
        self.precedent = {}           # mot à majuscule -> Counter du token juste avant
        incises = Counter()
        documents = [TOKEN.findall(t) for t in textes]
        for tokens in documents:
            for i, mot in enumerate(tokens):
                m = INCISE.match(mot)
                if m and i > 0 and tokens[i - 1] in AVANT_INCISE:
                    incises[m.group(1).lower()] += 1
                if mot.islower():
                    self.minuscules[mot] += 1
                    continue
                if not mot[0].isupper():
                    continue
                self.occurrences[mot] += 1
                avant = tokens[i - 1] if i > 0 else ""
                self.precedent.setdefault(mot, Counter())[avant.lower()] += 1
                if avant and not debut_de_phrase(avant):
                    self.milieu[mot] += 1
                j = i - 1
                while j >= 0 and tokens[j].lower() in self.articles:
                    j -= 1
                if j >= 0 and tokens[j].lower() in self.prepositions:
                    self.apres_preposition[mot] += 1

        # verbes de parole appris sur les incises, puis leurs sujets : « dit Seldon », « fit le Mulet »
        auxiliaires = charger_liste("auxiliaires.txt")
        self.verbes_parole = {v for v, n in incises.items() if n >= 2 and v not in auxiliaires}
        self.locuteur = Counter()
        for tokens in documents:
            for i, mot in enumerate(tokens):
                if mot[0].isupper():
                    j = i - 1
                    if j >= 0 and tokens[j].lower() in ("le", "la"):
                        j -= 1
                    if j >= 0 and tokens[j].lower() in self.verbes_parole:
                        self.locuteur[mot] += 1

    def part_apres(self, mot, avants):
        n = self.occurrences[mot]
        return sum(self.precedent.get(mot, Counter())[a] for a in avants) / n if n else 0.0

    def plutot_minuscule(self, mot):
        """« Vraiment » : plus souvent en minuscule qu'avec une majuscule en milieu de phrase."""
        return self.minuscules[mot.lower()] > self.milieu[mot]

    def normaliser(self, m):
        """Corrige les bords d'entité mal placés par spaCy :
        « L’Empereur » -> « Empereur » ; « Jéhu galopa » -> « Jéhu » ; « VI Le Maire » -> « Le Maire » ;
        en début de phrase seulement, « Grimace de Seldon » -> « Seldon » (mais « le Premier Orateur » reste)."""
        mots = ELISIONS.sub("", m.texte).split()
        while len(mots) > 1 and mots[-1][0].islower():
            mots.pop()
        while len(mots) > 1 and ROMAIN.match(mots[0]):
            mots.pop(0)
        if debut_de_phrase(m.precedent):
            while len(mots) > 1 and mots[0].lower() not in self.titres and self.plutot_minuscule(mots[0]):
                mots.pop(0)
                while len(mots) > 1 and mots[0][0].islower():
                    mots.pop(0)
        return " ".join(mots)

    def coeur(self, nom):
        return [m for m in nom.split() if m.lower() not in self.titres]

    def est_lieu(self, mot):
        if self.occurrences[mot] < MIN_OCCURRENCES:
            return False
        articles = self.part_apres(mot, self.articles | ARTICLES_CONTRACTES)
        return (self.apres_preposition[mot] / self.occurrences[mot] >= SEUIL_LIEU
                or self.part_apres(mot, {"à"}) >= SEUIL_A or self.part_apres(mot, {"de"}) >= SEUIL_DE
                or articles >= SEUIL_ARTICLE)

    def raison_du_rejet(self, nom):
        """Pourquoi la mention n'est pas un personnage, ou None si elle est gardée."""
        if any(c.isdigit() for c in nom):
            return "chiffre"
        coeur = self.coeur(nom)
        if not coeur:
            return None  # titre seul : décidé à la résolution d'alias
        if len(coeur) == 1:
            mot = coeur[0]
            forme = mot.capitalize() if mot.isupper() else mot  # « MYCOGÈNE » comme « Mycogène »
            if len(mot) < 3:
                return "trop court"  # « Ca » pour « Ça »
            if ROMAIN.match(mot):
                return "chiffre romain"
            if mot.lower().endswith(SUFFIXES_GENTILES):
                return "gentilé"  # avant les locuteurs : « dit le Spacien » n'en fait pas un nom (consignes)
            if self.locuteur[forme] >= MIN_LOCUTEUR:
                return None  # « fit Mis », « dit le Mulet » : personne sûre
            if self.plutot_minuscule(forme):
                return "minuscule ailleurs"
            if self.est_lieu(forme):
                return "lieu"
            # « Excellence », « Livre » (règle B de LP) ; un titre prouve la personne : « R. Sammy »
            # (Lexique range « sammy » parmi les noms communs)
            if mot.lower() in self.noms_communs and len(nom.split()) == 1:
                return "nom commun"
        return None

    def avec_article(self, m):
        """« le Mulet » : l'article fait partie du nom quand le nom le suit souvent (consignes d'annotation)."""
        coeur = self.coeur(m.texte)
        if (coeur and m.precedent.lower() in ("le", "la") and m.texte.split()[0] == coeur[0]
                and self.part_apres(coeur[0], {"le", "la"}) >= SEUIL_SURNOM):
            m.texte = f"{m.precedent} {m.texte}"
            m.debut -= 1

    def filtrer(self, mentions, journal=None):
        """Mentions gardées, avec leur nom normalisé ; les rejets sont comptés dans journal[raison][nom]."""
        gardees = []
        for m in mentions:
            m.texte = self.normaliser(m)
            raison = self.raison_du_rejet(m.texte)
            if raison is None:
                self.avec_article(m)
                gardees.append(m)
            elif journal is not None:
                journal.setdefault(raison, Counter())[m.texte] += 1
        return gardees
