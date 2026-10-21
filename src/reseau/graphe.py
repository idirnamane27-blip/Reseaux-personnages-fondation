"""Principe : un lien entre deux personnages = deux de leurs mentions séparées par 25 tokens ou moins.
Pourquoi : c'est la définition de la co-occurrence donnée par le sujet ; le poids compte les co-occurrences.
Exemple : « Seldon regarda Dors » -> lien Seldon—Dors de poids 1."""
import networkx as nx

DISTANCE = 25


def nom_du_noeud(groupe):
    """Le nom le plus long du groupe sert d'identifiant (« Hari Seldon » plutôt que « Hari »)."""
    return max(groupe, key=lambda n: (len(n.split()), len(n), n))


def construire_graphe(mentions, groupes, distance=DISTANCE):
    noeud_de = {}
    G = nx.Graph()
    for groupe in groupes:
        noeud = nom_du_noeud(groupe)
        G.add_node(noeud, names=";".join(sorted(groupe)))
        for nom in groupe:
            noeud_de[nom] = noeud

    # les titres seuls non rattachés n'ont pas de nœud
    mentions = sorted((m for m in mentions if m.texte in noeud_de), key=lambda m: m.debut)
    for i, a in enumerate(mentions):
        for b in mentions[i + 1:]:
            if b.debut - a.fin > distance:
                break
            u, v = noeud_de[a.texte], noeud_de[b.texte]
            if u != v:
                poids = G.edges[u, v]["weight"] if G.has_edge(u, v) else 0
                G.add_edge(u, v, weight=poids + 1)
    return G
