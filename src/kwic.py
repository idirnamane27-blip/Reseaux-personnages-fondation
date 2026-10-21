"""Principe : afficher chaque occurrence d'une forme au milieu de ses voisins (keyword in context).
Pourquoi : pour trancher un cas douteux de la référence, il faut le lire dans le texte, pas deviner.
Exemple : python -m src.kwic "Port" 5 -> « ... atterrit au | Port | de Terminus ... »."""
import sys

from src.corpus import formes_en, toutes_les_pages

LARGEUR = 8   # mots affichés de chaque côté


def occurrences(forme):
    for mots in toutes_les_pages():
        for i in range(len(mots)):
            for f, n in formes_en(mots, i):
                if f == forme:
                    gauche = " ".join(mots[max(0, i - LARGEUR):i])
                    droite = " ".join(mots[i + n:i + n + LARGEUR])
                    yield f"{gauche:>60} | {forme} | {droite}"


def main():
    forme, nb = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10
    for ligne in list(occurrences(forme))[:nb]:
        print(ligne)


if __name__ == "__main__":
    main()
