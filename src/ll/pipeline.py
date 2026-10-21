"""Tâche 3 : LL garde les candidats non-personnes que l'un des deux indices de lieu désigne.
Pourquoi : la préposition est sûre mais rare, spaCy voit plus large mais se trompe ; leur OU rattrape les lieux
que chacun manque ; titres et gentilés sont retirés avant.
Exemple : « Terminus » est gardé par les deux ; « Fondation » par spaCy seul ; « Trantor » par la préposition seule ;
« Korelliens » (gentilé) est retiré avant."""
from src.corpus import analyser_corpus
from src.liste_l import DOSSIER_RESULTATS, lire_L
from src.ll.l1_candidats import candidats_LL
from src.ll.l2_preposition import indice_preposition
from src.ll.l3_spacy import indice_spacy
from src.ll.nettoyage_ll import nettoyer

NB_EXEMPLES = 10   # exemples par liste dans le journal


def par_frequence(candidats, analyse):
    return sorted(candidats, key=lambda c: (-analyse["candidats"][c]["frequence"], c))


def indices_de(c, prep, spacy):
    """« prep », « spacy » ou « prep+spacy » : les indices qui ont fait entrer c dans LL."""
    return "+".join(nom for nom, indice in (("prep", prep), ("spacy", spacy)) if c in indice)


def ecrire_LL(LL, prep, spacy, analyse):
    fiches = analyse["candidats"]
    with open(DOSSIER_RESULTATS / "LL.txt", "w", encoding="utf-8") as f:
        for c in par_frequence(LL, analyse):
            f.write(f"{c}\t{fiches[c]['n']}\t{fiches[c]['frequence']}\t{indices_de(c, prep, spacy)}\n")


def bloc(titre, candidats, analyse):
    exemples = par_frequence(candidats, analyse)[:NB_EXEMPLES]
    return [f"{titre} : {len(candidats)}", "  " + ", ".join(exemples), ""]


def ecrire_journal(candidats, retires, prep, spacy, LL, analyse):
    lignes = [f"Candidats au départ (principe 1, moins LP) : {len(candidats) + len(retires)}", ""]
    for motif in ("titre", "gentilé"):
        lignes += bloc(f"Retirés, {motif}", [c for c, m in retires.items() if m == motif], analyse)
    lignes += bloc("Gardés par l'indice préposition", prep, analyse)
    lignes += bloc("Gardés par l'indice spaCy", spacy, analyse)
    lignes += bloc("Gardés par les deux", prep & spacy, analyse)
    lignes += bloc("Total LL (préposition OU spaCy)", LL, analyse)
    lignes += bloc("Rejetés", set(candidats) - LL, analyse)
    texte = "\n".join(lignes)
    (DOSSIER_RESULTATS / "LL_journal.txt").write_text(texte, encoding="utf-8")
    print(texte)


def main():
    L = lire_L()
    analyse = analyser_corpus(L)
    candidats, retires = nettoyer(candidats_LL(L, analyse))
    prep = indice_preposition(candidats, analyse)
    spacy = indice_spacy(candidats)
    LL = prep | spacy
    ecrire_LL(LL, prep, spacy, analyse)
    ecrire_journal(candidats, retires, prep, spacy, LL, analyse)


if __name__ == "__main__":
    main()
