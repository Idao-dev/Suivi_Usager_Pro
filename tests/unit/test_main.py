"""
Tests unitaires pour le module main.py.
Ce module teste les fonctions utilitaires et l'initialisation de l'application.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.main import get_base_path, get_resource_path, MainApplication


class TestMainFunctions(unittest.TestCase):
    """Tests pour les fonctions utilitaires dans main.py."""
    
    def test_get_base_path_dev(self):
        """Teste la fonction get_base_path en mode développement."""
        with patch('sys.frozen', False, create=True):
            base_path = get_base_path()
            self.assertTrue(os.path.isdir(base_path))
    
    def test_get_base_path_frozen(self):
        """Teste la fonction get_base_path en mode exécutable."""
        with patch('sys.frozen', True, create=True), \
             patch('sys._MEIPASS', '/fake/meipass/path', create=True):
            base_path = get_base_path()
            self.assertEqual(base_path, '/fake/meipass/path')
    
    def test_get_resource_path_dev(self):
        """Test de la fonction get_resource_path en développement."""
        with patch('sys.frozen', False, create=True):
            with patch('src.main.get_base_path', return_value='/fake/base/path'):
                # Utiliser un caractère de séparation de chemin normalisé '/'
                resource_path = get_resource_path('assets/icon.ico')
                # Normaliser le chemin attendu et le résultat pour éviter les problèmes de séparateurs
                expected_path = os.path.normpath(os.path.join('/fake/base/path', 'src', 'assets', 'icon.ico'))
                resource_path = os.path.normpath(resource_path)
                self.assertEqual(resource_path, expected_path)
    
    def test_get_resource_path_frozen(self):
        """Test de la fonction get_resource_path dans une application compilée."""
        with patch('sys.frozen', True, create=True):
            with patch('src.main.get_base_path', return_value='/fake/base/path'):
                # Utiliser un caractère de séparation de chemin normalisé '/'
                resource_path = get_resource_path('assets/icon.ico')
                # Normaliser le chemin attendu et le résultat pour éviter les problèmes de séparateurs
                expected_path = os.path.normpath(os.path.join('/fake/base/path', 'assets', 'icon.ico'))
                resource_path = os.path.normpath(resource_path)
                self.assertEqual(resource_path, expected_path)


class TestMainApplication(unittest.TestCase):
    """Tests pour la classe MainApplication."""
    
    @patch('customtkinter.CTk')
    @patch('src.main.DatabaseManager')
    @patch('src.main.MainWindow')
    @patch('src.main.get_dark_mode', return_value=True)
    @patch('src.main.set_dark_theme')
    def test_init_dark_theme(self, mock_set_dark_theme, mock_get_dark_mode, 
                           mock_main_window, mock_db_manager, mock_ctk):
        """Teste l'initialisation de l'application avec le thème sombre."""
        # Configurer les mocks
        mock_instance = mock_ctk.return_value
        mock_instance.iconbitmap = MagicMock()
        mock_dashboard = MagicMock()
        mock_main_window.return_value.dashboard = mock_dashboard
        
        # Désactiver l'ajout d'observer pour éviter l'erreur
        with patch('src.main.MainApplication.add_observer') as mock_add_observer:
            # Créer un répertoire temporaire pour les tests
            with tempfile.TemporaryDirectory() as temp_dir:
                # Patcher les fonctions liées aux fichiers
                with patch('os.path.exists', return_value=True), \
                    patch('src.main.get_base_path', return_value=temp_dir), \
                    patch('os.makedirs'):
                    
                    # Créer l'instance de MainApplication
                    app = MainApplication()
                    
                    # Vérifier que les méthodes attendues ont été appelées
                    mock_set_dark_theme.assert_called_once()
                    mock_main_window.assert_called_once()
                    mock_add_observer.assert_called_once_with(mock_dashboard)

    @patch('customtkinter.CTk')
    @patch('src.main.DatabaseManager')
    @patch('src.main.MainWindow')
    @patch('src.main.get_dark_mode', return_value=False)
    @patch('src.main.set_light_theme')
    def test_init_light_theme(self, mock_set_light_theme, mock_get_dark_mode, 
                            mock_main_window, mock_db_manager, mock_ctk):
        """Teste l'initialisation de l'application avec le thème clair."""
        # Configurer les mocks
        mock_instance = mock_ctk.return_value
        mock_instance.iconbitmap = MagicMock()
        mock_dashboard = MagicMock()
        mock_main_window.return_value.dashboard = mock_dashboard
        
        # Désactiver l'ajout d'observer pour éviter l'erreur
        with patch('src.main.MainApplication.add_observer') as mock_add_observer:
            # Créer un répertoire temporaire pour les tests
            with tempfile.TemporaryDirectory() as temp_dir:
                # Patcher les fonctions liées aux fichiers
                with patch('os.path.exists', return_value=True), \
                    patch('src.main.get_base_path', return_value=temp_dir), \
                    patch('os.makedirs'):
                    
                    # Créer l'instance de MainApplication
                    app = MainApplication()
                    
                    # Vérifier que les méthodes attendues ont été appelées
                    mock_set_light_theme.assert_called_once()
                    mock_main_window.assert_called_once()
                    mock_add_observer.assert_called_once_with(mock_dashboard)

    @patch('customtkinter.CTk')
    @patch('src.main.DatabaseManager')
    @patch('src.main.MainWindow')
    def test_update_interface(self, mock_main_window, mock_db_manager, mock_ctk):
        """Teste la méthode update_interface."""
        # Configurer les mocks
        mock_instance = mock_ctk.return_value
        mock_instance.iconbitmap = MagicMock()
        mock_dashboard = MagicMock()
        mock_main_window.return_value.dashboard = mock_dashboard
        
        # Désactiver l'ajout d'observer pour éviter l'erreur
        with patch('src.main.MainApplication.add_observer') as mock_add_observer:
            # Créer l'instance de MainApplication
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch('os.path.exists', return_value=True), \
                    patch('src.main.get_base_path', return_value=temp_dir), \
                    patch('os.makedirs'):
                    
                    app = MainApplication()
                    
                    # Patch de la méthode notify_observers
                    with patch('src.main.MainApplication.notify_observers') as mock_notify:
                        # Appeler la méthode à tester
                        app.update_interface()
                        
                        # Vérifier que notify_observers a été appelé
                        mock_notify.assert_called_once()

    @patch('customtkinter.CTk')
    @patch('src.main.DatabaseManager')
    @patch('src.main.MainWindow')
    def test_on_closing(self, mock_main_window, mock_db_manager, mock_ctk):
        """Teste la méthode on_closing."""
        # Configurer les mocks
        mock_instance = mock_ctk.return_value
        mock_instance.iconbitmap = MagicMock()
        mock_main_window_instance = mock_main_window.return_value
        mock_main_window_instance.on_closing = MagicMock()
        mock_dashboard = MagicMock()
        mock_main_window.return_value.dashboard = mock_dashboard
        
        # Désactiver l'ajout d'observer pour éviter l'erreur
        with patch('src.main.MainApplication.add_observer') as mock_add_observer:
            # Créer l'instance de MainApplication
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch('os.path.exists', return_value=True), \
                    patch('src.main.get_base_path', return_value=temp_dir), \
                    patch('os.makedirs'):
                    
                    app = MainApplication()
                    
                    # Patch de la méthode quit pour éviter l'erreur
                    with patch.object(app, 'quit') as mock_quit:
                        # Appeler la méthode à tester
                        app.on_closing()
                        
                        # Vérifier que on_closing et quit ont été appelés
                        mock_main_window_instance.on_closing.assert_called_once()
                        mock_quit.assert_called_once()


if __name__ == '__main__':
    unittest.main() 