import unittest
import os
import sys
import tempfile
import csv
import logging

# Ajoutez le répertoire racine du projet au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database.db_manager import DatabaseManager
from src.utils.csv_import_export import CSVExporter
from src.models.user import User
from src.models.workshop import Workshop

class TestCSVImport(unittest.TestCase):
    def setUp(self):
        # Créer une base de données temporaire pour les tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.initialize()
        self.csv_exporter = CSVExporter(self.db_manager)

    def tearDown(self):
        self.db_manager.close()
        self.temp_db.close()
        try:
            os.unlink(self.temp_db.name)
        except PermissionError:
            pass  # Ignorer l'erreur si le fichier ne peut pas être supprimé immédiatement

    def create_temp_csv(self, data, headers):
        temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, newline='', suffix='.csv', encoding='utf-8')
        writer = csv.DictWriter(temp_csv, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        temp_csv.close()
        return temp_csv.name

    def test_import_users(self):
        # Vérifier que la base de données est vide avant l'importation
        users_before = User.get_all(self.db_manager)
        self.assertEqual(len(users_before), 0, "La base de données n'est pas vide avant l'importation")

        # Créer un fichier CSV temporaire avec des données utilisateur
        user_data = [
            {"ID": "1", "Nom": "Doe", "Prénom": "John", "Date de naissance": "01/01/1990", "Téléphone": "0123456789", "Email": "john@example.com", "Adresse": "123 Rue Test"},
            {"ID": "2", "Nom": "Smith", "Prénom": "Jane", "Date de naissance": "02/02/1995", "Téléphone": "9876543210", "Email": "jane@example.com", "Adresse": "456 Avenue Test"}
        ]
        user_headers = ["ID", "Nom", "Prénom", "Date de naissance", "Téléphone", "Email", "Adresse"]
        user_csv = self.create_temp_csv(user_data, user_headers)

        # Importer les utilisateurs
        success, message = self.csv_exporter.import_data(user_csv)
        self.assertTrue(success, f"L'importation a échoué : {message}")

        # Vérifier que les utilisateurs ont été importés
        users = User.get_all(self.db_manager)
        self.assertEqual(len(users), 2, "Le nombre d'utilisateurs importés ne correspond pas")
        self.assertEqual(users[0].nom, "Doe")
        self.assertEqual(users[1].nom, "Smith")

        os.unlink(user_csv)

    def test_import_workshops(self):
        # Vérifier que la base de données est vide avant l'importation
        workshops_before = Workshop.get_all(self.db_manager)
        self.assertEqual(len(workshops_before), 0, "La base de données n'est pas vide avant l'importation")

        # Créer un fichier CSV temporaire avec des données d'atelier
        workshop_data = [
            {"User ID": "1", "Description": "Atelier 1", "Catégorie": "Atelier numérique", "Payant": "Oui", "Payé": "Oui", "Date": "01/03/2023", "Conseiller": "Conseiller 1"},
            {"User ID": "2", "Description": "Atelier 2", "Catégorie": "Démarche administrative", "Payant": "Non", "Payé": "Non", "Date": "02/03/2023", "Conseiller": "Conseiller 2"}
        ]
        workshop_headers = ["User ID", "Description", "Catégorie", "Payant", "Payé", "Date", "Conseiller"]
        workshop_csv = self.create_temp_csv(workshop_data, workshop_headers)

        # Importer les ateliers
        success, message = self.csv_exporter.import_data(workshop_csv)
        self.assertTrue(success, f"L'importation a échoué : {message}")

        # Vérifier que les ateliers ont été importés
        workshops = Workshop.get_all(self.db_manager)
        self.assertEqual(len(workshops), 2, "Le nombre d'ateliers importés ne correspond pas")
        self.assertEqual(workshops[0].categorie, "Atelier numérique")
        self.assertEqual(workshops[1].categorie, "Démarche administrative")

        os.unlink(workshop_csv)

    def test_import_invalid_data(self):
        # Créer un fichier CSV temporaire avec des données invalides
        invalid_data = [
            {"Invalid": "Data"}
        ]
        invalid_headers = ["Invalid"]
        invalid_csv = self.create_temp_csv(invalid_data, invalid_headers)

        # Tenter d'importer les données invalides
        success, message = self.csv_exporter.import_data(invalid_csv)
        self.assertFalse(success, "L'importation de données invalides aurait dû échouer")

        os.unlink(invalid_csv)

    def test_import_real_workshops(self):
        # Créer un fichier CSV temporaire avec des données d'atelier réalistes
        workshop_data = [
            {"User ID": "1", "Description": "Atelier Informatique", "Catégorie": "Atelier numérique", "Payant": "Oui", "Payé": "Oui", "Date": "01/03/2023", "Conseiller": "Idao"},
            {"User ID": "2", "Description": "Aide Formulaire", "Catégorie": "Démarche administrative", "Payant": "Non", "Payé": "Non", "Date": "02/03/2023", "Conseiller": "Idao"},
            {"User ID": "3", "Description": "Formation Excel", "Catégorie": "Atelier numérique", "Payant": "Oui", "Payé": "Non", "Date": "03/03/2023", "Conseiller": "Idao"},
            {"User ID": "4", "Description": "Création Email", "Catégorie": "Atelier numérique", "Payant": "Non", "Payé": "Non", "Date": "04/03/2023", "Conseiller": "Idao"},
            {"User ID": "5", "Description": "Démarche CAF", "Catégorie": "Démarche administrative", "Payant": "Non", "Payé": "Non", "Date": "05/03/2023", "Conseiller": "Idao"}
        ]
        workshop_headers = ["User ID", "Description", "Catégorie", "Payant", "Payé", "Date", "Conseiller"]
        workshop_csv = self.create_temp_csv(workshop_data, workshop_headers)
        
        # Compter le nombre d'ateliers avant l'importation
        workshops_before = Workshop.get_all(self.db_manager)
        count_before = len(workshops_before)

        # Importer les ateliers
        success, message = self.csv_exporter.import_data(workshop_csv)
        self.assertTrue(success, f"L'importation a échoué : {message}")

        # Vérifier que les ateliers ont été importés
        workshops_after = Workshop.get_all(self.db_manager)
        count_after = len(workshops_after)

        # Vérifier que le nombre d'ateliers a augmenté
        self.assertGreater(count_after, count_before, "Le nombre d'ateliers n'a pas augmenté après l'importation")

        # Vérifier quelques ateliers spécifiques
        for workshop in workshops_after[-5:]:  # Vérifier les 5 derniers ateliers
            self.assertIsNotNone(workshop.id)
            self.assertIsNotNone(workshop.description)
            self.assertIn(workshop.categorie, ["Atelier numérique", "Démarche administrative"])
            self.assertIn(workshop.payant, [True, False, 1, 0])
            self.assertIn(workshop.paid, [True, False, 1, 0])
            self.assertIsNotNone(workshop.date)
            self.assertEqual(workshop.conseiller, "Idao")

        logging.info(f"Nombre d'ateliers avant importation : {count_before}")
        logging.info(f"Nombre d'ateliers après importation : {count_after}")
        logging.info(f"Nombre d'ateliers importés : {count_after - count_before}")

        os.unlink(workshop_csv)

if __name__ == '__main__':
    unittest.main()
