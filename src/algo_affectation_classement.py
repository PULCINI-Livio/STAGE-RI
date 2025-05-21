import logging
import pandas as pd
import numpy as np

from excel_en_dataframe import charger_excels
from generateur_donnees_fictives import generer_df_choix_etudiants
from conversion_df_brute import conversion_df_brute_pour_affectation

# Configuration de base du logging
logging.basicConfig(
    filename='log.txt',                # Fichier de sortie
    filemode='a',                      # Mode 'a' = append (évite d’écraser)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO                 # Niveau minimal des messages (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

def get_nombre_places_total(df:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    """Retourne le nombre de places pour l'université correspondante.
    
    Paramètres :
    ------------        
    df: dataframe 
        Le dataframe des universités partenaires

    nom_du_partenaire: str
        Le nom de l'université

    Retour :
    --------
    int: val
        Le nombre de place affichés à la ligne pour le code univ correspondant
    """
    
    places = df.loc[df["NOM DU PARTENAIRE"] == nom_du_partenaire, "Places "+str(semestre)]
    if places.empty:
        return None
    val = places.iloc[0]
    if pd.isna(val):
        return None
    return int(val)

def get_nombre_places_prises(df:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    """Retourne le nombre de places prises pour l'université correspondante.
    
    Paramètres :
    ------------        
    df: dataframe 
        Le dataframe des universités partenaires

    nom_du_partenaire: str
        Le nom de l'université

    Retour :
    --------
    int: val
        Le nombre de place affichés à la ligne pour le code univ correspondant
    """
    
    places = df.loc[df["NOM DU PARTENAIRE"] == nom_du_partenaire, "Places Prises "+str(semestre)]
    if places.empty:
        return None
    val = places.iloc[0]
    if pd.isna(val):
        return None
    return int(val)

def place_est_disponible(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    """Retourne si il y a au moins une place disponible pour l'université correspondant au code univ.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        nom_du_partenaire: Le code correspondant à l'université

    Returns:
        bool: True si il y a au moins une place
        bool: False si il y a 0 place ou que la donnée est manquante
    """

    res = False
    nb_places_total = get_nombre_places_total(df=df_univ, nom_du_partenaire=nom_du_partenaire, semestre=semestre)
    nb_places_prises = get_nombre_places_prises(df=df_univ, nom_du_partenaire=nom_du_partenaire, semestre=semestre)

    if nb_places_total != None and nb_places_total > nb_places_prises:
        res = True
    return res

def incrementer_places_prise(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    """Incrémente de 1 le nombre de places prises pour l'université correspondante
    
    Args:
        df_univ: Le dataframe des universités partenaires
        nom_du_partenaire: Le nom de l'université

    """
    # Filtrage des lignes correspondantes
    mask = df_univ["NOM DU PARTENAIRE"] == nom_du_partenaire

    if mask.any():
        idx = df_univ[mask].index[0]  # Prend la première ligne correspondante
        current = df_univ.at[idx, "Places Prises " + str(semestre)]

        # Vérifie que la valeur est bien un nombre
        if pd.notna(current) and current >= 0:
            df_univ.at[idx, "Places Prises " + str(semestre)] = current + 1

def get_nb_places_disponibles(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    nb_places_total = get_nombre_places_total(df_univ, nom_du_partenaire, semestre)
    nb_places_prises = get_nombre_places_prises(df_univ, nom_du_partenaire, semestre)
    
    return nb_places_total-nb_places_prises

def get_taux_completion_places(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    nb_places_prises = get_nombre_places_prises(df_univ, nom_du_partenaire, semestre)
    nb_places_total = get_nombre_places_total(df_univ, nom_du_partenaire, semestre)
    return nb_places_prises/nb_places_total

def convertir_colonne_en_tuple(df:pd.DataFrame, colonne:str):
    """convertit toutes les valeurs d'un colonne d'un df en tuple
    
    Args:
        df: Le dataframe à traiter
        colonne: La colonne à traiter

    """
    df[colonne] = df[colonne].apply(lambda x: tuple(map(str.strip, x.split(","))) if pd.notna(x) else x)

def get_universite_la_moins_remplie(df_univ:pd.DataFrame, choix:tuple, semestre:str, calcul_completion:str="Taux") -> str:
    """Retourne un str correspondant à l'université la moins remplie selon la méthode de calcul 
    à un seul choix pour les semestres qu'il a choisi selon un scénario hybride entre le classement et la complétion des partenaires.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        choix: Le tuple contenant les universités partenaires choisi par l'étudiant
        semestre: Le semestre SX en str
        calcul_completion: Un str qui va donner la méthode de calcule de la complétion, "Taux" calcule selon le rapport entre le total de place disponible et le nombre de places prises et choisi le partenaire avec le taux le plus bas. "Places Prises" regarde seulement combien de places sont prises et choisi ceux avec le moins de places prises.

    Returns:
        res: le str de l'université la moins remplie selon la méthode de calcul
    """

    univ_la_moins_rempli = choix[0]
    i = 1
    while i < len(choix):
        courant = choix[i]
        if get_taux_completion_places(df_univ, courant, semestre) < get_taux_completion_places(df_univ, univ_la_moins_rempli, semestre):
            univ_la_moins_rempli = courant
        i += 1
    return univ_la_moins_rempli

def traitement_scenario_hybride(df_univ:pd.DataFrame, df_etudiants:pd.DataFrame, limite_ordre:int=0, calcul_completion:str="Taux"):
    """Retourne un df correspondant aux affectations de chaque étudiant 
    à un seul choix pour les semestres qu'il a choisi selon un scénario hybride entre le classement et la complétion des partenaires.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        df_etudiants: Le dataframe des choix des étudiants
        limite_ordre: Le nombre de voeux qui sont ordonnés, exemple : limite_ordre = 3, on traite les 3 premiers voeux, et si il ne sont pas disponibles, on choisi un des autres voeux de manière à maximiser la complétion.
        calcul_completion: Un str qui va donner la méthode de calcule de la complétion, "Taux" calcule selon le rapport entre le total de place disponible et le nombre de places prises et choisi le partenaire avec le taux le plus bas. "Places Prises" regarde seulement combien de places sont prises et choisi ceux avec le moins de places prises.

    Returns:
        df_res: le dataframe correspondant aux affectations de chaque étudiant 
    à un seul choix pour les semestres qu'il a choisi.
    """
    
    # Sécurité
    if limite_ordre > 5:
        limite_ordre = 5
    if limite_ordre < 0:
        limite_ordre = 0
    if calcul_completion != "Taux" and calcul_completion != "Places Prises":
        calcul_completion = "Taux"

    semestres = ["S8", "S9", "S10"]
    choix_final = ""
    # Conversion des choix en tuple pour tout les semestres
    for semestre in semestres:
        convertir_colonne_en_tuple(df_etudiants, "Choix " + str(semestre))
        logging.info("conversion colonne " + str(semestre) + " en tuple reussie")

    # On parcours ligne par ligne le df des étudiants
    for idx, row in df_etudiants.iterrows():
        for semestre in semestres: 
            attribution_faite = False
            tuple_choix = row["Choix " + str(semestre)] # On récupère le tuple de choix du semestre
            if pd.notna(tuple_choix): # Si le tuple n'est pas vide
                for i in range(0, limite_ordre): # Cette boucle reprend le scénario 1 (le major a toujours son 1er voeux)
                        choix_courant = tuple_choix[i]
                        logging.info("traitement choix numero " + str(i) + " ("+ str(choix_courant) + " " + str(semestre) + ") de l'etudiant " + str(row["Id Etudiant"]) )
                        if place_est_disponible(df_univ, choix_courant, semestre):
                            choix_final = choix_courant
                            attribution_faite = True
                # La condition suivante est vrai si pas encore d'attribution et qu'il reste des choix à traiter
                if not attribution_faite and limite_ordre <= 4: # Si l'attribution n'a pas été faite avec le scénario 1, on passe au scénario 2 avec les voeux restants
                    if len(tuple_choix) < 2: # Si un seul choix restant, pas besoin de comparer les taux de complétion
                        univ_la_moins_remplie = tuple_choix[0]
                    else:
                        univ_la_moins_remplie = get_universite_la_moins_remplie(choix=tuple_choix[limite_ordre:], semestre=semestre)
                    if place_est_disponible(df_univ, univ_la_moins_remplie, semestre):
                        choix_final = choix_courant
                        attribution_faite = True

                elif not attribution_faite: # Si tout les choix ont été rejeté
                    specialite = get_specialite()
                    univ_compatible_la_moins_remplie = get_univ_compatible_la_moins_remplie()
                    if place_est_disponible(df_univ, univ_compatible_la_moins_remplie, semestre):
                        choix_final = choix_courant
                        attribution_faite = True    

                else:
                    df_etudiants.at[idx, semestre] = np.nan
                    logging.info("plus de places disponibles dans aucun des choix pour etudiant " + str(row["Id Etudiant"]))

                if attribution_faite:
                    logging.info(str(get_nb_places_disponibles(df_univ, nom_du_partenaire=choix_final, semestre=semestre)) + " places disponibles pour " + str(choix_final) + " " + str(semestre))
                    # Modification dans les DataFrames etudiant et université
                    df_etudiants.at[idx, "choix_final " + str(semestre)] = choix_final
                    incrementer_places_prise(df_univ=df_univ, nom_du_partenaire=choix_final, semestre=semestre)
                    logging.info(str(choix_final) + " " + str(semestre) + " est attribue a " + str(row["Id Etudiant"]))
                    logging.info("Incrementation reussie, "+ str(get_nb_places_disponibles(df_univ, nom_du_partenaire=choix_final, semestre=semestre)) + " place(s) restant(es) pour " + str(choix_final) + " " + str(semestre))
            else:
                logging.info(str(row["Id Etudiant"]) + " n'a pas fait de choix au " + str(semestre))
test = True
if test:
    dataframes = charger_excels("data")
    #print(dataframes.keys())
    df_univ = conversion_df_brute_pour_affectation(dataframes)["universites_partenaires"]
    print(df_univ)
    df_etu_fictif = generer_df_choix_etudiants(400, df_univ["NOM DU PARTENAIRE"].tolist())
    #print(df_etu_fictif)

    print(traitement_scenario_hybride(df_univ, df_etu_fictif, 3, "Taux" ))
    #print(df_univ)
