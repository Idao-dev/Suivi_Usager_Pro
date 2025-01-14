import unittest
import sys
import os
import json
import customtkinter as ctk
from unittest.mock import MagicMock

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseUITestCase
from src.ui.settings import Settings
from src.utils.theme import set_dark_theme, set_light_theme
from src.utils.config_utils import (
    get_dark_mode, set_dark_mode, get_current_conseiller, get_inactivity_period,
    get_ateliers_entre_paiements, get_default_paid_workshops,
    get_conseillers, add_conseiller
)

class TestSettingsUI(BaseUITestCase):
    def setUp(self):
        super().setUp()
        # Créer un mock pour la fenêtre principale
        self.mock_main_window = MagicMock()
        self.window = Settings(self.root, self.db_manager, self.mock_main_window)

    def tearDown(self):
        super().tearDown()
        self.window.destroy()
        # Restaurer les paramètres par défaut
        if os.path.exists("config.json"):
            os.remove("config.json")

    def test_init(self):
        """Test l'initialisation de la fenêtre des paramètres"""
        self.assertIsNotNone(self.window)
        # Vérifier la présence des composants principaux
        self.assertTrue(hasattr(self.window, "dark_mode_switch"))
        self.assertTrue(hasattr(self.window, "dark_mode_var"))
        self.assertTrue(hasattr(self.window, "inactivity_period_var"))
        self.assertTrue(hasattr(self.window, "paid_workshops_var"))

    def test_theme_switch(self):
        """Test le changement de thème"""
        # Vérifier le thème par défaut
        initial_theme = get_dark_mode()
        
        # Changer le thème
        self.window.dark_mode_var.set("on" if not initial_theme else "off")
        
        # Simuler le changement de thème
        is_dark = self.window.dark_mode_var.get() == "on"
        set_dark_mode(is_dark)
        if is_dark:
            set_dark_theme()
        else:
            set_light_theme()
        
        # Vérifier que le thème a été changé
        self.assertNotEqual(initial_theme, get_dark_mode())

    def test_conseiller_management(self):
        """Test la gestion des conseillers"""
        # Simuler l'ajout d'un conseiller via la boîte de dialogue
        def mock_input_dialog(*args, **kwargs):
            mock = MagicMock()
            mock.get_input = lambda: "Test Conseiller"
            return mock
        
        original_dialog = ctk.CTkInputDialog
        ctk.CTkInputDialog = mock_input_dialog
        
        try:
            # Ajouter un nouveau conseiller
            initial_conseillers = get_conseillers()
            self.window.add_conseiller()
            
            # Vérifier que le conseiller a été ajouté
            current_conseillers = get_conseillers()
            self.assertIn("Test Conseiller", current_conseillers)
            
            # Vérifier que la méthode de mise à jour a été appelée
            self.mock_main_window.update_conseiller_dropdown.assert_called_once()
        finally:
            # Restaurer la classe d'origine
            ctk.CTkInputDialog = original_dialog

    def test_inactivity_period(self):
        """Test la modification de la période d'inactivité"""
        # Changer la période d'inactivité
        initial_period = int(get_inactivity_period())
        new_period = 12 if initial_period != 12 else 6
        
        self.window.inactivity_period_var.set(str(new_period))
        self.window.update_inactivity_period(str(new_period))
        
        # Vérifier que la période a été changée
        self.assertEqual(int(get_inactivity_period()), new_period)

    def test_paid_workshops(self):
        """Test la modification des types d'ateliers payants"""
        # Vérifier l'état initial
        initial_paid = get_default_paid_workshops()
        
        # Changer les types d'ateliers payants
        new_paid = ["Atelier numérique"]
        self.window.paid_workshops_var.set(", ".join(new_paid))
        
        # Sauvegarder les paramètres
        self.window.save_settings()
        
        # Vérifier que les paramètres ont été changés
        self.assertEqual(get_default_paid_workshops(), new_paid)

    def test_save_settings(self):
        """Test la sauvegarde des paramètres"""
        # Modifier plusieurs paramètres
        self.window.dark_mode_var.set("on")
        self.window.inactivity_period_var.set("12")
        self.window.paid_workshops_var.set("Atelier numérique")
        
        # Sauvegarder
        self.window.save_settings()
        
        # Vérifier que les paramètres ont été sauvegardés
        self.assertTrue(os.path.exists("config.json"))
        
        # Créer une nouvelle instance pour vérifier le chargement
        new_window = Settings(self.root, self.db_manager, self.mock_main_window)
        self.assertEqual(new_window.inactivity_period_var.get(), "12")
        self.assertEqual(new_window.paid_workshops_var.get(), "Atelier numérique")
        new_window.destroy() 