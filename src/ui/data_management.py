"""
Module de gestion des données de l'application.
Gère l'exportation/importation CSV, la conformité RGPD et la suppression des données inactives.
"""

import csv
import os
import customtkinter as ctk
from tkinter import messagebox
from src.utils.rgpd_manager import RGPDManager
from src.utils.csv_import_export import CSVExporter
from src.models.user import User
from datetime import timedelta
from datetime import datetime
from src.config import get_inactivity_period
from tkinter import filedialog
from src.utils.observer import Observer

class DataManagement(ctk.CTkFrame, Observer):
    """
    Interface de gestion des données de l'application.
    Permet l'export/import CSV et la gestion RGPD des utilisateurs inactifs.
    Implémente le pattern Observer pour les mises à jour en temps réel.
    """
    
    def __init__(self, master, db_manager, update_callback, **kwargs):
        """
        Initialise l'interface de gestion des données.
        
        Args:
            master: Widget parent
            db_manager: Gestionnaire de base de données
            update_callback: Fonction de mise à jour après modifications
        """
        super().__init__(master, **kwargs)
        self.db_manager = db_manager
        self.update_callback = update_callback
        
        # Configuration de la grille principale
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Titre
        self.title = ctk.CTkLabel(
            self,
            text="Gestion des données",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.csv_exporter = CSVExporter(self.db_manager)
        self.csv_exporter.add_observer(self)
        self.rgpd_manager = RGPDManager(self.db_manager)

        # Contenu
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Section RGPD
        self.rgpd_frame = self.create_section(self.content_frame, "Gestion RGPD", 0)
        self.rgpd_button = ctk.CTkButton(self.rgpd_frame, text="Gérer les données RGPD", command=self.manage_rgpd)
        self.rgpd_button.pack(pady=10)

        # Section Exportation CSV
        self.export_frame = self.create_section(self.content_frame, "Exportation CSV", 1)
        
        # Menu déroulant pour choisir le type d'export
        self.export_options = ["Utilisateurs", "Ateliers", "Toutes les données"]
        self.export_var = ctk.StringVar(value=self.export_options[0])
        self.export_menu = ctk.CTkOptionMenu(self.export_frame, variable=self.export_var, values=self.export_options)
        self.export_menu.pack(pady=(0, 10))

        # Bouton pour valider l'export
        self.export_button = ctk.CTkButton(self.export_frame, text="Exporter les données", command=self.export_csv)
        self.export_button.pack(pady=10)

        # Section Importation
        self.create_import_section()

    def create_section(self, parent, title, row):
        """
        Crée une section dans l'interface avec un titre.
        
        Args:
            parent: Widget parent
            title: Titre de la section
            row: Position dans la grille
        
        Returns:
            CTkFrame: Le cadre créé pour la section
        """
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        return frame

    def manage_rgpd(self):
        """
        Affiche et gère la fenêtre de conformité RGPD.
        Liste les utilisateurs inactifs et permet leur suppression.
        Utilise la période d'inactivité définie dans la configuration.
        """
        inactivity_period = int(get_inactivity_period())  
        inactive_users = self.rgpd_manager.get_inactive_users(inactivity_period)
        if not inactive_users:
            messagebox.showinfo("Information", "Aucun usager inactif depuis plus d'un an.")
            return

        rgpd_window = ctk.CTkToplevel(self)
        rgpd_window.title("Gestion RGPD")
        rgpd_window.geometry("600x400")

        rgpd_frame = ctk.CTkScrollableFrame(rgpd_window)
        rgpd_frame.pack(padx=20, pady=20, fill="both", expand=True)

        for user in inactive_users:
            user_frame = ctk.CTkFrame(rgpd_frame)
            user_frame.pack(fill="x", padx=5, pady=5)
            
            last_activity = user.last_activity_date if user.last_activity_date else "Jamais"
            ctk.CTkLabel(user_frame, text=f"{user.nom} {user.prenom} - Dernière activité : {last_activity}").pack(side="left", padx=5)
            ctk.CTkButton(user_frame, text="Supprimer", command=lambda u=user: self.delete_inactive_user(u)).pack(side="right", padx=5)

        delete_all_button = ctk.CTkButton(rgpd_window, text="Supprimer tous les usagers inactifs", command=self.delete_all_inactive_users)
        delete_all_button.pack(pady=10)

    def delete_inactive_user(self, user):
        """
        Supprime un utilisateur inactif après confirmation.
        
        Args:
            user: Instance de l'utilisateur à supprimer
        """
        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer définitivement l'usager {user.nom} {user.prenom} ?"):
            self.rgpd_manager.delete_inactive_user(user)
            messagebox.showinfo("Suppression", f"L'usager {user.nom} {user.prenom} a été supprimé.")
            self.manage_rgpd()  # Rafraîchir l'affichage

    def delete_all_inactive_users(self):
        """
        Supprime tous les utilisateurs inactifs après confirmation.
        Utilise la période d'inactivité définie dans la configuration.
        """
        inactivity_period = int(get_inactivity_period())
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer tous les usagers inactifs ?"):
            deleted_count = self.rgpd_manager.delete_all_inactive_users(inactivity_period)
            if deleted_count > 0:
                messagebox.showinfo("Suppression", f"{deleted_count} utilisateur(s) inactif(s) ont été supprimés.")
            else:
                messagebox.showinfo("Information", "Aucun utilisateur inactif n'a été trouvé ou supprimé.")
            self.manage_rgpd()  # Rafraîchir l'affichage

    def export_csv(self):
        """
        Exporte les données sélectionnées au format CSV.
        Gère l'export des utilisateurs, des ateliers ou de toutes les données.
        Affiche un message de confirmation ou d'erreur.
        
        Returns:
            bool: True si l'export a réussi, False sinon
        """
        export_type = self.export_var.get()
        success, message = False, ""
        
        if export_type == "Utilisateurs":
            success, message = self.csv_exporter.export_users()
        elif export_type == "Ateliers":
            success, message = self.csv_exporter.export_workshops()
        elif export_type == "Toutes les données":
            success, message = self.csv_exporter.export_all_data()
        else:
            messagebox.showerror("Erreur", "Type d'exportation non reconnu")
            return

        if success:
            messagebox.showinfo("Exportation réussie", message)
        elif message:  # Si un message est retourné mais success est False
            messagebox.showinfo("Exportation annulée", message)
        else:
            messagebox.showerror("Erreur d'exportation", "Une erreur s'est produite lors de l'exportation")
        
        return success

    def export_all_data(self):
        """
        Exporte toutes les données (utilisateurs et ateliers) en CSV.
        
        Returns:
            tuple: (succès, message) indiquant le résultat de l'opération
        """
        success_users, message_users = self.export_users()
        success_workshops, message_workshops = self.export_workshops()
        
        if success_users and success_workshops:
            return True, f"Exportation réussie : {message_users} et {message_workshops}"
        elif success_users:
            return False, f"Exportation partielle : {message_users} mais échec pour les ateliers : {message_workshops}"
        elif success_workshops:
            return False, f"Exportation partielle : {message_workshops} mais échec pour les utilisateurs : {message_users}"
        else:
            return False, f"Échec de l'exportation : {message_users} et {message_workshops}"

    def create_import_section(self):
        """
        Crée la section d'importation de données dans l'interface.
        Ajoute un bouton pour déclencher l'importation CSV.
        """
        self.import_frame = self.create_section(self.content_frame, "Importation de données", 2)
        self.import_button = ctk.CTkButton(self.import_frame, text="Importer des données", command=self.import_data)
        self.import_button.pack(pady=10)

    def update(self, observable, *args, **kwargs):
        """
        Méthode de callback du pattern Observer.
        Met à jour l'interface après une importation réussie.
        
        Args:
            observable: L'objet observé qui a déclenché la mise à jour
            args: Arguments positionnels de la notification
            kwargs: Arguments nommés de la notification
        """
        if isinstance(observable, CSVExporter) and args[0] == 'data_imported':
            self.update_callback()
            messagebox.showinfo("Importation réussie", f"Importation terminée. {args[1]['users']} utilisateurs et {args[1]['workshops']} ateliers importés.")

    def import_data(self):
        """
        Gère l'importation de données depuis un fichier CSV.
        Ouvre une boîte de dialogue pour sélectionner le fichier.
        Affiche un message de succès ou d'erreur.
        """
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            success, message = self.csv_exporter.import_data(file_path)
            if not success:
                messagebox.showerror("Erreur d'importation", message)
