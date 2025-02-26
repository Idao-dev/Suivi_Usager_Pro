"""
Tests unitaires pour le module csv_import_export.py.
Ces tests se concentrent sur les fonctionnalités unitaires de l'exportateur CSV,
sans dépendre de la base de données réelle.
"""

import pytest
import os
import tempfile
import csv
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.utils.csv_import_export import CSVExporter
from src.models.user import User
from src.models.workshop import Workshop

class TestCSVExporter:
    """Tests unitaires pour la classe CSVExporter."""
    
    @pytest.fixture
    def mock_db_manager(self):
        """Crée un mock du gestionnaire de base de données."""
        mock = MagicMock()
        mock.db_path = os.path.join(tempfile.gettempdir(), 'test_db.sqlite')
        return mock
    
    @pytest.fixture
    def csv_exporter(self, mock_db_manager):
        """Crée une instance de CSVExporter avec un db_manager mocké."""
        return CSVExporter(mock_db_manager)
    
    def test_init(self, csv_exporter, mock_db_manager):
        """Teste l'initialisation de l'exportateur CSV."""
        assert csv_exporter.db_manager == mock_db_manager
        assert os.path.exists(csv_exporter.export_dir)
        
    def test_export_users_path_generation(self, csv_exporter):
        """Teste la génération du chemin pour l'export des utilisateurs."""
        # Utiliser un patch plus simple pour datetime.now
        mock_date_str = "2023-01-01_12-00-00"
        
        # Patcher datetime.now et datetime.strftime simultanément
        with patch('src.utils.csv_import_export.datetime') as mock_datetime:
            # Configurer le mock pour retourner une date formatée
            mock_now = MagicMock()
            mock_now.strftime.return_value = mock_date_str
            mock_datetime.now.return_value = mock_now
            
            # Mock de User.get_all pour éviter d'avoir à interagir avec la base de données
            csv_exporter.db_manager.search_users = MagicMock(return_value=[])
            
            # Mock de csv.DictWriter pour éviter d'écrire réellement dans un fichier
            with patch('csv.DictWriter.writerow'), patch('csv.DictWriter.writeheader'):
                filepath = csv_exporter.export_users()
                
        # Vérifier que le chemin du fichier contient la date
        assert mock_date_str in filepath
        assert filepath.endswith('.csv')
    
    def test_export_workshops_path_generation(self, csv_exporter):
        """Teste la génération du chemin pour l'export des ateliers."""
        # Utiliser un patch plus simple pour datetime.now
        mock_date_str = "2023-01-01_12-00-00"
        
        # Patcher datetime.now et datetime.strftime simultanément
        with patch('src.utils.csv_import_export.datetime') as mock_datetime:
            # Configurer le mock pour retourner une date formatée
            mock_now = MagicMock()
            mock_now.strftime.return_value = mock_date_str
            mock_datetime.now.return_value = mock_now
            
            # Mock des méthodes pour éviter d'interagir avec la base de données
            csv_exporter.db_manager.get_all_workshops = MagicMock(return_value=[])
            
            # Mock de csv.DictWriter pour éviter d'écrire réellement dans un fichier
            with patch('csv.DictWriter.writerow'), patch('csv.DictWriter.writeheader'):
                filepath = csv_exporter.export_workshops()
                
        # Vérifier que le chemin du fichier contient la date
        assert mock_date_str in filepath
        assert filepath.endswith('.csv')
    
    def test_import_user_valid_data(self, csv_exporter):
        """Teste l'importation d'un utilisateur avec des données valides."""
        # Données utilisateur valides
        user_data = {
            "ID": "1",
            "Nom": "Dupont",
            "Prénom": "Jean",
            "Date de naissance": "01/01/1990",
            "Téléphone": "0123456789",
            "Email": "jean.dupont@example.com",
            "Adresse": "123 Rue Test"
        }
        
        # Mock de User.save pour éviter d'écrire dans la base de données
        with patch('src.models.user.User.save', return_value=1):
            result = csv_exporter.import_user(user_data)
            
        assert result == 1
    
    def test_import_user_invalid_data(self, csv_exporter):
        """Teste l'importation d'un utilisateur avec des données invalides."""
        # Données utilisateur avec date de naissance invalide
        user_data = {
            "ID": "1",
            "Nom": "Dupont",
            "Prénom": "Jean",
            "Date de naissance": "01-01-1990",  # Format incorrect
            "Téléphone": "0123456789",
            "Email": "jean.dupont@example.com",
            "Adresse": "123 Rue Test"
        }
        
        # L'importation devrait échouer
        result = csv_exporter.import_user(user_data)
        assert result is None
    
    def test_import_workshop_valid_data(self, csv_exporter):
        """Teste l'importation d'un atelier avec des données valides."""
        # Données atelier valides
        workshop_data = {
            "ID": "1",
            "User ID": "1",
            "Description": "Atelier test",
            "Date": "01/01/2023",
            "Durée": "60",
            "Notes": "Test notes"
        }
        
        # Mock des méthodes pour éviter d'interagir avec la base de données
        with patch('src.models.workshop.Workshop.save', return_value=1), \
             patch('src.models.user.User.get_by_id', return_value=User(id=1, nom="Test", prenom="User")):
            result = csv_exporter.import_workshop(workshop_data)
            
        assert result == 1
    
    def test_import_workshop_invalid_data(self, csv_exporter):
        """Teste l'importation d'un atelier avec des données invalides."""
        # Données atelier avec utilisateur inexistant
        workshop_data = {
            "ID": "1",
            "User ID": "999",  # ID utilisateur inexistant
            "Description": "Atelier test",
            "Date": "01/01/2023",
            "Durée": "60",
            "Notes": "Test notes"
        }
        
        # Mock de User.get_by_id pour simuler un utilisateur inexistant
        with patch('src.models.user.User.get_by_id', return_value=None):
            result = csv_exporter.import_workshop(workshop_data)
            
        assert result is None
    
    def test_export_specific_users(self, csv_exporter):
        """Teste l'exportation d'utilisateurs spécifiques."""
        # Créer des utilisateurs de test
        user1 = User(id=1, nom="Dupont", prenom="Jean")
        user2 = User(id=2, nom="Martin", prenom="Pierre")
        users = [user1, user2]
        
        # Utiliser un patch plus simple pour datetime.now
        mock_date_str = "2023-01-01_12-00-00"
        
        # Patcher datetime.now et datetime.strftime simultanément
        with patch('src.utils.csv_import_export.datetime') as mock_datetime:
            # Configurer le mock pour retourner une date formatée
            mock_now = MagicMock()
            mock_now.strftime.return_value = mock_date_str
            mock_datetime.now.return_value = mock_now
            
            # Mock de csv.DictWriter pour éviter d'écrire réellement dans un fichier
            with patch('csv.DictWriter.writerow') as mock_writerow, \
                 patch('csv.DictWriter.writeheader'):
                filepath = csv_exporter.export_specific_users(users)
                
                # Vérifier que writerow a été appelé pour chaque utilisateur
                assert mock_writerow.call_count == len(users)
                
        # Vérifier que le chemin du fichier est correct
        assert mock_date_str in filepath
        assert filepath.endswith('.csv') 