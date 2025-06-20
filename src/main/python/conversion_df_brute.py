from collections import defaultdict
import pandas as pd
from excel_en_dataframe import charger_excels

def conversion_df_brute_pour_affectation(dataframes:dict) -> dict:
    """Traite les dataframes du dictionnaire en entré pour que leur colonnes soit adapté à l'algorithme d'affectation.
    
    Args:
        dataframes: le dictionnaire contenant les dataframes issus des excels.
        
    Returns:
        res: Le dictionnaire contenant 2 df, celui des universités et celui du choix des étudiants
    """
    res = {}
    df_univ = dataframes["univ_data_mobility"]
    df_univ_modified = traitement_df_univ(df_univ)
    res["choix_etudiants"] = dataframes["choix_etudiants"]
    res["universites_partenaires"] = df_univ_modified
    return res

def traitement_df_univ(df:pd.DataFrame):
    """Traite le df des univ avec les nouvelles colonnes Nom, Places S8, Places Prises S8, Specialites Compatibles S8, Places S9, Places Prises S9, Specialites Compatibles S9.
    
    Keyword arguments:
    df -- Le dictionnaire des dataframes lié au universités partenaire
    Return: un dataframe avec les colonnes Nom, Places S8, Places Prises S8, Specialites Compatibles S8, Places S9, Places Prises S9, Specialites Compatibles S9
    """
    semestres = ["S8", "S9"]
    specialites = ["MM", "MC", "SNI", "BAT", "EIT", "IDU"]
    
    # Récupère les noms des partenaires depuis l'un des DataFrames
    noms_partenaires = df["nom_partenaire"].str.strip()

    data = {"nom_partenaire": noms_partenaires}
    for semestre in semestres:
        

        # Places disponibles
        data[f"Places {semestre}"] = df[f"{semestre}_total_places"].tolist()

        # Places prises initialisées à 0E
        data[f"Places Prises {semestre}"] = [0] * len(df)

        # Spécialités compatibles (liste des colonnes dont la valeur > 0)
        colonnes_semestre = [f"{semestre}_{spe}" for spe in specialites]
        data[f"Specialites Compatibles {semestre}"] = df[colonnes_semestre].apply(
            lambda row: [spe for spe in specialites if pd.notna(row[f"{semestre}_{spe}"]) and row[f"{semestre}_{spe}"] > 0],
            axis=1
        )

        # Université prioritaire ou non
        data[f"Prioritaire {semestre}"] = df[f"important"].tolist()

        # Université prioritaire ou non
        data[f"Note Min {semestre}"] = df[f"note_min"].tolist()

    return pd.DataFrame(data)

test = True
if test :
    dataframes_test = charger_excels("src\\main\\data")
    
    df_test = conversion_df_brute_pour_affectation(dataframes=dataframes_test)
    
    print(df_test["universites_partenaires"])
    #df_test["universites_partenaires"].to_excel("src\\main\\output\\univ_data_mobility_refined.xlsx", index=False)
