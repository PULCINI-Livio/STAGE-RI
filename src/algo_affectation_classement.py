import logging
import pandas as pd
import ast

from extract_data import charger_excels


# Configuration de base du logging
logging.basicConfig(
    filename='log.txt',                # Fichier de sortie
    filemode='a',                      # Mode 'a' = append (évite d’écraser)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO                 # Niveau minimal des messages (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

def get_nombre_places(df, code_univ, semestre) -> int:
    """Retourne le nombre de place pour l'université correspondant au code univ.
    
    Args:
        df: Le dataframe des universités partenaires
        code_univ: Le code correspondant à l'université

    Returns:
        int: Le nombre de place affichés à la ligne pour le code univ correspondant
    """
    
    places = df.loc[df["Code Univ"] == code_univ, "Nombre de places "+str(semestre)]
    if places.empty:
        return None
    val = places.iloc[0]
    if pd.isna(val):
        return None
    return int(val)

def place_est_disponible(df_univ, code_univ:str):
    """Retourne si il y a au moins une place disponible pour l'université correspondant au code univ.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        code_univ: Le code correspondant à l'université

    Returns:
        bool: True si il y a au moins une place
        bool: False si il y a 0 place ou que la donnée est manquante
    """

    res = False
    nb_places = get_nombre_places(df=df_univ, code_univ=code_univ)
    if nb_places != None and nb_places > 0:
        res = True
    return res

#print(place_est_disponible(df_univ, "GGGG"))
#logging.info("Début du traitement.")

dataframes = charger_excels("data")
df_univ = dataframes["universites_partenaires"]
df_etudiants = dataframes["choix_etudiants"]

def decrementer_place(df_univ, code_univ):
    """Décrémente de 1 le nombre de place pour l'univ dont le code correspond
    
    Args:
        df_univ: Le dataframe des universités partenaires
        code_univ: Le code correspondant à l'université

    """
    # Filtrage des lignes correspondantes
    mask = df_univ["Code Univ"] == code_univ

    if mask.any():
        idx = df_univ[mask].index[0]  # Prend la première ligne correspondante
        current = df_univ.at[idx, "Nombre de place"]

        # Vérifie que la valeur est bien un nombre
        if pd.notna(current) and current > 0:
            df_univ.at[idx, "Nombre de place"] = current - 1

def traitement(df_univ, df_etudiants, methode):
    """Retourne un df correspondant aux affectations de chaque étudiant 
    à un seul choix pour les semestres qu'il a choisi.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        df_etudiants: Le dataframe des choix des étudiants

    Returns:
        df_res: le dataframe correspondant aux affectations de chaque étudiant 
    à un seul choix pour les semestres qu'il a choisi
    """

    colonnes_choix = ["S8", "S9", "S10"]

    # Conversion des choix en tuple pour tout les semestres
    for col in colonnes_choix:
        df_etudiants[col].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else x)

    # On parcours ligne par ligne le df des étudiants
    for idx, row in df_etudiants.iterrows():
        for col in colonnes_choix: # Pour chaque semestre
            tuple_choix = row[col]
            if not pd.notna(tuple_choix):
                i = 0
                attribution_faite = False
                # Tant qu'un choix n'est pas attribué ou qu'on a encore des choix à traiter
                while not attribution_faite and i < len(tuple_choix):
                    choix = tuple_choix[i]
                    if place_est_disponible(df_univ, choix):
                        # Modification dans le DataFrame etudiant
                        df_etudiants.at[idx, col] = choix
                        decrementer_place(df_univ=df_univ, code_univ=choix)

                        attribution_faite = True
                        print(str(choix) + "a ete attribué, nombre de place restante : " + str(get_nombre_places(df_univ, code_univ=choix)))
                    i += 1
                if not attribution_faite:
                    print("plus de places disponibles dans aucun des choix")

print(get_nombre_places(df_univ, "AAAA", "S10"))