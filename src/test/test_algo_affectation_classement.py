import pandas as pd
import numpy as np
import pytest
import sys
import os

# Ajoute le dossier 'src' au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from algo_affectation_classement import (
    semestre_est_valide,
    get_nombre_places_total,
    get_nombre_places_prises,
    place_est_disponible,
    incrementer_places_prise,
    get_nb_places_disponibles,
    get_taux_completion_places,
    get_universite_la_moins_remplie,
    get_liste_univ_compatible,
    get_depuis_df_univ_prioritaire_avec_place_niveau_spe,
    scinder_liste_univ_par_prio,
    get_depuis_df_univs_avec_place,
    get_depuis_liste_univs_au_niveau,
    get_depuis_liste_univ_prioritaire_avec_place_et_niveau,
    etudiant_a_niveau_requis
)

def test_semestre_est_valide():
    assert semestre_est_valide("S8", ["S8", "S9"]) is True
    assert semestre_est_valide("S9", ["S8", "S9"]) is True
    assert semestre_est_valide("S10", ["S8", "S9"]) is False
    assert semestre_est_valide("S8") is True
    assert semestre_est_valide("S9") is True
    assert semestre_est_valide("S10") is False
    with pytest.raises(TypeError):
        semestre_est_valide(1, ["S8", "S9"])  # appel avec un type invalide
    with pytest.raises(TypeError):
        semestre_est_valide(1)  # appel avec un type invalide

def test_get_nombre_places_total():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Places S8": [1],
        "Places Prises S8": [1],
        "Places S9": [0],
        "Places Prises S9": [1],
    })
    assert get_nombre_places_total(dataframe_univ, "AAAA", "S8") == 1
    assert get_nombre_places_total(dataframe_univ, "AAAA", "S9") == 0
    assert get_nombre_places_total(dataframe_univ, "", "S8") == None
    assert get_nombre_places_total(dataframe_univ, "", "") == None
    assert get_nombre_places_total(dataframe_univ, "AAAA", "") == None

def test_get_nombre_places_prises():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Places S8": [1],
        "Places Prises S8": [1],
        "Places S9": [0],
        "Places Prises S9": [0],
    })
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S8") == 1
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S9") == 0
    assert get_nombre_places_prises(dataframe_univ, "", "S9") == None
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "") == None
    assert get_nombre_places_prises(dataframe_univ, "", "") == None

def test_place_est_disponible():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Places S8": [2],
        "Places Prises S8": [1],
        "Places S9": [1],
        "Places Prises S9": [1],
    })
    assert place_est_disponible(dataframe_univ, "AAAA", "S8") is True
    assert place_est_disponible(dataframe_univ, "AAAA", "S9") is False
    assert place_est_disponible(dataframe_univ, "", "S9") == None
    assert place_est_disponible(dataframe_univ, "AAAA", "") == None
    assert place_est_disponible(dataframe_univ, "", "") == None

def test_incrementer_places_prise():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Places S8": [2],
        "Places Prises S8": [1],
        "Places S9": [1],
        "Places Prises S9": [1],
    })
    incrementer_places_prise(dataframe_univ, "AAAA", "S8")
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S8") == 2
    incrementer_places_prise(dataframe_univ, "", "S8")
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S8") == 2
    incrementer_places_prise(dataframe_univ, "AAAA", "")
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S8") == 2
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S9") == 1
    incrementer_places_prise(dataframe_univ, "", "")
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S8") == 2
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S9") == 1

def test_get_nb_places_disponibles():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Places S8": [2],
        "Places Prises S8": [1],
        "Places S9": [1],
        "Places Prises S9": [1],
    })
    assert get_nb_places_disponibles(dataframe_univ, "AAAA", "S8") == 1
    assert get_nb_places_disponibles(dataframe_univ, "AAAA", "S9") == 0
    assert get_nb_places_disponibles(dataframe_univ, "AAAA", "") == None
    assert get_nb_places_disponibles(dataframe_univ, "", "S8") == None
    assert get_nb_places_disponibles(dataframe_univ, "", "") == None

def test_get_taux_completion_places():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Places S8": [2],
        "Places Prises S8": [1],
        "Places S9": [1],
        "Places Prises S9": [1],
    })
    assert get_taux_completion_places(dataframe_univ, "AAAA", "S8") == 0.5
    assert get_taux_completion_places(dataframe_univ, "AAAA", "S9") == 1
    assert get_taux_completion_places(dataframe_univ, "AAAA", "") == None
    assert get_taux_completion_places(dataframe_univ, "", "S9") == None
    assert get_taux_completion_places(dataframe_univ, "", "") == None

def test_get_universite_la_moins_remplie():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA", "BBBB"],
        "Places S8": [2, 10],
        "Places Prises S8": [1, 2],
        "Places S9": [1, 1],
        "Places Prises S9": [1, 1],
    })
    assert get_universite_la_moins_remplie(dataframe_univ, ("AAAA", "BBBB"), "S8", "Taux") == "BBBB"
    assert get_universite_la_moins_remplie(dataframe_univ, ("AAAA", "BBBB"), "S8", "Places Prises") == "AAAA"
    assert get_universite_la_moins_remplie(dataframe_univ, ("AAAA", "BBBB"), "S9", "Taux") == "AAAA"

def test_get_liste_univ_compatible():
    liste_specialite = ['MM', 'MMT', 'SNI', 'BAT', 'EIT', 'IDU', 'ESB', 'AM']
    liste_specialite_sans_IDU = ['MM', 'MMT', 'SNI', 'BAT', 'EIT', 'ESB', 'AM']
    liste_specialite_sans_SNI = ['MM', 'MMT', 'BAT', 'EIT', 'IDU', 'ESB', 'AM']
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA","BBBB"],
        "Places S8": [8, 10],
        "Places Prises S8": [1, 1],
        "Specialites Compatibles S8": [liste_specialite, liste_specialite_sans_IDU],
        "Places S9": [8, 10],
        "Places Prises S9": [1, 1],
        "Specialites Compatibles S9": [liste_specialite_sans_SNI, liste_specialite_sans_SNI]
    })
    
    assert get_liste_univ_compatible(dataframe_univ, "S8", "IDU") == ["AAAA"]
    assert get_liste_univ_compatible(dataframe_univ, "S9", "SNI") == []
    assert get_liste_univ_compatible(dataframe_univ, "S9", "IDU") == ["AAAA","BBBB"]

def test_etudiant_a_niveau_requis():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA"],
        "Note Min S8": [16],
        "Note Min S9": [np.nan],
    })
    assert etudiant_a_niveau_requis(dataframe_univ, note_etudiant=18, nom_du_partenaire="AAAA", semestre="S8" ) is True
    assert etudiant_a_niveau_requis(dataframe_univ, note_etudiant=16, nom_du_partenaire="AAAA", semestre="S8" ) is True
    assert etudiant_a_niveau_requis(dataframe_univ, note_etudiant=10, nom_du_partenaire="AAAA", semestre="S8" ) is False
    assert etudiant_a_niveau_requis(dataframe_univ, note_etudiant=0, nom_du_partenaire="AAAA", semestre="S9" ) is True
    assert etudiant_a_niveau_requis(dataframe_univ, note_etudiant=18, nom_du_partenaire="AAAA", semestre="S9" ) is True

def test_get_depuis_liste_univs_au_niveau():
    liste_univs = ["AAAA", "BBBB", "CCCC"]  
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": liste_univs,
        "Note Min S8": [18, 16, np.nan],
        "Note Min S9": [np.nan, np.nan, np.nan],
    })
    assert get_depuis_liste_univs_au_niveau(dataframe_univ, liste_univs, note_etudiant=18, semestre="S8") == ["AAAA","BBBB","CCCC"]
    assert get_depuis_liste_univs_au_niveau(dataframe_univ, liste_univs, note_etudiant=16, semestre="S8") == ["BBBB","CCCC"]
    assert get_depuis_liste_univs_au_niveau(dataframe_univ, liste_univs, note_etudiant=0, semestre="S8") == ["CCCC"]
    assert get_depuis_liste_univs_au_niveau(dataframe_univ, liste_univs, note_etudiant=18, semestre="S9") == ["AAAA","BBBB","CCCC"]
    assert get_depuis_liste_univs_au_niveau(dataframe_univ, liste_univs, note_etudiant=0, semestre="S9") == ["AAAA","BBBB","CCCC"]

def test_scinder_liste_univ_par_prio():
    liste_univs = ["AAAA", "BBBB", "CCCC", "DDDD"]  
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA", "BBBB", "CCCC", "DDDD"],
        "Prioritaire S8": ["Oui", "Non", "Non", "Non"],
        "Prioritaire S9": ["Non", "Non", "Non", "Non"],
    })
    assert scinder_liste_univ_par_prio(dataframe_univ, liste_univs, semestre="S8") == (["AAAA"], ["BBBB", "CCCC", "DDDD"])
    assert scinder_liste_univ_par_prio(dataframe_univ, liste_univs, semestre="S9") == ([], ["AAAA", "BBBB", "CCCC", "DDDD"])
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA", "BBBB", "CCCC", "DDDD"],
        "Prioritaire S8": ["Oui", "Oui", "Oui", "Oui"],
    })
    assert scinder_liste_univ_par_prio(dataframe_univ, liste_univs, semestre="S8") == (["AAAA", "BBBB", "CCCC", "DDDD"], [])

def test_get_depuis_df_univs_avec_place():
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA","BBBB"],
        "Places S8": [1, 2],
        "Places Prises S8": [0, 1],
        "Places S9": [2, 2],
        "Places Prises S9": [1, 2],
    })
    assert get_depuis_df_univs_avec_place(dataframe_univ, semestre="S8") == ["AAAA","BBBB"]
    assert get_depuis_df_univs_avec_place(dataframe_univ, semestre="S9") == ["AAAA"]
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": ["AAAA","BBBB"],
        "Places S8": [1, 1],
        "Places Prises S8": [1, 1],
        "Places S9": [0, 0],
        "Places Prises S9": [0, 0],
    })
    assert get_depuis_df_univs_avec_place(dataframe_univ, semestre="S8") == []
    assert get_depuis_df_univs_avec_place(dataframe_univ, semestre="S9") == []

def test_get_depuis_liste_univ_prioritaire_avec_place_et_niveau():
    liste_univs = ["AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH"]
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": liste_univs,
        "Places S8": [2, 2, 2, 2, 2, 2, 2, 2],
        "Places Prises S8": [0, 0, 0, 2, 2, 0, 2, 2],
        "Prioritaire S8": ["Oui", "Oui", "Non", "Oui", "Non", "Non", "Oui" , "Non"],
        "Note Min S8": [18, 16, 10, np.nan, 10, 18, 18, 18],
    })
    assert get_depuis_liste_univ_prioritaire_avec_place_et_niveau(
        dataframe_univ, 
        liste_choix=liste_univs, 
        note_etudiant=16, 
        semestre="S8", 
        calcul_completion="Taux") == "BBBB"
    
    assert get_depuis_liste_univ_prioritaire_avec_place_et_niveau(
        dataframe_univ, 
        liste_choix=liste_univs, 
        note_etudiant=18, 
        semestre="S8", 
        calcul_completion="Taux") == "AAAA"

    assert get_depuis_liste_univ_prioritaire_avec_place_et_niveau(
        dataframe_univ, 
        liste_choix=liste_univs, 
        note_etudiant=10, 
        semestre="S8", 
        calcul_completion="Taux") == "CCCC"

def test_get_depuis_df_univ_prioritaire_avec_place_niveau_spe():
    liste_univs = ["AAAA", "BBBB", "CCCC", "DDDD", "EEEE", "FFFF", "GGGG", "HHHH"]
    liste_specialite = ['MM', 'MMT', 'SNI', 'BAT', 'EIT', 'IDU', 'ESB', 'AM']
    liste_specialite_sans_IDU = ['MM', 'MMT', 'SNI', 'BAT', 'EIT', 'ESB', 'AM']
    dataframe_univ = pd.DataFrame({
        "NOM DU PARTENAIRE": liste_univs,
        "Places S8": [2, 2, 2, 2, 2, 2, 2, 2],
        "Places Prises S8": [0, 0, 0, 2, 2, 0, 2, 0],
        "Specialites Compatibles S8": [liste_specialite] * 7 + [liste_specialite_sans_IDU],
        "Prioritaire S8": ["Oui", "Oui", "Non", "Oui", "Non", "Non", "Oui" , "Non"],
        "Note Min S8": [18, 16, 10, np.nan, 10, 18, 18, 18],
    })
    
    assert get_depuis_df_univ_prioritaire_avec_place_niveau_spe(
        dataframe_univ, 
        note_etudiant=16, 
        semestre="S8", 
        specialite="IDU",
        calcul_completion="Taux") == "BBBB"
    
    assert get_depuis_df_univ_prioritaire_avec_place_niveau_spe(
        dataframe_univ, 
        note_etudiant=18, 
        semestre="S8", 
        specialite="IDU",
        calcul_completion="Taux") == "AAAA"

    assert get_depuis_df_univ_prioritaire_avec_place_niveau_spe(
        dataframe_univ, 
        note_etudiant=10, 
        semestre="S8", 
        specialite="IDU",
        calcul_completion="Taux") == "CCCC"