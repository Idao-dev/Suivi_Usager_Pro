# -*- coding: utf-8 -*-
"""
Module principal de l'interface graphique de SuiviUsagerPro.
Ce module gère la fenêtre principale de l'application et coordonne tous les composants UI.

Classes:
    MainWindow: Fenêtre principale de l'application qui contient la barre latérale,
                la barre supérieure et le contenu principal.
"""

import logging
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
import os
from PIL import Image
import sys

# Imports locaux - Utils
from src.utils.config_utils import (
    get_dark_mode,
    get_conseillers,
    get_current_conseiller,
    set_current_conseiller,
    add_conseiller
)
from src.utils.theme import set_dark_theme, set_light_theme

# Imports locaux - Database et Models
from src.database.db_manager import DatabaseManager
from src.models.user import User
from src.models.workshop import Workshop

# Imports locaux - UI Components
from .dashboard import Dashboard
from .add_user import AddUser
from .user_management import UserManagement
from .workshop_history import WorkshopHistory
from .settings import Settings
from .data_management import DataManagement
from .user_edit import UserEditFrame
from .add_workshop import AddWorkshop
from .edit_workshop import EditWorkshop

class MainWindow(ctk.CTkFrame):
    """
    Classe principale de l'interface graphique.
    Gère la disposition des éléments et la navigation entre les différentes sections.

    Attributes:
        db_manager (DatabaseManager): Gestionnaire de base de données
        update_callback (function): Fonction de rappel pour mettre à jour l'interface
        current_frame: Frame actuellement affiché
        user_edit: Frame d'édition d'utilisateur
    """

    def __init__(self, master, db_manager, update_callback, **kwargs):
        """
        Initialise la fenêtre principale.

        Args:
            master: Widget parent (root window)
            db_manager: Instance du gestionnaire de base de données
            update_callback: Fonction de rappel pour les mises à jour
            **kwargs: Arguments supplémentaires pour le Frame
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.update_callback = update_callback
        self.current_frame = None
        self.user_edit = None  # Ajoutez cette ligne si elle n'existe pas déjà

        # Initialiser le mode d'apparence
        self.set_initial_appearance()

        # Configuration du layout principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Barre latérale
        self.create_sidebar()

        # Barre supérieure
        self.create_top_bar()

        # Zone de contenu principal
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=1, column=1, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        # Initialiser les différentes sections
        self.dashboard = Dashboard(self.main_content, db_manager=self.db_manager)
        self.add_user = AddUser(self.main_content, db_manager=self.db_manager, update_callback=self.update_all_sections)
        self.user_management = UserManagement(
            self.main_content,
            db_manager=self.db_manager,
            edit_user_callback=self.edit_user,
            edit_workshop_callback=self.show_edit_workshop
        )
        self.workshop_history = WorkshopHistory(self.main_content, db_manager=self.db_manager)
        self.settings = Settings(self.main_content, db_manager=self.db_manager, main_window=self)
        self.data_management = DataManagement(self.main_content, db_manager=self.db_manager, update_callback=self.update_all_sections)

        # Afficher le tableau de bord par défaut
        self.show_dashboard()

        # Configurer les observateurs
        self.setup_observers()

    def set_initial_appearance(self):
        """
        Configure l'apparence initiale de l'application (thème clair/sombre).
        Utilise les préférences sauvegardées dans la configuration.
        """
        is_dark = get_dark_mode()
        if is_dark:
            ctk.set_appearance_mode("dark")
            set_dark_theme()
        else:
            ctk.set_appearance_mode("light")
            set_light_theme()

    def create_sidebar(self):
        """
        Crée la barre latérale avec le logo et les boutons de navigation.
        La barre latérale contient :
        - Logo de l'application
        - Boutons de navigation vers les différentes sections
        - Boutons Paramètres et Discord en bas
        """
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # Espace extensible avant le bouton Paramètres

        # Charger et afficher le logo
        if getattr(sys, 'frozen', False):
            # Si l'application est "gelée" (exécutable)
            logo_path = os.path.join(sys._MEIPASS, "assets", "logo.png")
        else:
            # En développement
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "assets", "logo.png")

        if os.path.exists(logo_path):
            try:
                pil_image = Image.open(logo_path)
                self.logo_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(175, 175))
                self.logo_label = ctk.CTkLabel(self.sidebar, image=self.logo_image, text="")
                self.logo_label.grid(row=0, column=0, padx=0, pady=0)
            except Exception as e:
                logging.error(f"Erreur lors du chargement du logo: {e}")
                self.logo_label = ctk.CTkLabel(self.sidebar, text="SuiviUsagerPro", font=ctk.CTkFont(size=20, weight="bold"))
                self.logo_label.grid(row=0, column=0, padx=0, pady=0)
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar, text="SuiviUsagerPro", font=ctk.CTkFont(size=20, weight="bold"))
            self.logo_label.grid(row=0, column=0, padx=0, pady=0)

        # Création des boutons de navigation
        self.sidebar_button_1 = ctk.CTkButton(self.sidebar, text="Tableau de bord", command=self.show_dashboard)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar, text="Ajouter un usager", command=self.show_add_user)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar, text="Gestion des usagers", command=self.show_user_management)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        self.sidebar_button_4 = ctk.CTkButton(self.sidebar, text="Historique des ateliers", command=self.show_workshop_history)
        self.sidebar_button_4.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_5 = ctk.CTkButton(self.sidebar, text="Gestion des données", command=self.show_data_management)
        self.sidebar_button_5.grid(row=5, column=0, padx=20, pady=10)

        # Boutons du bas
        self.settings_button = ctk.CTkButton(self.sidebar, text="Paramètres", command=self.show_settings)
        self.settings_button.grid(row=7, column=0, padx=20, pady=(0, 20), sticky="s")

        self.discord_button = ctk.CTkButton(self.sidebar, text="Rejoindre Discord", command=self.open_discord)
        self.discord_button.grid(row=8, column=0, padx=20, pady=(0, 20), sticky="s")

    def create_top_bar(self):
        """
        Crée la barre supérieure contenant :
        - Barre de recherche d'usagers
        - Bouton de recherche
        - Menu déroulant de sélection du conseiller
        """
        self.top_bar = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.top_bar.grid(row=0, column=1, sticky="ew")
        self.top_bar.grid_columnconfigure(0, weight=1)

        # Champ de recherche
        self.search_entry = ctk.CTkEntry(self.top_bar, placeholder_text="Rechercher")
        self.search_entry.grid(row=0, column=0, padx=(20, 10), pady=5, sticky="ew")
        self.search_entry.bind("<Return>", self.search_users)

        self.search_button = ctk.CTkButton(self.top_bar, text="Rechercher", command=self.search_users)
        self.search_button.grid(row=0, column=1, padx=(0, 20), pady=5)

        # Gestion des conseillers
        self.conseillers = get_conseillers()
        self.current_conseiller = get_current_conseiller()
        if not self.conseillers:
            self.ask_new_conseiller()
        else:
            self.create_conseiller_dropdown()

    def create_conseiller_dropdown(self):
        self.conseiller_var = ctk.StringVar(value=self.current_conseiller)
        self.conseiller_dropdown = ctk.CTkOptionMenu(
            self.top_bar, 
            values=self.conseillers,
            variable=self.conseiller_var,
            command=self.on_conseiller_change
        )
        self.conseiller_dropdown.grid(row=0, column=2, padx=20, pady=5)

    def ask_new_conseiller(self):
        new_name = ctk.CTkInputDialog(text="Entrez le nom du nouveau conseiller :", title="Ajouter un conseiller").get_input()
        if new_name:
            add_conseiller(new_name)
            self.conseillers = get_conseillers()
            self.current_conseiller = new_name
            set_current_conseiller(new_name)
            self.create_conseiller_dropdown()
        else:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide. Veuillez réessayer.")
            self.after(100, self.ask_new_conseiller)

    def on_conseiller_change(self, choice):
        set_current_conseiller(choice)

    def update_conseiller_dropdown(self):
        self.conseillers = get_conseillers()
        self.current_conseiller = get_current_conseiller()
        if hasattr(self, 'conseiller_dropdown'):
            self.conseiller_dropdown.configure(values=self.conseillers)
            self.conseiller_var.set(self.current_conseiller)
        else:
            self.create_conseiller_dropdown()

    def search_users(self, event=None):
        """
        Effectue une recherche d'usagers.
        
        Args:
            event: Événement déclencheur (optionnel, pour la touche Enter)
        """
        search_term = self.search_entry.get()
        try:
            if not search_term.strip():
                self.show_user_management()
                return

            users = self.db_manager.search_users(search_term)
            
            if not hasattr(self, 'user_management') or not self.user_management.winfo_exists():
                self.show_user_management()
            
            if isinstance(self.user_management, UserManagement):
                self.user_management.display_search_results(users)
            else:
                logging.error("Le widget user_management n'est pas une instance valide de UserManagement")
        except Exception as e:
            logging.error(f"Erreur lors de la recherche d'utilisateurs : {e}")
            import traceback
            traceback.print_exc()

    def show_dashboard(self):
        """
        Affiche le tableau de bord principal.
        Nettoie le contenu précédent et initialise le dashboard.
        """
        self.clear_main_content()
        self.dashboard = Dashboard(self.main_content, self.db_manager)
        self.dashboard.pack(fill="both", expand=True)
        self.current_frame = self.dashboard

    def show_user_management(self):
        """
        Affiche l'interface de gestion des usagers.
        Permet de voir la liste des usagers et d'accéder à leurs détails.
        """
        self.clear_main_content()
        self.user_management = UserManagement(
            self.main_content,
            db_manager=self.db_manager,
            edit_user_callback=self.edit_user,
            edit_workshop_callback=self.show_edit_workshop
        )
        self.user_management.pack(fill="both", expand=True)
        self.current_frame = self.user_management

    def show_workshop_history(self):
        """
        Affiche l'historique des ateliers.
        Permet de consulter et gérer tous les ateliers enregistrés.
        """
        self.clear_main_content()
        self.workshop_history = WorkshopHistory(
            self.main_content,
            db_manager=self.db_manager,
            edit_workshop_callback=self.show_edit_workshop
        )
        self.workshop_history.pack(fill="both", expand=True)
        self.current_frame = self.workshop_history

    def show_data_management(self):
        """
        Affiche l'interface de gestion des données.
        Permet d'importer/exporter des données et de gérer la base de données.
        """
        self.clear_main_content()
        self.data_management = DataManagement(self.main_content, db_manager=self.db_manager, update_callback=self.update_all_sections)
        self.data_management.pack(fill="both", expand=True)
        self.current_frame = self.data_management

    def show_settings(self):
        """
        Affiche les paramètres de l'application.
        Permet de configurer les préférences et les options générales.
        """
        self.clear_main_content()
        self.settings = Settings(self.main_content, db_manager=self.db_manager, main_window=self)
        self.settings.pack(fill="both", expand=True)
        self.current_frame = self.settings

    def show_add_user(self):
        """
        Affiche le formulaire d'ajout d'un nouvel usager.
        """
        self.clear_main_content()
        self.add_user = AddUser(self.main_content, db_manager=self.db_manager, update_callback=self.update_all_sections)
        self.add_user.pack(fill="both", expand=True)
        self.current_frame = self.add_user

    def edit_user(self, user, show_add_workshop=False):
        """
        Affiche l'interface d'édition d'un usager existant.
        
        Args:
            user: Instance de l'usager à éditer
            show_add_workshop (bool): Si True, redirige vers la page d'ajout d'atelier après chargement
        """
        self.clear_main_content()
        
        if show_add_workshop:
            # Rediriger directement vers la page d'ajout d'atelier
            logging.debug(f"Redirection directe vers l'ajout d'atelier pour l'utilisateur {user.id}")
            self.show_add_workshop(user)
        else:
            # Afficher la page d'édition de l'utilisateur
            self.user_edit = UserEditFrame(
                self.main_content,
                self.db_manager,
                user,
                show_user_management_callback=self.show_user_management,
                show_add_workshop_callback=self.show_add_workshop,
                edit_workshop_callback=self.show_edit_workshop,
                update_callback=self.update_all_sections
            )
            self.user_edit.pack(fill="both", expand=True)
            self.current_frame = self.user_edit

    def clear_main_content(self):
        """
        Nettoie la zone de contenu principal.
        Supprime tous les widgets existants pour préparer l'affichage d'une nouvelle section.
        """
        for widget in self.main_content.winfo_children():
            if isinstance(widget, ctk.CTkOptionMenu):
                widget.destroy()
            widget.destroy()
        self.main_content.update()

    def hide_all_frames(self):
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget != self:
                widget.grid_remove()

    def on_closing(self):
        """
        Gère la fermeture de l'application.
        Ferme proprement la connexion à la base de données.
        """
        self.db_manager.close()
        self.master.destroy()

    def update_all_sections(self):
        """
        Met à jour toutes les sections de l'interface :
        - Tableau de bord
        - Gestion des usagers
        - Historique des ateliers
        - Édition d'utilisateur
        - Ajout d'atelier
        """
        try:
            # Vérifier et mettre à jour le tableau de bord
            if hasattr(self, 'dashboard') and self.dashboard is not None and self.dashboard.winfo_exists():
                self.dashboard.update()

            # Vérifier et mettre à jour la gestion des usagers
            if hasattr(self, 'user_management') and self.user_management is not None and self.user_management.winfo_exists():
                self.user_management.load_users()

            # Vérifier et mettre à jour l'historique des ateliers
            if hasattr(self, 'workshop_history') and self.workshop_history is not None and self.workshop_history.winfo_exists():
                self.workshop_history.refresh_workshop_list()

            # Vérifier et mettre à jour l'édition d'utilisateur
            if hasattr(self, 'user_edit') and self.user_edit is not None and self.user_edit.winfo_exists():
                self.user_edit.update_user_info()

            # Vérifier et mettre à jour l'ajout d'atelier
            if hasattr(self, 'add_workshop') and self.add_workshop is not None and self.add_workshop.winfo_exists():
                self.add_workshop.update_payment_status()

        except Exception as e:
            logging.error(f"Erreur lors de la mise à jour des sections : {e}")
            # Ne pas afficher de message d'erreur à l'utilisateur car c'est une opération de fond

    def update_appearance(self):
        """
        Met à jour l'apparence de l'application (thème clair/sombre).
        Applique les changements à tous les widgets de l'interface.
        """
        is_dark = get_dark_mode()
        if is_dark:
            set_dark_theme()
        else:
            set_light_theme()
        
        # Mettre à jour tous les widgets
        self.update()
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkBaseClass):
                widget.configure(fg_color=widget.cget("fg_color"))
                widget.update()

        # Mettre à jour les sections spécifiques
        if hasattr(self, 'dashboard') and self.dashboard.winfo_exists():
            self.dashboard.update()
            self.dashboard.update_graph()
        if hasattr(self, 'add_user') and self.add_user.winfo_exists():
            self.add_user.update()
        if hasattr(self, 'user_management') and self.user_management.winfo_exists():
            self.user_management.update()
        if hasattr(self, 'workshop_history') and self.workshop_history.winfo_exists():
            self.workshop_history.update()
        if hasattr(self, 'settings') and self.settings.winfo_exists():
            self.settings.update()

    def show_add_workshop(self, user):
        """
        Affiche l'interface d'ajout d'un nouvel atelier pour un usager.
        
        Args:
            user: Instance de l'usager pour lequel créer l'atelier
        """
        logging.debug(f"Début de show_add_workshop avec user: {user}")
        logging.debug(f"Type de user: {type(user)}")
        logging.debug(f"Attributs de user: {vars(user)}")
        
        self.clear_main_content()
        
        logging.debug("Création de AddWorkshop")
        try:
            self.add_workshop = AddWorkshop(
                self.main_content,
                self.db_manager,
                user,
                show_user_edit_callback=lambda: self.show_user_edit(user),
                update_callback=self.update_all_sections
            )
            logging.debug("AddWorkshop créé avec succès")
        except Exception as e:
            logging.error(f"Erreur lors de la création de AddWorkshop: {e}")
            raise
        
        self.add_workshop.pack(fill="both", expand=True)
        self.current_frame = self.add_workshop
        logging.debug("Fin de show_add_workshop")

    def update_and_show_user_edit(self, user):
        self.update_all_sections()
        self.show_user_edit(user)

    def show_user_edit(self, user):
        logging.debug(f"Début de show_user_edit avec user: {user}")
        self.clear_main_content()
        self.user_edit = UserEditFrame(
            self.main_content,
            self.db_manager,
            user,
            show_user_management_callback=self.show_user_management,
            show_add_workshop_callback=self.show_add_workshop,
            edit_workshop_callback=self.show_edit_workshop,
            update_callback=self.update_all_sections
        )
        self.user_edit.pack(fill="both", expand=True)
        self.current_frame = self.user_edit
        logging.debug("Fin de show_user_edit")

    def show_edit_workshop(self, workshop):
        """
        Affiche l'interface d'édition d'un atelier existant.
        
        Args:
            workshop: Instance de l'atelier à éditer
        """
        self.clear_main_content()
        self.edit_workshop = EditWorkshop(
            self.main_content,
            self.db_manager,
            workshop,
            update_callback=self.update_all_sections,
            show_previous_page_callback=lambda: self.show_user_edit(User.get_by_id(self.db_manager, workshop.user_id))
        )
        self.edit_workshop.pack(fill="both", expand=True)
        self.current_frame = self.edit_workshop

    def setup_observers(self):
        """
        Configure le système d'observation pour les mises à jour automatiques.
        Connecte les observateurs aux modèles User et Workshop.
        """
        users = User.get_all(self.db_manager)
        if users:
            for user in users:
                user.add_observer(self.user_management)
                user.add_observer(self.dashboard)
        
        workshops = Workshop.get_all(self.db_manager)
        if workshops:
            for workshop in workshops:
                workshop.add_observer(self.workshop_history)
                workshop.add_observer(self.dashboard)

    def create_user(self, user_data):
        """
        Crée un nouvel usager dans la base de données.
        
        Args:
            user_data: Dictionnaire contenant les données de l'usager
        """
        user = User(**user_data)
        user.save(self.db_manager)
        user.add_observer(self.user_management)
        user.add_observer(self.dashboard)

    def create_workshop(self, workshop_data):
        """
        Crée un nouvel atelier dans la base de données.
        
        Args:
            workshop_data: Dictionnaire contenant les données de l'atelier
        """
        workshop = Workshop(**workshop_data)
        workshop.save(self.db_manager)
        workshop.add_observer(self.workshop_history)
        workshop.add_observer(self.dashboard)

    def open_discord(self):
        """
        Ouvre le lien Discord dans le navigateur par défaut.
        """
        discord_link = "https://discord.gg/FD4DdWEQ"
        webbrowser.open(discord_link)
