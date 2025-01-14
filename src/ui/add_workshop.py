# -*- coding: utf-8 -*-
"""
Module d'ajout d'atelier de SuiviUsagerPro.
Gère l'interface d'ajout d'un nouvel atelier pour un usager.

Ce module permet de :
- Créer un nouvel atelier pour un usager
- Gérer les informations de l'atelier (date, type, conseiller)
- Gérer le statut de paiement
- Ajouter une description détaillée
"""

import customtkinter as ctk
from tkinter import messagebox
from src.models.workshop import Workshop
from src.utils.date_utils import is_valid_date, convert_to_db_date, get_current_date
from src.config import get_current_conseiller
from src.models.user import User
import logging
from src.utils.config_utils import get_default_paid_workshops

def get_workshop_types():
    """
    Retourne la liste des types d'ateliers disponibles.
    
    Returns:
        list: Liste des types d'ateliers
    """
    return ["Atelier numérique", "Démarche administrative"]

class AddWorkshop(ctk.CTkFrame):
    """
    Interface d'ajout d'un nouvel atelier.
    Permet de créer un atelier pour un usager spécifique.

    Attributes:
        db_manager: Gestionnaire de base de données
        user: Usager pour lequel l'atelier est créé
        show_user_edit_callback: Fonction de retour à l'édition de l'usager
        update_callback: Fonction de mise à jour de l'interface
        default_paid_workshops: Liste des types d'ateliers payants par défaut
        workshop_type_var: Variable pour le type d'atelier
        paid_var: Variable pour le statut de paiement
    """

    def __init__(self, master, db_manager, user, show_user_edit_callback, update_callback):
        """
        Initialise l'interface d'ajout d'atelier.

        Args:
            master: Widget parent
            db_manager: Instance du gestionnaire de base de données
            user: Instance de l'usager
            show_user_edit_callback: Fonction pour revenir à l'édition de l'usager
            update_callback: Fonction pour mettre à jour l'interface
        """
        logging.debug(f"Initialisation de AddWorkshop avec user: {user}")
        super().__init__(master)
        self.db_manager = db_manager
        self.user = user
        self.show_user_edit_callback = show_user_edit_callback
        self.update_callback = update_callback
        self.default_paid_workshops = get_default_paid_workshops()

        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Création de l'interface
        self.create_title()
        self.create_form()
        self.create_payment_section()
        self.create_description_section()
        self.create_buttons()

        # Initialisation du statut de paiement
        self.user.calculate_workshop_payment_status(self.db_manager)
        self.update_payment_status()

    def create_title(self):
        """Crée le titre de la section avec le nom de l'usager."""
        self.title = ctk.CTkLabel(
            self, 
            text=f"Ajouter un atelier pour {self.user.nom} {self.user.prenom}",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

    def create_form(self):
        """Crée le formulaire principal avec les champs de base."""
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure((0, 1), weight=1)
        self.form_frame.grid_rowconfigure(4, weight=1)

        # Champs du formulaire avec valeurs par défaut
        current_date = get_current_date()
        current_conseiller = get_current_conseiller()

        self.date_entry = self.create_form_field(self.form_frame, "Date *", 0, current_date)
        self.create_workshop_type_dropdown(self.form_frame, "Type d'atelier *", 1)
        self.conseiller_entry = self.create_form_field(self.form_frame, "Conseiller *", 2, current_conseiller)

    def create_payment_section(self):
        """Crée la section de gestion du paiement."""
        self.paid_var = ctk.BooleanVar(value=False)
        
        # Frame pour le paiement
        self.payment_frame = ctk.CTkFrame(self.form_frame)
        self.payment_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")
        self.payment_frame.grid_columnconfigure(1, weight=1)

        # Statut de paiement
        self.payment_status_label = ctk.CTkLabel(self.payment_frame, text="Statut de paiement : ")
        self.payment_status_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
        self.payment_status_value = ctk.CTkLabel(self.payment_frame, text="")
        self.payment_status_value.grid(row=0, column=1, padx=(0, 10), pady=0, sticky="w")

        # Case à cocher pour le paiement
        self.paid_checkbox = ctk.CTkCheckBox(
            self.payment_frame,
            text="Payé",
            variable=self.paid_var,
            command=self.update_payment_status
        )
        self.paid_checkbox.grid(row=0, column=2, padx=(10, 0), pady=0, sticky="e")

    def create_description_section(self):
        """Crée la section de description de l'atelier."""
        ctk.CTkLabel(self.form_frame, text="Description").grid(
            row=4, column=0, padx=20, pady=(10, 0), sticky="nw"
        )
        self.description_entry = ctk.CTkTextbox(self.form_frame, height=100)
        self.description_entry.grid(
            row=4, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="nsew"
        )

    def create_buttons(self):
        """Crée les boutons d'action (Ajouter et Retour)."""
        self.button_frame = ctk.CTkFrame(self.form_frame)
        self.button_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Bouton d'ajout
        self.submit_button = ctk.CTkButton(
            self.button_frame,
            text="Ajouter l'atelier",
            command=self.add_workshop
        )
        self.submit_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Bouton de retour
        self.back_button = ctk.CTkButton(
            self.button_frame,
            text="Retour",
            command=self.show_user_edit_callback
        )
        self.back_button.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def create_form_field(self, parent, label, row, default_value=""):
        """
        Crée un champ de formulaire avec label et entrée.

        Args:
            parent: Widget parent
            label (str): Texte du label
            row (int): Numéro de ligne dans la grille
            default_value (str): Valeur par défaut du champ

        Returns:
            CTkEntry: Widget d'entrée créé
        """
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")
        entry.insert(0, default_value)
        return entry

    def create_workshop_type_dropdown(self, parent, label, row):
        """
        Crée un menu déroulant pour le type d'atelier.

        Args:
            parent: Widget parent
            label (str): Texte du label
            row (int): Numéro de ligne dans la grille
        """
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, padx=20, pady=(10, 0), sticky="w")
        self.workshop_type_var = ctk.StringVar(value=get_workshop_types()[0])
        workshop_type_dropdown = ctk.CTkOptionMenu(
            parent,
            variable=self.workshop_type_var,
            values=get_workshop_types()
        )
        workshop_type_dropdown.grid(row=row, column=1, padx=20, pady=(10, 0), sticky="ew")

    def add_workshop(self):
        """
        Ajoute un nouvel atelier à la base de données.
        Vérifie les champs obligatoires et met à jour le statut de paiement.
        
        Returns:
            bool: True si l'atelier a été ajouté avec succès, False sinon
        """
        logging.debug("=== Début de la méthode add_workshop ===")
        
        # Récupération des données du formulaire
        date = convert_to_db_date(self.date_entry.get())
        categorie = self.workshop_type_var.get()
        conseiller = self.conseiller_entry.get()
        is_paid_type = categorie in self.default_paid_workshops
        paid = self.paid_var.get()
        description = self.description_entry.get("1.0", "end-1c")
        
        logging.debug(f"Données du formulaire : date={date}, categorie={categorie}, conseiller={conseiller}, payant={is_paid_type}, payé={paid}")

        # Validation des champs obligatoires
        if not date or not categorie or not conseiller:
            logging.warning("Champs obligatoires manquants")
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires.")
            return False

        # Création et sauvegarde de l'atelier
        try:
            logging.debug("Création du nouvel atelier...")
            new_workshop = Workshop(
                user_id=self.user.id,
                date=date,
                categorie=categorie,
                conseiller=conseiller,
                payant=is_paid_type,
                paid=paid,
                description=description
            )
            new_workshop.save(self.db_manager)
            logging.debug("Atelier sauvegardé avec succès dans la base de données")

            # Mise à jour du statut de paiement si nécessaire
            if paid:
                logging.debug("Mise à jour de la date de dernier paiement")
                self.user.update_last_payment_date(self.db_manager)
            self.user.calculate_workshop_payment_status(self.db_manager)
            self.user.notify_observers('user_updated', self.user)
            logging.debug("Statut de paiement mis à jour")

            messagebox.showinfo("Succès", "L'atelier a été ajouté avec succès.")
            
            # Stocker le callback avant la destruction
            logging.debug("Stockage du callback")
            edit_callback = self.show_user_edit_callback
            
            # Destruction de cette frame
            logging.debug("Destruction de la frame AddWorkshop")
            self.destroy()
            
            # Appeler le callback d'édition utilisateur
            logging.debug("Appel du callback d'édition utilisateur")
            if edit_callback:
                edit_callback()
            
            logging.debug("=== Fin de la méthode add_workshop avec succès ===")    
            return True

        except Exception as e:
            logging.error(f"Erreur lors de l'ajout de l'atelier : {str(e)}", exc_info=True)
            messagebox.showerror("Erreur", f"Impossible d'ajouter l'atelier : {str(e)}")
            return False

    def update_payment_status(self):
        """Met à jour l'affichage du statut de paiement."""
        status = self.user.get_workshop_payment_status(self.db_manager)
        self.payment_status_value.configure(text=status)

# Types d'ateliers disponibles
WORKSHOP_TYPES = ["Atelier numérique", "Démarche administrative"]
