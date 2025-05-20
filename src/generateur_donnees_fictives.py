import random
import pandas as pd
import numpy as np
import string

def generer_dataframe_univ(n):
    """
    Génère un DataFrame contenant les codes universités et le nombre de places disponibles
    pour trois semestres (S8, S9, S10).

    Paramètres :
    ------------
    n : int
        Le nombre de lignes (universités) à générer. Limité à 26 (A à Z).

    Retour :
    --------
    DataFrame pandas avec les colonnes :
        - Code Univ : identifiant type AAAA, BBBB, etc.
        - Nombre de places S8 : entier entre 0 et 10
        - Nombre de places S9 : entier entre 0 et 10
        - Nombre de places S10 : entier entre 0 et 10
    """
    if n > 26:
        raise ValueError("Le nombre de lignes ne peut pas dépasser 26 (limité à une lettre répétée pour le Code Univ).")
    
    # Générer les codes univ : AAAA, BBBB, CCCC, etc.
    codes_univ = [char * 4 for char in string.ascii_uppercase[:n]]
    
    # Générer les données aléatoires pour chaque semestre
    places_s8 = np.random.randint(1, 11, size=n)
    places_s9 = np.random.randint(1, 11, size=n)
    places_s10 = np.random.randint(1, 11, size=n)

    # Créer le DataFrame
    df = pd.DataFrame({
        'Code Univ': codes_univ,
        'Nombre de places S8': places_s8,
        'Nombre de places S9': places_s9,
        'Nombre de places S10': places_s10
    })
    
    return df



def generer_df_choix_etudiants(n):
    """
    Génère un DataFrame contenant les choix d'université de n étudiants pour trois semestres.

    Paramètres :
    ------------
    n : int
        Le nombre d'étudiants (et donc de lignes du DataFrame).

    Retour :
    --------
    DataFrame pandas avec les colonnes :
        - Id Etudiant : identifiant numérique (1 à n)
        - Choix S8 : 5 codes Univ (ex: "AAAA, ZZZZ, BBBB, DDDD, GGGG")
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
    
    # Codes Univ fixes (AAAA à ZZZZ)
    codes_univ = [char * 4 for char in string.ascii_uppercase]  # 26 codes

    data = {
        "Id Etudiant": [],
        "Choix S8": [],
        "Choix S9": [],
        "Choix S10": []
    }

    for i in range(1, n + 1):
        data["Id Etudiant"].append(i)
        
        for semestre in ["Choix S8", "Choix S9", "Choix S10"]:
            choix = random.sample(codes_univ, 5)  # 5 codes différents, ordre aléatoire
            data[semestre].append(", ".join(choix))

    return pd.DataFrame(data)

#print(generer_dataframe_univ(26).head())
