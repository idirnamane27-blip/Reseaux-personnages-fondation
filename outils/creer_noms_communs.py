"""À lancer une seule fois : télécharge Lexique 3.83 et écrit ressources/noms_communs.txt,
les mots dont la catégorie grammaticale (cgram) la plus fréquente est NOM, en minuscule, un par ligne.
Pourquoi la plus fréquente : Lexique donne aussi NOM à des homographes de mots outils (« la » la note,
« dit » un dit, « vers » des vers, « une » la une) ; on garde le mot seulement si NOM est son emploi principal.
Source : New, Pallier et al., Lexique 3, http://www.lexique.org (base Lexique383.tsv, licence CC BY-SA 4.0)."""
import csv
import io
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

URL = "http://www.lexique.org/databases/Lexique383/Lexique383.tsv"
SORTIE = Path(__file__).resolve().parent.parent / "ressources" / "noms_communs.txt"


def main():
    with urllib.request.urlopen(URL, timeout=120) as reponse:
        texte = reponse.read().decode("utf-8")
    frequences = defaultdict(Counter)   # mot -> {catégorie: fréquence dans les livres + les films}
    for l in csv.DictReader(io.StringIO(texte), delimiter="\t", quoting=csv.QUOTE_NONE):
        if l["ortho"] and l["cgram"]:
            frequences[l["ortho"].lower()][l["cgram"]] += float(l["freqlivres"]) + float(l["freqfilms2"])
    noms = sorted(mot for mot, f in frequences.items()
                  if "NOM" in f and f["NOM"] >= max(f.values()))
    entete = [f"# Noms communs de Lexique 3.83 (catégorie la plus fréquente = NOM), en minuscule : {len(noms)} mots",
              f"# Source : {URL} (colonnes ortho, cgram, freqlivres, freqfilms2)",
              "# New B., Pallier C. et al., Lexique 3 (www.lexique.org), licence CC BY-SA 4.0",
              "# Créé par outils/creer_noms_communs.py"]
    SORTIE.write_text("\n".join(entete + noms) + "\n", encoding="utf-8")
    print(f"{len(noms)} noms communs écrits dans {SORTIE}")


if __name__ == "__main__":
    main()
