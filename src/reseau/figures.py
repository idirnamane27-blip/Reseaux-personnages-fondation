"""Principe : une figure par roman, nœuds colorés par communauté, taille = mentions, épaisseur = co-occurrences.
Pourquoi : illustrer l'analyse qualitative (article, oral) ; les communautés doivent rappeler les parties du roman.
Exemple : python -m src.reseau.figures -> resultats/reseau/livres/{fon,fee,sdf}.png (après src.reseau.livres)."""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as effets
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from networkx.algorithms.community import greedy_modularity_communities

from src.reseau.donnees import TRILOGIE
from src.reseau.livres import SORTIE, TITRES

# palette catégorielle validée (4 premiers emplacements) ; les petites communautés restent en gris
COULEURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
GRIS = "#b4b2a9"
ENCRE = "#2b2b29"
LIEN = "#c9c8c1"
ETIQUETTES = 14  # personnages nommés sur la figure (les plus forts)


def dessiner(G, titre, chemin):
    total = G.number_of_nodes()
    # seule la composante principale est dessinée : les petits groupes isolés écrasent le dessin
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    force = dict(G.degree(weight="weight"))
    communautes = sorted(greedy_modularity_communities(G, weight="weight"), key=lambda c: -sum(force[n] for n in c))
    couleur = {n: GRIS for n in G}
    legende = []
    for i, c in enumerate(communautes[:len(COULEURS)]):
        if len(c) < 3:
            continue
        for n in c:
            couleur[n] = COULEURS[i]
        tete = sorted(c, key=lambda n: -force[n])[:3]
        legende.append(Line2D([], [], marker="o", linestyle="", markersize=8, color=COULEURS[i],
                              markeredgecolor="white", label=", ".join(tete) + f" ({len(c)})"))

    position = nx.spring_layout(G, weight="weight", k=3 / math.sqrt(len(G)), iterations=500, seed=7)
    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
    poids = [G.edges[e]["weight"] for e in G.edges]
    nx.draw_networkx_edges(G, position, ax=ax, edge_color=LIEN, width=[0.4 + 1.2 * math.log1p(w) for w in poids])
    nx.draw_networkx_nodes(G, position, ax=ax, node_color=[couleur[n] for n in G],
                           node_size=[20 + 7 * G.nodes[n]["mentions"] for n in G],
                           edgecolors="white", linewidths=1.5)  # anneau de 2 px qui sépare les nœuds qui se touchent
    for n in sorted(G, key=lambda n: -force[n])[:ETIQUETTES]:
        x, y = position[n]
        texte = ax.text(x, y, n, fontsize=8, color=ENCRE, ha="center", va="center", fontweight="bold")
        texte.set_path_effects([effets.withStroke(linewidth=3, foreground="white")])
    ax.legend(handles=legende, loc="lower left", fontsize=7.5, frameon=False, title="Communautés (taille)",
              title_fontsize=8)
    ax.set_title(f"{titre} : composante principale, {G.number_of_nodes()} personnages et {G.number_of_edges()} liens "
                 f"({total - G.number_of_nodes()} autres personnages hors composante)", fontsize=11, color=ENCRE, loc="left")
    ax.text(1, -0.02, "taille du nœud = mentions · épaisseur du lien = co-occurrences (≤ 25 tokens)",
            transform=ax.transAxes, ha="right", fontsize=7, color="#6b6a64")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(chemin, facecolor="white")
    plt.close(fig)


def main():
    for _, code in TRILOGIE:
        G = nx.read_graphml(SORTIE / f"{code}.graphml")
        dessiner(G, TITRES[code], SORTIE / f"{code}.png")
        print(f"-> {SORTIE / f'{code}.png'}")


if __name__ == "__main__":
    main()
