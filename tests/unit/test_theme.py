"""
Tests unitaires pour le module theme.py.
Ces tests vérifient le comportement des fonctions de gestion des thèmes.
"""

import pytest
from unittest.mock import patch, MagicMock
import customtkinter as ctk

# Import du module à tester
from src.utils.theme import set_dark_theme, set_light_theme

class TestTheme:
    """Tests pour les fonctions de gestion des thèmes."""
    
    @pytest.fixture
    def mock_ctk(self):
        """Mock de customtkinter pour tester sans modifier l'environnement réel."""
        with patch('src.utils.theme.ctk') as mock:
            # Simuler la structure ThemeManager.theme pour éviter les erreurs
            mock.ThemeManager = MagicMock()
            # Initialiser avec toutes les clés possibles pour éviter les KeyError
            theme_components = [
                "CTk", "CTkFrame", "CTkButton", "CTkLabel", "CTkEntry",
                "CTkOptionMenu", "CTkSwitch", "CTkRadioButton", "CTkCheckBox",
                "CTkComboBox", "CTkScrollbar", "CTkProgressBar", "CTkTabview",
                "CTkTextbox", "CTkScrollableFrame", "CTkSegmentedButton", "CTkSlider"
            ]
            mock.ThemeManager.theme = {component: {} for component in theme_components}
            yield mock
    
    def test_set_dark_theme(self, mock_ctk):
        """Teste la configuration du thème sombre."""
        # Appeler la fonction de configuration du thème sombre
        set_dark_theme()
        
        # Vérifier que le mode d'apparence a été changé à "dark"
        mock_ctk.set_appearance_mode.assert_called_once_with("dark")
        
        # Vérifier que le thème de couleur par défaut a été changé à "blue"
        mock_ctk.set_default_color_theme.assert_called_once_with("blue")
        
        # Vérifier que certaines couleurs spécifiques ont été définies
        theme = mock_ctk.ThemeManager.theme
        
        # Vérifier les couleurs du fond principal
        assert theme["CTk"]["fg_color"] == ["#2B2B2B", "#2B2B2B"]
        
        # Vérifier les couleurs des boutons
        assert theme["CTkButton"]["fg_color"] == ["#1F6AA5", "#1F6AA5"]
        assert theme["CTkButton"]["hover_color"] == ["#144870", "#144870"]
        assert theme["CTkButton"]["text_color"] == ["#FFFFFF", "#FFFFFF"]
    
    def test_set_light_theme(self, mock_ctk):
        """Teste la configuration du thème clair."""
        # Appeler la fonction de configuration du thème clair
        set_light_theme()
        
        # Vérifier que le mode d'apparence a été changé à "light"
        mock_ctk.set_appearance_mode.assert_called_once_with("light")
        
        # Vérifier que le thème de couleur par défaut a été changé à "blue"
        mock_ctk.set_default_color_theme.assert_called_once_with("blue")
        
        # Vérifier que certaines couleurs spécifiques ont été définies
        theme = mock_ctk.ThemeManager.theme
        
        # Vérifier les couleurs des composants dans le thème clair
        # Ces assertions peuvent varier en fonction de la définition réelle dans set_light_theme()
        assert theme["CTk"]["fg_color"] is not None
        assert theme["CTkButton"]["fg_color"] is not None
        assert theme["CTkButton"]["text_color"] is not None
    
    def test_theme_consistency(self, mock_ctk):
        """
        Teste la cohérence entre les thèmes sombre et clair.
        Vérifie que tous les composants ont des couleurs définies dans les deux thèmes.
        """
        # Appliquer d'abord le thème sombre
        set_dark_theme()
        dark_theme = {}
        
        # Enregistrer les clés pour les composants importants
        components = ["CTk", "CTkButton", "CTkEntry", "CTkLabel"]
        for component in components:
            dark_theme[component] = set(mock_ctk.ThemeManager.theme[component].keys())
        
        # Réinitialiser le mock pour éviter les interférences
        mock_ctk.reset_mock()
        for component in components:
            mock_ctk.ThemeManager.theme[component] = {}
        
        # Appliquer ensuite le thème clair
        set_light_theme()
        light_theme = {}
        
        # Enregistrer les clés pour les mêmes composants
        for component in components:
            light_theme[component] = set(mock_ctk.ThemeManager.theme[component].keys())
        
        # Vérifier que les composants principaux ont les mêmes propriétés dans les deux thèmes
        for component in components:
            assert dark_theme[component] == light_theme[component], \
                f"Le composant {component} n'a pas les mêmes propriétés dans les deux thèmes" 