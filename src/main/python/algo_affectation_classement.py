import logging
import random
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

# Configuration de base du logging
import logging

# Logger général
logger_general = logging.getLogger('general')
logger_general.setLevel(logging.INFO)
fh_general = logging.FileHandler('log.txt', mode='a')
fh_general.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_general.addHandler(fh_general)

# Logger spécifique pour le taux
logger_taux = logging.getLogger('taux')
logger_taux.setLevel(logging.DEBUG)
fh_taux = logging.FileHandler('log_taux.txt', mode='a')
fh_taux.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_taux.addHandler(fh_taux)


def generer_df_choix_etudiants_spe_compatible(n, df_univ, proba_unique_semestre=0.1):
    """
    Génère un DataFrame contenant les choix d'université de n étudiants pour trois semestres, 
    en tenant compte de la spécialité et en permettant que certains étudiants ne fassent pas de choix,
    mais en garantissant qu'au moins un choix est fait pour chaque étudiant.

    Paramètres :
    ------------
    n : int
        Le nombre d'étudiants.
    df_univ : pd.DataFrame
        Le DataFrame des universités avec les colonnes 'Specialite', 'Semestre', 'Nom'.
    proba_unique_semestre : float (entre 0 et 1)
        Probabilité qu’un étudiant ne fasse qu'un choix sur les 3 semestres.

    Retour :
    --------
    pd.DataFrame avec :
        - Id Etudiant
        - Specialite
        - Choix S8 (ou None)
        - Choix S9 (ou None)
    """
    if n < 1:
        raise ValueError("Le nombre d'étudiants doit être au moins 1.")

    liste_semestre = ["S8", "S9"]
    liste_specialites = ["MM", "MC", "MMT", "SNI", "BAT", "EIT", "IDU", "ESB", "AM"]

    data = {
        "Id Etudiant": [],
        "Specialite": [],
        "Choix S8": [],
        "Choix S9": [],
    }

    for i in range(1, n + 1):
        data["Id Etudiant"].append(i)
        specialite_choisie = random.choice(liste_specialites)
        data["Specialite"].append(specialite_choisie)

        choix_par_semestre = {}

        # Génération avec probabilité de ne pas faire de choix
        for semestre in liste_semestre:
            if random.random() < proba_unique_semestre:
                choix_par_semestre[semestre] = None
            else:
                liste_univ_compatibles = get_liste_univ_compatible(df_univ, semestre, specialite_choisie)
                if not liste_univ_compatibles:
                    choix_par_semestre[semestre] = None
                else:
                    nb_choix = min(5, len(liste_univ_compatibles))
                    choix = random.sample(liste_univ_compatibles, nb_choix)
                    choix_par_semestre[semestre] = "; ".join(choix)

        # Vérifier s'il y a au moins un choix parmi les 3 semestres
        if all(val is None for val in choix_par_semestre.values()):
            # Forcer un semestre aléatoire à avoir un choix
            semestre_forcer = random.choice(liste_semestre)
            liste_univ_compatibles = get_liste_univ_compatible(df_univ, semestre_forcer, specialite_choisie)
            if liste_univ_compatibles:
                nb_choix = min(5, len(liste_univ_compatibles))
                choix = random.sample(liste_univ_compatibles, nb_choix)
                choix_par_semestre[semestre_forcer] = "; ".join(choix)
            else:
                # Pas d'université compatible du tout => reste None
                pass

        for semestre in liste_semestre:
            data[f"Choix {semestre}"].append(choix_par_semestre.get(semestre))

    return pd.DataFrame(data)

def semestre_est_valide(semestre:str, liste_semestres:list=["S8", "S9"]):
    return semestre in liste_semestres

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

    if not semestre_est_valide(semestre):
        return None
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
    
    if not semestre_est_valide(semestre):
        return None
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
    if not semestre_est_valide(semestre) or get_nb_places_disponibles(df_univ, nom_du_partenaire, semestre) == None:
        res = None
    elif get_nb_places_disponibles(df_univ, nom_du_partenaire, semestre) > 0:
        res = True
    else:
        res = False
    return res

def incrementer_places_prise(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    """Incrémente de 1 le nombre de places prises pour l'université correspondante
    
    Args:
        df_univ: Le dataframe des universités partenaires
        nom_du_partenaire: Le nom de l'université

    """
    # Filtrage des lignes correspondantes
    mask = df_univ["NOM DU PARTENAIRE"] == nom_du_partenaire

    if mask.any() and semestre_est_valide(semestre):
        idx = df_univ[mask].index[0]  # Prend la première ligne correspondante
        current = df_univ.at[idx, "Places Prises " + str(semestre)]

        # Vérifie que la valeur est bien un nombre
        if pd.notna(current) and current >= 0:
            df_univ.at[idx, "Places Prises " + str(semestre)] = current + 1

def get_nb_places_disponibles(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    nb_places_total = get_nombre_places_total(df_univ, nom_du_partenaire, semestre)
    nb_places_prises = get_nombre_places_prises(df_univ, nom_du_partenaire, semestre)
    if nb_places_total is not None and nb_places_prises is not None:
        res = nb_places_total-nb_places_prises
    else:
        res = None
    return res

def get_taux_completion_places(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    nb_places_prises = get_nombre_places_prises(df_univ, nom_du_partenaire, semestre)
    nb_places_total = get_nombre_places_total(df_univ, nom_du_partenaire, semestre)
    if nb_places_total is not None and nb_places_total != 0 and nb_places_prises is not None:
        res = nb_places_prises/nb_places_total
    elif nb_places_total == 0:
        res = 1
    else:
        res = None
    return res

import pandas as pd

def get_taux_completion_moyen(df_univ: pd.DataFrame, semestre: str) -> float:
    logger_taux.debug(f"bonjour")
    partenaires = df_univ['NOM DU PARTENAIRE'].unique()
    taux_list = []

    for partenaire in partenaires:
        taux = get_taux_completion_places(df_univ, partenaire, semestre)
        logger_taux.debug(f"taux de completion de {taux} pour {partenaire} au {semestre}")
        if taux is not None:
            taux_list.append(taux)

    if taux_list:
        return sum(taux_list) / len(taux_list)
    else:
        return None  # Aucun taux valide

def convertir_colonne_en_tuple(df:pd.DataFrame, colonne:str):
    """convertit toutes les valeurs d'un colonne d'un df en tuple
    
    Args:
        df: Le dataframe à traiter
        colonne: La colonne à traiter

    """
    df[colonne] = df[colonne].apply(lambda x: tuple(map(str.strip, x.split(";"))) if pd.notna(x) else x)

def get_universite_la_moins_remplie(df_univ: pd.DataFrame, choix: tuple | list, semestre: str, calcul_completion: str = "Taux") -> str:
    """Retourne un str correspondant à l'université la moins remplie selon la méthode de calcul. Si elles sont toutes remplies, la première de la liste|tuple est renvoyée.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        choix: Le tuple ou la liste contenant les universités partenaires choisis par l'étudiant
        semestre: Le semestre SX en str
        calcul_completion: Un str indiquant la méthode de calcul de la complétion ("Taux" ou "Places Prises")

    Returns:
        str: le nom de l'université la moins remplie ou "" si aucun choix n'est fourni
    """
    if not choix:
        return ""

    univ_la_moins_rempli = choix[0]
    for courant in choix[1:]:
        if calcul_completion == "Taux":
            if get_taux_completion_places(df_univ, courant, semestre) < get_taux_completion_places(df_univ, univ_la_moins_rempli, semestre):
                univ_la_moins_rempli = courant
        else:
            if get_nombre_places_prises(df_univ, courant, semestre) < get_nombre_places_prises(df_univ, univ_la_moins_rempli, semestre):
                univ_la_moins_rempli = courant

    return univ_la_moins_rempli


def get_liste_univ_compatible(df_univ:pd.DataFrame, semestre:str, specialite:str):
    """Retourne la liste des universités qui sont compatibles avec la spécialité et le semestre en paramètre.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        semestre: Le semestre choisi en str.

    Returns:
        res: la liste des universités qui sont compatibles avec la spécialité et le semestre en paramètre.
    """
    
    col = f"Specialites Compatibles {semestre}"
    mask = df_univ[col].apply(lambda lst: specialite in lst if isinstance(lst, list) else False)
    return df_univ.loc[mask, "NOM DU PARTENAIRE"].tolist()

def get_depuis_df_univ_prioritaire_avec_place_et_niveau(df_univ:pd.DataFrame, semestre:str, specialite:str, calcul_completion:str="Taux"):
    """Retourne le nom de l'université qui est la moins remplie en considérant d'abord les univ prioritaire.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        specialite: la spécialité de l'étudiant
        semestre: Le semestre choisi en str.

    Returns:
        res: le nom de l'université qui est la moins remplie en considérant d'abord les univ prioritaire ou une chaine vide si aucune n'est disponible.
    """
    res = ""
    liste_univ_compatibles = get_liste_univ_compatible(df_univ, semestre, specialite)
    if liste_univ_compatibles != []:
        res = get_depuis_liste_univ_prioritaire_avec_place_et_niveau(df_univ, liste_univ_compatibles, semestre, calcul_completion)
    return res

def scinder_liste_univ_par_prio(df_univ, liste_choix): 
    """Retourne deux listes, la première est celle des univ prioritaires, la deuxième les non prioritaires.
    
    Args:
        df_univ: Le DataFrame des universités partenaires.
        liste_choix: Une liste ou un tuple contenant des noms de partenaires.
        
    Returns:
        tuple: (liste_prioritaires, liste_non_prioritaires)
    """
    liste_prioritaires = []
    liste_non_prioritaires = []
    
    for nom in liste_choix:
        ligne = df_univ[df_univ["NOM DU PARTENAIRE"] == nom]
        if not ligne.empty:
            prioritaire = ligne.iloc[0]["Prioritaire"]
            if isinstance(prioritaire, str) and prioritaire.strip().lower() == "oui":
                liste_prioritaires.append(nom)
            else:
                liste_non_prioritaires.append(nom)

    return liste_prioritaires, liste_non_prioritaires

def get_depuis_liste_univ_prioritaire_avec_place_et_niveau(df_univ:pd.DataFrame, liste_choix:tuple|list, note_etudiant:int, semestre:str, calcul_completion:str="Taux"):
    """Retourne le nom de l'université qui est la moins remplie en considérant d'abord les univ prioritaire.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        choix: une liste ou tuple des partenaires
        note_etudiant: la note de l'étudiant
        semestre: Le semestre choisi en str.

    Returns:
        res: le nom de l'université qui est la moins remplie en considérant d'abord les univ prioritaire ou une chaine vide si aucune ne correspond.
    """
    res = ""
    univ_prioritaires, univ_non_prioritaires = scinder_liste_univ_par_prio(df_univ, liste_choix)
    univ_prio_la_moins_remplie = get_universite_la_moins_remplie(df_univ, univ_prioritaires, semestre)
    if place_est_disponible(df_univ, univ_prio_la_moins_remplie, semestre) and etudiant_a_niveau_requis(df_univ, note_etudiant, univ_prio_la_moins_remplie, semestre):
        res = univ_prio_la_moins_remplie
    else:
        univ_non_prio_la_moins_remplie = get_universite_la_moins_remplie(df_univ, univ_non_prioritaires)
        if place_est_disponible(df_univ, univ_non_prio_la_moins_remplie, semestre) and etudiant_a_niveau_requis(df_univ, note_etudiant, univ_non_prio_la_moins_remplie, semestre):
            res = univ_non_prio_la_moins_remplie
    return res

def etudiant_a_niveau_requis(df_univ, note_etudiant, nom_du_partenaire, semestre):
    """Vérifie que l'étudiant a une note suffisante si l'université en paramètre a une note minimale.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        note_etudiant: La note de l'etudiant.
        nom_du_partenaire: le nom de l'université
        semestre: le semestre choisi

    Returns:
        res: True si l'étudiant a le niveau requis ou qu'aucun niveau n'est précisé, False le cas échéant.
    """
    res = True
    note_min_univ = df_univ.loc[df_univ["NOM DU PARTENAIRE"] == nom_du_partenaire, "Note Min "+str(semestre)]
    note_min_valeur = note_min_univ.values[0] if not note_min_univ.empty else None
    if not pd.isna(note_min_valeur) and not None and note_min_valeur > note_etudiant:
        res = False
    return res

def traiter_etudiant_semestre(row, df_univ, semestre, limite_ordre, calcul_completion):
    # Préparer un mapping dynamique des noms
    col_choix = f"Choix_{semestre}"
    id_etudiant = getattr(row, "Id_Etudiant", None)
    tuple_choix = getattr(row, col_choix, None)
    note_etudiant = getattr(row, "Note", None)

    if not tuple_choix or not isinstance(tuple_choix, tuple):
        logger_general.info(f"{id_etudiant} n'a pas fait de choix pour le {semestre}")
        return np.nan

    # Scénario 1 : Voeux ordonnés
    for i, choix in enumerate(tuple_choix[:limite_ordre]):
        if place_est_disponible(df_univ, choix, semestre) and etudiant_a_niveau_requis(df_univ, note_etudiant, choix, semestre):
            logger_general.info(f"{id_etudiant} obtient le choix {choix} (ordre {i+1}) pour le {semestre}")
            return choix
        else:
            logger_general.info(f"{id_etudiant} n'obtient pas le choix {choix} pour {semestre} dans scénario 1")

    # Scénario 2 : Choix restants
    choix_restants = tuple_choix[limite_ordre:]
    if choix_restants:
        univ_choisie = get_depuis_liste_univ_prioritaire_avec_place_et_niveau(df_univ, choix_restants, semestre, calcul_completion)
        if univ_choisie != "":
            logger_general.info(f"{id_etudiant} obtient {univ_choisie} via les choix non ordonnés pour {semestre}")
            return univ_choisie
        else:
            logger_general.info(f"{id_etudiant} n'obtient pas un des choix pour {semestre} dans scénario 2")

    # Scénario 3 : Aucune des options précédentes
    specialite = getattr(row, "Specialite", None)
    univ_fallback = get_depuis_df_univ_prioritaire_avec_place_et_niveau(df_univ, semestre, specialite, calcul_completion)
    if univ_fallback != "":
        logger_general.info(f"{id_etudiant} affecté par fallback à {univ_fallback} pour {semestre}")
        return univ_fallback

    logger_general.info(f"Aucune attribution possible pour {id_etudiant} au {semestre}")
    return np.nan

def traitement_scenario_hybride(df_univ:pd.DataFrame, df_etudiants:pd.DataFrame, limite_ordre:int=0, calcul_completion:str="Taux"):
    """Retourne un df correspondant aux affectations de chaque étudiant 
    à un seul choix pour les semestres qu'il a choisi selon un scénario hybride entre le classement et la complétion des partenaires.
    
    Args:
        df_univ: Le dataframe des universités partenaires
        df_etudiants: Le dataframe des choix des étudiants
        limite_ordre: Le nombre de voeux qui sont ordonnés (entre 0 et 5), exemple : limite_ordre = 2, on traite les 2 premiers voeux dans l'ordre, et si il ne sont pas disponibles, on choisi un des autres voeux de manière à maximiser la complétion.
        calcul_completion: Un str qui va donner la méthode de calcule de la complétion, "Taux" calcule selon le rapport entre le total de place disponible et le nombre de places prises et choisi le partenaire avec le taux le plus bas. "Places Prises" regarde seulement combien de places sont prises et choisi ceux avec le moins de places prises.

    Returns:
        df_res: le dataframe correspondant aux affectations de chaque étudiant 
    à un seul choix pour les semestres qu'il a choisi.
    """
    
    # Validation des paramètres
    limite_ordre = min(max(limite_ordre, 0), 5)
    calcul_completion = calcul_completion if calcul_completion in ["Taux", "Places Prises"] else "Taux"
    semestres = ["S8", "S9"]

    # Convertir les colonnes de choix en tuples
    for semestre in semestres:
        convertir_colonne_en_tuple(df_etudiants, f"Choix {semestre}")
        logger_general.info(f"Conversion colonne Choix {semestre} en tuple réussie")

    df_etudiants.columns = df_etudiants.columns.str.replace(" ", "_")
    
    # Initialisation des colonnes résultat avec dtype=object pour éviter les FutureWarnings
    for semestre in semestres:
        col_final = f"choix_final {semestre}"
        if col_final not in df_etudiants.columns:
            df_etudiants[col_final] = pd.Series([np.nan] * len(df_etudiants), dtype=object)
        else:
            df_etudiants[col_final] = df_etudiants[col_final].astype(object)

    for row in df_etudiants.itertuples(index=True):
        for semestre in semestres:
            choix_final = traiter_etudiant_semestre(
                row=row,
                df_univ=df_univ,
                semestre=semestre,
                limite_ordre=limite_ordre,
                calcul_completion=calcul_completion
            )
            if pd.notna(choix_final):
                df_etudiants.at[row.Index, f"choix_final {semestre}"] = choix_final
                incrementer_places_prise(df_univ, choix_final, semestre)
    return df_etudiants