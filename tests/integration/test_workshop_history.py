from ..test_base import BaseTestCase
from src.ui.workshop_history import WorkshopHistory
from src.models.user import User
from src.models.workshop import Workshop
import customtkinter as ctk

class TestWorkshopHistory(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.root = ctk.CTk()
        self.workshop_history = WorkshopHistory(self.root, self.db_manager)

    def tearDown(self):
        super().tearDown()
        self.root.destroy()

    def test_load_history(self):
        # Créer des utilisateurs et des ateliers
        user1 = User(nom="Doe", prenom="John", telephone="0123456789")
        user1.save(self.db_manager)
        user2 = User(nom="Smith", prenom="Jane", telephone="9876543210")
        user2.save(self.db_manager)

        Workshop(user_id=user1.id, categorie="Test1", date="01/01/2023", conseiller="Conseiller1").save(self.db_manager)
        Workshop(user_id=user2.id, categorie="Test2", date="02/01/2023", conseiller="Conseiller2").save(self.db_manager)

        self.workshop_history.load_history()

        # Vérifier que les ateliers sont affichés dans l'historique
        children = self.workshop_history.history_frame.winfo_children()
        self.assertGreater(len(children), 2)  # Au moins les en-têtes et deux lignes d'ateliers
