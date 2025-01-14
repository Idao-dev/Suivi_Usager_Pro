"""
Module de gestion de la conformité RGPD (Règlement Général sur la Protection des Données).
Permet de gérer le cycle de vie des données personnelles des usagers :
- Identification des utilisateurs inactifs
- Suppression des données personnelles
- Export des données avant suppression
"""

from datetime import datetime, timedelta
from src.utils.csv_import_export import CSVExporter
from src.utils.date_utils import convert_to_db_date, convert_from_db_date
from src.models.user import User


class RGPDManager:
    """
    Gestionnaire de conformité RGPD.
    Implémente les fonctionnalités nécessaires pour respecter les exigences du RGPD
    concernant la conservation et la suppression des données personnelles.
    """

    def __init__(self, db_manager):
        """
        Initialise le gestionnaire RGPD.
        
        Args:
            db_manager: Instance du gestionnaire de base de données
        """
        self.db_manager = db_manager

    def get_inactive_users(self, inactivity_period_days):
        """
        Identifie les utilisateurs inactifs selon une période donnée.
        Un utilisateur est considéré inactif s'il n'a participé à aucun atelier
        et n'a pas été modifié depuis la période spécifiée.
        
        Args:
            inactivity_period_days (int): Nombre de jours d'inactivité
            
        Returns:
            list[User]: Liste des utilisateurs inactifs
        """
        cutoff_date = datetime.now() - timedelta(days=inactivity_period_days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        query = """
        WITH LastActivity AS (
            SELECT 
                u.id,
                COALESCE(
                    MAX(strftime('%Y-%m-%d', 
                        CASE 
                            WHEN w.date IS NOT NULL THEN replace(w.date, '/', '-')
                            ELSE replace(u.date_creation, '/', '-')
                        END
                    )),
                    replace(u.date_creation, '/', '-')
                ) as last_activity
            FROM users u
            LEFT JOIN workshops w ON u.id = w.user_id
            GROUP BY u.id
        )
        SELECT u.* 
        FROM users u
        JOIN LastActivity la ON u.id = la.id
        WHERE la.last_activity < ?
        ORDER BY la.last_activity ASC
        """
        
        rows = self.db_manager.fetch_all(query, (cutoff_date_str,))
        return [User.from_db(row) for row in rows]

    def delete_inactive_user(self, user):
        """
        Supprime un utilisateur inactif tout en préservant l'historique des ateliers.
        Les ateliers sont conservés mais anonymisés (user_id mis à NULL).
        
        Args:
            user (User): L'utilisateur à supprimer
        """
        # Mettre à jour les ateliers associés
        self.db_manager.execute("UPDATE workshops SET user_id = NULL WHERE user_id = ?", (user.id,))
        # Supprimer l'utilisateur
        User.delete(self.db_manager, user.id)

    def delete_all_inactive_users(self, inactivity_days):
        """
        Supprime tous les utilisateurs inactifs depuis plus de inactivity_days jours.
        Un utilisateur est considéré inactif si sa dernière activité (atelier ou création)
        est plus ancienne que la date limite.
        
        Args:
            inactivity_days (int): Nombre de jours d'inactivité avant suppression
        """
        cutoff_date = datetime.now() - timedelta(days=inactivity_days)
        cutoff_date_str = cutoff_date.strftime("%Y-%m-%d")
        
        query = """
        WITH LastActivity AS (
            SELECT 
                u.id,
                COALESCE(
                    MAX(strftime('%Y-%m-%d', 
                        CASE 
                            WHEN w.date IS NOT NULL THEN replace(w.date, '/', '-')
                            ELSE replace(u.date_creation, '/', '-')
                        END
                    )),
                    replace(u.date_creation, '/', '-')
                ) as last_activity
            FROM users u
            LEFT JOIN workshops w ON u.id = w.user_id
            GROUP BY u.id
        )
        DELETE FROM users
        WHERE id IN (
            SELECT u.id 
            FROM users u
            JOIN LastActivity la ON u.id = la.id
            WHERE la.last_activity < ?
        )
        """
        
        self.db_manager.execute(query, (cutoff_date_str,))

    def export_inactive_users(self, inactivity_period_days, filename):
        """
        Exporte les données des utilisateurs inactifs avant leur suppression.
        Permet de conserver une trace des données supprimées conformément au RGPD.
        
        Args:
            inactivity_period_days (int): Nombre de jours d'inactivité
            filename (str): Nom du fichier d'export
            
        Returns:
            bool: True si l'export a réussi, False sinon
        """
        inactive_users = self.get_inactive_users(inactivity_period_days)
        exporter = CSVExporter(self.db_manager)
        success, _ = exporter.export_specific_users(inactive_users, filename)
        return success
