import pandas as pd
from excel_en_dataframe import charger_excels

dataframes_test = charger_excels("data")

def conversion_df_brute_pour_affectation(dataframes:dict) -> dict:
    res = {}
    dict_df_partner = recup_dict_df_partner(dataframes)
    df_partner = fusion_df_partner(dict_df_partner)
    res["choix_etudiants"] = next(iter(dataframes.values()))
    res["universites_partenaires"] = df_partner
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
    """Fusionne les df du dictionnaire fourni en un seul df avec les colonnes Nom, Places S8, Places S9, Places S10.
    
    Keyword arguments:
    df -- Le dictionnaire des dataframes lié au univsersités partenaire, il y en a un par semestre (3)
    Return: un dataframe avec les colonnes Nom, Places S8, Places S9, Places S10
    """
    # On récupère la liste des noms des partenaires dans le premier df
    liste_noms = next(iter(dict_df.values()))["NOM DU PARTENAIRE"].tolist()
    dict_place_semestre = {} # De la forme {"Places S8":[], "Places S9":[], "Places S10":[]}

    for key in dict_df: # key = "partner_SX"
        semestre = key.split("_")[-1] # On récupère le semestre
        cle = "Places " + str(semestre)
        colonne = "Total " + str(semestre)
        dict_place_semestre[cle] = dict_df[key][colonne]

    data = {
        "NOM DU PARTENAIRE": liste_noms,
        "Places S8": dict_place_semestre["Places S8"],
        "Places S9": dict_place_semestre["Places S9"],
        "Places S10": dict_place_semestre["Places S10"]
    }

    return pd.DataFrame(data)

test = conversion_df_brute_pour_affectation(dataframes=dataframes_test)
print(test)