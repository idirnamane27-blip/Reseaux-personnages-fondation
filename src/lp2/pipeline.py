"""Tâche 2 : LP, la liste des personnages, apprise sur le texte seul, en cinq étapes (LP2).
Pourquoi : aucun nom n'est écrit à la main ; tout vient du texte donné, qui peut être un autre roman.
Lancer : python -m src.lp2.pipeline [fichiers .txt...] [--k K] [--p P] [--sortie DOSSIER]
(sans fichier : texte_propre/*.txt ; un fichier sans « ### PAGE » est lu comme une seule page).
Écrit dans DOSSIER (resultats/ par défaut) : LP.txt (personnage TAB fréquence TAB formes | ...),
LP_formes.txt (forme TAB n TAB fréquence, que LL retire de ses candidats) et LP_journal.txt."""
import argparse
import time
from collections import Counter
from pathlib import Path

from src.liste_l import DOSSIER_RESULTATS, candidats, decouper_mots
from src.lp2.dictionnaire import charger_noms_communs
from src.lp2.exemples import exemples, verbes_de_parole
from src.lp2.majuscule import majuscules, seuil_frequence
from src.lp2.modele import classer
from src.lp2.regroupement import regrouper
from src.lp2.spacy_lieux import etiquettes
from src.lp2.titres import titres
from src.nettoyage import DOSSIER_PROPRE, SEPARATEUR

K = 1      # étape 1 : apparitions pour 100 000 tokens (réglé sur Fondation et empire seul ; k = 2 rejeté, voir evaluation/tests_rejetes.txt)
P = 0.5    # étape 3 : probabilité minimale d'être une personne (réglé sur Fondation et empire seul)
NB_EXEMPLES = 40   # mots montrés par liste dans le journal


def lire_textes(chemins):
    """{chemin: [texte de chaque page]}, espaces normalisés."""
    textes = {}
    for chemin in map(Path, chemins):
        contenu = chemin.read_text(encoding="utf-8")
        pages = SEPARATEUR.split(contenu)[1:] if SEPARATEUR.search(contenu) else [contenu]
        textes[chemin] = [" ".join(t.split()) for t in pages]
    return textes


def construire_L(pages):
    """[(forme, n, fréquence)] comme resultats/L.txt, mais pour les pages données."""
    compte = Counter()
    for mots in pages:
        compte.update(candidats(mots))
    return [(c, c.count(" ") + 1, f) for c, f in compte.most_common()]


def liste(mots, fiches=None):
    mots = sorted(mots, key=lambda m: (-fiches[m], m)) if fiches else sorted(mots)
    suite = " ..." if len(mots) > NB_EXEMPLES else ""
    return ", ".join(mots[:NB_EXEMPLES]) + suite


def lancer(chemins, k=K, p=P):
    """Renvoie LP2 [(personnage, fréquence, formes)], les lignes du journal et {forme de L: fréquence}."""
    textes = lire_textes(chemins)
    pages = [decouper_mots(t) for pages_fichier in textes.values() for t in pages_fichier]
    nb_tokens = sum(1 for mots in pages for m in mots if m[0].isalnum())
    L = construire_L(pages)
    frequence = {c: f for c, n, f in L}

    retenus, fiches = majuscules(L, pages, nb_tokens, k)
    motifs = Counter(motif for t, f, motif in fiches.values())
    journal = [f"Corpus : {', '.join(Path(c).name for c in chemins)}",
               f"{nb_tokens} tokens, L : {len(L)} formes dont {len(fiches)} mots seuls ; "
               f"k = {k}, p = {p}", "",
               f"Étape 1 - majuscule : {len(fiches)} -> {len(retenus)} mots "
               f"(taux_maj >= 0.9, fréquence >= {seuil_frequence(nb_tokens, k):.1f})"]
    for motif in ("sans minuscule", "jamais en milieu de phrase", "minuscule", "rare"):
        retires = [m for m, (t, f, mo) in fiches.items() if mo == motif]
        journal.append(f"  retirés, {motif} : {motifs[motif]} : {liste(retires, frequence)}")
    journal.append(f"  gardés : {liste(retenus, frequence)}")

    est_nom_commun = charger_noms_communs()
    titres_calcules = titres(pages, set(retenus), est_nom_commun)
    journal += ["", "Règle A - titres (nom commun du dictionnaire devant un nom de l'étape 1 >= 3 fois, ou "
                f"abréviation hors dictionnaire suivie d'un point >= 90 % puis d'un nom) : {len(titres_calcules)}"]
    journal += [f"  {t} ({sorte}, {n} fois) : {', '.join(suivis)}"
                for t, (sorte, n, suivis) in sorted(titres_calcules.items(), key=lambda x: -x[1][1])]

    verbes = verbes_de_parole(pages)
    personnes, non_personnes, comptes = exemples(pages, retenus, etiquettes(textes), verbes, titres_calcules)
    journal += ["", "Étape 2 - exemples sûrs",
                f"  verbes de parole appris ({len(verbes)}) : {', '.join(sorted(verbes))}",
                f"  personnes (locuteur d'incise >= 2, article permis, jamais un titre) : {len(personnes)} : "
                f"{liste(personnes, frequence)}",
                f"  non-personnes : {len(non_personnes)} : {liste(non_personnes, frequence)}",
                f"    dont sur/vers/dans/à/en >= 20 % : {liste(comptes['preposition'], frequence)}",
                f"    dont article >= 50 % et jamais locuteur : {liste(comptes['article'], frequence)}",
                f"    dont spaCy LOC >= 70 % : {liste(comptes['spacy'], frequence)}",
                f"  article >= 50 % mais locuteur (pas exemples) : {liste(comptes['article mais locuteur'], frequence)}",
                f"  dans les deux groupes, retirés des deux : {len(comptes['les deux'])} : "
                f"{liste(comptes['les deux'], frequence)}"]

    gardes, proba, ajoutes = classer(pages, retenus, personnes, non_personnes, p)
    journal += ["", f"Étape 3 - bayésien naïf : {len(retenus)} -> {len(gardes)} personnes (p >= {p})",
                f"  ajoutés aux exemples au 2e tour (p > 0.9) : {len(ajoutes)} : {liste(ajoutes, frequence)}",
                "  exemples sûrs perdus : " + liste(personnes - gardes, frequence),
                "  non-personnes sûres gardées : " + liste(non_personnes & gardes, frequence),
                "  p de chaque candidat (du plus fréquent au moins fréquent) :"]
    journal += [f"    {c:<20}{proba[c]:.2f}  {'GARDÉ' if c in gardes else 'retiré'}"
                for c in sorted(retenus, key=lambda c: (-frequence[c], c))]

    LP2, etapes = regrouper(L, gardes, titres_calcules, est_nom_commun, comptes["locuteur"])
    supprimees = sorted(n for n, preuve in etapes["règle B"].items() if not preuve)
    gardees = sorted(f"{n} ({preuve} incises)" for n, preuve in etapes["règle B"].items() if preuve)
    journal += ["", "Étape 5 - regroupement",
                f"  noms complets : {len(etapes['complets'])} : {', '.join(sorted(etapes['complets']))}",
                f"  formes dont on a retiré le titre : " +
                ", ".join(f"{f} -> {n}" for f, n in sorted(etapes["titres retirés"].items())),
                f"  noms seuls rattachés : " + ", ".join(f"{n} -> {c}" for n, c in etapes["rattachés"].items()),
                f"  noms seuls ambigus (pas de ligne) : " +
                ", ".join(f"{n} ({' / '.join(c)})" for n, c in etapes["ambigus"].items()),
                f"  règle B, lignes nom commun supprimées (aucune preuve) : {len(supprimees)} : {', '.join(supprimees)}",
                f"  règle B, lignes nom commun gardées (preuve de personne) : {', '.join(gardees)}",
                "", f"LP2 : {len(LP2)} personnages"]
    return LP2, journal, frequence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fichiers", nargs="*")
    parser.add_argument("--k", type=float, default=K)
    parser.add_argument("--p", type=float, default=P)
    parser.add_argument("--sortie", default=DOSSIER_RESULTATS)
    args = parser.parse_args()
    chemins = args.fichiers or sorted(DOSSIER_PROPRE.glob("*.txt"))
    debut = time.time()
    LP2, journal, frequences = lancer(chemins, args.k, args.p)
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    with open(sortie / "LP.txt", "w", encoding="utf-8") as f:
        for nom, frequence, formes in LP2:
            f.write(f"{nom}\t{frequence}\t{' | '.join(formes)}\n")
    formes = sorted({forme for p in LP2 for forme in p[2]}, key=lambda c: (-frequences[c], c))
    with open(sortie / "LP_formes.txt", "w", encoding="utf-8") as f:
        for c in formes:
            f.write(f"{c}\t{c.count(' ') + 1}\t{frequences[c]}\n")
    journal.append(f"Durée : {time.time() - debut:.1f} s")
    (sortie / "LP_journal.txt").write_text("\n".join(journal) + "\n", encoding="utf-8")
    print(f"{len(LP2)} personnages -> {sortie / 'LP.txt'} ({journal[-1]})")


if __name__ == "__main__":
    main()
