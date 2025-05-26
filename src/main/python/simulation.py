import time
import pandas as pd
import matplotlib.pyplot as plt

from algo_affectation_classement import traitement_scenario_hybride, generer_df_choix_etudiants_spe_compatible, conversion_df_brute_pour_affectation
from excel_en_dataframe import charger_excels

nb_etudiants = 400
proba_unique_semestre = 0.5
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
