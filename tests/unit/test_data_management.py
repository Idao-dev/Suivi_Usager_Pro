from .test_base import BaseTestCase
from ui.data_management import DataManagement
import customtkinter as ctk
from models.user import User
from models.workshop import Workshop
from datetime import datetime, timedelta
import unittest.mock
import tempfile
import os
from utils.csv_import_export import CSVExporter
from .test_data_generator import generate_test_data

class TestDataManagement(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.root.update_appearance = lambda: None
        self.root.update_conseiller_dropdown = self.mock_update_conseiller_dropdown
        self.data_management = DataManagement(self.root, self.db_manager)
        self.users = generate_test_data(self.db_manager)

    def mock_update_conseiller_dropdown(self):
        pass

    @unittest.mock.patch('tkinter.filedialog.asksaveasfilename')
    @unittest.mock.patch('tkinter.filedialog.askdirectory')
    def test_export_csv(self, mock_askdirectory, mock_asksaveasfilename):
        with tempfile.TemporaryDirectory() as tmpdirname:
            mock_askdirectory.return_value = tmpdirname
            self.data_management.export_var.set("Toutes les données")
            
            success = self.data_management.export_csv()
            
            if not success:
                print("Export failed. Checking log file for details.")
                with open('app.log', 'r') as log_file:
                    print(log_file.read())
            
            self.assertTrue(success)
            
            users_file = os.path.join(tmpdirname, "users_export.csv")
            workshops_file = os.path.join(tmpdirname, "workshops_export.csv")
            
            self.assertTrue(os.path.exists(users_file))
            self.assertTrue(os.path.exists(workshops_file))
            
            # Vérifier le contenu des fichiers exportés
            with open(users_file, 'r') as f:
                users_content = f.read()
                print("Users CSV content:", users_content)
                self.assertIn("Dupont,Jean", users_content)
                self.assertIn("SansAtelier", users_content)
            
            with open(workshops_file, 'r') as f:
                workshops_content = f.read()
                print("Workshops CSV content:", workshops_content)
                self.assertIn("Informatique", workshops_content)
                self.assertIn("Atelier sans utilisateur", workshops_content)

    # Ajoutez d'autres tests si nécessaire

    def tearDown(self):
        self.root.destroy()
        super().tearDown()
