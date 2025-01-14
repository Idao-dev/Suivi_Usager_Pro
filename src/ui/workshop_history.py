# -*- coding: utf-8 -*-
"""
Module d'historique des ateliers de SuiviUsagerPro.
Affiche l'historique des ateliers dans un tableau interactif.

Ce module gère :
- L'affichage paginé des ateliers
- Le tri et le filtrage des ateliers
- L'interaction avec les ateliers (clic pour éditer)
- Les effets visuels (survol, sélection)
"""

import customtkinter as ctk
from src.database.db_manager import DatabaseManager
from src.utils.date_utils import convert_from_db_date
from src.models.workshop import Workshop


class WorkshopHistory(ctk.CTkFrame):
    """
    Interface d'historique des ateliers.
    Affiche un tableau paginé avec les ateliers et leurs informations.

    Attributes:
        db_manager: Gestionnaire de base de données
        edit_workshop_callback: Fonction de rappel pour l'édition d'un atelier
        workshops (list): Liste des ateliers chargés
        offset (int): Décalage pour la pagination
        limit (int): Nombre d'ateliers par page
        _hover_color (str): Couleur au survol des lignes
        _default_color (str): Couleur par défaut des lignes
        _text_color (str): Couleur du texte
        _columns_config (dict): Configuration des colonnes du tableau
    """

    def __init__(self, master, db_manager=None, edit_workshop_callback=None, **kwargs):
        """
        Initialise l'interface d'historique des ateliers.

        Args:
            master: Widget parent
            db_manager: Instance du gestionnaire de base de données
            edit_workshop_callback: Fonction pour éditer un atelier
            **kwargs: Arguments supplémentaires pour le Frame
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.edit_workshop_callback = edit_workshop_callback
        self.workshops = []
        self.offset = 0
        self.limit = 25  # Nombre d'ateliers par page

        # Configuration des couleurs pour les effets visuels
        self._hover_color = "#1f538d"  # Bleu foncé pour le survol
        self._default_color = self._apply_appearance_mode(("gray95", "gray15"))
        self._text_color = self._apply_appearance_mode(("gray10", "gray90"))

        # Configuration des colonnes du tableau
        self._columns_config = {
            "Nom": {"weight": 2, "align": "w", "minwidth": 100},
            "Prénom": {"weight": 2, "align": "w", "minwidth": 100},
            "Date": {"weight": 1, "align": "center", "minwidth": 80},
            "Type d'atelier": {"weight": 3, "align": "w", "minwidth": 150},
            "Conseiller": {"weight": 1, "align": "center", "minwidth": 80}
        }

        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Création de l'interface
        self.create_title_frame()
        self.create_history_frame()
        self.create_load_more_button()

        # Chargement initial des ateliers
        self.load_history()

    def create_title_frame(self):
        """Crée le titre et les filtres."""
        # Titre
        self.title = ctk.CTkLabel(
            self,
            text="Historique des ateliers",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

    def create_history_frame(self):
        """Crée le frame principal contenant le tableau d'historique."""
        self.history_frame = ctk.CTkScrollableFrame(self)
        self.history_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)

        # Création des en-têtes du tableau
        for i, (header, config) in enumerate(self._columns_config.items()):
            label = ctk.CTkLabel(
                self.history_frame,
                text=header,
                font=ctk.CTkFont(weight="bold", size=13),
                anchor=config["align"],
                fg_color=self._apply_appearance_mode(("gray85", "gray20")),
                corner_radius=0
            )
            label.grid(row=0, column=i, padx=(0, 0), pady=(0, 2), sticky="ew")
            self.history_frame.grid_columnconfigure(i, weight=config["weight"])

    def create_load_more_button(self):
        """Crée le bouton 'Charger plus' pour la pagination."""
        self.load_more_button = ctk.CTkButton(
            self, 
            text="Charger plus", 
            command=self.load_history,
            height=32
        )
        self.load_more_button.grid(row=2, column=0, pady=(10, 20), padx=20, sticky="ew")

    def load_history(self):
        """
        Charge une nouvelle page d'ateliers depuis la base de données.
        Met à jour l'affichage avec les nouveaux ateliers.
        """
        new_workshops = Workshop.get_paginated_with_users(self.db_manager, self.offset, self.limit)
        self.workshops.extend(new_workshops)
        self.display_workshops(new_workshops)
        self.offset += self.limit

        # Masquer le bouton si tous les ateliers sont chargés
        if len(new_workshops) < self.limit:
            self.load_more_button.grid_remove()

    def display_workshops(self, workshops):
        """
        Affiche les ateliers dans le tableau.
        Crée une ligne pour chaque atelier avec les informations associées.

        Args:
            workshops (list): Liste des ateliers à afficher
        """
        # Calcul de la ligne de départ pour l'ajout des nouveaux ateliers
        start_row = len([w for w in self.history_frame.winfo_children() 
                        if isinstance(w, ctk.CTkLabel) and w.winfo_y() > 0]) // len(self._columns_config) + 1

        for i, workshop in enumerate(workshops, start=start_row):
            user = workshop.get_user(self.db_manager)
            
            # Préparation des données pour chaque colonne
            data = {
                "Nom": user.nom if user else "N/A",
                "Prénom": user.prenom if user else "N/A",
                "Date": workshop.date,
                "Type d'atelier": workshop.categorie,
                "Conseiller": workshop.conseiller
            }

            # Création des cellules pour chaque colonne
            row_labels = []
            for j, (header, text) in enumerate(data.items()):
                config = self._columns_config[header]
                label = ctk.CTkLabel(
                    self.history_frame,
                    text=text,
                    anchor=config["align"],
                    fg_color=self._default_color,
                    corner_radius=0,
                    padx=10,
                    width=0,
                    cursor="hand2"  # Curseur de type "main" pour indiquer la possibilité de clic
                )
                label.grid(row=i, column=j, padx=(0, 0), pady=(0, 0), sticky="nsew")
                row_labels.append(label)

            # Configuration des événements pour chaque cellule
            for label in row_labels:
                label.bind("<Button-1>", lambda e, w=workshop: self.on_workshop_click(w))
                label.bind("<Enter>", lambda e, labels=row_labels: self._on_enter(labels))
                label.bind("<Leave>", lambda e, labels=row_labels: self._on_leave(labels))

    def _on_enter(self, labels):
        """
        Effet visuel quand la souris entre dans une ligne.
        Change la couleur de fond et du texte.

        Args:
            labels (list): Liste des labels de la ligne survolée
        """
        for label in labels:
            label.configure(
                fg_color=self._hover_color,
                text_color="white"
            )

    def _on_leave(self, labels):
        """
        Effet visuel quand la souris quitte une ligne.
        Restaure les couleurs par défaut.

        Args:
            labels (list): Liste des labels de la ligne quittée
        """
        for label in labels:
            label.configure(
                fg_color=self._default_color,
                text_color=self._text_color
            )

    def refresh_workshop_list(self):
        """
        Rafraîchit complètement la liste des ateliers.
        Réinitialise la pagination et recharge les données.
        """
        # Réinitialisation des variables de pagination
        self.workshops = []
        self.offset = 0

        # Suppression de tous les widgets sauf l'en-tête
        for widget in self.history_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.winfo_y() > 0:
                widget.destroy()

        # Rechargement des données
        self.load_history()
        self.load_more_button.grid(row=2, column=0, pady=(10, 20), padx=20, sticky="ew")

    def on_frame_configure(self, event):
        """
        Gère la configuration du frame lors du redimensionnement.
        Met à jour la zone de défilement.
        """
        self.history_frame.configure(scrollregion=self.history_frame.bbox("all"))

    def on_mousewheel(self, event):
        """
        Gère le défilement de la souris.
        Charge plus d'ateliers si on atteint le bas de la liste.
        """
        if self.history_frame.winfo_height() < self.history_frame.bbox("all")[3]:
            if self.history_frame.yview()[1] >= 0.9:
                self.load_history()

    def on_workshop_click(self, workshop):
        """
        Gère le clic sur un atelier.
        Appelle la fonction de callback pour éditer l'atelier.

        Args:
            workshop: Atelier sélectionné
        """
        if self.edit_workshop_callback:
            self.edit_workshop_callback(workshop)
