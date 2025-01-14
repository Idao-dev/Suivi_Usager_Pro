"""
Module de gestion de la base de données SQLite.
Fournit une interface pour interagir avec la base de données de manière sécurisée.
Gère les connexions, transactions et opérations CRUD sur les données.
"""

import sqlite3
import os
import logging
from contextlib import contextmanager
from src.models.user import User
from src.models.workshop import Workshop
import sys

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Gestionnaire de base de données SQLite.
    Gère la connexion, l'initialisation et les opérations sur la base de données.
    Implémente des méthodes sécurisées pour les transactions et requêtes.
    """
    
    def __init__(self, db_path):
        """
        Initialise le gestionnaire de base de données.
        
        Args:
            db_path: Chemin vers le fichier de base de données SQLite
        """
        self.db_path = db_path
        self.connection = None

    def initialize(self):
        """
        Initialise la base de données avec le schéma SQL.
        Crée les tables et colonnes nécessaires si elles n'existent pas.
        Gère les différents environnements (développement/production).
        
        Raises:
            FileNotFoundError: Si le fichier schema.sql n'est pas trouvé
            Exception: Pour toute autre erreur d'initialisation
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Déterminer le chemin correct vers schema.sql
                if getattr(sys, 'frozen', False):
                    # Si l'application est "gelée" (exécutable)
                    application_path = sys._MEIPASS
                else:
                    # Si l'application est en cours d'exécution à partir du script
                    application_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                schema_path = os.path.join(application_path, 'database', 'schema.sql')
                
                logging.info(f"Chemin du schéma SQL : {schema_path}")
                if not os.path.exists(schema_path):
                    logging.error(f"Le fichier schema.sql n'existe pas à l'emplacement : {schema_path}")
                    raise FileNotFoundError(f"schema.sql non trouvé : {schema_path}")
                
                with open(schema_path, 'r', encoding='utf-8', errors='ignore') as schema_file:
                    schema = schema_file.read()
                cursor.executescript(schema)
            logging.info("Base de données initialisée avec succès.")
        except Exception as e:
            logging.error(f"Erreur détaillée lors de l'initialisation de la base de données : {str(e)}")
            logging.error(f"Chemin de la base de données : {self.db_path}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Gestionnaire de contexte pour obtenir une connexion à la base de données.
        Assure la fermeture automatique de la connexion après utilisation.
        Configure l'encodage UTF-8 et le format des lignes.
        
        Yields:
            sqlite3.Connection: Connexion à la base de données
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Configurer l'encodage UTF-8 pour SQLite
            conn.execute('PRAGMA encoding = "UTF-8"')
            yield conn
        finally:
            conn.close()

    def execute(self, query, params=None):
        """
        Exécute une requête SQL avec paramètres optionnels.
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres de la requête (optionnel)
            
        Returns:
            sqlite3.Cursor: Curseur après exécution de la requête
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor

    def fetch_one(self, query, params=None):
        """
        Récupère une seule ligne de résultat d'une requête.
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres de la requête (optionnel)
            
        Returns:
            sqlite3.Row: Ligne de résultat ou None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()

    def fetch_all(self, query, params=None):
        """
        Récupère toutes les lignes de résultat d'une requête.
        
        Args:
            query: Requête SQL à exécuter
            params: Paramètres de la requête (optionnel)
            
        Returns:
            list[sqlite3.Row]: Liste des lignes de résultat
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def create_tables(self, connection):
        with open('database/schema.sql', 'r', encoding='utf-8') as schema_file:
            schema = schema_file.read()
        connection.executescript(schema)

    def get_last_insert_id(self):
        return self.fetch_one("SELECT last_insert_rowid()")[0]

    # Méthodes pour les utilisateurs
    def get_all_users(self):
        rows = self.fetch_all("SELECT * FROM users")
        return [User.from_db(row) for row in rows]

    def _soundex(self, s):
        """
        Méthode privée implémentant l'algorithme Soundex pour la recherche phonétique.
        
        Args:
            s (str): Chaîne à convertir en code Soundex
            
        Returns:
            str: Code Soundex de la chaîne (4 caractères)
        """
        if not s:
            return "0000"
        
        # Conversion en majuscules et suppression des caractères non alphabétiques
        s = ''.join(c for c in s.upper() if c.isalpha())
        if not s:
            return "0000"
        
        # Table de conversion Soundex
        soundex_table = {
            'BFPV': '1', 'CGJKQSXZ': '2', 'DT': '3',
            'L': '4', 'MN': '5', 'R': '6'
        }
        
        # Première lettre + conversion des autres lettres
        code = s[0]
        previous = '0'
        
        for char in s[1:]:
            current = '0'
            for key in soundex_table:
                if char in key:
                    current = soundex_table[key]
                    break
            if current != '0' and current != previous:
                code += current
            previous = current
        
        # Ajustement à 4 caractères
        code = code.ljust(4, '0')
        return code[:4]

    def _levenshtein_distance(self, s1, s2):
        """
        Méthode privée calculant la distance de Levenshtein entre deux chaînes.
        
        Args:
            s1 (str): Première chaîne
            s2 (str): Deuxième chaîne
            
        Returns:
            int: Distance de Levenshtein (nombre minimum de modifications)
        """
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def search_users(self, search_term):
        """
        Recherche intelligente d'utilisateurs avec une approche en plusieurs étapes.
        Les étapes sont appliquées dans l'ordre jusqu'à obtenir suffisamment de résultats.
        
        1. Recherche exacte (=)
        2. Recherche phonétique (Soundex) si le terme ressemble à un nom
        3. Recherche partielle (LIKE) si pas assez de résultats
        4. Recherche approximative (Levenshtein) si toujours pas assez de résultats
        
        Args:
            search_term (str): Terme de recherche
            
        Returns:
            list[User]: Liste des utilisateurs correspondants
        """
        logging.info(f"Début de la recherche pour le terme : {search_term}")
        results = []
        
        # Étape 1 : Recherche exacte
        query = """
        SELECT * FROM users 
        WHERE nom = ? OR prenom = ? OR telephone = ? OR email = ?
        """
        rows = self.fetch_all(query, (search_term,) * 4)
        results = [User.from_db(row) for row in rows]
        
        # Si on a des résultats exacts et que ce n'est pas un nom, on retourne directement
        if results and not (search_term and search_term[0].isupper()):
            logging.info(f"Recherche exacte : {len(results)} résultats trouvés")
            return results
        
        # Récupérer tous les utilisateurs pour les recherches avancées
        all_users = self.fetch_all("SELECT * FROM users")
        
        # Si le terme ressemble à un nom (commence par une majuscule), on ajoute Soundex
        if search_term and search_term[0].isupper():
            logging.info("Application de Soundex pour les noms similaires")
            search_soundex = self._soundex(search_term)
            
            # Si on a une correspondance exacte, on cherche uniquement les variantes phonétiques
            if results:
                nom_recherche = results[0].nom
                for row in all_users:
                    user = User.from_db(row)
                    if user not in results and self._soundex(user.nom) == self._soundex(nom_recherche):
                        results.append(user)
            else:
                # Sinon, on cherche les correspondances Soundex sur les noms uniquement
                for row in all_users:
                    user = User.from_db(row)
                    if user not in results:  # Éviter les doublons
                        nom_soundex = self._soundex(user.nom)
                        if search_soundex == nom_soundex:  # Comparaison stricte sur les noms
                            results.append(user)
        
        # Si on a assez de résultats après Soundex, on retourne
        if len(results) >= 4:
            logging.info(f"Recherche exacte + Soundex : {len(results)} résultats trouvés")
            return results[:4]  # Limiter à 4 résultats
            
        # Étape 2 : Recherche partielle avec LIKE
        if len(results) < 4:
            query = """
            SELECT * FROM users 
            WHERE nom LIKE ? OR prenom LIKE ? OR telephone LIKE ? OR email LIKE ?
            """
            search_pattern = f"%{search_term}%"
            rows = self.fetch_all(query, (search_pattern,) * 4)
            for row in rows:
                user = User.from_db(row)
                if user not in results:  # Éviter les doublons
                    results.append(user)
                    if len(results) >= 4:
                        break
        
        if len(results) >= 4:
            logging.info(f"Recherche LIKE : {len(results)} résultats trouvés")
            return results[:4]  # Limiter à 4 résultats
        
        # Étape 3 : Distance de Levenshtein
        logging.info("Moins de 4 résultats, application de Levenshtein")
        max_distance = 2  # Distance maximale acceptable
        
        # Si on cherche un nom (majuscule), on applique Levenshtein uniquement sur les noms
        if search_term and search_term[0].isupper():
            # Chercher d'abord les correspondances exactes avec Levenshtein
            distance_1_matches = []
            distance_2_matches = []
            
            for row in all_users:
                user = User.from_db(row)
                if user not in results:  # Éviter les doublons
                    nom_distance = self._levenshtein_distance(search_term.lower(), user.nom.lower())
                    if nom_distance == 1:
                        distance_1_matches.append(user)
                    elif nom_distance == 2:
                        distance_2_matches.append(user)
            
            # Ajouter d'abord les correspondances à distance 1
            results.extend(distance_1_matches)
            if len(results) < 4:
                # Puis les correspondances à distance 2 si nécessaire
                results.extend(distance_2_matches[:4 - len(results)])
        else:
            # Pour les autres recherches, utiliser la distance sur tous les champs
            levenshtein_results = []
            for row in all_users:
                user = User.from_db(row)
                if user not in results:  # Éviter les doublons
                    nom_distance = self._levenshtein_distance(search_term.lower(), user.nom.lower())
                    prenom_distance = self._levenshtein_distance(search_term.lower(), user.prenom.lower())
                    min_distance = min(nom_distance, prenom_distance)
                    if min_distance <= max_distance:
                        levenshtein_results.append((user, min_distance))
            
            # Trier par distance et ajouter les résultats
            levenshtein_results.sort(key=lambda x: x[1])
            for user, _ in levenshtein_results[:4 - len(results)]:
                results.append(user)
        
        logging.info(f"Recherche finale : {len(results)} résultats trouvés")
        return results[:4]  # Assurer la limite de 4 résultats

    # Méthodes pour les ateliers
    def get_all_workshops(self):
        rows = self.fetch_all("SELECT * FROM workshops")
        return [Workshop.from_db(row) for row in rows]

    # Méthodes privées pour l'ajout de colonnes
    def _add_columns(self):
        """
        Ajoute les colonnes supplémentaires aux tables existantes.
        Méthode privée appelée lors de l'initialisation.
        """
        self._add_last_activity_date_column()
        self._add_last_payment_date_column()
        self._add_paid_today_column()

    def _add_last_activity_date_column(self):
        self._add_column_if_not_exists('users', 'last_activity_date', 'TEXT')

    def _add_last_payment_date_column(self):
        self._add_column_if_not_exists('users', 'last_payment_date', 'TEXT')

    def _add_paid_today_column(self):
        self._add_column_if_not_exists('workshops', 'paid_today', 'INTEGER DEFAULT 0')

    def _add_column_if_not_exists(self, table, column, data_type):
        """
        Ajoute une colonne à une table si elle n'existe pas déjà.
        
        Args:
            table: Nom de la table
            column: Nom de la colonne à ajouter
            data_type: Type de données SQL de la colonne
        """
        columns = self.fetch_all(f"PRAGMA table_info({table});")
        if column not in [col['name'] for col in columns]:
            self.execute(f"ALTER TABLE {table} ADD COLUMN {column} {data_type};")
            logging.info(f"Colonne {column} ajoutée avec succès à la table {table}.")
        else:
            logging.info(f"La colonne {column} existe déjà dans la table {table}.")

    def commit(self):
        with self.get_connection() as conn:
            conn.commit()

    def rollback(self):
        with self.get_connection() as conn:
            conn.rollback()

    def close(self):
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.ProgrammingError:
                logging.warning("Tentative de fermeture d'une connexion déjà fermée.")
            finally:
                self.connection = None
        logging.info("Connexion à la base de données fermée.")

    def get_connection(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.connection.row_factory = sqlite3.Row
            except sqlite3.OperationalError as e:
                logging.error(f"Erreur lors de la connexion à la base de données : {e}")
                # Vérifier si le dossier parent existe
                parent_dir = os.path.dirname(self.db_path)
                if not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir)
                        logging.info(f"Dossier créé : {parent_dir}")
                        # Réessayer la connexion
                        self.connection = sqlite3.connect(self.db_path)
                        self.connection.row_factory = sqlite3.Row
                    except Exception as e:
                        logging.error(f"Impossible de créer le dossier de la base de données : {e}")
                        raise
                else:
                    raise
        return self.connection

    def begin_transaction(self):
        """
        Démarre une nouvelle transaction SQL.
        Doit être suivie de commit_transaction() ou rollback_transaction().
        """
        self.connection.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        """
        Valide la transaction en cours.
        Enregistre définitivement les modifications dans la base de données.
        """
        self.connection.commit()

    def rollback_transaction(self):
        """
        Annule la transaction en cours.
        Annule toutes les modifications effectuées depuis le début de la transaction.
        """
        self.connection.rollback()

    def add_user(self, user):
        """
        Ajoute un nouvel utilisateur dans la base de données.
        
        Args:
            user (User): L'objet utilisateur à ajouter
            
        Returns:
            int: L'ID de l'utilisateur ajouté
        """
        query = """
        INSERT INTO users (nom, prenom, date_naissance, telephone, email, adresse)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (user.nom, user.prenom, user.date_naissance, user.telephone, user.email, user.adresse)
        self.execute(query, params)
        return self.get_last_insert_id()

    def add_workshop(self, workshop):
        """
        Ajoute un nouvel atelier dans la base de données.
        
        Args:
            workshop (Workshop): L'objet atelier à ajouter
            
        Returns:
            int: L'ID de l'atelier ajouté
        """
        query = """
        INSERT INTO workshops (user_id, description, categorie, payant, paid, date, conseiller)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (workshop.user_id, workshop.description, workshop.categorie, 
                 workshop.payant, workshop.paid, workshop.date, workshop.conseiller)
        self.execute(query, params)
        return self.get_last_insert_id()

    def get_user(self, user_id):
        """
        Récupère un utilisateur par son ID.
        
        Args:
            user_id (int): L'ID de l'utilisateur
            
        Returns:
            User: L'objet utilisateur ou None si non trouvé
        """
        query = "SELECT * FROM users WHERE id = ?"
        result = self.fetch_one(query, (user_id,))
        if result:
            return User(**result)
        return None

    def get_workshop(self, workshop_id):
        """
        Récupère un atelier par son ID.
        
        Args:
            workshop_id (int): L'ID de l'atelier
            
        Returns:
            Workshop: L'objet atelier ou None si non trouvé
        """
        query = "SELECT * FROM workshops WHERE id = ?"
        result = self.fetch_one(query, (workshop_id,))
        if result:
            return Workshop(**result)
        return None

    def get_user_workshops(self, user_id):
        """
        Récupère tous les ateliers d'un utilisateur.
        
        Args:
            user_id (int): L'ID de l'utilisateur
            
        Returns:
            list[Workshop]: Liste des ateliers de l'utilisateur
        """
        query = "SELECT * FROM workshops WHERE user_id = ? ORDER BY date DESC"
        results = self.fetch_all(query, (user_id,))
        return [Workshop(**row) for row in results]
