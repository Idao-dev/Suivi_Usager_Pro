# -*- coding: utf-8 -*-
"""
Module d'édition d'atelier de SuiviUsagerPro.
Gère l'interface de modification d'un atelier existant.

Ce module permet de :
- Modifier les informations d'un atelier existant
- Gérer le statut de paiement
- Mettre à jour la description
- Suivre l'historique des modifications
"""

import customtkinter as ctk
from tkinter import messagebox
from src.models.workshop import Workshop
from src.models.user import User
from src.utils.date_utils import convert_to_db_date, convert_from_db_date
import logging

class EditWorkshop(ctk.CTkFrame):
    """
    Interface d'édition d'un atelier existant.
    Permet de modifier toutes les informations d'un atelier.

    Attributes:
        db_manager: Gestionnaire de base de données
        workshop: Atelier à modifier
        update_callback: Fonction de mise à jour de l'interface
        show_previous_page_callback: Fonction de retour à la page précédente
        payant_original: État initial du statut payant de l'atelier
        user: Usager associé à l'atelier
        paid_var: Variable pour le statut de paiement
    """

    def __init__(self, master, db_manager, workshop, update_callback, show_previous_page_callback, **kwargs):
        """
        Initialise l'interface d'édition d'atelier.

        Args:
            master: Widget parent
            db_manager: Instance du gestionnaire de base de données
            workshop: Instance de l'atelier à modifier
            update_callback: Fonction pour mettre à jour l'interface
            show_previous_page_callback: Fonction pour revenir à la page précédente
            **kwargs: Arguments supplémentaires pour le Frame
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.workshop = workshop
        self.update_callback = update_callback
        self.show_previous_page_callback = show_previous_page_callback
        self.payant_original = workshop.payant

        # Récupération de l'usager associé
        self.user = User.get_by_id(self.db_manager, self.workshop.user_id)
        if self.user:
            self.user.calculate_workshop_payment_status(self.db_manager)

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
        self.update_payment_status()

    def create_title(self):
        """Crée le titre de la section."""
        self.title = ctk.CTkLabel(
            self, 
            text="Éditer l'atelier",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

    def create_form(self):
        """Crée le formulaire principal avec les champs de base."""
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.form_frame.grid_columnconfigure((0, 1), weight=1)

        # Champs du formulaire avec les valeurs actuelles
        self.date_entry = self.create_form_field(
            self.form_frame, "Date", 0,
            convert_from_db_date(self.workshop.date)
        )
        self.categorie_entry = self.create_form_field(
            self.form_frame, "Catégorie", 1,
            self.workshop.categorie
        )
        self.conseiller_entry = self.create_form_field(
            self.form_frame, "Conseiller", 2,
            self.workshop.conseiller
        )

    def create_payment_section(self):
        """Crée la section de gestion du paiement."""
        self.paid_var = ctk.BooleanVar(value=self.workshop.paid)
        
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
        self.description_entry.insert("1.0", self.workshop.description)

    def create_buttons(self):
        """Crée les boutons d'action (Mettre à jour et Retour)."""
        self.button_frame = ctk.CTkFrame(self.form_frame)
        self.button_frame.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        # Bouton de mise à jour
        self.submit_button = ctk.CTkButton(
            self.button_frame,
            text="Mettre à jour l'atelier",
            command=self.update_workshop
        )
        self.submit_button.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        # Bouton de retour
        self.back_button = ctk.CTkButton(
            self.button_frame,
            text="Retour",
            command=self.show_previous_page_callback
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

    def update_workshop(self):
        """
        Met à jour l'atelier dans la base de données.
        Gère également la mise à jour du statut de paiement de l'usager.
        """
        # Sauvegarde de l'ancien statut de paiement
        old_paid = self.workshop.paid

        # Mise à jour des données de l'atelier
        self.workshop.date = convert_to_db_date(self.date_entry.get())
        self.workshop.categorie = self.categorie_entry.get()
        self.workshop.conseiller = self.conseiller_entry.get()
        self.workshop.paid = self.paid_var.get()
        self.workshop.description = self.description_entry.get("1.0", "end-1c")

        try:
            # Sauvegarde des modifications
            self.workshop.save(self.db_manager)
            
            # Mise à jour du statut de paiement de l'usager si nécessaire
            user = User.get_by_id(self.db_manager, self.workshop.user_id)
            if user:
                if self.workshop.paid != old_paid:
                    user.update_last_payment_date(self.db_manager)
                user.update_payment_status(self.db_manager)

            messagebox.showinfo("Succès", "L'atelier a été mis à jour avec succès.")
            
            # Mise à jour de l'interface
            self.update_callback()
            self.update_payment_status()

        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de mettre à jour l'atelier : {str(e)}")

    def update_payment_status(self):
        """Met à jour l'affichage du statut de paiement."""
        if self.user:
            status = self.user.get_workshop_payment_status(self.db_manager)
            self.payment_status_value.configure(text=status)
