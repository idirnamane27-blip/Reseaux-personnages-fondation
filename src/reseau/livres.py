"""Principe : un graphe par roman de la trilogie = les graphes de ses blocs additionnés, avec les groupes d'alias du livre.
Pourquoi : le sujet demande un réseau par livre et un commentaire qualitatif ; les mesures (degré, intermédiarité,
communautés) disent si le graphe retrouve la structure en parties des romans.
Exemple : python -m src.reseau.livres -> resultats/reseau/livres/{fon,fee,sdf}.graphml + mesures.txt."""
from collections import Counter

import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities

from src.extraction import RACINE
from src.reseau.alias import groupes_du_chapitre
from src.reseau.donnees import TRILOGIE, chapitres_trilogie
from src.reseau.graphe import construire_graphe
from src.reseau.pipeline import analyser, livre
from src.ressources import charger_liste

SORTIE = RACINE / "resultats" / "reseau" / "livres"
TITRES = {"fon": "Fondation", "fee": "Fondation et Empire", "sdf": "Seconde Fondation"}


def libelle(groupe, freq, titres):
    """Nom affiché : le nom sans titre qui a le plus de mots, à égalité le plus cité
    ({monsieur Hardin, Salvor Hardin, Hardin} -> « Salvor Hardin »)."""
    def sans_titre(nom):
        return " ".join(m for m in nom.split() if m.lower() not in titres) or nom
    meilleur = max(groupe, key=lambda n: (len(sans_titre(n).split()), freq[n], n))
    return sans_titre(meilleur)


def graphes_par_livre(chapitres, nom_corpus="trilogie"):
    """{livre: Graph} ; nœud = groupe d'alias du livre (attributs names, mentions, blocs), poids = co-occurrences."""
    gardees, groupes_livre, _ = analyser(chapitres, nom_corpus, verbeux=False)
    titres = charger_liste("titres.txt")
    freq = Counter(m.texte for ms in gardees.values() for m in ms)
    graphes = {}
    for code, groupes in groupes_livre.items():
        G = nx.Graph()
        noeud_de = {}
        for groupe in groupes:
            noeud = libelle(groupe, freq, titres)
            while noeud in G:  # deux groupes de même libellé (rare) : on les distingue
                noeud += "'"
            G.add_node(noeud, names=";".join(sorted(groupe)), mentions=0, blocs=0)
            noeud_de.update({nom: noeud for nom in groupe})
        for identifiant, mentions in gardees.items():
            if livre(identifiant) != code:
                continue
            for m in mentions:
                if m.texte in noeud_de:
                    G.nodes[noeud_de[m.texte]]["mentions"] += 1
            H = construire_graphe(mentions, groupes_du_chapitre(mentions, groupes))
            for n, d in H.nodes(data=True):
                G.nodes[noeud_de[d["names"].split(";")[0]]]["blocs"] += 1
            for u, v, d in H.edges(data=True):
                a = noeud_de[H.nodes[u]["names"].split(";")[0]]
                b = noeud_de[H.nodes[v]["names"].split(";")[0]]
                poids = G.edges[a, b]["weight"] if G.has_edge(a, b) else 0
                G.add_edge(a, b, weight=poids + d["weight"])
        G.remove_nodes_from([n for n, d in G.nodes(data=True) if d["mentions"] == 0])
        graphes[code] = G
    return graphes


def mesures(G, k=10):
    """Texte : taille, densité, personnages les plus centraux, communautés (modularité gloutonne pondérée)."""
    lignes = [f"{G.number_of_nodes()} personnages, {G.number_of_edges()} liens, densité {nx.density(G):.3f}, "
              f"{nx.number_connected_components(G)} composantes (dont {sum(1 for c in nx.connected_components(G) if len(c) == 1)} isolés)"]
    force = dict(G.degree(weight="weight"))
    inter = nx.betweenness_centrality(G, weight=lambda u, v, d: 1 / d["weight"])
    lignes.append(f"{'personnage':28} {'mentions':>8} {'blocs':>5} {'degré':>5} {'force':>6} {'intermédiarité':>14}")
    for n in sorted(G, key=lambda n: -force[n])[:k]:
        lignes.append(f"{n[:28]:28} {G.nodes[n]['mentions']:8} {G.nodes[n]['blocs']:5} {G.degree(n):5} "
                      f"{force[n]:6} {inter[n]:14.3f}")
    communautes = greedy_modularity_communities(G, weight="weight")
    lignes.append(f"communautés ({len(communautes)}) :")
    for i, c in enumerate(sorted(communautes, key=lambda c: -sum(force[n] for n in c))):
        if len(c) > 1:
            membres = sorted(c, key=lambda n: -force[n])
            lignes.append(f"  {i + 1}. " + ", ".join(membres[:10]) + (" ..." if len(membres) > 10 else ""))
    return "\n".join(lignes)


def main():
    SORTIE.mkdir(parents=True, exist_ok=True)
    graphes = graphes_par_livre(chapitres_trilogie())
    rapport = []
    for _, code in TRILOGIE:
        G = graphes[code]
        nx.write_graphml(G, SORTIE / f"{code}.graphml")
        rapport += [f"== {TITRES[code]} ({code})", mesures(G), ""]
    (SORTIE / "mesures.txt").write_text("\n".join(rapport), encoding="utf-8")
    print("\n".join(rapport))


if __name__ == "__main__":
    main()
