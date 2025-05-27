import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
from pathlib import Path

from algo_affectation_classement import traitement_scenario_hybride, generer_df_choix_etudiants_spe_compatible, conversion_df_brute_pour_affectation
from excel_en_dataframe import charger_excels

# App setup
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Traitement de 3 fichiers Excel")
app.geometry("600x400")

# Variables pour les chemins
chemins = [None, None, None]
labels = []

def upload_file(index):
    filepath = filedialog.askopenfilename(
        filetypes=[("Fichiers Excel", "*.xlsx *.xls")]
    )
    if filepath:
        chemins[index] = filepath
        nom_fichier = os.path.basename(filepath)
        labels[index].configure(text=nom_fichier)
    verifier_fichiers()

def verifier_fichiers():
    if all(chemins):
        bouton_traiter.configure(state="normal")

# Création des lignes d'upload
for i in range(3):
    frame = ctk.CTkFrame(app)
    frame.pack(pady=10, padx=20, fill="x")

    bouton = ctk.CTkButton(frame, text=f"Choisir fichier Excel Partenaires S{i+8}", command=lambda i=i: upload_file(i))
    bouton.pack(side="left", padx=(10, 10))

    label = ctk.CTkLabel(frame, text="Aucun fichier sélectionné", anchor="w")
    label.pack(side="left", expand=True, fill="x", padx=(10, 10))

    labels.append(label)

def traitement_personnalise():
    try:
        dataframes = charger_excels("src\\main\\data_test")
        dataframes_convertis = conversion_df_brute_pour_affectation(dataframes)
        df_univ = dataframes_convertis["universites_partenaires"]
        df_etu = dataframes_convertis["choix_etudiants"]
        limite_ordre = 3
        df_resultat = traitement_scenario_hybride(df_univ, df_etu, limite_ordre, "Taux" )
        return df_resultat
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def traiter():
    try:
        # Dossier pour les copies
        dossier_upload = Path("src\\main\\data_test")
        dossier_upload.mkdir(exist_ok=True)

        chemins_copies = []

        for i, chemin_source in enumerate(chemins):
            ext = Path(chemin_source).suffix
            chemin_copie = dossier_upload / f"partner_S{i+8}{ext}"
            shutil.copy(chemin_source, chemin_copie)
            chemins_copies.append(str(chemin_copie))

        # Traitement sur les fichiers copiés
        df_resultat = traitement_personnalise()

        # Sauvegarde du fichier généré
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Fichier Excel", "*.xlsx")]
        )
        if save_path:
            df_resultat.to_excel(save_path, index=False)
            messagebox.showinfo("Succès", f"Fichier généré :\n{save_path}")

    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Bouton traiter
bouton_traiter = ctk.CTkButton(app, text="Traiter les fichiers", command=traiter, state="disabled")
bouton_traiter.pack(pady=30)

# Bouton Simulation
bouton_simulation = ctk.CTkButton(app, text="Générer un fichier exemple", command=traiter)
bouton_simulation.pack(pady=30)

app.mainloop()