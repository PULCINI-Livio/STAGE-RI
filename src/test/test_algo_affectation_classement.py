import sys
import os

# Ajoute le dossier 'src' au PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from algo_affectation_classement import (
    get_nombre_places_total,
    get_nombre_places_prises,
    place_est_disponible,
    incrementer_places_prise,
    get_nb_places_disponibles,
    get_taux_completion_places,
    get_universite_la_moins_remplie,
    get_liste_univ_compatible,
    get_univ_compatible_la_moins_remplie,
)
import pandas as pd

liste_specialite = ['MM', 'MMT', 'SNI', 'BAT', 'EIT', 'IDU', 'ESB', 'AM']
dataframe_univ = pd.DataFrame({
    "NOM DU PARTENAIRE": ["AAAA","BBBB"],
    "Places S8": [8, 10],
    "Places Prises S8": [1, 1],
    "Specialites Compatibles S8": [['MM', 'IDU'], ['MM', 'MMT', 'BAT', 'EIT', 'ESB', 'AM']],
    "Places S9": [0, 10],
    "Places Prises S9": [0, 10],
    "Specialites Compatibles S9": [liste_specialite, liste_specialite],
    "Places S10": [None, 100],
    "Places Prises S10": [0, 10],
    "Specialites Compatibles S10": [liste_specialite, liste_specialite]
})

def test_get_nombre_places_total():
    assert get_nombre_places_total(dataframe_univ, "AAAA", "S8") == 8
    assert get_nombre_places_total(dataframe_univ, "AAAA", "S9") == 0
    assert get_nombre_places_total(dataframe_univ, "AAAA", "S10") == None
    assert get_nombre_places_total(dataframe_univ, "", "S10") == None
    assert get_nombre_places_total(dataframe_univ, "", "") == None
    assert get_nombre_places_total(dataframe_univ, "AAAA", "") == None

def test_get_nombre_places_prises():
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S8") == 1
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "S9") == 0
    assert get_nombre_places_prises(dataframe_univ, "", "S9") == None
    assert get_nombre_places_prises(dataframe_univ, "AAAA", "") == None
    assert get_nombre_places_prises(dataframe_univ, "", "") == None

def test_place_est_disponible():
    assert place_est_disponible(dataframe_univ, "BBBB", "S8") == True
    assert place_est_disponible(dataframe_univ, "BBBB", "S9") == False
    assert place_est_disponible(dataframe_univ, "", "S9") == None
    assert place_est_disponible(dataframe_univ, "BBBB", "") == None
    assert place_est_disponible(dataframe_univ, "", "") == None

def test_incrementer_places_prise():
    dataframe_univ_bis = dataframe_univ.copy(deep=True)
    incrementer_places_prise(dataframe_univ_bis, "AAAA", "S8")
    assert get_nombre_places_prises(dataframe_univ_bis, "AAAA", "S8") == 2
    incrementer_places_prise(dataframe_univ_bis, "", "S8")
    assert get_nombre_places_prises(dataframe_univ_bis, "AAAA", "S8") == 2
    incrementer_places_prise(dataframe_univ_bis, "AAAA", "")
    assert get_nombre_places_prises(dataframe_univ_bis, "AAAA", "S8") == 2
    incrementer_places_prise(dataframe_univ_bis, "", "")
    assert get_nombre_places_prises(dataframe_univ_bis, "AAAA", "S8") == 2

def test_get_nb_places_disponibles():
    assert get_nb_places_disponibles(dataframe_univ, "AAAA", "S8") == 7
    assert get_nb_places_disponibles(dataframe_univ, "AAAA", "S10") == None
    assert get_nb_places_disponibles(dataframe_univ, "AAAA", "") == None
    assert get_nb_places_disponibles(dataframe_univ, "", "S10") == None
    assert get_nb_places_disponibles(dataframe_univ, "", "") == None

def test_get_taux_completion_places():
    assert get_taux_completion_places(dataframe_univ, "BBBB", "S10") == 0.1
    assert get_taux_completion_places(dataframe_univ, "AAAA", "S9") == 1
    assert get_taux_completion_places(dataframe_univ, "AAAA", "") == None
    assert get_taux_completion_places(dataframe_univ, "", "S9") == None
    assert get_taux_completion_places(dataframe_univ, "", "") == None

def test_get_universite_la_moins_remplie():
    assert get_universite_la_moins_remplie(
        dataframe_univ, 
        ("AAAA", "BBBB"), 
        "S8", 
        "Taux"
        ) == "BBBB"
    
    assert get_universite_la_moins_remplie(
        dataframe_univ, 
        ("AAAA", "BBBB"), 
        "S9", 
        "Taux"
        ) == "AAAA"
    
    assert get_universite_la_moins_remplie(
        dataframe_univ, 
        ("BBBB", "AAAA"), 
        "S9", 
        "Taux"
        ) == "BBBB"
    
def test_get_liste_univ_compatible():
    assert get_liste_univ_compatible(dataframe_univ, "S8", "IDU") == ["AAAA"]
    assert get_liste_univ_compatible(dataframe_univ, "S8", "SNI") == []
    assert get_liste_univ_compatible(dataframe_univ, "S9", "IDU") == ["AAAA","BBBB"]

def test_get_univ_compatible_la_moins_remplie():
    assert get_univ_compatible_la_moins_remplie(dataframe_univ, "S8", "MM", "Taux") == "BBBB"
    assert get_univ_compatible_la_moins_remplie(dataframe_univ, "S8", "SNI", "Taux") == ""