"""Principe : rendu/ reçoit les trois listes finales, telles que dans resultats/, avec une ligne d'en-tête.
Pourquoi : le rendu doit pouvoir être refait à l'identique après une relance complète du pipeline.
Exemple : python -m src.rendu -> rendu/L.txt, rendu/LP.txt, rendu/LL.txt (UTF-8)."""
from src.extraction import RACINE
from src.liste_l import DOSSIER_RESULTATS

DOSSIER_RENDU = RACINE / "rendu"
LISTES = {"L.txt": "forme\tnb_mots\tfrequence",
          "LP.txt": "personnage\tfrequence\tformes",
          "LL.txt": "forme\tnb_mots\tfrequence\tindice"}


def main():
    for nom, entete in LISTES.items():
        contenu = (DOSSIER_RESULTATS / nom).read_text(encoding="utf-8")
        (DOSSIER_RENDU / nom).write_text(entete + "\n" + contenu, encoding="utf-8", newline="\n")
        print(f"rendu/{nom} : {contenu.count(chr(10))} lignes")


if __name__ == "__main__":
    main()
