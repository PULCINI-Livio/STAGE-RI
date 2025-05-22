from collections import defaultdict
import pandas as pd
import numpy as np
from excel_en_dataframe import charger_excels

def conversion_df_brute_pour_affectation(dataframes:dict) -> dict:
    """Converti un dictionnaire composé de 4 dataframe issue des excels (1 sur les étudiants, 3 pour chaque partenaire par semestre) en un dictionnaire de 2 df, celui des univ et celui du choix des étudiants.
    
    Args:
        dataframes: le dictionnaire contenant tous les dataframes issus des excels.
        
    Returns:
        res: Le dictionnaire contenant 2 df, celui des univ et celui du choix des étudiants
    """
    res = {}
    dict_df_partner = recup_dict_df_partner(dataframes)
    df_partner_complet = fusion_df_partner(dict_df_partner)
    res["choix_etudiants"] = next(iter(dataframes.values()))
    res["universites_partenaires"] = df_partner_complet
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
    """Fusionne les 3 df partner_SX du dictionnaire fourni en un seul df avec les colonnes Nom, Places SX, Places Prises SX, Specialites Compatibles SX.
    
    Keyword arguments:
    df -- Le dictionnaire des dataframes lié au univsersités partenaire, il y en a un par semestre (3)
    Return: un dataframe avec les colonnes Nom, Places S8, Places S9, Places S10
    """
    # On récupère la liste des noms des partenaires dans le premier df
    liste_noms = next(iter(dict_df.values()))["NOM DU PARTENAIRE"].tolist()
    dict_place_semestre = {} # De la forme {"Places S8":[], "Places S9":[], "Places S10":[]}
    dict_spe_compatible_semestre = defaultdict(list) # De la forme {"Specialites Compatibles S8":[], "Specialites Compatibles S9":[], "Specialites Compatibles S10":[]}
    liste_specialites = ["MM", "MC", "MMT", "SNI", "BAT", "EIT", "IDU", "ESB", "AM"]
    
    # On parcours les 3 df
    for key in dict_df: # key = "partner_SX"
        semestre = key.split("_")[-1] # On récupère le semestre
        cle = "Places " + str(semestre) # clé du dictionnaire
        colonne = "Total " + str(semestre) # Colonne du df
        dict_place_semestre[cle] = dict_df[key][colonne]

        # On va regarder les spécialités compatible (place > 0) de chaque ligne
        for idx, row in dict_df[key].iterrows(): # On parcours chaque ligne du df courant
            liste_specialites_pour_univ_courante = []
            for spe in liste_specialites:
                if pd.notna(row[spe]) and row[spe] > 0: # Si la spécialité est compatible
                    liste_specialites_pour_univ_courante.append(spe)
            dict_spe_compatible_semestre["Specialites Compatibles " + str(semestre)].append(liste_specialites_pour_univ_courante)
    
    data = {
        "NOM DU PARTENAIRE": liste_noms,
        "Places S8": dict_place_semestre["Places S8"],
        "Places Prises S8":0,
        "Specialites Compatibles S8": dict_spe_compatible_semestre["Specialites Compatibles S8"],
        "Places S9": dict_place_semestre["Places S9"],
        "Places Prises S9":0,
        "Specialites Compatibles S9": dict_spe_compatible_semestre["Specialites Compatibles S9"],
        "Places S10": dict_place_semestre["Places S10"],
        "Places Prises S10":0,
        "Specialites Compatibles S10": dict_spe_compatible_semestre["Specialites Compatibles S10"]
    }

    return pd.DataFrame(data)

test = False
if test :
    dataframes_test = charger_excels("data")
    test = conversion_df_brute_pour_affectation(dataframes=dataframes_test)
    print(test)
    test['universites_partenaires'].to_excel("df_univ.xlsx") 