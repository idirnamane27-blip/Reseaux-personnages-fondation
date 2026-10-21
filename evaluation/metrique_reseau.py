"""Principe : la métrique du leaderboard (section 3.3 du sujet), recodée pour évaluer sans Kaggle.
Pourquoi : les soumissions sont limitées et Kaggle ne dit pas quelles erreurs coûtent des points.
Exemple : score(G_predit, G_reference) -> {"noeuds_f1": 0.8, "aretes_f1": 0.6, "score": 0.7, ...}.

Nœuds (Vala et al., 2015) : chaque nœud est un ensemble de noms (attribut names, séparé par « ; »).
  précision : couplage biparti maximal avec sim_p(E, G) = 1 - |E - G| / |E|, moyenne sur les nœuds prédits ;
  rappel    : couplage biparti maximal avec sim_r(E, G) = 1 si E ∩ G non vide, moyenne sur les nœuds de référence.
Arêtes : couplage biparti maximal des nœuds avec l'indice de Jaccard des noms ; une arête prédite est juste
  si ses deux extrémités sont couplées à deux nœuds reliés dans la référence (et inversement pour le rappel)."""
import numpy as np
from scipy.optimize import linear_sum_assignment


def noms(G, n):
    return frozenset(x.strip() for x in G.nodes[n]["names"].split(";") if x.strip())


def couplage(predits, reference, similarite):
    """{indice prédit: indice référence} qui maximise la somme des similarités (paires de similarité nulle exclues)."""
    if not predits or not reference:
        return {}
    matrice = np.array([[similarite(e, g) for g in reference] for e in predits])
    lignes, colonnes = linear_sum_assignment(matrice, maximize=True)
    return {i: j for i, j in zip(lignes, colonnes) if matrice[i, j] > 0}


def sim_p(e, g):
    return 1 - len(e - g) / len(e)


def sim_r(e, g):
    return 1.0 if e & g else 0.0


def jaccard(e, g):
    return len(e & g) / len(e | g)


def f1(p, r):
    return 2 * p * r / (p + r) if p + r else 0.0


def score(predit, reference):
    E = [noms(predit, n) for n in predit.nodes]
    G = [noms(reference, n) for n in reference.nodes]

    f = couplage(E, G, sim_p)
    precision_n = sum(sim_p(E[i], G[j]) for i, j in f.items()) / len(E) if E else 0.0
    g = couplage(E, G, sim_r)
    rappel_n = len(g) / len(G) if G else 0.0

    c = couplage(E, G, jaccard)
    noeuds_E, noeuds_G = list(predit.nodes), list(reference.nodes)
    vers_ref = {noeuds_E[i]: noeuds_G[j] for i, j in c.items()}
    vers_pred = {v: k for k, v in vers_ref.items()}
    justes_p = sum(1 for u, v in predit.edges
                   if u in vers_ref and v in vers_ref and reference.has_edge(vers_ref[u], vers_ref[v]))
    justes_r = sum(1 for u, v in reference.edges
                   if u in vers_pred and v in vers_pred and predit.has_edge(vers_pred[u], vers_pred[v]))
    precision_a = justes_p / predit.number_of_edges() if predit.number_of_edges() else 0.0
    rappel_a = justes_r / reference.number_of_edges() if reference.number_of_edges() else 0.0

    resultat = {"noeuds_p": precision_n, "noeuds_r": rappel_n, "noeuds_f1": f1(precision_n, rappel_n),
                "aretes_p": precision_a, "aretes_r": rappel_a, "aretes_f1": f1(precision_a, rappel_a)}
    resultat["score"] = (resultat["noeuds_f1"] + resultat["aretes_f1"]) / 2
    return resultat
