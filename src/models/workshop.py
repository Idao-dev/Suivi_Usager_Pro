"""
Module de gestion des ateliers.
Définit la classe Workshop qui représente un atelier avec ses attributs et méthodes.
Gère le stockage, la récupération et la mise à jour des ateliers dans la base de données.
"""

from src.utils.date_utils import convert_to_db_date, convert_from_db_date
from datetime import datetime
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING
from src.utils.observer import Observable

if TYPE_CHECKING:
    from src.models.user import User



class Workshop(Observable):
    """
    Classe représentant un atelier du système.
    Hérite d'Observable pour notifier les changements aux observateurs.
    Gère les informations de l'atelier, son statut de paiement et son association avec un utilisateur.
    """
    
    def __init__(self, id=None, user_id=None, description=None, categorie=None, payant=False, paid=False, date=None, conseiller=None):
        """
        Initialise un nouvel atelier.
        
        Args:
            id: Identifiant unique de l'atelier
            user_id: Identifiant de l'utilisateur associé
            description: Description de l'atelier
            categorie: Catégorie de l'atelier
            payant: Indique si l'atelier est payant
            paid: Indique si l'atelier a été payé
            date: Date de l'atelier
            conseiller: Nom du conseiller
        """
        super().__init__()
        self.id = id
        self.user_id = user_id
        self.description = description
        self.categorie = categorie
        self.payant = payant
        self.paid = paid 
        self.date = date
        self.conseiller = conseiller

    @classmethod
    def from_db(cls, row):
        """
        Crée une instance Workshop à partir d'une ligne de la base de données.
        
        Args:
            row: Dictionnaire contenant les données de l'atelier
        
        Returns:
            Workshop: Instance de l'atelier créée
        """
        return cls(
            id=row['id'],
            user_id=row['user_id'] if row['user_id'] is not None else None,
            description=row['description'],
            categorie=row['categorie'],
            payant=row['payant'],
            paid=row['paid'],  
            date=row['date'],
            conseiller=row['conseiller']
        )

    def to_dict(self):
        """
        Convertit l'instance en dictionnaire.
        Utilisé pour la sérialisation et l'export des données.
        
        Returns:
            dict: Dictionnaire des attributs de l'atelier
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'categorie': self.categorie,
            'payant': self.payant,
            'paid': self.paid, 
            'date': self.date,
            'conseiller': self.conseiller
        }

    def save(self, db_manager):
        """
        Sauvegarde ou met à jour l'atelier dans la base de données.
        Gère l'insertion d'un nouvel atelier ou la mise à jour d'un existant.
        Notifie les observateurs après la sauvegarde.
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            int: ID de l'atelier sauvegardé
        """
        if self.id is None:
            query = """
            INSERT INTO workshops (user_id, description, categorie, payant, paid, date, conseiller)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.paid, self.date, self.conseiller)
        else:
            query = """
            UPDATE workshops
            SET user_id=?, description=?, categorie=?, payant=?, paid=?, date=?, conseiller=?
            WHERE id=?
            """
            params = (self.user_id, self.description, self.categorie, self.payant, self.paid, self.date, self.conseiller, self.id)

        cursor = db_manager.execute(query, params)
        if self.id is None:
            self.id = cursor.lastrowid
        
        self.notify_observers('workshop_updated', self)
        return self.id

  
    @staticmethod
    def get_all(db_manager):
        query = "SELECT * FROM workshops"
        rows = db_manager.fetch_all(query)
        return [Workshop.from_db(row) for row in rows]

    @staticmethod
    def get_by_id(db_manager, workshop_id):
        query = "SELECT * FROM workshops WHERE id = ?"
        row = db_manager.fetch_one(query, (workshop_id,))
        if row:
            workshop = Workshop.from_db(row)
            if workshop.user_id is None:
                workshop.user_id = None
            return workshop
        return None

    @classmethod
    def get_by_user(cls, db_manager, user_id):
        query = "SELECT * FROM workshops WHERE user_id = ? ORDER BY date DESC"
        rows = db_manager.fetch_all(query, (user_id,))
        return [cls.from_db(row) for row in rows]

    @classmethod
    def delete(cls, db_manager, workshop_id):
        query = "DELETE FROM workshops WHERE id = ?"
        db_manager.execute(query, (workshop_id,))

    @classmethod
    def get_all_with_users(cls, db_manager):
        """
        Récupère tous les ateliers avec les informations des utilisateurs associés.
        Limite les résultats aux 50 derniers ateliers.
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            list[Workshop]: Liste des ateliers avec informations utilisateurs
        """
        query = """
        SELECT w.*, u.nom, u.prenom
        FROM workshops w
        JOIN users u ON w.user_id = u.id
        ORDER BY w.date DESC
        LIMIT 50
        """
        try:
            results = db_manager.fetch_all(query)
            logging.debug(f"Fetched results: {results}")
            workshops = []
            for row in results:
                logging.debug(f"Processing row: {row}")
                workshop = cls(
                    id=row['id'],
                    user_id=row['user_id'],
                    description=row['description'],
                    categorie=row['categorie'],
                    payant=row['payant'],
                    paid=row['paid'], 
                    date=convert_from_db_date(row['date']),  # Convertir la date du format DB au format DD/MM/YYYY
                    conseiller=row['conseiller']
                )
                workshop.user_nom = row['nom']
                workshop.user_prenom = row['prenom']
                workshops.append(workshop)
            return workshops
        except Exception as e:
            logging.error(f"Error fetching workshops with users: {e}")
            logging.exception("Detailed error:")
            return []

    @staticmethod
    def get_orphan_workshops(db_manager):
        """
        Récupère les ateliers sans utilisateur associé.
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            list[Workshop]: Liste des ateliers orphelins
        """
        query = "SELECT * FROM workshops WHERE user_id IS NULL"
        rows = db_manager.fetch_all(query)
        return [Workshop.from_db(row) for row in rows]

    @classmethod
    def get_paginated_with_users(cls, db_manager, offset, limit):
        """
        Récupère une page d'ateliers avec les informations des utilisateurs.
        
        Args:
            db_manager: Gestionnaire de base de données
            offset: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            
        Returns:
            list[Workshop]: Liste paginée des ateliers
        """
        query = """
        SELECT w.*, u.nom, u.prenom
        FROM workshops w
        JOIN users u ON w.user_id = u.id
        ORDER BY w.date DESC, w.id DESC
        LIMIT ? OFFSET ?
        """
        results = db_manager.fetch_all(query, (limit, offset))
        return [cls.from_db_with_user(row) for row in results]

    @classmethod
    def from_db_with_user(cls, row):
        workshop = cls.from_db(row)
        workshop.user_nom = row['nom']
        workshop.user_prenom = row['prenom']
        return workshop

    @staticmethod
    def get_user_workshops(db_manager, user_id):
        query = "SELECT * FROM workshops WHERE user_id = ? ORDER BY date"
        rows = db_manager.fetch_all(query, (user_id,))
        return [Workshop.from_db(row) for row in rows]

    @classmethod
    def from_db(cls, row):
        return cls(
            id=row['id'],
            user_id=row['user_id'] if row['user_id'] is not None else None,
            description=row['description'],
            categorie=row['categorie'],
            payant=row['payant'],
            paid=row['paid'],  
            date=row['date'],
            conseiller=row['conseiller']
        )

    def get_state(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'description': self.description,
            'categorie': self.categorie,
            'payant': self.payant,
            'paid': self.paid, 
            'date': self.date,
            'conseiller': self.conseiller
        }

    @property
    def user(self):
        """
        Propriété pour accéder à l'utilisateur associé à l'atelier.
        Évite les imports circulaires avec une importation locale.
        
        Returns:
            User: Instance de l'utilisateur associé ou None
        """
        # Import à l'intérieur de la méthode pour éviter les importations circulaires
        from src.models.user import User
        if not hasattr(self, 'db_manager'):
            return None
        return User.get_by_id(self.db_manager, self.user_id) if self.user_id else None

    def get_user(self, db_manager):
        """
        Récupère l'utilisateur associé à cet atelier.
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            User: Instance de l'utilisateur associé ou None
        """
        # Import à l'intérieur de la méthode pour éviter les importations circulaires
        from src.models.user import User
        return User.get_by_id(db_manager, self.user_id) if self.user_id else None

    def refresh_user_list(self):
        # Code pour rafraîchir la liste des utilisateurs
        self.load_users()

    def refresh_workshop_list(self):
        # Si nécessaire, ajoutez du code pour rafraîchir la liste des ateliers
        pass