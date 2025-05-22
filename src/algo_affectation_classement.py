import logging
import random
import pandas as pd
import numpy as np

from excel_en_dataframe import charger_excels
from conversion_df_brute import conversion_df_brute_pour_affectation

# Configuration de base du logging
logging.basicConfig(
    filename='log.txt',                # Fichier de sortie
    filemode='a',                      # Mode 'a' = append (évite d’écraser)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO                 # Niveau minimal des messages (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)

def generer_df_choix_etudiants_spe_compatible(n, df_univ):
    """
    Génère un DataFrame contenant les choix d'université de n étudiants pour trois semestres. On prend en compte la spécialités des univ et des étudiants.

    Paramètres :
    ------------
    n : int
        Le nombre d'étudiants (et donc de lignes du DataFrame).

    Retour :
    --------
    DataFrame pandas avec les colonnes :
        - Id Etudiant : identifiant numérique (1 à n)
        - Choix S8 : 5 noms d'univ
        - Choix S9 : idem
        - Choix S10 : idem

    Remarques :
    -----------
    - Les codes Univ proviennent de la liste fixe ['AAAA', ..., 'ZZZZ'] (26 codes possibles).
    - Aucun doublon n'est présent dans une même ligne de choix.
    - L'ordre des codes dans chaque choix est aléatoire.
    """
    if n < 1:
        raise ValueError("Le nombre d'étudiants doit être au moins 1.")
    
    liste_semestre = ["S8", "S9", "S10"]
    liste_specialites = ["MM", "MC", "MMT", "SNI", "BAT", "EIT", "IDU", "ESB", "AM"]
    
    
    data = {
        "Id Etudiant": [],
        "Specialite": [],
        "Choix S8": [],
        "Choix S9": [],
        "Choix S10": []
    }

    for i in range(1, n + 1):
        data["Id Etudiant"].append(i)
        specialite_choisie = random.choice(liste_specialites)
        data["Specialite"].append(specialite_choisie)
        for semestre in liste_semestre:
            liste_univ_compatibles = get_liste_univ_compatible(df_univ, semestre, specialite_choisie)
            choix = random.sample(liste_univ_compatibles, 5)  # 5 noms différents, ordre aléatoire
            data["Choix " + str(semestre)].append(", ".join(choix))
    return pd.DataFrame(data)

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

def get_universite_la_moins_remplie(df_univ:pd.DataFrame, choix:tuple|list, semestre:str, calcul_completion:str="Taux") -> str:
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
        if calcul_completion == "Taux":
            if get_taux_completion_places(df_univ, courant, semestre) < get_taux_completion_places(df_univ, univ_la_moins_rempli, semestre):
                univ_la_moins_rempli = courant
        else:
            if get_nombre_places_prises(df_univ, courant, semestre) < get_nombre_places_prises(df_univ, univ_la_moins_rempli, semestre):
                univ_la_moins_rempli = courant
        i += 1
    return univ_la_moins_rempli

def get_liste_univ_compatible(df_univ:pd.DataFrame, semestre:str, specialite:str):
    """Retourne la liste des universités qui sont compatibles avec la spécialité et le semestre en paramètre.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        semestre: Le semestre choisi en str.

    Returns:
        res: la liste des universités qui sont compatibles avec la spécialité et le semestre en paramètre.
    """
    
    res = []
    for idx, row in df_univ.iterrows(): # On parcours chaque ligne du df
        if specialite in row["Specialites Compatibles " + str(semestre)]: # Si l'univ est compatible 
            res.append(row["NOM DU PARTENAIRE"])
    return res

def get_univ_compatible_la_moins_remplie(df_univ:pd.DataFrame, semestre:str, specialite:str, calcul_completion:str="Taux"):
    """Retourne le nom de l'université qui est compatible avec la spécialité en paramètre et qui est la moins remplie.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        semestre: Le semestre choisi en str.

    Returns:
        res: le nom de l'université qui est compatible avec la spécialité en paramètre et qui est la moins remplie.
    """
    
    liste_univ_compatibles = get_liste_univ_compatible(df_univ, semestre, specialite)
    return get_universite_la_moins_remplie(df_univ, liste_univ_compatibles, semestre, calcul_completion)

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
                    specialite = row["Specialite"]
                    univ_compatible_la_moins_remplie = get_univ_compatible_la_moins_remplie(df_univ, semestre, specialite, calcul_completion)
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
    df_etu_fictif = generer_df_choix_etudiants_spe_compatible(20, df_univ)
    print(df_etu_fictif)
    #df_etu_fictif.to_excel("df_etu_fictif.xlsx") 
    #print(traitement_scenario_hybride(df_univ, df_etu_fictif, 3, "Taux" ))
    #print(df_univ)
