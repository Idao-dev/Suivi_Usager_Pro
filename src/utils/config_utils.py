"""
Module de gestion de la configuration de l'application.
Gère la persistance des paramètres de l'application dans un fichier JSON.

Ce module permet de :
- Gérer les conseillers (ajout, suppression, sélection)
- Configurer le thème (mode sombre/clair)
- Définir les périodes d'inactivité
- Gérer les paramètres de paiement des ateliers
"""

import json
import os

# Chemin du fichier de configuration, peut être surchargé par une variable d'environnement
CONFIG_FILE = os.environ.get("CONFIG_FILE", "config.json")

def load_config():
    """
    Charge la configuration depuis le fichier JSON.
    Crée une configuration par défaut si le fichier n'existe pas.
    
    Returns:
        dict: La configuration chargée ou une configuration par défaut
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"conseillers": [], "current_conseiller": ""}

def save_config(config):
    """
    Sauvegarde la configuration dans le fichier JSON.
    
    Args:
        config (dict): La configuration à sauvegarder
    """
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_conseillers():
    """
    Récupère la liste des conseillers.
    
    Returns:
        list: Liste des noms des conseillers
    """
    config = load_config()
    return config["conseillers"]

def add_conseiller(name):
    """
    Ajoute un nouveau conseiller s'il n'existe pas déjà.
    
    Args:
        name (str): Nom du conseiller à ajouter
    """
    config = load_config()
    if name and name not in config["conseillers"]:
        config["conseillers"].append(name)
        save_config(config)

def remove_conseiller(name):
    """
    Supprime un conseiller et réinitialise le conseiller courant si nécessaire.
    
    Args:
        name (str): Nom du conseiller à supprimer
    """
    config = load_config()
    if name in config["conseillers"]:
        config["conseillers"].remove(name)
    if config["current_conseiller"] == name:
        config["current_conseiller"] = ""
    save_config(config)

def get_current_conseiller():
    """
    Récupère le nom du conseiller actuellement sélectionné.
    
    Returns:
        str: Nom du conseiller courant ou chaîne vide si aucun
    """
    config = load_config()
    return config.get("current_conseiller", "")

def set_current_conseiller(conseiller):
    """
    Définit le conseiller actuellement sélectionné.
    
    Args:
        conseiller (str): Nom du conseiller à définir comme courant
    """
    config = load_config()
    config["current_conseiller"] = conseiller
    save_config(config)

def get_dark_mode():
    """
    Récupère l'état du mode sombre.
    
    Returns:
        bool: True si le mode sombre est activé, False sinon
    """
    config = load_config()
    return config.get("dark_mode", False)

def set_dark_mode(is_dark):
    """
    Active ou désactive le mode sombre.
    
    Args:
        is_dark (bool): True pour activer le mode sombre, False pour le désactiver
    """
    config = load_config()
    config["dark_mode"] = is_dark
    save_config(config)

def get_inactivity_period():
    """
    Récupère la période d'inactivité configurée.
    
    Returns:
        str: Nombre de mois d'inactivité avant alerte (défaut: "12")
    """
    config = load_config()
    return config.get("inactivity_period", "12")

def set_inactivity_period(period):
    """
    Définit la période d'inactivité.
    
    Args:
        period (str): Nombre de mois d'inactivité avant alerte
    """
    config = load_config()
    config["inactivity_period"] = str(period)
    save_config(config)

def get_ateliers_entre_paiements():
    """
    Récupère le nombre d'ateliers entre deux paiements.
    
    Returns:
        int: Nombre d'ateliers avant demande de paiement (défaut: 5)
    """
    config = load_config()
    return config.get("ateliers_entre_paiements", 5)

def set_ateliers_entre_paiements(nombre):
    """
    Définit le nombre d'ateliers entre deux paiements.
    
    Args:
        nombre (int): Nombre d'ateliers avant demande de paiement
    """
    config = load_config()
    config["ateliers_entre_paiements"] = int(nombre)
    save_config(config)

def get_default_paid_workshops():
    """
    Récupère la liste des types d'ateliers payants par défaut.
    
    Returns:
        list: Liste des types d'ateliers payants (défaut: ["Atelier numérique"])
    """
    config = load_config()
    return config.get("default_paid_workshops", ["Atelier numérique"])

def set_default_paid_workshops(workshops):
    """
    Définit la liste des types d'ateliers payants par défaut.
    
    Args:
        workshops (list): Liste des types d'ateliers payants
    """
    config = load_config()
    config["default_paid_workshops"] = workshops
    save_config(config)
