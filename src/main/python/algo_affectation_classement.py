import logging
import random
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

from excel_en_dataframe import charger_excels
from conversion_df_brute import conversion_df_brute_pour_affectation

# Configuration de base du logging
logging.basicConfig(
    filename='log.txt',                # Fichier de sortie
    filemode='a',                      # Mode 'a' = append (évite d’écraser)
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO                 # Niveau minimal des messages (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)


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
        - Choix S10 (ou None)
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
        #print(str(nom_du_partenaire) + " " + semestre + " est vide, on retourne None")
        return None
    val = places.iloc[0]
    if pd.isna(val):
        #print(str(nom_du_partenaire) + " " + semestre + " isna, on retourne None")
        return None
    #print(str(nom_du_partenaire) + " " + semestre + " est bon avec " + str(int(places)) + " places")
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
    if get_nb_places_disponibles(df_univ, nom_du_partenaire, semestre) > 0:
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
    res = 0
    nb_places_total = get_nombre_places_total(df_univ, nom_du_partenaire, semestre)
    nb_places_prises = get_nombre_places_prises(df_univ, nom_du_partenaire, semestre)
    if nb_places_total is not None and nb_places_prises is not None:
        res = nb_places_total-nb_places_prises
    return res

def get_taux_completion_places(df_univ:pd.DataFrame, nom_du_partenaire:str, semestre:str):
    res = 1.0
    nb_places_prises = get_nombre_places_prises(df_univ, nom_du_partenaire, semestre)
    nb_places_total = get_nombre_places_total(df_univ, nom_du_partenaire, semestre)
    if nb_places_total is not None and nb_places_total != 0:
        res = nb_places_prises/nb_places_total
    return res

def convertir_colonne_en_tuple(df:pd.DataFrame, colonne:str):
    """convertit toutes les valeurs d'un colonne d'un df en tuple
    
    Args:
        df: Le dataframe à traiter
        colonne: La colonne à traiter

    """
    df[colonne] = df[colonne].apply(lambda x: tuple(map(str.strip, x.split(";"))) if pd.notna(x) else x)

def get_universite_la_moins_remplie(df_univ:pd.DataFrame, choix:tuple|list, semestre:str, calcul_completion:str="Taux") -> str:
    """Retourne un str correspondant à l'université la moins remplie selon la méthode de calcul. Si elles sont toutes remplies, la première de la liste|tuple est renvoyée.
    
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
    
    col = f"Specialites Compatibles {semestre}"
    mask = df_univ[col].apply(lambda lst: specialite in lst if isinstance(lst, list) else False)
    return df_univ.loc[mask, "NOM DU PARTENAIRE"].tolist()

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

def traiter_etudiant_semestre(row, df_univ, semestre, limite_ordre, calcul_completion):
    # Préparer un mapping dynamique des noms
    col_choix = f"Choix_{semestre}"
    id_etudiant = getattr(row, "Id_Etudiant", None)
    tuple_choix = getattr(row, col_choix, None)

    if not tuple_choix or not isinstance(tuple_choix, tuple):
        logging.info(f"{id_etudiant} n'a pas fait de choix pour le {semestre}")
        return np.nan

    # Scénario 1 : Voeux ordonnés
    for i, choix in enumerate(tuple_choix[:limite_ordre]):
        if place_est_disponible(df_univ, choix, semestre):
            logging.info(f"{id_etudiant} obtient le choix {choix} (ordre {i+1}) pour le {semestre}")
            return choix

    # Scénario 2 : Choix restants
    choix_restants = tuple_choix[limite_ordre:]
    if choix_restants:
        if len(choix_restants) == 1:
            univ_choisie = choix_restants[0]
        else:
            univ_choisie = get_universite_la_moins_remplie(df_univ, choix_restants, semestre, calcul_completion)
        if place_est_disponible(df_univ, univ_choisie, semestre):
            logging.info(f"{id_etudiant} obtient {univ_choisie} via les choix non ordonnés pour {semestre}")
            return univ_choisie

    # Scénario 3 : Aucune des options précédentes
    specialite = getattr(row, "Specialite", None)
    univ_fallback = get_univ_compatible_la_moins_remplie(df_univ, semestre, specialite, calcul_completion)
    if place_est_disponible(df_univ, univ_fallback, semestre):
        logging.info(f"{id_etudiant} affecté par fallback à {univ_fallback} pour {semestre}")
        return univ_fallback

    logging.info(f"Aucune attribution possible pour {id_etudiant} au {semestre}")
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
    semestres = ["S8", "S9", "S10"]

    # Convertir les colonnes de choix en tuples
    for semestre in semestres:
        convertir_colonne_en_tuple(df_etudiants, f"Choix {semestre}")
        logging.info(f"Conversion colonne Choix {semestre} en tuple réussie")

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


###############################################

test = False

if test:
    nb_etudiants = 400
    proba_unique_semestre = 0.7
    start = time.time()

    dataframes = charger_excels("src\\main\\data")

    df_univ = conversion_df_brute_pour_affectation(dataframes)["universites_partenaires"]
    df_etu_fictif = generer_df_choix_etudiants_spe_compatible(nb_etudiants, df_univ, proba_unique_semestre)
    df_final = traitement_scenario_hybride(df_univ, df_etu_fictif, 3, "Taux" )
    end = time.time()
    df_etu_fictif.to_excel("statistics\\df_etu_fictif.xlsx") 
    df_univ.to_excel("statistics\\df_univ.xlsx") 
    df_final.to_excel("statistics\\df_final.xlsx") 
    print(f"Temps d'exécution : {end - start:.2f} secondes pour " + str(nb_etudiants) + " etudiant et un proba de faire un unique semestre de "  + str(proba_unique_semestre))

benchmark = False
if benchmark:
    # Paramètres du benchmark
    taille_echantillons = [20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200, 250, 300, 350, 400]
    temps_execution = []

    for nb_etudiants in taille_echantillons:
        print(f"Test avec {nb_etudiants} étudiants...")
        
        # Chargement des données de base
        dataframes = charger_excels("src\\main\\data")
        df_univ = conversion_df_brute_pour_affectation(dataframes)["universites_partenaires"]

        # Génération des étudiants fictifs
        df_etu_fictif = generer_df_choix_etudiants_spe_compatible(nb_etudiants, df_univ)

        # Exécution avec mesure de temps
        start = time.time()
        df_univ_copy = df_univ.copy()
        df_etu_copy = df_etu_fictif.copy()
        df_final = traitement_scenario_hybride(df_univ_copy, df_etu_copy, 3, "Taux")
        end = time.time()

        # Sauvegarde
        temps = round(end - start, 2)
        temps_execution.append(temps)
        print(f"  → Temps : {temps} sec")

    # Résultats sous forme de DataFrame
    df_benchmark = pd.DataFrame({
        "nb_etudiants": taille_echantillons,
        "temps_execution": temps_execution
    })

    # Sauvegarde des résultats
    df_benchmark.to_excel("statistics\\benchmark_affectation.xlsx", index=False)

    # Affichage de la courbe
    plt.figure(figsize=(10, 6))
    plt.plot(df_benchmark["nb_etudiants"], df_benchmark["temps_execution"], marker='o')
    plt.title("Temps d'exécution en fonction du nombre d'étudiants")
    plt.xlabel("Nombre d'étudiants")
    plt.ylabel("Temps d'exécution (secondes)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("courbe_temps_affectation.png")
    plt.show()
