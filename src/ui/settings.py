# -*- coding: utf-8 -*-
"""
Module de paramètres de SuiviUsagerPro.
Gère l'interface des paramètres de l'application.

Ce module permet de configurer :
- Le thème (clair/sombre)
- Les conseillers (ajout/suppression)
- Les paramètres RGPD (période d'inactivité)
- Les paramètres des ateliers (paiements, types d'ateliers)
"""

import customtkinter as ctk
from tkinter import messagebox
from src.utils.config_utils import (
    get_conseillers,
    add_conseiller,
    remove_conseiller,
    get_current_conseiller,
    set_current_conseiller,
    get_dark_mode,
    set_dark_mode,
    get_inactivity_period,
    set_inactivity_period,
    get_ateliers_entre_paiements,
    set_ateliers_entre_paiements,
    get_default_paid_workshops,
    set_default_paid_workshops
)
from src.utils.theme import set_dark_theme, set_light_theme
from src.ui.add_workshop import WORKSHOP_TYPES, get_workshop_types

class Settings(ctk.CTkFrame):
    """
    Interface des paramètres de l'application.
    Permet de configurer différents aspects de l'application.

    Attributes:
        db_manager: Gestionnaire de base de données
        main_window: Fenêtre principale de l'application
        dark_mode_var: Variable pour le mode sombre
        inactivity_period_var: Variable pour la période d'inactivité
        ateliers_var: Variable pour le nombre d'ateliers entre paiements
        paid_workshops_var: Variable pour les types d'ateliers payants
    """

    def __init__(self, master, db_manager, main_window, **kwargs):
        """
        Initialise l'interface des paramètres.

        Args:
            master: Widget parent
            db_manager: Instance du gestionnaire de base de données
            main_window: Instance de la fenêtre principale
            **kwargs: Arguments supplémentaires pour le Frame
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.main_window = main_window
        
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre
        self.title = ctk.CTkLabel(
            self,
            text="Paramètres",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Frame principal des paramètres
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        # Section des paramètres généraux
        self.create_general_settings()
        
        # Section de gestion des conseillers
        self.create_conseiller_settings()
        
        # Section des paramètres RGPD
        self.create_rgpd_settings()
        
        # Section des paramètres des ateliers
        self.create_workshop_settings()

        # Bouton de sauvegarde
        self.save_button = ctk.CTkButton(self.settings_frame, text="Sauvegarder", command=self.save_settings)
        self.save_button.grid(row=10, column=0, padx=20, pady=(20, 10), sticky="ew")

    def create_general_settings(self):
        """Configure la section des paramètres généraux (mode sombre)."""
        self.other_settings_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Paramètres", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.other_settings_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Switch du mode sombre
        is_dark = get_dark_mode()
        self.dark_mode_var = ctk.StringVar(value="on" if is_dark else "off")
        self.dark_mode_switch = ctk.CTkSwitch(
            self.settings_frame, 
            text="Activer le mode sombre",
            variable=self.dark_mode_var,
            command=self.toggle_dark_mode,
            onvalue="on",
            offvalue="off"
        )
        self.dark_mode_switch.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.dark_mode_switch.select() if is_dark else self.dark_mode_switch.deselect()

    def create_conseiller_settings(self):
        """Configure la section de gestion des conseillers."""
        self.conseillers_label = ctk.CTkLabel(
            self.settings_frame, 
            text="Gestion des conseillers",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.conseillers_label.grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")

        # Boutons d'ajout et de suppression
        self.add_conseiller_button = ctk.CTkButton(
            self.settings_frame,
            text="Ajouter un conseiller",
            command=self.add_conseiller
        )
        self.add_conseiller_button.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.remove_conseiller_button = ctk.CTkButton(
            self.settings_frame,
            text="Supprimer un conseiller",
            command=self.remove_conseiller
        )
        self.remove_conseiller_button.grid(row=4, column=0, padx=20, pady=10, sticky="w")

    def create_rgpd_settings(self):
        """Configure la section des paramètres RGPD."""
        self.rgpd_label = ctk.CTkLabel(
            self.settings_frame,
            text="Paramètre RGPD",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.rgpd_label.grid(row=5, column=0, padx=20, pady=(20, 10), sticky="w")

        # Frame pour la période d'inactivité
        self.inactivity_frame = ctk.CTkFrame(self.settings_frame)
        self.inactivity_frame.grid(row=6, column=0, padx=20, pady=10, sticky="ew")
        self.inactivity_frame.grid_columnconfigure(1, weight=1)

        self.inactivity_period_label = ctk.CTkLabel(
            self.inactivity_frame,
            text="Période d'inactivité :"
        )
        self.inactivity_period_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")

        # Menu déroulant pour la période d'inactivité
        self.inactivity_period_var = ctk.StringVar(value=get_inactivity_period())
        self.inactivity_period_menu = ctk.CTkOptionMenu(
            self.inactivity_frame,
            values=["12", "18", "24", "30", "36"],
            variable=self.inactivity_period_var,
            command=self.update_inactivity_period
        )
        self.inactivity_period_menu.grid(row=0, column=1, padx=0, pady=0, sticky="e")

    def create_workshop_settings(self):
        """Configure la section des paramètres des ateliers."""
        self.ateliers_settings_label = ctk.CTkLabel(
            self.settings_frame,
            text="Paramètres des ateliers",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.ateliers_settings_label.grid(row=7, column=0, padx=20, pady=(20, 10), sticky="w")

        # Frame pour le nombre d'ateliers entre paiements
        self.ateliers_frame = ctk.CTkFrame(self.settings_frame)
        self.ateliers_frame.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.ateliers_frame.grid_columnconfigure(1, weight=1)

        self.ateliers_label = ctk.CTkLabel(
            self.ateliers_frame,
            text="Nombre d'ateliers entre chaque paiement :"
        )
        self.ateliers_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")

        # Menu déroulant pour le nombre d'ateliers
        self.ateliers_var = ctk.StringVar(value=str(get_ateliers_entre_paiements()))
        self.ateliers_dropdown = ctk.CTkOptionMenu(
            self.ateliers_frame,
            variable=self.ateliers_var,
            values=[str(i) for i in range(1, 11)]
        )
        self.ateliers_dropdown.grid(row=0, column=1, padx=0, pady=0, sticky="ew")

        # Frame pour les types d'ateliers payants
        self.paid_workshops_frame = ctk.CTkFrame(self.settings_frame)
        self.paid_workshops_frame.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
        self.paid_workshops_frame.grid_columnconfigure(1, weight=1)

        self.paid_workshops_label = ctk.CTkLabel(
            self.paid_workshops_frame,
            text="Types d'ateliers payants par défaut :"
        )
        self.paid_workshops_label.grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")

        # Menu déroulant pour les types d'ateliers
        self.paid_workshops_var = ctk.StringVar(value=", ".join(get_default_paid_workshops()))
        self.paid_workshops_dropdown = ctk.CTkOptionMenu(
            self.paid_workshops_frame,
            variable=self.paid_workshops_var,
            values=get_workshop_types()
        )
        self.paid_workshops_dropdown.grid(row=0, column=1, padx=0, pady=0, sticky="ew")

    def toggle_dark_mode(self):
        """Active ou désactive le mode sombre et met à jour l'interface."""
        is_dark = self.dark_mode_var.get() == "on"
        set_dark_mode(is_dark)
        if is_dark:
            set_dark_theme()
        else:
            set_light_theme()
        self.main_window.update_appearance()
        self.update()

    def add_conseiller(self):
        """
        Ajoute un nouveau conseiller.
        Affiche une boîte de dialogue pour saisir le nom du conseiller.
        """
        new_name = ctk.CTkInputDialog(
            text="Entrez le nom du nouveau conseiller :",
            title="Ajouter un conseiller"
        ).get_input()
        
        if new_name:
            add_conseiller(new_name)
            self.main_window.update_conseiller_dropdown()
            messagebox.showinfo("Succès", f"Le conseiller {new_name} a été ajouté.")
        else:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide. Aucun conseiller n'a été ajouté.")

    def remove_conseiller(self):
        """
        Supprime un conseiller existant.
        Affiche une boîte de dialogue pour sélectionner le conseiller à supprimer.
        """
        conseillers = get_conseillers()
        if not conseillers:
            messagebox.showerror("Erreur", "Il n'y a aucun conseiller à supprimer.")
            return
        
        to_remove = ctk.CTkInputDialog(
            text="Entrez le nom du conseiller à supprimer :",
            title="Supprimer un conseiller"
        ).get_input()
        
        if to_remove in conseillers:
            remove_conseiller(to_remove)
            self.main_window.update_conseiller_dropdown()
            messagebox.showinfo("Succès", f"Le conseiller {to_remove} a été supprimé.")
        else:
            messagebox.showerror("Erreur", f"Le conseiller {to_remove} n'existe pas.")

    def update_inactivity_period(self, choice):
        """
        Met à jour la période d'inactivité.
        
        Args:
            choice (str): Nouvelle période d'inactivité en mois
        """
        set_inactivity_period(int(choice))

    def update_appearance(self):
        """Met à jour l'apparence de tous les widgets selon le thème actuel."""
        is_dark = get_dark_mode()
        
        # Mise à jour récursive de tous les widgets
        for widget in self.winfo_children():
            self.update_widget_appearance(widget, is_dark)
        
        for widget in self.settings_frame.winfo_children():
            self.update_widget_appearance(widget, is_dark)
        
        # Mise à jour du switch de mode sombre
        self.dark_mode_switch.select() if is_dark else self.dark_mode_switch.deselect()
        
        self.update()

    def update_widget_appearance(self, widget, is_dark):
        """
        Met à jour l'apparence d'un widget et de ses enfants.
        
        Args:
            widget: Widget à mettre à jour
            is_dark (bool): True si le mode sombre est actif
        """
        if isinstance(widget, ctk.CTkBaseClass):
            # Définition des couleurs selon le thème
            if is_dark:
                fg_color = "gray20"
                text_color = "white"
            else:
                fg_color = "gray90"
                text_color = "black"
            
            # Application des couleurs selon le type de widget
            if isinstance(widget, (ctk.CTkButton, ctk.CTkEntry, ctk.CTkOptionMenu)):
                widget.configure(fg_color=fg_color, text_color=text_color)
            elif isinstance(widget, ctk.CTkLabel):
                widget.configure(text_color=text_color)
            elif isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=fg_color)
            
            # Mise à jour récursive des widgets enfants
            for child_widget in widget.winfo_children():
                self.update_widget_appearance(child_widget, is_dark)

    def save_settings(self):
        """Sauvegarde tous les paramètres modifiés."""
        # Sauvegarde du nombre d'ateliers entre paiements
        ateliers = int(self.ateliers_var.get())
        set_ateliers_entre_paiements(ateliers)
        
        # Sauvegarde des types d'ateliers payants
        paid_workshops = [self.paid_workshops_var.get()]
        set_default_paid_workshops(paid_workshops)
        
        messagebox.showinfo("Succès", "Les paramètres ont été sauvegardés avec succès.")
