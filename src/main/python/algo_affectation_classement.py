import logging
import random
import pandas as pd
import numpy as np

# Configuration de base du logging
import logging

# Logger général
logger_general = logging.getLogger('general')
logger_general.setLevel(logging.INFO)
fh_general = logging.FileHandler('log.txt', mode='w')
fh_general.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_general.addHandler(fh_general)

# Logger spécifique pour le taux
logger_debug = logging.getLogger('taux')
logger_debug.setLevel(logging.DEBUG)
fh_taux = logging.FileHandler('log_debug.txt', mode='w')
fh_taux.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger_debug.addHandler(fh_taux)


import pandas as pd
import random

def generer_df_choix_etudiants_spe_compatible(n, df_univ, proba_un_seul_semestre=0.3):
    """
    Génère un DataFrame contenant les choix d'université de n étudiants répartis selon les quotas
    des spécialités, avec une note aléatoire et des choix compatibles pour les semestres S8 et S9.
    Une certaine proportion d'étudiants ne fait de choix que pour un semestre (selon la probabilité spécifiée).

    Paramètres :
    ------------
    n : int
        Le nombre total d'étudiants.
    df_univ : pd.DataFrame
        Le DataFrame des universités avec les colonnes 'Specialite', 'Semestre', 'Nom'.
    proba_un_seul_semestre : float (entre 0 et 1)
        Probabilité qu'un étudiant ne fasse des vœux que pour un seul semestre.

    Retour :
    --------
    pd.DataFrame trié par note décroissante avec :
        - Id Etudiant
        - Specialite
        - Note
        - Choix S8
        - Choix S9
    """
    if n < 1:
        raise ValueError("Le nombre d'étudiants doit être au moins 1.")

    taille_groupe_spe = {"MM":40, "MC":20, "SNI":20, "BAT":40, "EIT":20, "IDU":20}
    liste_semestre = ["S8", "S9"]

    total_defini = sum(taille_groupe_spe.values())
    effectifs_par_spe = {spe: round(taille_groupe_spe[spe] / total_defini * n) for spe in taille_groupe_spe}

    data = {
        "Id Etudiant": [],
        "Specialite": [],
        "Note": [],
        "Choix S8": [],
        "Choix S9": [],
    }

    id_etudiant = 1
    for spe, nb_etudiants in effectifs_par_spe.items():
        for _ in range(nb_etudiants):
            data["Id Etudiant"].append(id_etudiant)
            data["Specialite"].append(spe)
            note = round(random.uniform(0, 20), 2)
            data["Note"].append(note)

            # Décider si l'étudiant fait des voeux pour un ou deux semestres
            fait_un_seul_semestre = random.random() < proba_un_seul_semestre
            if fait_un_seul_semestre:
                semestre_choisi = random.choice(liste_semestre)
            else:
                semestre_choisi = None  # signifie les deux

            for semestre in liste_semestre:
                if fait_un_seul_semestre and semestre != semestre_choisi:
                    data[f"Choix {semestre}"].append("")
                else:
                    liste_univ_compatibles = get_liste_univ_compatible(df_univ, semestre, spe)
                    if not liste_univ_compatibles:
                        choix = ""
                    else:
                        nb_choix = min(5, len(liste_univ_compatibles))
                        choix = "; ".join(random.sample(liste_univ_compatibles, nb_choix))
                    data[f"Choix {semestre}"].append(choix)

            id_etudiant += 1

    df_etudiants = pd.DataFrame(data)
    df_etudiants.sort_values(by="Note", ascending=False, inplace=True)
    df_etudiants.reset_index(drop=True, inplace=True)

    return df_etudiants


def semestre_est_valide(semestre:str, liste_semestres:list[str]=["S8", "S9"]):
    """Vérifie que le semestre en entré est dans la liste liste_semestre.
    
    Args:
        semestre: Le semestre à vérifier
        liste_semestres: Une liste de semestres valides

    Returns:
        bool: True si le semestre est valide
        bool: False si le semestre n'est pas valide
    """    
    if type(semestre) != str:
        raise TypeError("Le semestre doit être un str")
    return semestre in liste_semestres 

def get_nombre_places_total(df:pd.DataFrame, nom_du_partenaire:str, semestre:str) -> int | None:
    """Retourne le nombre de places pour l'université correspondante.
    
    Args:
        df: Le dataframe des universités partenaires
        nom_du_partenaire: Le nom de l'université

    Returns:
        val: Le nombre de place affichés à la ligne pour le code univ correspondant
    """

    if not semestre_est_valide(semestre):
        return None
    places = df.loc[df["nom_partenaire"] == nom_du_partenaire, "Places "+str(semestre)]
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
    places = df.loc[df["nom_partenaire"] == nom_du_partenaire, "Places Prises "+str(semestre)]
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
    mask = df_univ["nom_partenaire"] == nom_du_partenaire

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

def comparaison_taux_completion_prio_non_prio(df_univ):
    res = []
    semestre = "S8"
    liste_univs = df_univ["nom_partenaire"].tolist()
    liste_prio, liste_non_prio = scinder_liste_univ_par_prio(df_univ, liste_univs, semestre)
    taux_moyen_prio = 0
    taux_moyen_non_prio = 0
    for univ in liste_prio:
       taux_moyen_prio += get_taux_completion_places(df_univ, univ, semestre)
    for univ in liste_non_prio:
       taux_moyen_non_prio += get_taux_completion_places(df_univ, univ, semestre)

    taux_moyen_prio = taux_moyen_prio/len(liste_prio)
    taux_moyen_non_prio = taux_moyen_non_prio/len(liste_non_prio)
    print(f"taux_moyen_prio : {taux_moyen_prio}")
    print(f"taux_moyen_non_prio : {taux_moyen_non_prio}")

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
    return df_univ.loc[mask, "nom_partenaire"].tolist()

def get_depuis_df_univ_prioritaire_avec_place_niveau_spe(df_univ:pd.DataFrame, note_etudiant:int, semestre:str, specialite:str, calcul_completion:str="Taux"):
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
        res = get_depuis_liste_univ_prioritaire_avec_place_et_niveau(df_univ, liste_univ_compatibles, note_etudiant, semestre, calcul_completion)
    else:
        logger_debug.debug(f"Aucune univ compatible pour {note_etudiant}")
    return res

def scinder_liste_univ_par_prio(df_univ, liste_choix, semestre): 
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
        ligne = df_univ[df_univ["nom_partenaire"] == nom]
        if not ligne.empty:
            prioritaire = ligne.iloc[0][f"Prioritaire {semestre}"]
            if isinstance(prioritaire, str) and prioritaire.strip().lower() == "oui":
                liste_prioritaires.append(nom)
            else:
                liste_non_prioritaires.append(nom)

    return liste_prioritaires, liste_non_prioritaires

def get_depuis_liste_univs_avec_place(df_univ:pd.DataFrame, liste_univs:list[str], semestre:str) -> list:
    """Retourne une liste d'universités qui ont des places disponibles.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        liste_univs: La liste des univs à traiter
        semestre: Le semestre choisi en str.

    Returns:
        res: une liste d'universités qui ont des places disponibles ou une liste vide.
    """
    univs_disponibles = []
    for nom_du_partenaire in liste_univs:
        if place_est_disponible(df_univ, nom_du_partenaire, semestre):
            univs_disponibles.append(nom_du_partenaire)
    return univs_disponibles

def get_depuis_liste_univs_au_niveau(df_univ:pd.DataFrame, liste_univs:list, note_etudiant:int, semestre:str):
    univs_au_niveau = []
    for nom_du_partenaire in liste_univs:
        if etudiant_a_niveau_requis(df_univ, note_etudiant, nom_du_partenaire, semestre):
            univs_au_niveau.append(nom_du_partenaire)
    return univs_au_niveau

def get_depuis_liste_univ_prioritaire_avec_place_et_niveau(df_univ:pd.DataFrame, liste_choix:tuple|list, note_etudiant:int, semestre:str, calcul_completion:str="Taux"):
    """Retourne le nom de l'université qui est la moins remplie de la liste fournie en considérant d'abord les univ prioritaire.
    
    Args:
        df_univ: Le dataframe des universités partenaires.
        choix: une liste ou tuple des partenaires
        note_etudiant: la note de l'étudiant
        semestre: Le semestre choisi en str.

    Returns:
        res: le nom de l'université qui est la moins remplie de la liste fournie en considérant d'abord les univ prioritaire ou une chaine vide si aucune ne correspond.
    """

    res = ""
    liste_univs_avec_place = get_depuis_liste_univs_avec_place(df_univ, liste_choix, semestre)
    liste_univs_au_niveau = get_depuis_liste_univs_au_niveau(df_univ, liste_univs_avec_place, note_etudiant, semestre)
    univ_prioritaires, univ_non_prioritaires = scinder_liste_univ_par_prio(df_univ, liste_univs_au_niveau, semestre)

    univ_prio_la_moins_remplie = get_universite_la_moins_remplie(df_univ, univ_prioritaires, semestre, calcul_completion)
    if univ_prio_la_moins_remplie != "":
        res = univ_prio_la_moins_remplie
    else:
        logger_debug.debug(f"pas de place disponible dans les univ prio pour note = {note_etudiant}")
        univ_non_prio_la_moins_remplie = get_universite_la_moins_remplie(df_univ, univ_non_prioritaires, semestre, calcul_completion)
        if univ_non_prio_la_moins_remplie != "":
            res = univ_non_prio_la_moins_remplie
        else:
            logger_debug.debug(f"pas de places dispo dans les univ non prio pour etudiant {note_etudiant}")
    return res

def etudiant_a_niveau_requis(df_univ:pd.DataFrame, note_etudiant:float, nom_du_partenaire:str, semestre:str):
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
    note_min_univ = df_univ.loc[df_univ["nom_partenaire"] == nom_du_partenaire, "Note Min "+str(semestre)]
    note_min_valeur = note_min_univ.values[0] if not note_min_univ.empty else None
    if note_min_valeur is not None and not pd.isna(note_min_valeur) and note_min_valeur > note_etudiant:
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
        logger_debug.debug(f"{id_etudiant} n'a pas fait de choix pour le {semestre}")
        return np.nan

    # Scénario 1 : Voeux ordonnés
    for i, choix in enumerate(tuple_choix[:limite_ordre]):
        if place_est_disponible(df_univ, choix, semestre) and etudiant_a_niveau_requis(df_univ, note_etudiant, choix, semestre):
            logger_general.info(f"{id_etudiant} obtient le choix {choix} (ordre {i+1}) pour le {semestre}")
            return choix
        else:
            logger_general.info(f"{id_etudiant} n'obtient pas le choix {choix} pour {semestre} dans scénario 1")
            logger_debug.debug(f"{id_etudiant} n'obtient pas le choix {choix} pour {semestre} dans scénario 1")

    # Scénario 2 : Choix restants
    choix_restants = tuple_choix[limite_ordre:]
    if choix_restants:
        univ_choisie = get_depuis_liste_univ_prioritaire_avec_place_et_niveau(df_univ, choix_restants, note_etudiant, semestre, calcul_completion)
        if univ_choisie != "":
            logger_general.info(f"{id_etudiant} obtient {univ_choisie} via les choix non ordonnés pour {semestre}")
            return univ_choisie
        else:
            logger_general.info(f"{id_etudiant} n'obtient pas un des choix pour {semestre} dans scénario 2")

    # Scénario 3 : Aucune des options précédentes
    specialite = getattr(row, "Specialite", None)

    univ_fallback = get_depuis_df_univ_prioritaire_avec_place_niveau_spe(df_univ, note_etudiant, semestre, specialite, calcul_completion)
    if univ_fallback != "":
        logger_general.info(f"{id_etudiant} affecté par fallback à {univ_fallback} pour {semestre}")
        return univ_fallback
    
    logger_general.info(f"Aucune attribution possible pour {id_etudiant} au {semestre}")
    return np.nan

def tri_df_etudiant_semestre_ponderation(df_etudiants:pd.DataFrame, alpha=0.05):
    """Retourne un df des étudiants trié selon la priorité calculée.
    
    Args:
        df_etudiants: Le dataframe des choix des étudiants
        alpha: Le coefficient de pénalité, entre 0 et 1, plus il est élevé, plus les doubles choix de mobilité perdent des places dans le nouveau classement.

    Returns:
        df_res: le df des étudiants trié selon la priorité calculée.
    """    

    total_etudiants = len(df_etudiants)

    # Calcul du rang basé sur l'index (commençant à 1 pour que le major ait rang = 1)
    df_etudiants['Rang'] = df_etudiants.index + 1

    # Calcul du nombre de semestres demandés
    df_etudiants['Nb_semestres_demandes'] = df_etudiants[['Choix S8', 'Choix S9']].apply(
        lambda row: int(bool(row['Choix S8'])) + int(bool(row['Choix S9'])),
        axis=1
    )

    # Calcul de la priorité
    df_etudiants['Priorite'] = (df_etudiants['Rang'] / total_etudiants) + alpha * (df_etudiants['Nb_semestres_demandes'] - 1)

    # Ajout d'un index original (optionnel ici car rang = index + 1)
    df_etudiants['Index_original'] = df_etudiants.index

    # Tri final
    df_etudiants_sorted = df_etudiants.sort_values(by=['Priorite', 'Index_original'], ascending=[True, True])

    return df_etudiants_sorted


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