"""Principe : une figure par roman, nœuds colorés par communauté, taille = mentions, épaisseur = co-occurrences.
Pourquoi : illustrer l'analyse qualitative (article, oral) ; les communautés doivent rappeler les parties du roman.
Exemple : python -m src.reseau.figures -> resultats/reseau/livres/{fon,fee,sdf}.png (après src.reseau.livres),
et {fon,fee,sdf}_article.pdf au format d'une colonne d'article."""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as effets
import matplotlib.pyplot as plt
import networkx as nx
from adjustText import adjust_text
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


def dessiner(G, titre, chemin, article=False):
    """article=True : format d'une colonne d'article (8,5 cm), sans titre, polices lisibles une fois imprimées."""
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

    if article:
        # Kamada-Kawai répartit mieux le cœur du réseau quand la place est petite
        position = nx.kamada_kawai_layout(G, pos=nx.spring_layout(G, seed=7))
    else:
        position = nx.spring_layout(G, weight="weight", k=3 / math.sqrt(len(G)), iterations=500, seed=7)
    taille = (3.35, 3.0) if article else (10, 8)  # pouces ; 3,35 = largeur d'une colonne Interspeech
    fig, ax = plt.subplots(figsize=taille, dpi=300 if article else 200)
    echelle = 0.12 if article else 1  # surface des nœuds proportionnelle à la surface de la figure
    poids = [G.edges[e]["weight"] for e in G.edges]
    epaisseur = 0.35 if article else 1.0
    nx.draw_networkx_edges(G, position, ax=ax, edge_color=LIEN,
                           width=[epaisseur * (0.4 + 1.2 * math.log1p(w)) for w in poids])
    nx.draw_networkx_nodes(G, position, ax=ax, node_color=[couleur[n] for n in G],
                           node_size=[echelle * (20 + 7 * G.nodes[n]["mentions"]) for n in G],
                           edgecolors="white", linewidths=0.5 if article else 1.5)  # anneau de 2 px qui sépare les nœuds qui se touchent
    textes = []
    for n in sorted(G, key=lambda n: -force[n])[:8 if article else ETIQUETTES]:
        x, y = position[n]
        texte = ax.text(x, y, n, fontsize=6 if article else 8, color=ENCRE, ha="center", va="center",
                        fontweight="bold")
        texte.set_path_effects([effets.withStroke(linewidth=1.5 if article else 3, foreground="white")])
        textes.append(texte)
    if article:
        # écarte les étiquettes qui se chevauchent, avec un trait fin vers leur nœud
        adjust_text(textes, ax=ax, expand=(1.15, 1.3),
                    arrowprops=dict(arrowstyle="-", color="#6b6a64", lw=0.4))
        for h in legende:
            h.set_markersize(4)
        ax.legend(handles=legende, loc="upper center", bbox_to_anchor=(0.5, 0.0), fontsize=5.5, frameon=False,
                  ncol=1, handletextpad=0.3, borderaxespad=0)
        ax.axis("off")
        fig.tight_layout(pad=0.2)
        fig.savefig(chemin, facecolor="white", bbox_inches="tight", pad_inches=0.02)
        plt.close(fig)
        return
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
        dessiner(G, TITRES[code], SORTIE / f"{code}_article.pdf", article=True)
        print(f"-> {SORTIE / f'{code}.png'} et {code}_article.pdf")


if __name__ == "__main__":
    main()
