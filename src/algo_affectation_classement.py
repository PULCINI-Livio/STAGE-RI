import logging
import pandas as pd
import numpy as np

from excel_en_dataframe import charger_excels
from generateur_donnees_fictives import generer_dataframe_univ, generer_df_choix_etudiants

# Configuration de base du logging
logging.basicConfig(
    filename='log.txt',                # Fichier de sortie
    filemode='a',                      # Mode 'a' = append (évite d’écraser)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO                 # Niveau minimal des messages (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

def get_nombre_places(df, code_univ, semestre) -> int:
    """Retourne le nombre de place pour l'université correspondant au code univ.
    
    Paramètres :
    ------------        
    df: dataframe 
        Le dataframe des universités partenaires

    code_univ: str
        Le code correspondant à l'université

    Retour :
    --------
    int: val
        Le nombre de place affichés à la ligne pour le code univ correspondant
    """
    
    places = df.loc[df["Code Univ"] == code_univ, "Nombre de places "+str(semestre)]
    if places.empty:
        return None
    val = places.iloc[0]
    if pd.isna(val):
        return None
    return int(val)

def place_est_disponible(df_univ, code_univ:str, semestre:str):
    """Retourne si il y a au moins une place disponible pour l'université correspondant au code univ.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        code_univ: Le code correspondant à l'université

    Returns:
        bool: True si il y a au moins une place
        bool: False si il y a 0 place ou que la donnée est manquante
    """

    res = False
    nb_places = get_nombre_places(df=df_univ, code_univ=code_univ, semestre=semestre)
    if nb_places != None and nb_places > 0:
        res = True
    return res

#print(place_est_disponible(df_univ, "GGGG"))
#logging.info("Début du traitement.")

dataframes = charger_excels("data")
df_univ_ = dataframes["universites_partenaires"]
df_etudiants_ = dataframes["choix_etudiants"]

def decrementer_place(df_univ, code_univ, semestre):
    """Décrémente de 1 le nombre de place pour l'univ dont le code correspond
    
    Args:
        df_univ: Le dataframe des universités partenaires
        code_univ: Le code correspondant à l'université

    """
    # Filtrage des lignes correspondantes
    mask = df_univ["Code Univ"] == code_univ

    if mask.any():
        idx = df_univ[mask].index[0]  # Prend la première ligne correspondante
        current = df_univ.at[idx, "Nombre de places "+str(semestre)]

        # Vérifie que la valeur est bien un nombre
        if pd.notna(current) and current > 0:
            df_univ.at[idx, "Nombre de places "+str(semestre)] = current - 1

def convertir_colonne_en_tuple(df, colonne):
    """convertit toutes les valeurs d'un colonne d'un df en tuple
    
    Args:
        df: Le dataframe à traiter
        colonne: La colonne à traiter

    """
    df[colonne] = df[colonne].apply(lambda x: tuple(map(str.strip, x.split(","))) if pd.notna(x) else x)

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

    semestres = ["S8", "S9", "S10"]

    # Conversion des choix en tuple pour tout les semestres
    for semestre in semestres:
        convertir_colonne_en_tuple(df_etudiants, "Choix " + str(semestre))
        logging.info("conversion colonne " + str(semestre) + " en tuple reussie")

    # On parcours ligne par ligne le df des étudiants
    for idx, row in df_etudiants.iterrows():
        for semestre in semestres: 
            tuple_choix = row["Choix " + str(semestre)] # On récupère sous forme de tuple la liste de choix du semestre
            if pd.notna(tuple_choix): # Si le tuple n'est pas vide
                i = 0
                attribution_faite = False
                # Tant qu'un choix n'est pas attribué ou qu'on a encore des choix à traiter
                while not attribution_faite and i < len(tuple_choix):
                    choix = tuple_choix[i]
                    logging.info("traitement choix numero " + str(i) + " ("+ str(choix) + " " + str(semestre) + ") de l'etudiant " + str(row["Id Etudiant"]) )
                    if place_est_disponible(df_univ, choix, semestre):
                        logging.info(str(get_nombre_places(df_univ, code_univ=choix, semestre=semestre)) + " places disponibles pour " + str(choix) + " " + str(semestre))
                        # Modification dans les DataFrames etudiant et université
                        df_etudiants.at[idx, "Choix " + str(semestre)] = choix
                        decrementer_place(df_univ=df_univ, code_univ=choix, semestre=semestre)
                        logging.info(str(choix) + " " + str(semestre) + " est attribue a " + str(row["Id Etudiant"]))
                        logging.info("decrementation reussie, "+ str(get_nombre_places(df_univ, code_univ=choix, semestre=semestre)) + " place(s) restant(es) pour " + str(choix) + " " + str(semestre))
                        attribution_faite = True
                    else:
                        logging.info(" Aucune places disponibles pour " + str(choix) + " " + str(semestre))

                    i += 1
                if not attribution_faite:
                    df_etudiants.at[idx, semestre] = np.nan
                    logging.info("plus de places disponibles dans aucun des choix pour etudiant " + str(row["Id Etudiant"]))
                    # Faire une attribution autre que celles des choix
            else:
                logging.info(str(row["Id Etudiant"]) + " n'a pas fait de choix au " + str(semestre))
    return df_etudiants

df_univ_fictif = generer_dataframe_univ(26)
print(df_univ_fictif)

df_etu_fictif = generer_df_choix_etudiants(100)
print(df_etu_fictif)

print(traitement(df_univ=df_univ_fictif, df_etudiants=df_etu_fictif, methode="classement"))

