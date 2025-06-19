from collections import defaultdict
import time
import pandas as pd
import numpy as np
from excel_en_dataframe import charger_excels

def conversion_df_brute_pour_affectation(dataframes:dict) -> dict:
    """Converti un dictionnaire composé de 3 dataframe issue des excels (1 sur les étudiants, 2 pour chaque partenaire par semestre) en un dictionnaire de 2 df, celui des univ et celui du choix des étudiants.
    
    Args:
        dataframes: le dictionnaire contenant tous les dataframes issus des excels.
        
    Returns:
        res: Le dictionnaire contenant 2 df, celui des univ et celui du choix des étudiants
    """
    res = {}
    df_univ = dataframes["univ_data_mobility"]
    df_univ_modified = traitement_df_univ(df_univ)
    res["choix_etudiants"] = dataframes["choix_etudiants"]
    res["universites_partenaires"] = df_univ_modified
    return res

def recup_dict_df_partner(dataframes:dict) -> dict:
    """Récupère les dataframes liés aux universités partenaires et les insère dans un dictionnaire
    
    Paramètres :
    ------------        
    dataframes :
        Un dictionnaire contenant tous les dataframes issus des excels.

    Retour :
    --------
    res :
        Un dictionnaire des dataframes liés aux universités partenaires
    """
    
    res = {}
    for key in dataframes.keys():
        if "partner" in key.lower():
            res[key] = dataframes[key]
    return res

def fusion_df_partner(dict_df:dict):
    """Fusionne les 2 df partner_SX du dictionnaire fourni en un seul df avec les colonnes Nom, Places SX, Places Prises SX, Specialites Compatibles SX.
    
    Keyword arguments:
    df -- Le dictionnaire des dataframes lié au univsersités partenaire, il y en a un par semestre (2)
    Return: un dataframe avec les colonnes Nom, Places S8, Places S9
    """
    semestres = ["S8", "S9"]
    specialites = ["MM", "MC", "SNI", "BAT", "EIT", "IDU"]
    
    # Récupère les noms des partenaires depuis l'un des DataFrames
    noms_partenaires = dict_df[f"partner_{semestres[0]}"]["NOM DU PARTENAIRE"].str.strip()

    data = {"NOM DU PARTENAIRE": noms_partenaires}
    
    for semestre in semestres:
        df = dict_df[f"partner_{semestre}"]

        # Places disponibles
        data[f"Places {semestre}"] = df[f"Total {semestre}"].tolist()

        # Places prises initialisées à 0
        data[f"Places Prises {semestre}"] = [0] * len(df)

        # Spécialités compatibles (liste des colonnes dont la valeur > 0)
        data[f"Specialites Compatibles {semestre}"] = df[specialites].apply(
            lambda row: [spe for spe in specialites if pd.notna(row[spe]) and row[spe] > 0],
            axis=1
        )

        # Université prioritaire ou non
        data[f"Prioritaire {semestre}"] = df[f"Prioritaire"].tolist()

        # Université prioritaire ou non
        data[f"Note Min {semestre}"] = df[f"Note Min"].tolist()

    return pd.DataFrame(data)

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
    
    print(df_test)
    df_test["universites_partenaires"].to_excel("src\\main\\output\\univ_data_mobility_refined.xlsx", index=False)
