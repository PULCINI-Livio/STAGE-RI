import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import shutil
from pathlib import Path

from src.main.python.algo_affectation_classement import tri_df_etudiant_semestre_ponderation, traitement_scenario_hybride
from src.main.python.conversion_df_brute import conversion_df_brute_pour_affectation
from src.main.python.excel_en_dataframe import charger_excels

# App setup
ctk.set_appearance_mode("System")
#ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Algorithme D'affectation")
app.geometry("800x500")
app.resizable(False, False)

# Nettoyage du dossier data au démarrage
dossier_data_test = Path("src/main/data")
if dossier_data_test.exists():
    for f in dossier_data_test.iterdir():
        if f.is_file():
            f.unlink()

# Variables
chemins = [None, None]  # [0] univ, [1] étudiants
labels = []

def upload_file(index):
    filepath = filedialog.askopenfilename(filetypes=[("Fichiers Excel", "*.xlsx *.xls")])
    if filepath:
        chemins[index] = filepath
        nom_fichier = os.path.basename(filepath)
        labels[index].configure(text=nom_fichier)
    verifier_fichiers()

def verifier_fichiers():
    if all(chemins):
        bouton_traiter.configure(state="normal")

def telecharger_fichier_exemple(nom_fichier_source):
    try:
        dossier_source = Path("src/main/data_exemple")
        chemin_source = dossier_source / nom_fichier_source

        save_path = filedialog.asksaveasfilename(
            initialfile=nom_fichier_source,
            defaultextension=".xlsx",
            filetypes=[("Fichier Excel", "*.xlsx")]
        )
        if save_path:
            shutil.copy(chemin_source, save_path)
            messagebox.showinfo("Téléchargement", f"Fichier enregistré :\n{save_path}")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# Upload fichiers
frame = ctk.CTkFrame(app)
frame.pack(pady=10, padx=20, fill="x")

# Bouton d’upload fichier université
bouton_univ = ctk.CTkButton(frame, text="Choisir fichier Universités", command=lambda: upload_file(0))
bouton_univ.pack(side="left", padx=(10, 5))

# Bouton de téléchargement du fichier exemple université
btn_dl_univ = ctk.CTkButton(frame, text="Télécharger exemple", command=lambda: telecharger_fichier_exemple("univ_data_mobility_exemple.xlsx"))
btn_dl_univ.pack(side="left", padx=(5, 10))


label = ctk.CTkLabel(frame, text="Aucun fichier sélectionné", anchor="w")
label.pack(side="left", expand=True, fill="x", padx=(10, 10))

labels.append(label)


frame2 = ctk.CTkFrame(app)
frame2.pack(pady=10, padx=20, fill="x")

# Bouton d’upload fichier étudiant
bouton_etu = ctk.CTkButton(frame2, text="Choisir fichier Étudiants", command=lambda: upload_file(1))
bouton_etu.pack(side="left", padx=(10, 5))

# Bouton de téléchargement du fichier exemple étudiant
btn_dl_etu = ctk.CTkButton(frame2, text="Télécharger exemple", command=lambda: telecharger_fichier_exemple("choix_etudiant_exemple.xlsx"))
btn_dl_etu.pack(side="left", padx=(5, 10))

label2 = ctk.CTkLabel(frame2, text="Aucun fichier sélectionné", anchor="w")
label2.pack(side="left", expand=True, fill="x", padx=(10, 10))

labels.append(label2)

label_info = ctk.CTkLabel(
    app,
    text="Pour commencer, charger les fichiers excel 'Universités' et 'Etudiant', des exemples téléchargeables sont disponibles.\nUne fois les fichiers chargés, vous pouvez appuyer sur le bouton 'Traiter les fichiers'.\nVous serez invité à enregistrer le fichier excel qui contient les affectations des étudiants.",
    font=("Arial", 14),
    text_color="gray"
)
label_info.pack(pady=10)
# Sliders

# Variables pour les sliders
alpha_var = ctk.DoubleVar(value=0.05)
limite_ordre_var = ctk.IntVar(value=3)

# Slider Alpha
frame_alpha = ctk.CTkFrame(app)
frame_alpha.pack(pady=10, padx=20, fill="x")

label_alpha = ctk.CTkLabel(frame_alpha, text="Coefficient de pénalité :")
label_alpha.pack(side="left", padx=10)

slider_alpha = ctk.CTkSlider(
    frame_alpha, from_=0.0, to=1.0, number_of_steps=100, variable=alpha_var,
    command=lambda v: alpha_value_label.configure(text=f"{float(v):.2f}")
)
slider_alpha.pack(side="left", expand=True, fill="x", padx=10)

alpha_value_label = ctk.CTkLabel(frame_alpha, text=f"{alpha_var.get():.2f}")
alpha_value_label.pack(side="left", padx=10)


# Slider Limite Ordre
frame_limite = ctk.CTkFrame(app)
frame_limite.pack(pady=10, padx=20, fill="x")

label_limite = ctk.CTkLabel(frame_limite, text="Nombre de voeux ordonnés :")
label_limite.pack(side="left", padx=10)

slider_limite = ctk.CTkSlider(
    frame_limite, from_=1, to=5, number_of_steps=4, variable=limite_ordre_var,
    command=lambda v: limite_value_label.configure(text=f"{int(float(v))}")
)
slider_limite.pack(side="left", expand=True, fill="x", padx=10)

limite_value_label = ctk.CTkLabel(frame_limite, text=f"{limite_ordre_var.get()}")
limite_value_label.pack(side="left", padx=10)

label_info = ctk.CTkLabel(
    app,
    text="Le coefficient de pénalité est entre 0 et 1, plus il est élevé, plus les doubles choix de mobilité\nperdent des places dans le classement.\nNombre de voeux ordonnés définit le nombre de voeux traité selon l'ordre donnés par l'étudiant.\nPassé cette valeur, les voeux seront choisit selon l'importance de l'université et le taux de place prises.",
    font=("Arial", 14),
    text_color="gray"
)
label_info.pack(pady=10)

# Traitement
def traitement_personnalise():
    try:
        alpha = alpha_var.get()
        limite_ordre = limite_ordre_var.get()
        dataframes = charger_excels("src\\main\\data")
        dataframes_convertis = conversion_df_brute_pour_affectation(dataframes)
        df_univ = dataframes_convertis["universites_partenaires"]
        df_etu = dataframes_convertis["choix_etudiants"]
        df_etu = tri_df_etudiant_semestre_ponderation(df_etu, alpha=alpha)
        df_resultat = traitement_scenario_hybride(df_univ, df_etu, limite_ordre, "Taux")
        return df_resultat
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

def traiter():
    try:
        dossier_upload = Path("src\\main\\data")
        dossier_upload.mkdir(exist_ok=True)

        chemins_copies = []
        noms_fichiers = ["univ_data_mobility.xlsx", "choix_etudiants.xlsx"]  # ordre important : [0]=univ, [1]=étudiants

        for i, chemin_source in enumerate(chemins):
            ext = Path(chemin_source).suffix
            chemin_copie = dossier_upload / noms_fichiers[i]
            shutil.copy(chemin_source, chemin_copie)
            chemins_copies.append(str(chemin_copie))

        df_resultat = traitement_personnalise()

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

# Lancement de l'app
app.mainloop()
