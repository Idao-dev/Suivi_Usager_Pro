"""
Module de gestion des utilisateurs.
Définit la classe User qui représente un utilisateur du système avec ses attributs et méthodes.
Gère le stockage, la récupération et la mise à jour des données utilisateur dans la base de données.
"""

from src.utils.date_utils import convert_to_db_date, convert_from_db_date
from datetime import datetime, timedelta
from src.utils.config_utils import get_ateliers_entre_paiements, get_default_paid_workshops
import logging
from src.utils.observer import Observable
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.models.workshop import Workshop



class User(Observable):
    """
    Classe représentant un utilisateur du système.
    Hérite d'Observable pour notifier les changements aux observateurs.
    Gère les informations personnelles, l'historique des activités et le statut de paiement.
    """
    
    def __init__(self, id=None, nom="", prenom="", date_naissance=None, telephone="", email=None, adresse=None, date_creation=None, last_activity_date=None, last_payment_date=None):
        """
        Initialise un nouvel utilisateur.
        
        Args:
            id: Identifiant unique de l'utilisateur
            nom: Nom de famille
            prenom: Prénom
            date_naissance: Date de naissance (format JJ/MM/AAAA)
            telephone: Numéro de téléphone
            email: Adresse email
            adresse: Adresse postale
            date_creation: Date de création du compte
            last_activity_date: Date de dernière activité
            last_payment_date: Date du dernier paiement
        """
        super().__init__()
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.date_naissance = date_naissance  # Ne pas convertir ici
        self.telephone = telephone
        self.email = email
        self.adresse = adresse
        self.date_creation = date_creation or datetime.now().strftime("%d/%m/%Y")  # Format JJ/MM/AAAA
        self.last_activity_date = last_activity_date
        self.last_payment_date = last_payment_date

    @classmethod
    def from_db(cls, row):
        """
        Crée une instance User à partir d'une ligne de la base de données.
        
        Args:
            row: Dictionnaire contenant les données de l'utilisateur
        
        Returns:
            User: Instance de l'utilisateur créée
        """
        user = cls(
            id=row['id'],
            nom=row['nom'],
            prenom=row['prenom'],
            date_naissance=row['date_naissance'],
            telephone=row['telephone'],
            email=row['email'],
            adresse=row['adresse'],
            date_creation=row['date_creation'],
            last_activity_date=row['last_activity_date'] if 'last_activity_date' in row.keys() else None,
            last_payment_date=row['last_payment_date'] if 'last_payment_date' in row.keys() else None
        )
        return user

    def to_dict(self):
        """
        Convertit l'instance en dictionnaire.
        Utilisé pour la sérialisation et l'export des données.
        
        Returns:
            dict: Dictionnaire des attributs de l'utilisateur
        """
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance,
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse,
            'date_creation': self.date_creation
        }

    def save(self, db_manager):
        """
        Sauvegarde ou met à jour l'utilisateur dans la base de données.
        Gère l'insertion d'un nouvel utilisateur ou la mise à jour d'un existant.
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        try:
            if self.id is None:
                query = """
                    INSERT INTO users (nom, prenom, date_naissance, telephone, email, adresse, date_creation, last_activity_date, last_payment_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.date_creation, self.last_activity_date, self.last_payment_date)
                cursor = db_manager.execute(query, values)
                self.id = cursor.lastrowid
                logging.info(f"Nouvel utilisateur inséré avec l'ID : {self.id}")
            else:
                query = """
                    UPDATE users
                    SET nom=?, prenom=?, date_naissance=?, telephone=?, email=?, adresse=?, date_creation=?, last_activity_date=?, last_payment_date=?
                    WHERE id=?
                """
                values = (self.nom, self.prenom, self.date_naissance, self.telephone, self.email, self.adresse, self.date_creation, self.last_activity_date, self.last_payment_date, self.id)
                db_manager.execute(query, values)
                logging.info(f"Utilisateur mis à jour avec l'ID : {self.id}")
            self.notify_observers('user_updated', self)
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de l'utilisateur : {str(e)}")
            return False

    @staticmethod
    def get_all(db_manager):
        query = "SELECT id, nom, prenom, date_naissance, telephone, email, adresse, date_creation, last_activity_date FROM users"
        rows = db_manager.fetch_all(query)
        return [User.from_db(row) for row in rows]

    @classmethod
    def get_by_id(cls, db_manager, user_id):
        query = "SELECT * FROM users WHERE id = ?"
        user_row = db_manager.fetch_one(query, (user_id,))
        if user_row:
            user_dict = dict(user_row)
            if user_dict['date_naissance']:
                user_dict['date_naissance'] = convert_from_db_date(user_dict['date_naissance'])
            return cls(**user_dict)
        return None

    @classmethod
    def get_inactive_users(cls, db_manager, inactivity_days):
        """
        Récupère les utilisateurs inactifs depuis plus de inactivity_days jours.
        Un utilisateur est considéré inactif si sa dernière activité (atelier ou création)
        est plus ancienne que la date limite.
        
        Args:
            db_manager: Instance du gestionnaire de base de données
            inactivity_days (int): Nombre de jours d'inactivité
            
        Returns:
            list[User]: Liste des utilisateurs inactifs
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
        SELECT u.* 
        FROM users u
        JOIN LastActivity la ON u.id = la.id
        WHERE la.last_activity < ?
        """
        
        rows = db_manager.fetch_all(query, (cutoff_date_str,))
        return [cls.from_db(row) for row in rows]

    def delete(self, db_manager):
        query = "DELETE FROM users WHERE id = ?"
        db_manager.execute_query(query, (self.id,))

    @staticmethod
    def delete_inactive_users(db_manager, inactive_period):
        cutoff_date = (datetime.now() - inactive_period).strftime("%Y-%m-%d %H:%M:%S")
        query = """
        DELETE FROM users
        WHERE id IN (
            SELECT u.id FROM users u
            LEFT JOIN workshops w ON u.id = w.user_id
            GROUP BY u.id
            HAVING MAX(w.date) < ? OR MAX(w.date) IS NULL
        )
        """
        db_manager.execute_query(query, (cutoff_date,))

    @property
    def last_activity_date(self):
        if not hasattr(self, '_last_activity_date'):
            self._last_activity_date = None
        return self._last_activity_date

    @last_activity_date.setter
    def last_activity_date(self, value):
        self._last_activity_date = value

    def get_last_activity_date(self, db_manager):
        query = "SELECT MAX(date) as last_activity FROM workshops WHERE user_id = ?"
        result = db_manager.fetch_one(query, (self.id,))
        last_activity = result['last_activity'] if result and result['last_activity'] else None
        self.last_activity_date = last_activity
        return self.last_activity_date

    @classmethod
    def delete(cls, db_manager, user_id):
        # Mettre à jour les ateliers associés pour définir user_id à NULL
        try:
            logging.info(f"Tentative de suppression de l'utilisateur avec l'ID {user_id}")
            db_manager.execute("UPDATE workshops SET user_id = NULL WHERE user_id = ?", (user_id,))
            # Ensuite, supprimez l'utilisateur
            db_manager.execute("DELETE FROM users WHERE id = ?", (user_id,))
            logging.info(f"Utilisateur avec l'ID {user_id} supprimé avec succès")
            return True
        except Exception as e:
            logging.error(f"Erreur lors de la suppression de l'utilisateur {user_id}: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def get_paginated(db_manager, offset, limit):
        query = "SELECT * FROM users ORDER BY nom, prenom LIMIT ? OFFSET ?"
        rows = db_manager.fetch_all(query, (limit, offset))
        return [User.from_db(row) for row in rows]

    def is_workshop_payment_up_to_date(self, db_manager):
        """
        Vérifie si l'utilisateur est à jour dans ses paiements d'ateliers.
        Calcule le nombre d'ateliers payants et les paiements effectués.
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            bool: True si l'utilisateur est à jour, False sinon
        """
        ateliers_entre_paiements = get_ateliers_entre_paiements()
        default_paid_workshops = get_default_paid_workshops()
        
        query = """
        WITH paid_workshops AS (
            SELECT ROW_NUMBER() OVER (ORDER BY date) as row_num, date, paid
            FROM workshops
            WHERE user_id = ? AND categorie IN ({}) AND paid = 1
            ORDER BY date
        )
        SELECT COUNT(*) as total_paid_workshops,
               (SELECT COUNT(*) FROM paid_workshops WHERE date <= ?) as paid_workshops_count,
               (SELECT COUNT(*) FROM paid_workshops WHERE row_num % ? = 1) as payments_made,
               (SELECT COUNT(*) FROM paid_workshops WHERE row_num > (SELECT MAX(row_num) FROM paid_workshops) - ?) as last_payment_check
        FROM paid_workshops
        """
        placeholders = ','.join(['?' for _ in default_paid_workshops])
        query = query.format(placeholders)
        
        placeholders = ','.join(['?' for _ in default_paid_workshops]) + ','
        query = query.format(placeholders)
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        result = db_manager.fetch_one(query, (self.id, *default_paid_workshops, current_date, ateliers_entre_paiements, ateliers_entre_paiements))
        
        if result:
            total_paid_workshops = result['total_paid_workshops']
            paid_workshops_count = result['paid_workshops_count']
            payments_made = result['payments_made']
            last_payment_check = result['last_payment_check']
            
            if total_paid_workshops == 0:
                return True  # Aucun atelier payant, considéré comme à jour
            
            payments_required = (total_paid_workshops - 1) // ateliers_entre_paiements + 1
            
            return payments_made >= payments_required and last_payment_check > 0
        
        return True  # En cas d'erreur, on considère l'utilisateur comme à jour

    def calculate_workshop_payment_status(self, db_manager):
        """
        Calcule le statut détaillé des paiements d'ateliers.
        Met à jour le statut interne (_payment_status).
        
        Args:
            db_manager: Gestionnaire de base de données
            
        Returns:
            str: Statut de paiement ('À jour' ou 'En retard')
        """
        # Import à l'intérieur de la méthode pour éviter les importations circulaires
        from src.models.workshop import Workshop
        
        ateliers_entre_paiements = get_ateliers_entre_paiements()
        default_paid_workshops = get_default_paid_workshops()
        
        logging.info(f"Ateliers entre paiements: {ateliers_entre_paiements}")
        logging.info(f"Ateliers payants par défaut: {default_paid_workshops}")
        
        if not default_paid_workshops:
            default_paid_workshops = ['Atelier numérique']  # Valeur par défaut
        
        # 1. Récupérer les ateliers de l'utilisateur
        workshops = Workshop.get_user_workshops(db_manager, self.id)
        paid_workshops = [w for w in workshops if w.payant]
        
        if not paid_workshops:
            logging.info("Aucun atelier payant, statut: À jour")
            self._payment_status = "À jour"
            return self._payment_status
        
        # 2. Calculer le cycle actuel et les paiements requis
        total_paid_count = len(paid_workshops)
        paid_count = sum(1 for w in paid_workshops if w.paid)
        
        current_cycle = (total_paid_count - 1) // ateliers_entre_paiements
        required_payments = current_cycle + 1
        
        logging.info(f"Total ateliers payants: {total_paid_count}, Payés: {paid_count}")
        logging.info(f"Cycle actuel: {current_cycle}, Paiements requis: {required_payments}")
        
        # 3. Déterminer le statut
        if paid_count >= required_payments:
            self._payment_status = "À jour"
            logging.info(f"Statut: À jour ({paid_count} >= {required_payments})")
        else:
            self._payment_status = "En retard"
            logging.info(f"Statut: En retard ({paid_count} < {required_payments})")
        
        return self._payment_status

    def get_workshop_payment_status(self, db_manager):
        """
        Récupère le statut de paiement sous forme de texte.
        """
        status = self.calculate_workshop_payment_status(db_manager)
        # Le statut est directement retourné sous forme de chaîne par calculate_workshop_payment_status
        return status, ""  # Retourne le statut et une chaîne vide pour les détails

    def get_full_name(self):
        """
        Retourne le nom complet de l'utilisateur (prénom + nom).
        
        Returns:
            str: Nom complet de l'utilisateur
        """
        return f"{self.prenom} {self.nom}"

    def update_last_payment_date(self, db_manager):
        """
        Met à jour la date du dernier paiement.
        Utilise la date actuelle comme date de paiement.
        
        Args:
            db_manager: Gestionnaire de base de données
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        query = "UPDATE users SET last_payment_date = ? WHERE id = ?"
        db_manager.execute(query, (current_date, self.id))

    def update_payment_status(self, db_manager):
        self.payment_status = self.get_workshop_payment_status(db_manager)

    def get_state(self):
        return {
            'id': self.id,
            'nom': self.nom,
            'prenom': self.prenom,
            'date_naissance': self.date_naissance,
            'telephone': self.telephone,
            'email': self.email,
            'adresse': self.adresse,
            'last_activity_date': self.last_activity_date
        }

    def refresh_from_db(self, db_manager):
        updated_user = User.get_by_id(db_manager, self.id)
        if updated_user:
            self.__dict__.update(updated_user.__dict__)
        self.calculate_workshop_payment_status(db_manager)
        self.notify_observers('user_updated', self)

    def get_workshops(self, db_manager):
        """
        Récupère tous les ateliers associés à cet utilisateur.
        
        Args:
            db_manager: Instance du gestionnaire de base de données
            
        Returns:
            list: Liste des ateliers associés à l'utilisateur
        """
        # Import à l'intérieur de la méthode pour éviter les importations circulaires
        from src.models.workshop import Workshop
        return Workshop.get_by_user(db_manager, self.id) if self.id else []

    def refresh_user_list(self):
        # Code pour rafraîchir la liste des utilisateurs
        self.load_users()

    def refresh_workshop_list(self):
        # Si nécessaire, ajoutez du code pour rafraîchir la liste des ateliers
        pass

    def update_last_activity_date(self, db_manager, activity_date):
        if not self.last_activity_date or activity_date > self.last_activity_date:
            self.last_activity_date = activity_date
            query = "UPDATE users SET last_activity_date = ? WHERE id = ?"
            db_manager.execute(query, (activity_date, self.id))

    @classmethod
    def search(cls, db_manager, search_term):
        """
        Recherche des utilisateurs par nom, prénom, téléphone ou email.
        
        Args:
            db_manager: Gestionnaire de base de données
            search_term (str): Terme de recherche
            
        Returns:
            list: Liste des utilisateurs correspondant aux critères
        """
        search_pattern = f"%{search_term}%"
        query = """
            SELECT * FROM users 
            WHERE nom LIKE ? 
            OR prenom LIKE ? 
            OR telephone LIKE ? 
            OR email LIKE ?
            ORDER BY nom, prenom
        """
        rows = db_manager.fetch_all(query, (search_pattern, search_pattern, search_pattern, search_pattern))
        return [cls.from_db(row) for row in rows]



