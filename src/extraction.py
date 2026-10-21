"""Étape 1 : extrait le texte de chaque PDF du corpus, page par page."""
from pathlib import Path

import pymupdf

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_CORPUS = RACINE / "corpus"
DOSSIER_TEXTE = RACINE / "texte"


def extraire_pdf(chemin_pdf):
    """Renvoie la liste des textes des pages, dans l'ordre."""
    with pymupdf.open(chemin_pdf) as document:
        return [page.get_text(sort=True) for page in document]


def ecrire_pages(pages, chemin_sortie):
    """Écrit les pages dans un fichier texte, séparées par ### PAGE n."""
    with open(chemin_sortie, "w", encoding="utf-8") as f:
        for numero, texte in enumerate(pages, start=1):
            f.write(f"### PAGE {numero}\n{texte}\n")


def main():
    DOSSIER_TEXTE.mkdir(exist_ok=True)
    pdfs = sorted(DOSSIER_CORPUS.glob("*.pdf"))

    if not pdfs:
        print("Aucun PDF trouvé dans", DOSSIER_CORPUS)
        return

    for chemin_pdf in pdfs:
        pages = extraire_pdf(chemin_pdf)
        ecrire_pages(pages, DOSSIER_TEXTE / f"{chemin_pdf.stem}.txt")
        print(f"{chemin_pdf.name} : {len(pages)} pages")


if __name__ == "__main__":
    main()
