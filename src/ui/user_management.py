# -*- coding: utf-8 -*-
"""
Module de gestion des utilisateurs de SuiviUsagerPro.
Permet de visualiser, modifier et supprimer les utilisateurs.

Ce module gère :
- L'affichage de la liste des utilisateurs
- La recherche d'utilisateurs
- La modification des informations utilisateur
- La suppression d'utilisateurs
- L'ajout d'ateliers pour un utilisateur
"""

import customtkinter as ctk
from tkinter import messagebox
from src.models.user import User
from src.models.workshop import Workshop
from datetime import datetime, timedelta
import csv
from src.utils.date_utils import convert_from_db_date
from src.utils.observer import Observer
import logging

class UserManagement(ctk.CTkFrame, Observer):
    """
    Interface de gestion des utilisateurs.
    Hérite de CTkFrame pour l'interface graphique et Observer pour les mises à jour automatiques.

    Attributes:
        db_manager: Gestionnaire de base de données
        edit_user_callback: Fonction de rappel pour l'édition d'un utilisateur
        edit_workshop_callback: Fonction de rappel pour l'édition d'un atelier
        users (list): Liste des utilisateurs chargés
        offset (int): Décalage pour la pagination
        limit (int): Nombre d'utilisateurs par page
    """

    def __init__(self, master, db_manager, edit_user_callback, edit_workshop_callback, **kwargs):
        """
        Initialise l'interface de gestion des utilisateurs.
        
        Args:
            master: Widget parent
            db_manager: Instance du gestionnaire de base de données
            edit_user_callback: Fonction pour éditer un utilisateur
            edit_workshop_callback: Fonction pour éditer un atelier
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.edit_user_callback = edit_user_callback
        self.edit_workshop_callback = edit_workshop_callback
        self.users = []
        self.offset = 0
        self.limit = 20
        self.update_callback = self.update_user_list
        
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre
        self.title = ctk.CTkLabel(
            self, 
            text="Gestion des usagers",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Création du conteneur de défilement
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Frame pour la liste des utilisateurs
        self.users_frame = ctk.CTkFrame(self.scrollable_frame)
        self.users_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.users_frame.grid_columnconfigure(0, weight=1)
        
        # Bouton "Charger plus" pour la pagination
        self.load_more_button = ctk.CTkButton(
            self,
            text="Charger plus",
            command=self.load_more_users
        )
        self.load_more_button.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        
        # Chargement initial des utilisateurs
        self.load_users()
        
        # Configurer le défilement
        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)

    def load_users(self):
        """
        Charge une nouvelle page d'utilisateurs depuis la base de données.
        Utilise la pagination pour charger les utilisateurs par lots.
        """
        new_users = User.get_paginated(self.db_manager, self.offset, self.limit)
        self.users.extend(new_users)
        self.display_users(new_users)
        self.offset += self.limit

        # Masquer le bouton si tous les utilisateurs sont chargés
        if len(new_users) < self.limit:
            self.load_more_button.grid_remove()

    def load_more_users(self):
        self.load_users()

    def display_users(self, users):
        """
        Affiche la liste des utilisateurs dans l'interface.
        
        Args:
            users (list): Liste des utilisateurs à afficher
        """
        # Effacer les utilisateurs précédents
        for widget in self.users_frame.winfo_children():
            widget.destroy()
            
        # Afficher les nouveaux utilisateurs
        if not users:
            no_users_label = ctk.CTkLabel(
                self.users_frame,
                text="Aucun utilisateur trouvé",
                font=ctk.CTkFont(size=14)
            )
            no_users_label.pack(pady=20)
            return
            
        # Créer un cadre pour chaque utilisateur
        for user in users:
            user_frame = ctk.CTkFrame(self.users_frame)
            user_frame.grid(sticky="ew", padx=10, pady=5)
            user_frame.grid_columnconfigure(1, weight=1)
            
            # Informations de l'utilisateur
            info_text = f"{user.nom} {user.prenom}"
            if user.telephone:
                info_text += f" - {user.telephone}"
            if user.email:
                info_text += f" - {user.email}"
                
            user_label = ctk.CTkLabel(
                user_frame,
                text=info_text,
                font=ctk.CTkFont(size=14)
            )
            user_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Boutons d'action
            action_frame = ctk.CTkFrame(user_frame)
            action_frame.grid(row=0, column=1, padx=10, pady=5, sticky="e")
            
            edit_button = ctk.CTkButton(
                action_frame,
                text="Éditer",
                command=lambda u=user: self.edit_user(u),
                width=80
            )
            edit_button.grid(row=0, column=0, padx=5)
            
            delete_button = ctk.CTkButton(
                action_frame,
                text="Supprimer",
                command=lambda u=user: self.delete_user(u),
                width=80,
                fg_color="red",
                hover_color="darkred"
            )
            delete_button.grid(row=0, column=1, padx=5)
            
            add_workshop_button = ctk.CTkButton(
                action_frame,
                text="+ Atelier",
                command=lambda u=user: self.add_workshop(u.id),
                width=80
            )
            add_workshop_button.grid(row=0, column=2, padx=5)

    def on_frame_configure(self, event):
        """Configure la zone de défilement."""
        self.scrollable_frame._parent_canvas.configure(scrollregion=self.scrollable_frame._parent_canvas.bbox("all"))

    def on_mousewheel(self, event):
        """Gère le défilement avec la molette de la souris."""
        self.scrollable_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def edit_user(self, user):
        self.edit_user_callback(user)

    def delete_user(self, user):
        """
        Supprime un utilisateur après confirmation.

        Args:
            user: Instance de l'utilisateur à supprimer
        """
        if messagebox.askyesno("Confirmation", 
                              f"Êtes-vous sûr de vouloir supprimer l'usager {user.nom} {user.prenom} ?"):
            try:
                User.delete(self.db_manager, user.id)
                messagebox.showinfo("Suppression", 
                                  f"L'usager {user.nom} {user.prenom} a été supprimé.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Erreur", 
                                   f"Impossible de supprimer l'usager : {str(e)}")

    def add_workshop(self, user_id):
        """Affiche l'interface d'ajout d'atelier pour un usager."""
        logging.debug(f"=== Début de add_workshop pour l'utilisateur {user_id} ===")
        from ui.add_workshop import AddWorkshop  # Import local pour éviter les imports circulaires
        user = User.get_by_id(self.db_manager, user_id)
        if user:
            logging.debug("Utilisateur trouvé, création de l'interface d'ajout d'atelier")
            # Nettoyer l'interface actuelle
            self.clear_frame()
            
            # Configuration de la grille
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            
            # Créer et afficher l'interface d'ajout d'atelier
            logging.debug("Création de la frame AddWorkshop")
            add_workshop_frame = AddWorkshop(
                self,
                self.db_manager,
                user,
                lambda: self.edit_user_callback(user),
                self.update_callback
            )
            add_workshop_frame.grid(row=0, column=0, sticky="nsew")
            
            logging.debug("=== Fin de add_workshop avec succès ===")
        else:
            logging.error(f"Utilisateur {user_id} non trouvé")

    def update_user_list(self):
        # Cette méthode est appelée après l'ajout d'un atelier pour rafraîchir la liste des utilisateurs
        self.load_users()

    def update_user_info(self, user_id):
        user = User.get_by_id(self.db_manager, user_id)
        if user:
            # Mettre à jour les informations de l'utilisateur
            user.nom = self.nom_entry.get()
            user.prenom = self.prenom_entry.get()
            user.date_naissance = self.date_naissance_entry.get()
            user.telephone = self.telephone_entry.get()
            user.email = self.email_entry.get()
            user.adresse = self.adresse_entry.get()
            
            # Mettre à jour la last_activity_date
            user.last_activity_date = datetime.now().strftime("%Y-%m-%d")
            
            user.save(self.db_manager)
            messagebox.showinfo("Mise à jour", "Les informations de l'utilisateur ont été mises à jour.")
            self.update_user_list()
        else:
            messagebox.showerror("Erreur", "Utilisateur non trouvé.")

    def update(self, observable, *args, **kwargs):
        """
        Méthode de l'interface Observer.
        Met à jour l'interface quand un utilisateur ou un atelier est modifié.

        Args:
            observable: Objet qui a déclenché la mise à jour
            *args, **kwargs: Arguments supplémentaires
        """
        if isinstance(observable, User):
            self.refresh_user_list()
        elif isinstance(observable, Workshop):
            self.refresh_workshop_list()

    def refresh_user_list(self):
        """
        Rafraîchit la liste des utilisateurs.
        Recharge tous les utilisateurs depuis la base de données.
        """
        # Nettoyage de la liste
        for widget in self.users_frame.winfo_children():
            widget.destroy()
        
        # Rechargement des données
        self.users = User.get_all(self.db_manager)
        
        # Mise à jour de l'affichage
        self.display_users(self.users)

    def select_user(self, user_id):
        """
        Sélectionne un utilisateur et affiche ses détails.
        
        Args:
            user_id: ID de l'utilisateur à sélectionner
        """
        self._selected_user_id = user_id
        user = User.get_by_id(self.db_manager, user_id)
        if user:
            self.edit_user(user)

    def refresh_workshop_list(self):
        """
        Rafraîchit la liste des ateliers.
        Recharge tous les ateliers depuis la base de données.
        """
        if hasattr(self, 'workshop_list'):
            for widget in self.workshop_list.winfo_children():
                widget.destroy()
        
            workshops = Workshop.get_all(self.db_manager)
            
            for workshop in workshops:
                user = User.get_by_id(self.db_manager, workshop.user_id)
                workshop_frame = ctk.CTkFrame(self.workshop_list)
                workshop_frame.pack(fill="x", padx=5, pady=5)
                
                info_text = f"{convert_from_db_date(workshop.date)} - {workshop.categorie} - {workshop.conseiller}"
                if user:
                    info_text = f"{user.nom} {user.prenom} - {info_text}"
                
                ctk.CTkLabel(workshop_frame, text=info_text).pack(side="left", padx=5)
                
                edit_button = ctk.CTkButton(
                    workshop_frame,
                    text="Modifier",
                    command=lambda w=workshop: self.edit_workshop_callback(w)
                )
                edit_button.pack(side="right", padx=5)

    def get_displayed_users(self):
        """
        Retourne la liste des utilisateurs actuellement affichés.
        
        Returns:
            list: Liste des utilisateurs affichés
        """
        return self.users

    def get_selected_user(self):
        """
        Retourne l'utilisateur actuellement sélectionné.
        
        Returns:
            User: L'utilisateur sélectionné ou None si aucun n'est sélectionné
        """
        if hasattr(self, '_selected_user_id'):
            return User.get_by_id(self.db_manager, self._selected_user_id)
        return None

    def get_displayed_workshops(self):
        """
        Retourne la liste des ateliers affichés pour l'utilisateur sélectionné.
        
        Returns:
            list: Liste des ateliers affichés
        """
        if hasattr(self, '_selected_user_id'):
            return Workshop.get_by_user(self.db_manager, self._selected_user_id)
        return []

    def display_search_results(self, users):
        """
        Affiche les résultats de la recherche d'utilisateurs.
        
        Args:
            users (list): Liste des utilisateurs à afficher
        """
        # Effacer les résultats précédents
        for widget in self.users_frame.winfo_children():
            widget.destroy()
            
        # Afficher les nouveaux résultats
        if not users:
            no_results_label = ctk.CTkLabel(
                self.users_frame,
                text="Aucun utilisateur trouvé",
                font=ctk.CTkFont(size=14)
            )
            no_results_label.pack(pady=20)
            return
            
        # Afficher chaque utilisateur trouvé
        self.display_users(users)

    def clear_frame(self):
        """Nettoie le contenu de la frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def show_user_edit(self, user):
        """Affiche l'interface d'édition d'un utilisateur."""
        logging.debug(f"=== Début de show_user_edit pour l'utilisateur {user.id} ===")
        try:
            # Nettoyer l'interface actuelle
            logging.debug("Nettoyage de l'interface")
            self.clear_frame()
            
            # Recréer la structure de base
            logging.debug("Recréation de la structure de base")
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
            
            # Titre
            logging.debug("Création du titre")
            self.title = ctk.CTkLabel(
                self, 
                text="Gestion des usagers",
                font=ctk.CTkFont(size=24, weight="bold")
            )
            self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
            
            # Création du conteneur de défilement
            logging.debug("Création du conteneur de défilement")
            self.scrollable_frame = ctk.CTkScrollableFrame(self)
            self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
            self.scrollable_frame.grid_columnconfigure(0, weight=1)
            
            # Frame pour la liste des utilisateurs
            logging.debug("Création de la frame utilisateurs")
            self.users_frame = ctk.CTkFrame(self.scrollable_frame)
            self.users_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            self.users_frame.grid_columnconfigure(0, weight=1)
            
            # Configurer le défilement
            logging.debug("Configuration du défilement")
            self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
            self.scrollable_frame.bind("<MouseWheel>", self.on_mousewheel)
            
            # Afficher l'utilisateur
            logging.debug("Affichage de l'utilisateur")
            self.display_users([user])
            
            logging.debug("=== Fin de show_user_edit avec succès ===")
            
        except Exception as e:
            logging.error(f"Erreur lors de l'affichage de l'édition utilisateur : {str(e)}", exc_info=True)
            # Recharger complètement l'interface en cas d'erreur
            logging.debug("Tentative de rechargement complet de l'interface")
            self.__init__(self.master, self.db_manager, self.edit_user_callback, self.edit_workshop_callback)
            self.display_users([user])

    def search_users(self, search_term=None):
        """
        Recherche des utilisateurs selon les critères entrés.
        
        Args:
            search_term (str, optional): Terme de recherche. Si None, rafraîchit la liste.
        """
        if search_term:
            users = User.search(self.db_manager, search_term)
            self.display_search_results(users)
        else:
            self.refresh_user_list()

