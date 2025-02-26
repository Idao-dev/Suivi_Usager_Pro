import unittest
from src.utils.date_utils import is_valid_date, convert_to_db_date, convert_from_db_date
from src.utils.csv_import_export import CSVExporter
from tests.test_base import BaseTestCase
import os
import tempfile
import shutil
from src.models.user import User
from src.models.workshop import Workshop

class TestDateUtils(unittest.TestCase):
    def test_is_valid_date(self):
        self.assertTrue(is_valid_date("01/01/2023"))
        self.assertFalse(is_valid_date("2023-01-01"))
        self.assertFalse(is_valid_date("01-01-2023"))

    def test_convert_to_db_date(self):
        self.assertEqual(convert_to_db_date("01/01/2023"), "2023-01-01")

    def test_convert_from_db_date(self):
        self.assertEqual(convert_from_db_date("2023-01-01"), "01/01/2023")

class TestCSVExport(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Créer un répertoire temporaire pour les exports de test
        self.temp_dir = tempfile.mkdtemp()
        # Créer un exportateur
        self.exporter = CSVExporter(self.db_manager)
        # Sauvegarde du répertoire d'export original
        self.original_export_dir = self.exporter.export_dir
        # Modification pour utiliser le répertoire temporaire
        self.exporter.export_dir = self.temp_dir

    def tearDown(self):
        # Restauration du répertoire d'export original
        self.exporter.export_dir = self.original_export_dir
        # Suppression du répertoire temporaire
        shutil.rmtree(self.temp_dir)
        super().tearDown()

    def test_export_users(self):
        # Ajouter des utilisateurs de test à la base de données
        user = User(nom="Test", prenom="User", telephone="1234567890")
        user.save(self.db_manager)
        
        success, filepath = self.exporter.export_users()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))
        self.assertIn('users_', os.path.basename(filepath))
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('ID,Nom,Prénom,Date de naissance,Téléphone,Email,Adresse', content)

    def test_export_workshops(self):
        # Ajouter un atelier de test à la base de données
        user = User(nom="Test", prenom="User", telephone="1234567890")
        user.save(self.db_manager)
        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Test", conseiller="Test Conseiller")
        workshop.save(self.db_manager)
        
        success, filepath = self.exporter.export_workshops()
        self.assertTrue(success)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.csv'))
        self.assertIn('workshops_', os.path.basename(filepath))
        
        # Vérifier le contenu du fichier
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('ID,User ID,Description,Catégorie,Payant,Payé,Date,Conseiller', content)

if __name__ == '__main__':
    unittest.main()
