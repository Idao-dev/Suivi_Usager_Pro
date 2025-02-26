import unittest
import sys
import os
from datetime import datetime
import tkinter as tk
import customtkinter as ctk

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseUITestCase
from src.ui.user_management import UserManagement
from src.models.user import User
from src.models.workshop import Workshop

class TestUserManagement(BaseUITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = tk.Tk()
        cls.root.withdraw()
        # Initialiser le thème CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'root') and cls.root is not None:
            try:
                cls.root.quit()
            except:
                pass
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        def edit_user_callback(user_id):
            pass
        def edit_workshop_callback(workshop_id):
            pass
        self.user_management = UserManagement(
            self.root,
            self.db_manager,
            edit_user_callback,
            edit_workshop_callback
        )
        
    def tearDown(self):
        if hasattr(self, 'user_management'):
            try:
                self.user_management.destroy()
            except:
                pass
        super().tearDown()

    def test_init(self):
        """Test l'initialisation de la gestion des utilisateurs"""
        self.assertIsNotNone(self.user_management)
        self.assertIsNotNone(self.user_management.user_list)
        self.assertIsNotNone(self.user_management.search_frame)

    def test_user_list_display(self):
        """Test l'affichage de la liste des utilisateurs"""
        # Créer des utilisateurs de test
        users = [
            User(nom="Test1", prenom="User1", telephone="0123456789"),
            User(nom="Test2", prenom="User2", telephone="9876543210")
        ]
        for user in users:
            user.save(self.db_manager)

        # Rafraîchir la liste
        self.user_management.refresh_user_list()

        # Vérifier que les utilisateurs sont affichés
        displayed_users = self.user_management.get_displayed_users()
        self.assertEqual(len(displayed_users), 2)

    def test_user_search(self):
        """Test la fonction de recherche d'utilisateurs"""
        # Créer des utilisateurs avec différents noms
        users = [
            User(nom="Dupont", prenom="Jean", telephone="0123456789"),
            User(nom="Martin", prenom="Paul", telephone="9876543210"),
            User(nom="Durand", prenom="Marie", telephone="5555555555")
        ]
        for user in users:
            user.save(self.db_manager)

        # Tester la recherche
        self.user_management.search_users("Dup")

        # Vérifier les résultats
        search_results = self.user_management.get_search_results()
        self.assertEqual(len(search_results), 1)
        self.assertEqual(search_results[0].nom, "Dupont")

    def test_user_selection(self):
        """Test la sélection d'un utilisateur"""
        # Créer un utilisateur
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)

        # Rafraîchir la liste
        self.user_management.refresh_user_list()

        # Simuler la sélection
        self.user_management.select_user(user.id)

        # Vérifier que l'utilisateur est sélectionné
        selected_user = self.user_management.get_selected_user()
        self.assertIsNotNone(selected_user)
        self.assertEqual(selected_user.id, user.id)

    def test_user_workshop_display(self):
        """Test l'affichage des ateliers d'un utilisateur"""
        # Créer un utilisateur avec des ateliers
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)

        workshops = [
            Workshop(user_id=user.id, categorie="Test 1", date=datetime.now().strftime("%Y-%m-%d"), conseiller="Test"),
            Workshop(user_id=user.id, categorie="Test 2", date=datetime.now().strftime("%Y-%m-%d"), conseiller="Test")
        ]
        for workshop in workshops:
            workshop.save(self.db_manager)

        # Sélectionner l'utilisateur
        self.user_management.select_user(user.id)

        # Vérifier l'affichage des ateliers
        displayed_workshops = self.user_management.get_displayed_workshops()
        self.assertEqual(len(displayed_workshops), 2)

if __name__ == '__main__':
    unittest.main() 