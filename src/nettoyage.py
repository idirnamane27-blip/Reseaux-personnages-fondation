"""Étape 2 : nettoie le texte extrait (numéros de page, mots coupés, espaces)."""
import re

from src.extraction import DOSSIER_TEXTE, RACINE, ecrire_pages

DOSSIER_PROPRE = RACINE / "texte_propre"

SEPARATEUR = re.compile(r"^### PAGE \d+\n", re.MULTILINE)
NUMERO_PAGE = re.compile(r"^[^\w\n]*\d+[^\w\n]*\s*\Z", re.MULTILINE)
MOT_COUPE = re.compile(r"(\w)-[ \t]*\n\s*(\w)")


def lire_pages(chemin):
    """Renvoie la liste des textes des pages d'un fichier produit par extraction.py."""
    contenu = chemin.read_text(encoding="utf-8")
    return SEPARATEUR.split(contenu)[1:]


def nettoyer_page(texte):
    """Renvoie le texte nettoyé, le nombre de numéros retirés et de mots recollés."""
    texte, nb_numeros = NUMERO_PAGE.subn("", texte)
    texte, nb_mots = MOT_COUPE.subn(r"\1-\2", texte)
    return " ".join(texte.split()), nb_numeros, nb_mots


def main():
    DOSSIER_PROPRE.mkdir(exist_ok=True)
    fichiers = sorted(DOSSIER_TEXTE.glob("*.txt"))

    if not fichiers:
        print("Aucun texte trouvé dans", DOSSIER_TEXTE)
        return

    for chemin in fichiers:
        pages, total_numeros, total_mots = [], 0, 0
        for texte in lire_pages(chemin):
            texte, nb_numeros, nb_mots = nettoyer_page(texte)
            pages.append(texte)
            total_numeros += nb_numeros
            total_mots += nb_mots

        ecrire_pages(pages, DOSSIER_PROPRE / chemin.name)
        print(f"{chemin.name} : {len(pages)} pages, {total_numeros} numéros retirés, "
              f"{total_mots} mots recollés")


if __name__ == "__main__":
    main()
