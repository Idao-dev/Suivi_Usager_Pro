from .test_base import BaseTestCase
from ui.settings import Settings
import customtkinter as ctk
from src.config import get_conseillers, get_current_conseiller, add_conseiller, remove_conseiller

class TestSettings(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.root.update_appearance = lambda: None
        self.root.update_conseiller_dropdown = self.mock_update_conseiller_dropdown
        self.settings = Settings(self.root, self.db_manager, self.root)

    def mock_update_conseiller_dropdown(self):
        # Cette méthode ne fait rien, elle est juste là pour éviter l'erreur
        pass

    def tearDown(self):
        super().tearDown()
        self.root.destroy()

    def test_add_conseiller(self):
        initial_conseillers = get_conseillers()
        
        # Simuler l'ajout d'un conseiller
        add_conseiller("Nouveau Conseiller")
        
        updated_conseillers = get_conseillers()
        self.assertIn("Nouveau Conseiller", updated_conseillers)
        self.assertEqual(len(updated_conseillers), len(initial_conseillers) + 1)

    def test_remove_conseiller(self):
        # Ajouter un conseiller pour le test
        add_conseiller("Conseiller à Supprimer")
        
        initial_conseillers = get_conseillers()
        
        # Simuler la suppression d'un conseiller
        remove_conseiller("Conseiller à Supprimer")
        
        updated_conseillers = get_conseillers()
        self.assertNotIn("Conseiller à Supprimer", updated_conseillers)
        self.assertEqual(len(updated_conseillers), len(initial_conseillers) - 1)

    def test_toggle_dark_mode(self):
        initial_mode = self.settings.dark_mode_var.get()
        
        # Forcer le changement de mode
        new_mode = "on" if initial_mode == "off" else "off"
        self.settings.dark_mode_var.set(new_mode)
        self.settings.toggle_dark_mode()

        updated_mode = self.settings.dark_mode_var.get()
        self.assertNotEqual(initial_mode, updated_mode)
