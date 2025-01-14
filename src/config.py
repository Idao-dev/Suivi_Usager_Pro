"""
Module de gestion de la configuration de l'application.
Gère le chargement, la sauvegarde et l'accès aux paramètres de configuration.
Les paramètres sont stockés dans un fichier JSON et incluent :
- Liste des conseillers
- Conseiller actuel
- Période d'inactivité
- Nombre d'ateliers entre paiements
"""

import json
import os
import customtkinter as ctk
from src.utils.config_utils import *
import sys

# Chemin du fichier de configuration, adapté selon le mode d'exécution (développement ou production)
CONFIG_FILE = os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__), "config.json")

def load_config():
    """
    Charge la configuration depuis le fichier JSON.
    Crée une configuration par défaut si le fichier n'existe pas.
    
    Returns:
        dict: Configuration chargée ou configuration par défaut
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"conseillers": [], "current_conseiller": ""}

def save_config(config):
    """
    Sauvegarde la configuration dans le fichier JSON.
    
    Args:
        config (dict): Configuration à sauvegarder
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def setUp(self):
    """
    Configure l'environnement de test.
    Crée un fichier de configuration temporaire pour les tests.
    Sauvegarde la configuration initiale.
    """
    self.test_config_file = "test_config.json"
    self.original_config_file = os.environ.get("CONFIG_FILE", "config.json")
    os.environ["CONFIG_FILE"] = self.test_config_file
    
    # Réinitialiser la configuration pour chaque test
    initial_config = {"conseillers": [], "current_conseiller": ""}
    save_config(initial_config)

def tearDown(self):
    """
    Nettoie l'environnement après les tests.
    Restaure la configuration originale et supprime le fichier de test.
    """
    super().tearDown()
    os.environ["CONFIG_FILE"] = self.original_config_file
    if os.path.exists(self.test_config_file):
        os.remove(self.test_config_file)
    self.root.destroy()

def get_inactivity_period():
    """
    Récupère la période d'inactivité configurée.
    
    Returns:
        str: Période d'inactivité en mois (par défaut "12")
    """
    config = load_config()
    return config.get("inactivity_period", "12")  # Par défaut 12 mois

def set_inactivity_period(period):
    """
    Définit la période d'inactivité.
    
    Args:
        period (int): Nouvelle période d'inactivité en mois
    """
    config = load_config()
    config["inactivity_period"] = str(period)
    save_config(config)

def get_ateliers_entre_paiements():
    """
    Récupère le nombre d'ateliers entre deux paiements.
    
    Returns:
        int: Nombre d'ateliers (par défaut 5)
    """
    config = load_config()
    return config.get("ateliers_entre_paiements", 5)  # Par défaut 5 ateliers

def set_ateliers_entre_paiements(nombre):
    """
    Définit le nombre d'ateliers entre deux paiements.
    
    Args:
        nombre (int): Nouveau nombre d'ateliers
    """
    config = load_config()
    config["ateliers_entre_paiements"] = int(nombre)
    save_config(config)
