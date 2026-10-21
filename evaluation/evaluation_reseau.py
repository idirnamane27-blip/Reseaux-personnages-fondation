"""Principe : on compare les graphes du pipeline aux graphes de référence annotés à la main, avec la métrique du sujet.
Pourquoi : mesurer chaque idée sans dépenser de soumission Kaggle, et voir quelles erreurs coûtent des points.
Exemple : python -m evaluation.evaluation_reseau -> tableau par passage + resultats/reseau/evaluation_locale.txt."""
import argparse
from pathlib import Path
from statistics import mean

import spacy
from spacy.matcher import PhraseMatcher

from evaluation.metrique_reseau import noms, score
from src.extraction import RACINE
from src.reseau.donnees import chapitres_trilogie
from src.reseau.graphe import construire_graphe
from src.reseau.ner import MODELE, Mention
from src.reseau.pipeline import extraire_reseaux

DOSSIER_ANNOTATIONS = Path(__file__).parent / "annotations_reseau"
SORTIE = RACINE / "resultats" / "reseau" / "evaluation_locale.txt"


def lire_annotation(chemin):
    """Liste de personnages, chacun une liste de formes."""
    lignes = chemin.read_text(encoding="utf-8").splitlines()
    return [[f.strip() for f in l.split(";") if f.strip()] for l in lignes if l.strip() and not l.startswith("#")]


def graphe_reference(texte, personnages, nlp):
    """Occurrences des formes annotées (la plus longue d'abord), puis liens à 25 tokens comme le pipeline."""
    doc = nlp(texte)
    matcher = PhraseMatcher(nlp.vocab)
    formes = [f for p in personnages for f in p]
    matcher.add("PER", list(nlp.tokenizer.pipe(formes)))
    occupe, mentions = set(), []
    for _, debut, fin in sorted(matcher(doc), key=lambda m: -(m[2] - m[1])):
        if not set(range(debut, fin)) & occupe:
            occupe |= set(range(debut, fin))
            mentions.append(Mention(doc[debut:fin].text, debut, fin))
    presentes = {m.texte for m in mentions}
    groupes = [set(p) & presentes for p in personnages if set(p) & presentes]
    return construire_graphe(mentions, groupes)


def diagnostic(predit, reference):
    """Nœuds prédits sans aucun nom commun avec la référence, et personnages de référence jamais trouvés."""
    ref = [noms(reference, n) for n in reference.nodes]
    pred = [noms(predit, n) for n in predit.nodes]
    en_trop = [sorted(p) for p in pred if not any(p & r for r in ref)]
    manques = [sorted(r) for r in ref if not any(p & r for p in pred)]
    melanges = [sorted(p) for p in pred if sum(1 for r in ref if p & r) > 1]
    return en_trop, manques, melanges


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sans-rappel", action="store_true")
    args = parser.parse_args()

    chapitres = chapitres_trilogie()
    textes = dict(chapitres)
    graphes, _ = extraire_reseaux(chapitres, "trilogie", rappel=not args.sans_rappel, verbeux=False)
    nlp = spacy.load(MODELE, exclude=["tok2vec", "morphologizer", "parser", "attribute_ruler", "lemmatizer", "ner"])

    lignes, scores = [], []
    entete = f"{'passage':8} {'N-P':>5} {'N-R':>5} {'N-F1':>5} {'A-P':>5} {'A-R':>5} {'A-F1':>5} {'score':>6}"
    lignes.append(entete)
    details = []
    for chemin in sorted(DOSSIER_ANNOTATIONS.glob("*.txt")):
        identifiant = chemin.stem
        if identifiant not in textes:
            continue
        reference = graphe_reference(textes[identifiant], lire_annotation(chemin), nlp)
        s = score(graphes[identifiant], reference)
        scores.append(s)
        lignes.append(f"{identifiant:8} {s['noeuds_p']:5.2f} {s['noeuds_r']:5.2f} {s['noeuds_f1']:5.2f} "
                      f"{s['aretes_p']:5.2f} {s['aretes_r']:5.2f} {s['aretes_f1']:5.2f} {s['score']:6.3f}")
        en_trop, manques, melanges = diagnostic(graphes[identifiant], reference)
        details.append(f"== {identifiant} : {reference.number_of_nodes()} personnages, "
                       f"{reference.number_of_edges()} liens dans la référence ; prédit "
                       f"{graphes[identifiant].number_of_nodes()} nœuds, {graphes[identifiant].number_of_edges()} liens")
        details += [f"   en trop  : {';'.join(x)}" for x in en_trop]
        details += [f"   manqué   : {';'.join(x)}" for x in manques]
        details += [f"   mélangé  : {';'.join(x)}" for x in melanges]
    moyenne = {k: mean(s[k] for s in scores) for k in scores[0]}
    lignes.append(f"{'MOYENNE':8} {moyenne['noeuds_p']:5.2f} {moyenne['noeuds_r']:5.2f} {moyenne['noeuds_f1']:5.2f} "
                  f"{moyenne['aretes_p']:5.2f} {moyenne['aretes_r']:5.2f} {moyenne['aretes_f1']:5.2f} {moyenne['score']:6.3f}")
    texte = "\n".join(lignes + [""] + details) + "\n"
    SORTIE.write_text(texte, encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main()
