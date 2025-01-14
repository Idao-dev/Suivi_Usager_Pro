import unittest
import tkinter as tk
import customtkinter as ctk
from src.database.db_manager import DatabaseManager
import os
import tempfile

class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = os.environ.get('TEST_DB_PATH')
        cls.db_manager = DatabaseManager(cls.db_path)

    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db_manager = DatabaseManager(self.temp_db.name)
        self.db_manager.initialize()

    def tearDown(self):
        self.db_manager.close()
        os.unlink(self.temp_db.name)

    @classmethod
    def tearDownClass(cls):
        """
        Nettoyage après tous les tests de la classe.
        Ferme la connexion à la base de données et détruit la fenêtre.
        """
        if hasattr(cls, 'db_manager'):
            cls.db_manager.close()
        if hasattr(cls, 'root') and cls.root is not None:
            try:
                cls.root.quit()
                cls.root.destroy()
            except:
                pass

class BaseUITestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Initialiser Tkinter et CustomTkinter
        cls.root = tk.Tk()
        cls.root.withdraw()  # Cacher la fenêtre principale
        
        # Importer et configurer le thème
        from src.utils.theme import set_dark_theme
        set_dark_theme()
        
        # Définir une taille par défaut pour les tests
        cls.root.geometry("800x600")

    def setUp(self):
        super().setUp()
        # Forcer la mise à jour de l'interface
        self.root.update()

    def tearDown(self):
        super().tearDown()
        # Nettoyer les widgets créés pendant le test
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.update()

    @classmethod
    def tearDownClass(cls):
        # Détruire la fenêtre principale
        cls.root.destroy()
        super().tearDownClass()

    def simulate_click(self, widget):
        """Simule un clic sur un widget"""
        widget.event_generate('<Button-1>')
        widget.event_generate('<ButtonRelease-1>')
        widget.invoke()  # Pour les boutons CustomTkinter
        self.root.update()

    def simulate_key(self, widget, key):
        """Simule une frappe de touche dans un widget"""
        widget.event_generate('<Key>', keysym=key)
        self.root.update()

    def wait_for(self, condition, timeout=1000):
        """Attend qu'une condition soit vraie avec timeout"""
        start = self.root.tk.call('clock', 'milliseconds')
        while not condition():
            self.root.update()
            if self.root.tk.call('clock', 'milliseconds') - start > timeout:
                raise TimeoutError("Condition non remplie dans le délai imparti")
