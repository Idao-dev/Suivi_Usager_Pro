"""
Module de gestion des imports/exports CSV pour la sauvegarde et la restauration des données.
Permet d'exporter et d'importer les données des utilisateurs et des ateliers au format CSV.

Fonctionnalités principales :
- Export des utilisateurs et de leurs données
- Export des ateliers et de leurs détails
- Import de données avec vérification et validation
- Gestion des erreurs et logging détaillé
"""

import csv
import logging
from src.utils.date_utils import convert_from_db_date, is_valid_date, convert_to_db_date
import os
from datetime import datetime
from src.models.user import User
from src.models.workshop import Workshop
from src.utils.observer import Observable

# Configuration du logging pour le suivi des opérations
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='w')

class CSVExporter(Observable):
    """
    Classe gérant l'export et l'import des données au format CSV.
    Hérite de Observable pour notifier les changements aux observateurs.
    
    Attributs:
        db_manager: Gestionnaire de base de données
        export_dir: Répertoire de destination des exports
    """

    def __init__(self, db_manager):
        """
        Initialise l'exportateur CSV.
        
        Args:
            db_manager: Instance du gestionnaire de base de données
            
        Le répertoire d'export est créé s'il n'existe pas.
        En cas d'erreur, utilise le répertoire utilisateur comme fallback.
        """
        super().__init__()
        self.db_manager = db_manager
        self.export_dir = os.path.join(os.path.dirname(db_manager.db_path), 'exports')
        try:
            if not os.path.exists(self.export_dir):
                os.makedirs(self.export_dir)
            logging.info(f"Répertoire d'exportation : {self.export_dir}")
        except OSError as e:
            logging.error(f"Impossible de créer le répertoire d'exportation : {e}")
            self.export_dir = os.path.expanduser("~")
            logging.info(f"Utilisation du répertoire alternatif : {self.export_dir}")

    def export_users(self, filename=None):
        """
        Exporte tous les utilisateurs dans un fichier CSV.
        Le nom du fichier inclut un horodatage pour éviter les écrasements si aucun nom n'est spécifié.
        
        Args:
            filename (str, optional): Chemin du fichier de sortie. Si non spécifié, un nom sera généré.
            
        Returns:
            tuple: (bool, str) Succès/échec et chemin du fichier ou message d'erreur
        """
        if filename is None:
            file_path = os.path.join(self.export_dir, f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        else:
            file_path = filename

        try:
            users = self.db_manager.get_all_users()
            logging.info(f"Nombre d'utilisateurs récupérés : {len(users)}")
            for user in users:
                logging.debug(f"Utilisateur : {vars(user)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # En-têtes des colonnes
                writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Téléphone', 
                               'Email', 'Adresse', 'Date de création', 'Dernière activité', 
                               'Dernier paiement'])
                # Données des utilisateurs
                for user in users:
                    writer.writerow([
                        user.id,
                        user.nom,
                        user.prenom,
                        convert_from_db_date(user.date_naissance) if user.date_naissance else '',
                        user.telephone,
                        user.email,
                        user.adresse,
                        convert_from_db_date(user.date_creation),
                        convert_from_db_date(user.last_activity_date) if user.last_activity_date else '',
                        convert_from_db_date(user.last_payment_date) if user.last_payment_date else ''
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des utilisateurs : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des utilisateurs : {str(e)}"

    def export_workshops(self):
        """
        Exporte tous les ateliers dans un fichier CSV.
        Le nom du fichier inclut un horodatage pour éviter les écrasements.
        
        Returns:
            tuple: (bool, str) Succès/échec et chemin du fichier ou message d'erreur
        """
        file_path = os.path.join(self.export_dir, f"workshops_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

        try:
            workshops = self.db_manager.get_all_workshops()
            logging.info(f"Nombre d'ateliers récupérés : {len(workshops)}")
            for workshop in workshops:
                logging.debug(f"Atelier : {vars(workshop)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # En-têtes des colonnes
                writer.writerow(['ID', 'User ID', 'Description', 'Catégorie', 'Payant', 
                               'Payé', 'Date', 'Conseiller'])
                # Données des ateliers
                for workshop in workshops:
                    writer.writerow([
                        workshop.id,
                        workshop.user_id,
                        workshop.description,
                        workshop.categorie,
                        'Oui' if workshop.payant else 'Non',
                        'Oui' if workshop.paid else 'Non',
                        convert_from_db_date(workshop.date) if workshop.date else '',
                        workshop.conseiller
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des ateliers : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des ateliers : {str(e)}"

    def export_all_data(self):
        """
        Exporte à la fois les utilisateurs et les ateliers dans des fichiers CSV distincts.
        
        Returns:
            tuple: (bool, str) Succès/échec et message de résultat
        """
        try:
            # Exporter les utilisateurs
            users_success, users_path = self.export_users()
            if not users_success:
                return False, f"Échec de l'exportation des utilisateurs: {users_path}"
            
            # Exporter les ateliers
            workshops_success, workshops_path = self.export_workshops()
            if not workshops_success:
                return False, f"Échec de l'exportation des ateliers: {workshops_path}"
            
            return True, f"Utilisateurs exportés vers {users_path}\nAteliers exportés vers {workshops_path}"
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation complète des données : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des données : {str(e)}"

    def import_data(self, file_path):
        """
        Importe des données depuis un fichier CSV.
        Détecte automatiquement le type de données (utilisateurs ou ateliers).
        Utilise des transactions pour garantir l'intégrité des données.
        
        Args:
            file_path (str): Chemin du fichier CSV à importer
            
        Returns:
            tuple: (bool, str) Succès/échec et message de résultat
        """
        try:
            logging.info(f"Début de l'importation du fichier : {file_path}")
            self.db_manager.begin_transaction()
            logging.info("Transaction commencée")

            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                # Détection automatique du format CSV
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                reader = csv.reader(csvfile, dialect)
                headers = next(reader)
                logging.info(f"En-têtes détectés : {headers}")

                imported_count = {'users': 0, 'workshops': 0}
                errors = []

                # Détection du type de données et import
                if 'Nom' in headers and 'Prénom' in headers:
                    logging.info("Importation d'utilisateurs détectée")
                    for row in reader:
                        try:
                            user = self.import_user(dict(zip(headers, row)))
                            user.save(self.db_manager)
                            logging.info(f"Utilisateur importé avec succès : ID {user.id}")
                            imported_count['users'] += 1
                        except Exception as e:
                            error_msg = f"Erreur lors de l'importation de l'utilisateur {row[0]} {row[1]}: {str(e)}"
                            logging.error(error_msg)
                            errors.append(error_msg)
                elif 'User ID' in headers and all(header in headers for header in ['Description', 'Catégorie', 'Payant', 'Payé', 'Date', 'Conseiller']):
                    logging.info("Importation d'ateliers détectée")
                    for row in reader:
                        try:
                            workshop = self.import_workshop(dict(zip(headers, row)))
                            workshop.save(self.db_manager)
                            logging.info(f"Atelier importé avec succès : ID {workshop.id}")
                            imported_count['workshops'] += 1
                        except Exception as e:
                            error_msg = f"Erreur lors de l'importation de l'atelier pour l'utilisateur {row[headers.index('User ID')]}: {str(e)}"
                            logging.error(error_msg)
                            errors.append(error_msg)
                else:
                    logging.error(f"Format de fichier non reconnu. En-têtes : {headers}")
                    self.db_manager.rollback_transaction()
                    return False, "Format de fichier non reconnu. Assurez-vous d'importer un fichier CSV d'utilisateurs ou d'ateliers valide."

            self.db_manager.commit_transaction()
            logging.info("Transaction validée avec succès")
            logging.info(f"Importation terminée. Utilisateurs importés : {imported_count['users']}, Ateliers importés : {imported_count['workshops']}")
            return True, f"Importation réussie. {imported_count['users']} utilisateurs et {imported_count['workshops']} ateliers importés."

        except Exception as e:
            self.db_manager.rollback_transaction()
            logging.error(f"Erreur lors de l'importation : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'importation : {str(e)}"

    def _verify_imported_users(self, imported_ids):
        """
        Vérifie que les utilisateurs ont été correctement importés.
        
        Args:
            imported_ids (list): Liste des IDs des utilisateurs importés
        """
        check_query = "SELECT COUNT(*) as count FROM users WHERE id = ?"
        for user_id in imported_ids:
            result = self.db_manager.fetch_one(check_query, (user_id,))
            if result['count'] == 0:
                logging.error(f"L'utilisateur avec l'ID {user_id} n'a pas été importé correctement.")

    def _verify_imported_workshops(self, imported_ids):
        """
        Vérifie que les ateliers ont été correctement importés.
        
        Args:
            imported_ids (list): Liste des IDs des ateliers importés
        """
        check_query = "SELECT COUNT(*) as count FROM workshops WHERE id = ?"
        for workshop_id in imported_ids:
            result = self.db_manager.fetch_one(check_query, (workshop_id,))
            if result['count'] == 0:
                logging.error(f"L'atelier avec l'ID {workshop_id} n'a pas été importé correctement.")

    def import_user(self, row):
        """
        Crée un objet User à partir d'une ligne CSV.
        
        Args:
            row (dict): Dictionnaire contenant les données de l'utilisateur
            
        Returns:
            User: Instance de l'utilisateur créée
            
        Raises:
            ValueError: Si des données sont manquantes ou invalides
        """
        try:
            user = User(
                nom=row['Nom'],
                prenom=row.get('Prénom', ''),
                date_naissance=convert_to_db_date(row.get('Date de naissance', '')) if row.get('Date de naissance') else None,
                telephone=row.get('Téléphone', ''),
                email=row.get('Email', ''),
                adresse=row.get('Adresse', ''),
                date_creation=convert_to_db_date(row.get('Date de création', '')) if row.get('Date de création') else None,
                last_activity_date=convert_to_db_date(row.get('Dernière activité', '')) if row.get('Dernière activité') else None,
                last_payment_date=convert_to_db_date(row.get('Dernier paiement', '')) if row.get('Dernier paiement') else None
            )
            return user
        except KeyError as e:
            raise ValueError(f"Champ manquant dans les données utilisateur : {str(e)}")
        except ValueError as e:
            raise ValueError(f"Erreur de conversion de données pour l'utilisateur : {str(e)}")

    def import_workshop(self, row):
        """
        Crée un objet Workshop à partir d'une ligne CSV.
        Gère les différents formats de date possibles.
        
        Args:
            row (dict): Dictionnaire contenant les données de l'atelier
            
        Returns:
            Workshop: Instance de l'atelier créée
            
        Raises:
            ValueError: Si des données sont manquantes ou invalides
        """
        try:
            date = row['Date']
            if date:
                # Essayer d'abord le format JJ/MM/YYYY
                try:
                    date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
                except ValueError:
                    # Si ça échoue, essayer le format YYYY-MM-DD
                    date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            workshop = Workshop(
                user_id=int(row['User ID']) if row['User ID'] else None,
                description=row['Description'],
                categorie=row['Catégorie'],
                payant=row['Payant'] == 'Oui',
                paid=row.get('Payé', 'Non') == 'Oui',
                date=date,
                conseiller=row['Conseiller']
            )
            
            # Mise à jour de la date de dernière activité de l'utilisateur
            if workshop.user_id and workshop.date:
                workshop_date = datetime.strptime(workshop.date, "%Y-%m-%d")
                if (datetime.now() - workshop_date).days <= 365:
                    user = User.get_by_id(self.db_manager, workshop.user_id)
                    if user:
                        user.update_last_activity_date(self.db_manager, workshop.date)
            
            return workshop
        except KeyError as e:
            raise ValueError(f"Champ manquant dans les données de l'atelier : {str(e)}")
        except ValueError as e:
            raise ValueError(f"Erreur de conversion de données pour l'atelier : {str(e)}")

    def export_specific_users(self, users, filename=None):
        """
        Exporte une liste spécifique d'utilisateurs dans un fichier CSV.
        
        Args:
            users (list[User]): Liste des utilisateurs à exporter
            filename (str, optional): Chemin du fichier de sortie. Si non spécifié, un nom sera généré.
            
        Returns:
            tuple: (bool, str) Succès/échec et chemin du fichier ou message d'erreur
        """
        if filename is None:
            file_path = os.path.join(self.export_dir, f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        else:
            file_path = filename

        try:
            logging.info(f"Export de {len(users)} utilisateurs spécifiques")
            for user in users:
                logging.debug(f"Utilisateur à exporter : {vars(user)}")

            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # En-têtes des colonnes
                writer.writerow(['ID', 'Nom', 'Prénom', 'Date de naissance', 'Téléphone', 
                               'Email', 'Adresse', 'Date de création', 'Dernière activité', 
                               'Dernier paiement'])
                # Données des utilisateurs
                for user in users:
                    writer.writerow([
                        user.id,
                        user.nom,
                        user.prenom,
                        convert_from_db_date(user.date_naissance) if user.date_naissance else '',
                        user.telephone,
                        user.email,
                        user.adresse,
                        convert_from_db_date(user.date_creation),
                        convert_from_db_date(user.last_activity_date) if user.last_activity_date else '',
                        convert_from_db_date(user.last_payment_date) if user.last_payment_date else ''
                    ])
            return True, file_path
        except Exception as e:
            logging.error(f"Erreur lors de l'exportation des utilisateurs spécifiques : {str(e)}", exc_info=True)
            return False, f"Une erreur s'est produite lors de l'exportation des utilisateurs : {str(e)}"
