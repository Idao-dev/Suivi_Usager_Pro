import unittest
import threading
import time
import customtkinter as ctk
from tkinter import TclError
import sys
import os
import queue
import sqlite3
import tempfile

# Ajoutez le répertoire racine du projet au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ui.main_window import MainWindow
from src.database.db_manager import DatabaseManager
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = None
        cls.temp_db = tempfile.NamedTemporaryFile(delete=False)
        cls.db_name = cls.temp_db.name
        cls.initialize_database()
        
        cls.gui_ready = threading.Event()
        cls.gui_queue = queue.Queue()
        
        def create_gui():
            cls.root = ctk.CTk()
            db_manager = DatabaseManager(cls.db_name)
            cls.main_window = MainWindow(cls.root, db_manager=db_manager)
            cls.main_window.pack(fill="both", expand=True)
            cls.gui_ready.set()
            cls.root.mainloop()

        cls.gui_thread = threading.Thread(target=create_gui)
        cls.gui_thread.start()
        cls.gui_ready.wait()

    @classmethod
    def tearDownClass(cls):
        if cls.root:
            cls.root.after(0, cls.root.quit)
            cls.gui_thread.join(timeout=5)
        if hasattr(cls, 'main_window'):
            cls.main_window.db_manager.close()
        cls.temp_db.close()
        time.sleep(0.1)  # Donnez un peu de temps pour que toutes les connexions se ferment
        try:
            os.unlink(cls.db_name)
        except PermissionError:
            print(f"Impossible de supprimer {cls.db_name}. Il sera supprimé à la prochaine exécution.")

    @classmethod
    def initialize_database(cls):
        db_manager = DatabaseManager(cls.db_name)
        db_manager.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                nom TEXT,
                prenom TEXT,
                telephone TEXT
            )
        """)
        db_manager.execute("""
            CREATE TABLE IF NOT EXISTS workshops (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                date TEXT,
                categorie TEXT,
                conseiller TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        db_manager.close()

    def setUp(self):
        self.db_manager = DatabaseManager(self.db_name)

    def tearDown(self):
        self.db_manager.close()

    def run_gui_command(self, command):
        self.gui_queue.put(command)
        self.root.after(0, self.process_gui_queue)
        time.sleep(0.2)  # Augmentez ce délai si nécessaire

    def process_gui_queue(self):
        try:
            command = self.gui_queue.get_nowait()
            command()
            self.gui_queue.task_done()
        except queue.Empty:
            pass

    def check_current_frame(self, expected_frame):
        if self.main_window.current_frame is None:
            self.fail(f"current_frame is None, expected {expected_frame}")
        current_frame = self.main_window.current_frame.__class__.__name__
        self.assertEqual(current_frame, expected_frame, f"Expected {expected_frame}, but got {current_frame}")

    def test_navigation_flow(self):
        logger.info("Starting navigation test")
        
        self.run_gui_command(self.main_window.show_user_management)
        self.check_current_frame("UserManagement")
        
        self.run_gui_command(self.main_window.show_add_user)
        self.check_current_frame("AddUser")
        
        self.run_gui_command(self.main_window.show_workshop_history)
        self.check_current_frame("WorkshopHistory")
        
        self.run_gui_command(self.main_window.show_settings)
        self.check_current_frame("Settings")
        
        self.run_gui_command(self.main_window.show_data_management)
        self.check_current_frame("DataManagement")
        
        self.run_gui_command(self.main_window.show_dashboard)
        self.check_current_frame("Dashboard")

    def test_add_user_navigation(self):
        logger.info("Testing add user navigation")
        self.run_gui_command(self.main_window.show_add_user)
        self.check_current_frame("AddUser")
        
        def add_user():
            self.main_window.add_user.nom_entry.insert(0, "Doe")
            self.main_window.add_user.prenom_entry.insert(0, "John")
            self.main_window.add_user.telephone_entry.insert(0, "0123456789")
            self.main_window.add_user.add_user()

        self.run_gui_command(add_user)
        self.check_current_frame("UserManagement")  # Assuming it redirects to UserManagement after adding

    def test_edit_user_navigation(self):
        logger.info("Testing edit user navigation")
        self.db_manager.execute("INSERT INTO users (nom, prenom, telephone) VALUES (?, ?, ?)", ("Doe", "John", "0123456789"))
        user_id = self.db_manager.cursor.lastrowid
        
        self.run_gui_command(self.main_window.show_user_management)
        self.check_current_frame("UserManagement")
        
        self.run_gui_command(lambda: self.main_window.user_management.edit_user(user_id))
        self.check_current_frame("UserEdit")

    def test_add_workshop_navigation(self):
        logger.info("Testing add workshop navigation")
        self.db_manager.execute("INSERT INTO users (nom, prenom, telephone) VALUES (?, ?, ?)", ("Doe", "John", "0123456789"))
        user_id = self.db_manager.cursor.lastrowid
        
        self.run_gui_command(self.main_window.show_user_management)
        self.check_current_frame("UserManagement")
        
        self.run_gui_command(lambda: self.main_window.user_management.add_workshop(user_id))
        self.check_current_frame("AddWorkshop")

if __name__ == '__main__':
    unittest.main()