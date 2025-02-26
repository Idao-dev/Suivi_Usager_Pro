from tests.test_base import BaseTestCase
from src.ui.data_management import DataManagement
import customtkinter as ctk
from src.models.user import User
from src.models.workshop import Workshop
from datetime import datetime, timedelta
import unittest.mock
import tempfile
import os
from src.utils.csv_import_export import CSVExporter
from tests.unit.test_data_generator import generate_test_data
from unittest.mock import patch
import shutil

class TestDataManagement(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.root.update_appearance = lambda: None
        self.root.update_conseiller_dropdown = self.mock_update_conseiller_dropdown
        self.update_callback = lambda: None
        self.data_management = DataManagement(self.root, self.db_manager, self.update_callback)
        self.users = generate_test_data(self.db_manager)

    def mock_update_conseiller_dropdown(self):
        pass

    def test_export_csv(self):
        """Test de l'exportation des données en CSV."""
        test_dir = tempfile.mkdtemp()
        users_file = os.path.join(test_dir, "users_export.csv")
        workshops_file = os.path.join(test_dir, "workshops_export.csv")
        
        try:
            # Patch de la méthode export_users et export_workshops de CSVExporter
            with patch('src.utils.csv_import_export.CSVExporter.export_users', return_value=(True, users_file)), \
                 patch('src.utils.csv_import_export.CSVExporter.export_workshops', return_value=(True, workshops_file)), \
                 patch('src.utils.csv_import_export.CSVExporter.export_all_data', return_value=(True, f"Utilisateurs exportés dans {users_file} et ateliers exportés dans {workshops_file}")):
                
                # Appeler la méthode pour exporter en CSV
                success = self.data_management.export_csv()
                
                # Vérifier que l'export a réussi
                self.assertTrue(success)
                
        finally:
            # Nettoyage du répertoire temporaire
            shutil.rmtree(test_dir)

    # Ajoutez d'autres tests si nécessaire

    def tearDown(self):
        self.root.destroy()
        super().tearDown()
