import unittest
import os
import tempfile
import json

# Importer les fonctions individuellement pour éviter les problèmes de portée globale
from src.utils.config_utils import add_conseiller, remove_conseiller, load_config, save_config, get_current_conseiller, set_current_conseiller

class TestConfig(unittest.TestCase):
    """Tests pour le module de configuration."""
    
    def setUp(self):
        # Créer un fichier temporaire pour la configuration
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        
        # Sauvegarder le chemin original et définir le chemin temporaire
        from src.utils.config_utils import CONFIG_FILE as ORIGINAL_CONFIG_FILE
        self.original_config_file = ORIGINAL_CONFIG_FILE
        
        # Définir le fichier temporaire comme configuration
        os.environ["CONFIG_FILE"] = self.temp_file.name
        
        # Initialiser avec une configuration vide
        with open(self.temp_file.name, 'w') as f:
            json.dump({"conseillers": [], "current_conseiller": ""}, f)

    def tearDown(self):
        # Restaurer le chemin de configuration original
        os.environ["CONFIG_FILE"] = self.original_config_file
        
        # Supprimer le fichier temporaire
        os.unlink(self.temp_file.name)

    def test_load_and_save_config(self):
        config = load_config()
        self.assertIn("conseillers", config)
        self.assertIn("current_conseiller", config)

        config["test_key"] = "test_value"
        save_config(config)

        new_config = load_config()
        self.assertEqual(new_config["test_key"], "test_value")

    def test_add_and_remove_conseiller(self):
        add_conseiller("Test Conseiller")
        config = load_config()
        self.assertIn("Test Conseiller", config["conseillers"])

        remove_conseiller("Test Conseiller")
        config = load_config()
        self.assertNotIn("Test Conseiller", config["conseillers"])

    def test_get_and_set_current_conseiller(self):
        set_current_conseiller("Current Conseiller")
        self.assertEqual(get_current_conseiller(), "Current Conseiller")
