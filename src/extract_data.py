import pandas as pd

# Chemin du fichier Excel
chemin_fichier = "data\\universites_partenaires.xlsx"

# Lire le fichier Excel (par défaut, lit la première feuille)
df = pd.read_excel(chemin_fichier)

# Afficher les premières lignes du DataFrame
print(df.head())
