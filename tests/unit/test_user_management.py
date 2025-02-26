"""
Tests unitaires pour le module user_management.py.
Ces tests vérifient les fonctionnalités de l'interface de gestion des utilisateurs.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import customtkinter as ctk
from src.ui.user_management import UserManagement
from src.models.user import User
from src.models.workshop import Workshop


class TestUserManagement(unittest.TestCase):
    """Tests pour la classe UserManagement."""
    
    def setUp(self):
        """Préparation des tests."""
        self.root = MagicMock()
        self.db_manager = MagicMock()
        self.update_callback = MagicMock()
        self.edit_workshop_callback = MagicMock()
        
        # Créer une instance de UserManagement pour les tests
        with patch('customtkinter.CTkScrollableFrame'), \
             patch('customtkinter.CTkFrame'), \
             patch('customtkinter.CTkButton'), \
             patch('customtkinter.CTkEntry'), \
             patch('customtkinter.CTkLabel'):
            self.user_management = UserManagement(self.root, self.db_manager, self.update_callback, self.edit_workshop_callback)
        
        # Mocker les méthodes d'instance qui ne sont pas testées directement
        self.user_management.clear_frame = MagicMock()
        self.user_management.display_users = MagicMock()
        self.user_management.display_search_results = MagicMock()
        
        # Remplacer la méthode update_user_list par un mock
        self.user_management.update_user_list = MagicMock()
    
    def tearDown(self):
        """Nettoyage après les tests."""
        self.user_management.destroy()
        self.root.destroy()
    
    def create_mock_users(self, count=5):
        """Crée une liste de mock users pour les tests."""
        users = []
        for i in range(1, count + 1):
            user = MagicMock(spec=User)
            user.id = i
            user.nom = f"Nom{i}"
            user.prenom = f"Prenom{i}"
            user.date_naissance = f"1980-01-{i:02d}"
            user.telephone = f"060000000{i}"
            user.email = f"user{i}@example.com"
            user.adresse = f"Adresse {i}"
            user.derniere_visite = datetime.now().strftime("%Y-%m-%d")
            user.get_full_name.return_value = f"Prenom{i} Nom{i}"
            users.append(user)
        return users
    
    def test_init_components(self):
        """Teste l'initialisation des composants de l'interface."""
        # Vérifier que les composants principaux sont créés
        self.assertIsNotNone(self.user_management.title)
        self.assertIsNotNone(self.user_management.scrollable_frame)
        self.assertIsNotNone(self.user_management.users_frame)
        self.assertIsNotNone(self.user_management.load_more_button)
    
    def test_load_users(self):
        """Teste le chargement initial des utilisateurs."""
        # Configurer le mock pour renvoyer des utilisateurs
        mock_users = self.create_mock_users(5)
        self.db_manager.get_users_with_pagination.return_value = mock_users
        
        # Patcher la méthode display_users pour vérifier son appel
        with patch.object(self.user_management, 'display_users') as mock_display:
            # Appeler la méthode à tester
            self.user_management.load_users()
            
            # Vérifier que les méthodes ont été appelées
            self.db_manager.get_users_with_pagination.assert_called_once_with(0, 10)
            mock_display.assert_called_once_with(mock_users)
            
            # Vérifier que les attributs ont été mis à jour
            self.assertEqual(self.user_management.users, mock_users)
            self.assertEqual(self.user_management.offset, 10)
    
    def test_load_more_users(self):
        """Teste le chargement de plus d'utilisateurs (pagination)."""
        # Initialiser l'offset pour simuler un premier chargement
        self.user_management.offset = 10
        self.user_management.users = self.create_mock_users(10)
        
        # Configurer le mock pour renvoyer des utilisateurs supplémentaires
        more_users = self.create_mock_users(5)
        self.db_manager.get_users_with_pagination.return_value = more_users
        
        # Patcher la méthode display_users pour vérifier son appel
        with patch.object(self.user_management, 'display_users') as mock_display:
            # Appeler la méthode à tester
            self.user_management.load_more_users()
            
            # Vérifier que les méthodes ont été appelées
            self.db_manager.get_users_with_pagination.assert_called_once_with(10, 10)
            
            # Vérifier que les attributs ont été mis à jour
            self.assertEqual(len(self.user_management.users), 15)  # 10 existants + 5 nouveaux
            self.assertEqual(self.user_management.offset, 20)
            
            # Vérifier que display_users a été appelé avec tous les utilisateurs
            all_users = self.user_management.users
            mock_display.assert_called_once_with(all_users)
    
    def test_display_users(self):
        """Teste l'affichage des utilisateurs."""
        # Créer des mock users
        mock_users = self.create_mock_users(3)
        
        # Patcher la méthode clear_frame pour éviter l'interaction avec l'interface
        with patch.object(self.user_management, 'clear_frame'), \
             patch('customtkinter.CTkFrame.grid'), \
             patch('customtkinter.CTkLabel.grid'), \
             patch('customtkinter.CTkButton.grid'):
            
            # Appeler la méthode à tester
            self.user_management.display_users(mock_users)
            
            # Vérifier que clear_frame a été appelé
            self.user_management.clear_frame.assert_called_once()
    
    def test_update_user_list(self):
        """Teste la mise à jour de la liste des utilisateurs."""
        # Patcher les méthodes pour vérifier leurs appels
        with patch.object(self.user_management, 'load_users') as mock_load:
            # Appeler la méthode à tester
            self.user_management.update_user_list()
            
            # Vérifier que load_users a été appelé
            mock_load.assert_called_once()
    
    def test_edit_user(self):
        """Teste l'édition d'un utilisateur."""
        # Créer un mock user
        user = MagicMock(spec=User)
        
        # Appeler la méthode à tester
        self.user_management.edit_user(user)
        
        # Vérifier que le callback a été appelé
        self.update_callback.assert_called_once_with(user)
    
    def test_delete_user_confirmed(self):
        """Teste la suppression d'un utilisateur avec confirmation."""
        # Créer un mock user
        user = MagicMock(spec=User)
        user.id = 1
        user.nom = "Test"
        user.prenom = "User"
        user.get_full_name.return_value = "Test User"
        
        # Patcher messagebox.askyesno pour simuler une confirmation
        with patch('src.ui.user_management.messagebox.askyesno', return_value=True), \
             patch.object(self.user_management, 'update_user_list'):
            
            # Appeler la méthode à tester
            self.user_management.delete_user(user)
            
            # Vérifier que l'utilisateur a été supprimé
            self.db_manager.delete_user.assert_called_once_with(user.id)
            self.user_management.update_user_list.assert_called_once()
    
    def test_delete_user_cancelled(self):
        """Teste l'annulation de la suppression d'un utilisateur."""
        # Créer un mock user
        user = MagicMock(spec=User)
        user.id = 1
        user.nom = "Test"
        user.prenom = "User"
        user.get_full_name.return_value = "Test User"
        
        # Patcher messagebox.askyesno pour simuler une annulation
        with patch('src.ui.user_management.messagebox.askyesno', return_value=False), \
             patch.object(self.user_management, 'update_user_list'):
            
            # Appeler la méthode à tester
            self.user_management.delete_user(user)
            
            # Vérifier que l'utilisateur n'a pas été supprimé
            self.db_manager.delete_user.assert_not_called()
            self.user_management.update_user_list.assert_not_called()
    
    def test_add_workshop(self):
        """Teste l'ajout d'un atelier pour un utilisateur."""
        # Configurer un ID utilisateur pour le test
        user_id = 1
        
        # Créer un mock d'utilisateur
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id
        mock_user.nom = "Test"
        mock_user.prenom = "User"
        
        # Créer un mock de l'atelier qui sera créé
        mock_workshop = MagicMock(spec=Workshop)
        mock_workshop.user_id = user_id
        
        # Patcher la méthode get_by_id pour renvoyer notre mock
        with patch('src.models.user.User.get_by_id', return_value=mock_user), \
             patch('src.ui.add_workshop.AddWorkshop') as mock_add_window:
            
            # Simuler la création d'un atelier via la fenêtre modale
            def side_effect(*args, **kwargs):
                # Simuler l'appel au callback d'édition d'atelier lorsque l'atelier est créé
                self.edit_workshop_callback(mock_workshop)
                return MagicMock()  # Retourne un mock de la fenêtre
                
            mock_add_window.side_effect = side_effect
            
            # Appeler la méthode à tester
            self.user_management.add_workshop(user_id)
            
            # Vérifier que User.get_by_id a été appelé avec les bons arguments
            User.get_by_id.assert_called_once_with(self.db_manager, user_id)
            
            # Vérifier que la fenêtre AddWorkshop a été créée
            mock_add_window.assert_called_once()
            
            # Vérifier que le callback d'édition d'atelier a été appelé
            self.edit_workshop_callback.assert_called_once_with(mock_workshop)
    
    def test_update_observer(self):
        """Teste la mise à jour via le pattern Observer."""
        # Patcher les méthodes pour vérifier leurs appels
        with patch.object(self.user_management, 'update_user_list') as mock_update:
            # Appeler la méthode update (appelée par l'Observable)
            observable = MagicMock()
            self.user_management.update(observable)
            
            # Vérifier que update_user_list a été appelé
            mock_update.assert_called_once()
    
    def test_search_users(self):
        """Teste la recherche d'utilisateurs."""
        # Configurer le mock pour renvoyer des résultats de recherche
        search_term = "test"
        mock_results = self.create_mock_users(2)
        self.db_manager.search_users.return_value = mock_results
        
        # Patcher la méthode display_search_results pour vérifier son appel
        with patch.object(self.user_management, 'display_search_results') as mock_display:
            # Appeler la méthode à tester
            self.user_management.search_users(search_term)
            
            # Vérifier que les méthodes ont été appelées
            self.db_manager.search_users.assert_called_once_with(search_term)
            mock_display.assert_called_once_with(mock_results)
            
            # Vérifier que les résultats ont été stockés
            self.assertEqual(self.user_management.search_results, mock_results)
    
    def test_get_search_results(self):
        """Teste la récupération des résultats de recherche."""
        # Configurer les résultats de recherche
        mock_results = self.create_mock_users(2)
        self.user_management.search_results = mock_results
        
        # Appeler la méthode à tester
        results = self.user_management.get_search_results()
        
        # Vérifier les résultats
        self.assertEqual(results, mock_results)
    
    def test_display_search_results(self):
        """Teste l'affichage des résultats de recherche."""
        # Créer des mock users pour les résultats
        mock_results = self.create_mock_users(2)
        
        # Patcher les méthodes pour éviter l'interaction avec l'interface
        with patch.object(self.user_management, 'clear_frame'), \
             patch('customtkinter.CTkFrame.grid'), \
             patch('customtkinter.CTkLabel.grid'), \
             patch('customtkinter.CTkButton.grid'):
            
            # Appeler la méthode à tester
            self.user_management.display_search_results(mock_results)
            
            # Vérifier que clear_frame a été appelé
            self.user_management.clear_frame.assert_called_once()


if __name__ == '__main__':
    unittest.main() 