# -*- coding: utf-8 -*-
"""
Module du tableau de bord de SuiviUsagerPro.
Affiche les statistiques principales et un graphique des ateliers.

Ce module gère l'affichage des informations clés de l'application :
- Nombre total d'usagers
- Nombre total d'ateliers
- Nombre d'usagers actifs
- Nombre d'ateliers du mois en cours
- Graphique des ateliers sur les 12 derniers mois
"""

import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.database.db_manager import DatabaseManager
import logging
import matplotlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
matplotlib.set_loglevel("WARNING")  # Réduire les logs de matplotlib

class Dashboard(ctk.CTkFrame):
    """
    Classe principale du tableau de bord.
    Affiche les statistiques et le graphique des ateliers.

    Attributes:
        db_manager (DatabaseManager): Gestionnaire de base de données
        stats_frame: Frame contenant les widgets de statistiques
        graph_frame: Frame contenant le graphique
    """

    def __init__(self, master, db_manager, **kwargs):
        """
        Initialise le tableau de bord.

        Args:
            master: Widget parent
            db_manager: Instance du gestionnaire de base de données
            **kwargs: Arguments supplémentaires pour le Frame
        """
        super().__init__(master, **kwargs)
        if db_manager is None:
            raise ValueError("DatabaseManager ne peut pas être None")
        self.db_manager = db_manager

        # Contenu du tableau de bord avec marges
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configuration de la grille pour une disposition flexible
        content_frame.grid_rowconfigure(2, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Titre du tableau de bord
        self.title = ctk.CTkLabel(content_frame, text="Tableau de bord", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, pady=(10, 5), sticky="ew")

        # Frame des statistiques avec hauteur fixe
        self.stats_frame = ctk.CTkFrame(content_frame, fg_color="transparent", height=100)
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.stats_frame.grid_propagate(False)  # Maintenir la hauteur fixe
        
        # Configuration de la grille des statistiques (4 colonnes égales)
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="column")

        # Création des widgets de statistiques
        self.users_count_frame, self.users_count_label = self.create_stat_widget(
            self.stats_frame, "Nombre d'usagers", "0")
        self.users_count_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.workshops_count_frame, self.workshops_count_label = self.create_stat_widget(
            self.stats_frame, "Nombre d'ateliers", "0")
        self.workshops_count_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.active_users_frame, self.active_users_label = self.create_stat_widget(
            self.stats_frame, "Usagers actifs", "0")
        self.active_users_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.workshops_this_month_frame, self.workshops_this_month_label = self.create_stat_widget(
            self.stats_frame, "Ateliers ce mois", "0")
        self.workshops_this_month_frame.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")

        # Frame du graphique (espace restant)
        self.graph_frame = ctk.CTkFrame(content_frame)
        self.graph_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        # Initialisation des composants
        self.create_graph()
        self.update_stats()
        self.update_graph()

    def create_stat_widget(self, parent, label, value):
        """
        Crée un widget de statistique avec un label et une valeur.

        Args:
            parent: Widget parent
            label (str): Titre de la statistique
            value (str): Valeur initiale

        Returns:
            tuple: (frame, label_widget) Le frame contenant le widget et le label de la valeur
        """
        frame = ctk.CTkFrame(parent, corner_radius=6, border_width=1)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(padx=10, pady=5, expand=True)
        
        ctk.CTkLabel(content, text=label, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=(0, 2))
        value_label = ctk.CTkLabel(content, text=value, font=ctk.CTkFont(size=24, weight="bold"))
        value_label.pack(pady=(0, 0))
        
        return frame, value_label

    def create_graph(self):
        """
        Crée le graphique initial avec des données factices.
        Ce graphique sera remplacé par les données réelles lors de l'appel à update_graph.
        """
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Données d'exemple pour l'initialisation
        months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
        individual = [4, 3, 5, 2, 6, 3, 4, 3, 4, 4, 4, 4]
        administrative = [2, 4, 2, 5, 1, 4, 3, 4, 3, 3, 3, 3]

        # Création du graphique empilé
        ax.bar(months, individual, label='Atelier individuel', color='#4CAF50')
        ax.bar(months, administrative, bottom=individual, label='Atelier administratif', color='#2196F3')

        ax.set_ylabel('Nombre d\'ateliers')
        ax.set_title('Ateliers par mois')
        ax.legend()

        # Intégration du graphique dans l'interface
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def update_stats(self):
        """
        Met à jour les statistiques affichées.
        Récupère les données depuis la base de données.
        """
        try:
            # Requêtes SQL pour obtenir les statistiques
            users_count = self.db_manager.fetch_all("SELECT COUNT(*) FROM users")[0][0]
            workshops_count = self.db_manager.fetch_all("SELECT COUNT(*) FROM workshops")[0][0]
            active_users = self.db_manager.fetch_all(
                "SELECT COUNT(DISTINCT user_id) FROM workshops WHERE date >= date('now', '-30 days')")[0][0]
            workshops_this_month = self.db_manager.fetch_all(
                "SELECT COUNT(*) FROM workshops WHERE date >= date('now', 'start of month')")[0][0]

            # Mise à jour des labels
            self.users_count_label.configure(text=str(users_count))
            self.workshops_count_label.configure(text=str(workshops_count))
            self.active_users_label.configure(text=str(active_users))
            self.workshops_this_month_label.configure(text=str(workshops_this_month))
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des statistiques : {e}")

    def update_graph(self):
        """
        Met à jour le graphique avec les données réelles de la base de données.
        Affiche les ateliers des 12 derniers mois, séparés par catégorie.
        """
        try:
            # Calcul de la période de 12 mois
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            # Requête SQL pour obtenir les données
            data = self.db_manager.fetch_all("""
                SELECT strftime('%Y-%m', date) as month,
                       SUM(CASE WHEN categorie = 'Atelier numérique' THEN 1 ELSE 0 END) as numerique,
                       SUM(CASE WHEN categorie = 'Démarche administrative' THEN 1 ELSE 0 END) as administratif
                FROM workshops
                WHERE date >= ? AND date <= ?
                GROUP BY month
                ORDER BY month
            """, (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            logger.info(f"Données récupérées détaillées : {[dict(row) for row in data]}")
            
            if not data:
                logger.warning("Aucune donnée disponible pour le graphique")
                self.display_no_data_graph()
                return

            # Génération de tous les mois sur la période
            all_months = []
            current_date = end_date
            for _ in range(12):
                all_months.append(current_date.strftime('%Y-%m'))
                current_date = current_date.replace(day=1) - timedelta(days=1)
            all_months.reverse()

            month_labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
            
            # Initialisation des données
            numerique = [0] * 12
            administratif = [0] * 12

            # Organisation des données par mois
            data_dict = {row['month']: row for row in data}

            # Remplissage des données pour chaque mois
            for i, month in enumerate(all_months):
                if month in data_dict:
                    row = data_dict[month]
                    numerique[i] = int(row['numerique'] or 0)
                    administratif[i] = int(row['administratif'] or 0)
                logger.info(f"Mois {month}: numerique={numerique[i]}, administratif={administratif[i]}")

            logger.info(f"Données traitées : numerique={numerique}, administratif={administratif}")

            # Affichage du graphique avec les données
            self.display_graph(all_months, month_labels, numerique, administratif)

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du graphique : {e}")
            logger.exception("Détails de l'erreur:")
            self.display_no_data_graph()

    def display_no_data_graph(self):
        """
        Affiche un graphique vide avec un message lorsqu'aucune donnée n'est disponible.
        """
        if hasattr(self, 'graph_frame'):
            self.graph_frame.destroy()
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Création d'une figure vide
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Utilisation des couleurs du thème
        bg_color = ctk.ThemeManager.theme["CTk"]["fg_color"][1]
        text_color = ctk.ThemeManager.theme["CTk"]["text"][1]
        
        # Configuration des couleurs
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.text(0.5, 0.5, "Aucune donnée disponible", ha='center', va='center', transform=ax.transAxes, color=text_color)
        
        # Masquer les axes
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        # Intégration du graphique
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    def display_graph(self, all_months, month_labels, numerique, administratif):
        """
        Affiche le graphique avec les données fournies.

        Args:
            all_months (list): Liste des mois au format YYYY-MM
            month_labels (list): Liste des étiquettes de mois (Jan, Fév, etc.)
            numerique (list): Nombre d'ateliers numériques par mois
            administratif (list): Nombre de démarches administratives par mois
        """
        logging.info(f"Affichage du graphique avec : {len(all_months)} mois, {len(numerique)} ateliers numériques, {len(administratif)} démarches administratives")
        
        # Recréation du frame du graphique
        if hasattr(self, 'graph_frame'):
            self.graph_frame.destroy()
        self.graph_frame = ctk.CTkFrame(self)
        self.graph_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Création de la figure
        fig = Figure(figsize=(10, 4), dpi=100)
        ax = fig.add_subplot(111)

        # Calcul des totaux pour l'échelle
        total_workshops = [i + a for i, a in zip(numerique, administratif)]
        max_workshops = max(total_workshops) if total_workshops else 0

        x = range(len(all_months))
        
        # Configuration des couleurs selon le thème
        bg_color = ctk.ThemeManager.theme["CTk"]["fg_color"][1]
        text_color = ctk.ThemeManager.theme["CTk"]["text"][1]

        # Application des couleurs
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(bg_color)
        ax.tick_params(colors=text_color, length=5)
        ax.grid(True, axis='y', linestyle='--', alpha=0.3, color=text_color)
        
        for spine in ax.spines.values():
            spine.set_color(text_color)
            spine.set_linewidth(0.5)

        # Création des barres empilées
        bars_num = ax.bar(x, numerique, label='Atelier numérique', color='#4CAF50', width=0.8)
        bars_admin = ax.bar(x, administratif, bottom=numerique, label='Démarche administrative', color='#2196F3', width=0.8)

        # Configuration des tooltips
        def on_hover(event):
            """Gère l'affichage des tooltips lors du survol des barres."""
            if event.inaxes == ax:
                for i, (num, admin) in enumerate(zip(numerique, administratif)):
                    if abs(event.xdata - i) < 0.4:
                        if event.ydata <= num:
                            ax.set_title(f'Ateliers numériques: {num}', color=text_color, pad=10)
                        elif event.ydata <= (num + admin):
                            ax.set_title(f'Démarches administratives: {admin}', color=text_color, pad=10)
                        fig.canvas.draw_idle()
                        return
                ax.set_title('Ateliers par mois', color=text_color, pad=10)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect('motion_notify_event', on_hover)

        # Configuration des labels et titres
        ax.set_ylabel('Nombre d\'ateliers', color=text_color, fontsize=10)
        ax.set_title('Ateliers par mois', color=text_color, pad=10)
        ax.set_ylim(0, max_workshops * 1.1 if max_workshops > 0 else 1)

        # Configuration de la légende
        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, 
                          facecolor=bg_color, edgecolor=text_color, labelcolor=text_color,
                          framealpha=0.8)
        legend.get_frame().set_linewidth(0.5)

        fig.tight_layout()
        fig.subplots_adjust(bottom=0.2)

        # Amélioration des étiquettes de l'axe X
        ax.set_xticks(x)
        ax.set_xticklabels([f"{month_labels[datetime.strptime(m, '%Y-%m').month - 1]}\n{m[:4]}" 
                           for m in all_months], rotation=45, ha='right', color=text_color)

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

        logger.info("Graphique mis à jour avec succès")

    def get_graph_data(self):
        # Méthode pour récupérer les données du graphique
        data = ...  # Votre logique pour récupérer les données
        logging.info(f"Données récupérées pour le graphique : {data}")
        return data

    def import_data(self, file_path):
        # Votre code d'importation ici
        success, message = self.csv_exporter.import_data(file_path)
        if success:
            self.refresh_dashboard()  # Méthode pour mettre à jour le dashboard
        return success, message

    def refresh_dashboard(self):
        """
        Rafraîchit toutes les données du tableau de bord.
        Met à jour les statistiques et le graphique.
        """
        self.update_stats()
        self.update_graph()
