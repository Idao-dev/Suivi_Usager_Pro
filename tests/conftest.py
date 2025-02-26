"""
Configuration des tests pour le projet SuiviUsagerPro.
Ce fichier est automatiquement chargé par pytest et sert à configurer l'environnement de test.
"""

import os
import sys
import pytest
import sqlite3
import tempfile
import time

# Ajouter le répertoire racine au PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Fixtures pour les tests
@pytest.fixture
def temp_db():
    """Crée une base de données temporaire pour les tests."""
    fd, path = tempfile.mkstemp()
    conn = sqlite3.connect(path)
    
    # Créer les tables nécessaires
    create_tables(conn)
    
    yield path
    
    # Nettoyer après les tests
    conn.close()
    os.close(fd)
    try:
        os.unlink(path)
    except PermissionError:
        # Si le fichier est encore utilisé, attendez un peu et réessayez
        time.sleep(0.5)
        try:
            os.unlink(path)
        except PermissionError:
            print(f"Impossible de supprimer le fichier temporaire: {path}")

def create_tables(conn):
    """Crée les tables nécessaires pour les tests."""
    cursor = conn.cursor()
    
    # Table users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        prenom TEXT NOT NULL,
        date_naissance TEXT,
        email TEXT,
        telephone TEXT,
        adresse TEXT,
        date_creation TEXT,
        last_activity_date TEXT,
        last_payment_date TEXT
    )
    ''')
    
    # Table workshops
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workshops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        description TEXT,
        categorie TEXT,
        payant BOOLEAN,
        paid BOOLEAN,
        date TEXT,
        conseiller TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Table settings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,
        value TEXT
    )
    ''')
    
    conn.commit()

@pytest.fixture
def db_manager():
    """Fixture pour obtenir un gestionnaire de base de données pour les tests."""
    from src.database.db_manager import DatabaseManager
    
    # Créer une base de données temporaire
    fd, path = tempfile.mkstemp()
    db = DatabaseManager(path)
    
    # Créer les tables - On utilise get_connection au lieu de conn
    with db.get_connection() as conn:
        create_tables(conn)
    
    yield db
    
    # Nettoyer - Assurez-vous que la connexion est fermée
    try:
        # Fermer explicitement toutes les connexions
        with db.get_connection() as conn:
            conn.close()
    except:
        pass
        
    os.close(fd)
    try:
        os.unlink(path)
    except PermissionError:
        # Si le fichier est encore utilisé, attendez un peu et réessayez
        time.sleep(0.5)
        try:
            os.unlink(path)
        except PermissionError:
            print(f"Impossible de supprimer le fichier temporaire: {path}")

@pytest.fixture
def mock_tkinter():
    """Fixture pour mocker tkinter pour les tests d'UI."""
    import sys
    from unittest.mock import MagicMock
    
    # Créer des mocks pour tkinter et ses modules
    sys.modules['tkinter'] = MagicMock()
    sys.modules['tkinter.ttk'] = MagicMock()
    sys.modules['tkinter.filedialog'] = MagicMock()
    sys.modules['tkinter.messagebox'] = MagicMock()
    sys.modules['customtkinter'] = MagicMock()
    
    yield
    
    # Nettoyer
    del sys.modules['tkinter']
    del sys.modules['tkinter.ttk']
    del sys.modules['tkinter.filedialog']
    del sys.modules['tkinter.messagebox']
    del sys.modules['customtkinter'] 