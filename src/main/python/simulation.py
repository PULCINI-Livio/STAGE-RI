import time

from algo_affectation_classement import traitement_scenario_hybride, generer_df_choix_etudiants_spe_compatible, comparaison_taux_completion_prio_non_prio, tri_df_etudiant_semestre_ponderation 
from conversion_df_brute import conversion_df_brute_pour_affectation
from excel_en_dataframe import charger_excels

dataframes = charger_excels("src\\main\\data")
df_univ = conversion_df_brute_pour_affectation(dataframes)["universites_partenaires"]

df_etu_fictif = generer_df_choix_etudiants_spe_compatible(200, df_univ, proba_un_seul_semestre=0.2)
#df_etu_fictif = conversion_df_brute_pour_affectation(dataframes)["choix_etudiants"]

df_etu_fictif.to_excel("src\\main\\output\\df_etu_fictif.xlsx", index=False)
df_etu_fictif = tri_df_etudiant_semestre_ponderation(df_etu_fictif, alpha=0.1)
df_final = traitement_scenario_hybride(df_univ, df_etu_fictif, limite_ordre=1)
df_univ.to_excel("src\\main\\output\\df_univ.xlsx", index=False)
df_final.to_excel("src\\main\\output\\df_etu_fictif_final.xlsx", index=False)
comparaison_taux_completion_prio_non_prio(df_univ)

###########################################
test = False
if test:
    nb_etudiants = 150
    proba_unique_semestre = 0.0
    start = time.time()
    limite_ordre = 0
    dataframes = charger_excels("src\\main\\data")

    df_univ = conversion_df_brute_pour_affectation(dataframes)["universites_partenaires"]
    #df_etu_fictif = generer_df_choix_etudiants_spe_compatible(nb_etudiants, df_univ, proba_unique_semestre)
    df_etu_fictif = conversion_df_brute_pour_affectation(dataframes)["choix_etudiants"]
    df_etu_fictif.to_excel("statistics\\df_etu_fictif.xlsx")
    df_final = traitement_scenario_hybride(df_univ, df_etu_fictif, limite_ordre, "Taux" )
    end = time.time()
    df_etu_fictif.to_excel("statistics\\df_etu_fictif_final.xlsx") 
    df_univ.to_excel("statistics\\df_univ.xlsx") 
    df_final.to_excel("statistics\\df_final.xlsx") 
    print(f"Temps d'exécution : {end - start:.2f} secondes pour " + str(nb_etudiants) + " etudiant et un proba de faire un unique semestre de "  + str(proba_unique_semestre) + " et une limite d'ordre de " + str(limite_ordre))

