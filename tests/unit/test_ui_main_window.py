import unittest
import sys
import os
from datetime import datetime

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseUITestCase
from src.ui.main_window import MainWindow
from src.models.user import User
from src.models.workshop import Workshop

class TestMainWindow(BaseUITestCase):
    def setUp(self):
        super().setUp()
        def update_callback():
            pass  # Callback vide pour les tests
        self.window = MainWindow(self.root, self.db_manager, update_callback)
        
    def tearDown(self):
        super().tearDown()
        self.window.destroy()

    def test_init(self):
        """Test l'initialisation de la fenêtre principale"""
        # Vérifier la présence des composants principaux
        self.assertIsNotNone(self.window)
        self.assertIsNotNone(self.window.frames["Dashboard"])
        self.assertIsNotNone(self.window.frames["UserManagement"])
        
        # Vérifier que le dashboard est affiché par défaut
        self.assertTrue(self.window.frames["Dashboard"].winfo_viewable())
        self.assertFalse(self.window.frames["UserManagement"].winfo_viewable())
        
        # Vérifier la présence des boutons de navigation
        self.assertTrue(hasattr(self.window, "nav_buttons"))
        self.assertGreater(len(self.window.nav_buttons), 0)

    def test_menu_navigation(self):
        """Test la navigation entre les différentes sections"""
        # Test Dashboard
        self.window.show_frame("Dashboard")
        self.root.update()
        self.assertTrue(self.window.frames["Dashboard"].winfo_viewable())
        self.assertFalse(self.window.frames["UserManagement"].winfo_viewable())
        
        # Vérifier l'état des boutons
        self.assertEqual(
            self.window.nav_buttons["Dashboard"].cget("fg_color"),
            self.theme["CTkButton"]["fg_color"][1]  # Couleur sélectionnée
        )

        # Test User Management
        self.window.show_frame("UserManagement")
        self.root.update()
        self.assertFalse(self.window.frames["Dashboard"].winfo_viewable())
        self.assertTrue(self.window.frames["UserManagement"].winfo_viewable())
        
        # Vérifier l'état des boutons
        self.assertEqual(
            self.window.nav_buttons["UserManagement"].cget("fg_color"),
            self.theme["CTkButton"]["fg_color"][1]  # Couleur sélectionnée
        )

    def test_navigation_buttons(self):
        """Test les boutons de navigation"""
        # Cliquer sur le bouton User Management
        self.simulate_click(self.window.nav_buttons["UserManagement"])
        self.root.update()
        
        # Vérifier le changement de vue
        self.assertFalse(self.window.frames["Dashboard"].winfo_viewable())
        self.assertTrue(self.window.frames["UserManagement"].winfo_viewable())
        
        # Cliquer sur le bouton Dashboard
        self.simulate_click(self.window.nav_buttons["Dashboard"])
        self.root.update()
        
        # Vérifier le retour à la vue précédente
        self.assertTrue(self.window.frames["Dashboard"].winfo_viewable())
        self.assertFalse(self.window.frames["UserManagement"].winfo_viewable())

    def test_frame_updates(self):
        """Test la mise à jour des frames lors des changements"""
        # Créer un utilisateur de test
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)

        # Mettre à jour les frames
        self.window.frames["Dashboard"].update_content()
        self.window.frames["UserManagement"].update_content()
        
        # Vérifier que les frames sont à jour
        self.assertTrue(self.window.frames["Dashboard"].winfo_exists())
        self.assertTrue(self.window.frames["UserManagement"].winfo_exists())
        
        # Vérifier que les données sont affichées
        dashboard = self.window.frames["Dashboard"]
        self.assertIsNotNone(dashboard.stats_frame)
        self.assertIsNotNone(dashboard.recent_activities_frame)
        
        user_management = self.window.frames["UserManagement"]
        self.assertIsNotNone(user_management.user_list)
        self.assertIsNotNone(user_management.search_frame)

    def test_responsive_layout(self):
        """Test le comportement responsive de l'interface"""
        # Test avec une petite fenêtre
        self.root.geometry("400x300")
        self.root.update()
        self.wait_for(lambda: self.window.winfo_width() == 400)
        
        # Vérifier que l'interface s'adapte
        dashboard = self.window.frames["Dashboard"]
        self.assertLessEqual(dashboard.winfo_width(), 400)
        
        # Test avec une grande fenêtre
        self.root.geometry("1200x800")
        self.root.update()
        self.wait_for(lambda: self.window.winfo_width() == 1200)
        
        # Vérifier que l'interface s'adapte
        self.assertLessEqual(dashboard.winfo_width(), 1200)

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
        super().tearDownClass()

if __name__ == '__main__':
    unittest.main() 