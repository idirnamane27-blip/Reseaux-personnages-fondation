"""Principe : on compare LP et LL à des listes de référence (personnes, lieux) faites à la main.
Pourquoi : la précision dit combien de noms trouvés sont justes, le rappel combien de vrais noms sont trouvés.
Exemple : LP = {Seldon, Terminus}, référence = {Seldon, Hardin} -> précision 50 %, rappel 50 %.
Écrit resultats/evaluation.txt : LP par personnage et par livre, LP par forme, LL (avec ses deux indices)."""
from collections import Counter
from pathlib import Path

from src.corpus import formes_en
from src.liste_l import DOSSIER_RESULTATS, decouper_mots, lire_L
from src.nettoyage import DOSSIER_PROPRE, lire_pages

DOSSIER_REFERENCES = Path(__file__).resolve().parent


def lire_reference(nom_fichier):
    """Un nom par ligne ; « ? » (cas douteux mais retenu) et commentaires # ignorés."""
    lignes = (DOSSIER_REFERENCES / nom_fichier).read_text(encoding="utf-8").splitlines()
    return {l.strip().rstrip("?").strip() for l in lignes if l.strip() and not l.startswith("#")}


def f_mesure(p, r):
    return 2 * p * r / (p + r) if p + r else 0


def scores(trouves, reference, frequences):
    """Précision, rappel, F par forme, puis pondérés par la fréquence dans le corpus."""
    justes = trouves & reference
    poids = lambda noms: sum(frequences.get(c, 0) for c in noms)
    p, r = len(justes) / len(trouves), len(justes) / len(reference)
    pp, rp = poids(justes) / poids(trouves), poids(justes) / poids(reference)
    return {"lignes": len(trouves), "justes": len(justes), "faux": len(trouves - reference),
            "ratés": len(reference - trouves), "P": p, "R": r, "F": f_mesure(p, r),
            "Pp": pp, "Rp": rp, "Fp": f_mesure(pp, rp)}


ENTETE = (f"  {'liste':<24}{'lignes':>7}{'justes':>8}{'faux':>6}{'ratés':>7}{'P':>8}{'R':>8}{'F':>8}"
          f"   |{'P pond.':>9}{'R pond.':>9}{'F pond.':>9}")


def ligne(nom, s):
    return (f"  {nom:<24}{s['lignes']:>7}{s['justes']:>8}{s['faux']:>6}{s['ratés']:>7}{s['P']:>8.1%}{s['R']:>8.1%}"
            f"{s['F']:>8.1%}   |{s['Pp']:>9.1%}{s['Rp']:>9.1%}{s['Fp']:>9.1%}")


def avec_frequence(noms, frequences):
    return ", ".join(f"{c} ({frequences.get(c, 0)})" for c in sorted(noms, key=lambda c: (-frequences.get(c, 0), c)))


def compter_par_livre(formes):
    """{livre: Counter des formes} : combien de fois chaque forme apparaît dans chaque livre."""
    comptes = {}
    for chemin in sorted(DOSSIER_PROPRE.glob("*.txt")):
        compte = Counter()
        for texte in lire_pages(chemin):
            mots = decouper_mots(texte)
            for i in range(len(mots)):
                compte.update(f for f, n in formes_en(mots, i) if f in formes)
        comptes[chemin.stem.replace("_impaires", "")] = compte
    return comptes


def personnages_par_livre():
    """LP par personnage : dans chaque livre, on ne compte que les personnages (de LP et de la référence) dont
    une forme y apparaît. Une ligne est juste si son nom est une forme d'un personnage de la référence ;
    une deuxième ligne pour le même personnage est un doublon."""
    lignes_ref = (DOSSIER_REFERENCES / "personnages_reference.txt").read_text(encoding="utf-8").splitlines()
    reference = [l.split(" | ") for l in lignes_ref if l.strip() and not l.startswith("#")]
    LP = [(l.split("\t")[0], l.split("\t")[2].split(" | "))
          for l in (DOSSIER_RESULTATS / "LP.txt").read_text(encoding="utf-8").splitlines()]
    personnage_de = {forme: i for i, formes in enumerate(reference) for forme in formes}
    comptes = compter_par_livre({f for g in reference for f in g} | {f for n, fs in LP for f in fs})
    comptes["Total"] = sum(comptes.values(), Counter())
    sortie = [f"LP par personnage (personnages_reference.txt, {len(reference)} personnages)",
              f"  {'livre':<34}{'lignes':>7}{'réf':>6}{'justes':>8}{'doublons':>10}{'faux':>6}{'ratés':>7}"
              f"{'P':>8}{'R':>8}{'F1':>8}"]
    for livre, compte in comptes.items():
        attendus = {i for i, formes in enumerate(reference) if any(compte[f] for f in formes)}
        lignes = [nom for nom, formes in LP if any(compte[f] for f in formes)]
        justes = [personnage_de[n] for n in lignes if personnage_de.get(n) in attendus]
        trouves = set(justes)
        p, r = len(trouves) / len(lignes), len(trouves) / len(attendus)
        nom = livre + (" (réglage)" if "empire" in livre else "")
        sortie.append(f"  {nom:<34}{len(lignes):>7}{len(attendus):>6}{len(trouves):>8}{len(justes) - len(trouves):>10}"
                      f"{len(lignes) - len(justes):>6}{len(attendus) - len(trouves):>7}{p:>8.1%}{r:>8.1%}"
                      f"{f_mesure(p, r):>8.1%}")
    return sortie


def precision_a(classement, reference, n):
    return sum(c in reference for c in classement[:n]) / min(n, len(classement))


def main():
    frequences = {c: f for c, n, f in lire_L("L.txt")}
    personnes = lire_reference("reference_personnes.txt")
    lieux = lire_reference("reference_lieux.txt")
    formes_LP = {c for c, n, f in lire_L("LP_formes.txt")}
    LL = [l.split("\t") for l in (DOSSIER_RESULTATS / "LL.txt").read_text(encoding="utf-8").splitlines()]
    classement = [l[0] for l in LL]   # LL.txt est triée par fréquence
    indices = {l[0]: l[3] for l in LL}
    hapax = {c for c in lieux if frequences.get(c) == 1}

    lignes = personnages_par_livre()
    lignes += ["", f"LP par forme (reference_personnes.txt, {len(personnes)} noms)", ENTETE,
               ligne("LP_formes.txt", scores(formes_LP, personnes, frequences))]
    lignes += ["", f"LL (reference_lieux.txt, {len(lieux)} noms, dont {len(hapax)} vus une seule fois ; "
                   f"{len(lieux & formes_LP)} pris par LP : {', '.join(sorted(lieux & formes_LP))})", ENTETE]
    for nom, trouves in (("préposition seule", {c for c, i in indices.items() if "prep" in i}),
                         ("spaCy seul", {c for c, i in indices.items() if "spacy" in i}),
                         ("LL (préposition OU spaCy)", set(classement))):
        lignes.append(ligne(nom, scores(trouves, lieux, frequences)))
    lignes.append("  précision des premières lignes de LL (par fréquence) : "
                  + ", ".join(f"P@{n} = {precision_a(classement, lieux, n):.0%}" for n in (20, 50, 100)))
    details = ["", "=== LP_formes.txt",
               "En trop   : " + avec_frequence(formes_LP - personnes, frequences),
               "Manquants : " + avec_frequence(personnes - formes_LP, frequences),
               "", "=== LL.txt",
               "En trop   : " + avec_frequence(set(classement) - lieux, frequences),
               "Manquants : " + avec_frequence(lieux - set(classement), frequences)]
    (DOSSIER_RESULTATS / "evaluation.txt").write_text("\n".join(lignes + details) + "\n", encoding="utf-8")
    print("\n".join(lignes))


if __name__ == "__main__":
    main()
