"""Principe : un graphe graphml par chapitre du corpus leaderboard, réunis dans le CSV attendu par Kaggle.
Pourquoi : format imposé par le sujet (colonnes ID et graphml, noms séparés par « ; »).
Exemple : python -m src.reseau.soumission -> resultats/reseau/soumission.csv + un .graphml par chapitre."""
import argparse

import networkx as nx
import pandas as pd

from src.extraction import RACINE
from src.reseau.donnees import chapitres_leaderboard
from src.reseau.pipeline import extraire_reseaux

SORTIE = RACINE / "resultats" / "reseau"


def ecrire_rejets(journal, chemin):
    with open(chemin, "w", encoding="utf-8") as f:
        for raison, noms in sorted(journal.items()):
            f.write(f"## {raison} ({sum(noms.values())} mentions)\n")
            f.writelines(f"{n}\t{nom}\n" for nom, n in noms.most_common())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sans-cache", action="store_true", help="relance spaCy même si le cache existe")
    parser.add_argument("--sans-rappel", action="store_true", help="ne recherche pas les noms validés dans tout le livre")
    args = parser.parse_args()

    chapitres = chapitres_leaderboard()
    graphes, journal = extraire_reseaux(chapitres, "leaderboard", not args.sans_cache, not args.sans_rappel)
    (SORTIE / "graphml").mkdir(parents=True, exist_ok=True)

    lignes = {"ID": [], "graphml": []}
    for identifiant, G in graphes.items():
        nx.write_graphml(G, SORTIE / "graphml" / f"{identifiant}.graphml")
        lignes["ID"].append(identifiant)
        lignes["graphml"].append("".join(nx.generate_graphml(G)))
        print(f"{identifiant}: {G.number_of_nodes()} personnages, {G.number_of_edges()} liens")
    ecrire_rejets(journal, SORTIE / "rejets.txt")

    df = pd.DataFrame(lignes).set_index("ID")
    df.to_csv(SORTIE / "soumission.csv")
    print(f"-> {SORTIE / 'soumission.csv'} ({len(df)} chapitres)")


if __name__ == "__main__":
    main()
