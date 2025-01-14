"""
Module de gestion et de conversion des dates pour l'application.
Fournit des fonctions utilitaires pour manipuler les dates entre différents formats
et assurer la cohérence des données entre l'interface utilisateur et la base de données.
"""

from dateutil import parser
from datetime import datetime
import re

def convert_to_db_date(date_string):
    """
    Convertit une date du format français (DD/MM/YYYY) au format de la base de données (YYYY-MM-DD).
    
    Args:
        date_string (str): La date au format DD/MM/YYYY
        
    Returns:
        str: La date au format YYYY-MM-DD pour la base de données
        None: Si la chaîne d'entrée est vide
        
    Example:
        >>> convert_to_db_date("25/12/2024")
        "2024-12-25"
    """
    if not date_string:
        return None
    if not is_valid_date(date_string):
        return date_string  # Retourner la date telle quelle si elle n'est pas au format DD/MM/YYYY
    day, month, year = date_string.split('/')
    return f"{year}-{month}-{day}"

def convert_from_db_date(db_date):
    """
    Convertit une date du format base de données (YYYY-MM-DD) au format français (DD/MM/YYYY).
    Gère aussi la conversion inverse si la date est déjà au bon format.
    
    Args:
        db_date (str): La date au format YYYY-MM-DD ou DD/MM/YYYY
        
    Returns:
        str: La date au format DD/MM/YYYY
        
    Raises:
        ValueError: Si le format de la date est invalide
        
    Example:
        >>> convert_from_db_date("2024-12-25")
        "25/12/2024"
    """
    try:
        # Essaie d'abord le format YYYY-MM-DD
        return datetime.strptime(db_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    except ValueError:
        try:
            # Si ça échoue, essaie le format DD/MM/YYYY
            datetime.strptime(db_date, '%d/%m/%Y')
            return db_date  # La date est déjà au bon format
        except ValueError:
            raise ValueError("Format de date invalide. Utilisez YYYY-MM-DD ou DD/MM/YYYY.")

def is_valid_date(date_string):
    """
    Vérifie si une chaîne représente une date valide au format français (DD/MM/YYYY).
    
    Args:
        date_string (str): La chaîne à valider
        
    Returns:
        bool: True si la date est valide et au bon format, False sinon
        
    Example:
        >>> is_valid_date("31/12/2024")
        True
        >>> is_valid_date("32/12/2024")
        False
    """
    # Vérifie d'abord le format avec une expression régulière
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', date_string):
        return False
    
    # Essaie de convertir la chaîne en objet date
    try:
        datetime.strptime(date_string, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def get_current_date():
    """
    Retourne la date actuelle au format français (JJ/MM/AAAA).
    Utile pour pré-remplir les champs de date avec la date du jour.
    
    Returns:
        str: La date actuelle au format JJ/MM/AAAA
        
    Example:
        >>> get_current_date()
        "06/01/2024"
    """
    return datetime.now().strftime("%d/%m/%Y")
