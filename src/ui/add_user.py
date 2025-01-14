"""
Module de gestion de l'interface d'ajout d'un nouvel utilisateur.
Fournit un formulaire pour créer un nouvel utilisateur dans le système.
"""

import customtkinter as ctk
from tkinter import messagebox
from src.models.user import User
from src.utils.date_utils import convert_to_db_date, is_valid_date

class AddUser(ctk.CTkFrame):
    """
    Frame permettant l'ajout d'un nouvel utilisateur via un formulaire.
    Gère la validation des champs obligatoires et la création en base de données.
    """
    
    def __init__(self, master, db_manager, update_callback, **kwargs):
        """
        Initialise l'interface d'ajout d'utilisateur.
        
        Args:
            master: Widget parent
            db_manager: Gestionnaire de base de données
            update_callback: Fonction de mise à jour après création
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.update_callback = update_callback

        # Configuration de la grille principale avec poids pour le redimensionnement
        self.grid_columnconfigure(0, weight=1)
        for i in range(8):  # Pour toutes les lignes du formulaire
            self.grid_rowconfigure(i, weight=0)
        self.grid_rowconfigure(1, weight=1)  # La ligne du formulaire peut s'étendre

        # Titre
        self.title = ctk.CTkLabel(self, text="Ajouter un usager", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Formulaire d'ajout d'usager avec configuration responsive
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Configuration de la grille du formulaire pour le redimensionnement
        self.form_frame.grid_columnconfigure(0, weight=1)  # Colonne des labels
        self.form_frame.grid_columnconfigure(1, weight=3)  # Colonne des champs de saisie
        for i in range(8):  # Pour toutes les lignes du formulaire
            self.form_frame.grid_rowconfigure(i, weight=1)
        
        # Création des champs du formulaire
        self.nom_entry = self.create_form_field(self.form_frame, "Nom *", 0)
        self.prenom_entry = self.create_form_field(self.form_frame, "Prénom *", 1)
        self.telephone_entry = self.create_form_field(self.form_frame, "Numéro de téléphone *", 2)
        self.date_naissance_entry = self.create_form_field(self.form_frame, "Date de naissance", 3)
        self.email_entry = self.create_form_field(self.form_frame, "Mail", 4)
        self.adresse_entry = self.create_form_field(self.form_frame, "Adresse postale", 5)

        # Bouton de soumission
        self.submit_button = ctk.CTkButton(self.form_frame, text="Valider la création du nouvel utilisateur", command=self.add_user)
        self.submit_button.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        # Note pour les champs obligatoires
        self.obligatory_note = ctk.CTkLabel(self.form_frame, text="* obligatoire", font=ctk.CTkFont(size=12, slant="italic"))
        self.obligatory_note.grid(row=7, column=1, padx=20, pady=(0, 10), sticky="e")

    def create_form_field(self, parent, label, row):
        """
        Crée un champ de formulaire avec son label.
        
        Args:
            parent: Widget parent
            label: Texte du label
            row: Numéro de ligne dans la grille
        
        Returns:
            CTkEntry: Le widget de saisie créé
        """
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        return entry

    def add_user(self):
        """
        Valide et enregistre un nouvel utilisateur.
        Vérifie les champs obligatoires avant la création.
        Nettoie le formulaire après succès.
        """
        nom = self.nom_entry.get()
        prenom = self.prenom_entry.get()
        date_naissance = convert_to_db_date(self.date_naissance_entry.get())
        telephone = self.telephone_entry.get()
        email = self.email_entry.get()
        adresse = self.adresse_entry.get()

        if not nom or not prenom or not telephone:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return

        new_user = User(nom=nom, prenom=prenom, telephone=telephone, date_naissance=date_naissance, email=email, adresse=adresse)
        new_user.save(self.db_manager)
        
        messagebox.showinfo("Succès", "L'usager a été ajouté avec succès.")
        self.clear_form()
        self.update_callback()

    def clear_fields(self):
        """
        Vide tous les champs du formulaire individuellement.
        Méthode alternative à clear_form.
        """
        self.nom_entry.delete(0, 'end')
        self.prenom_entry.delete(0, 'end')
        self.date_naissance_entry.delete(0, 'end')
        self.telephone_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.adresse_entry.delete(0, 'end')

    def clear_form(self):
        """
        Vide tous les champs du formulaire en une seule opération.
        Méthode préférée pour réinitialiser le formulaire.
        """
        for entry in [self.nom_entry, self.prenom_entry, self.telephone_entry, 
                      self.date_naissance_entry, self.email_entry, self.adresse_entry]:
            entry.delete(0, 'end')
