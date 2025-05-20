import os
import pandas as pd

# Chemin du dossier contenant les fichiers Excel
dossier = r"data"  # Exemple : r"C:\Users\pulci\Documents\excels"

def charger_excels(dossier: str) -> dict:
    """
    Charge tous les fichiers Excel (.xlsx, .xls) d'un dossier en DataFrames pandas.

    Parcourt les fichiers présents dans le dossier spécifié, lit ceux qui sont des fichiers Excel,
    et les stocke dans un dictionnaire où chaque clé est le nom du fichier (sans extension)
    et chaque valeur est un DataFrame pandas.

    Args:
        dossier (str): Le chemin vers le dossier contenant les fichiers Excel.

    Returns:
        dict: Un dictionnaire où les clés sont les noms de fichiers sans extension
              et les valeurs sont les DataFrames correspondants.
    """
    
    dataframes = {}
    for fichier in os.listdir(dossier):
        if fichier.endswith((".xlsx", ".xls")):
            chemin = os.path.join(dossier, fichier)
            nom = os.path.splitext(fichier)[0]
            try:
                df = pd.read_excel(chemin)
                dataframes[nom] = df
            except Exception as e:
                print(f"Erreur avec {fichier}: {e}")
    return dataframes

display_prints = False

if display_prints:
    # Chemin du dossier contenant les fichiers Excel
    dossier = r"data"  

    print("affichage des prints")
    dataframes = charger_excels(dossier)
    print(dataframes.keys())
    # Afficher les 5 premières lignes de chaque DataFrame
    for nom, df in dataframes.items():
        print(f"\n--- {nom} ---")
        print(df.head())
