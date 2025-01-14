import unittest
import os
from src.config import load_config, save_config, add_conseiller, remove_conseiller, get_current_conseiller, set_current_conseiller

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_config_file = "test_config.json"
        self.original_config_file = "config.json"
        os.environ["CONFIG_FILE"] = self.test_config_file
        
        # Réinitialiser la configuration pour chaque test
        initial_config = {"conseillers": [], "current_conseiller": ""}
        save_config(initial_config)

    def tearDown(self):
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
        os.environ["CONFIG_FILE"] = self.original_config_file

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
