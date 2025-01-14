import unittest
import time
from ..test_base import BaseTestCase
from models.user import User
from models.workshop import Workshop

class TestPerformance(BaseTestCase):
    def test_bulk_operations(self):
        start_time = time.time()

        # Créer 1000 utilisateurs
        for i in range(1000):
            user = User(nom=f"User{i}", prenom=f"Test{i}", telephone=f"0123456{i:03d}")
            user.save(self.db_manager)

        # Créer 5000 ateliers
        for i in range(5000):
            workshop = Workshop(user_id=(i % 1000) + 1, description=f"Workshop{i}", categorie="Test")
            workshop.save(self.db_manager)

        # Effectuer 1000 recherches
        for i in range(1000):
            User.get_by_id(self.db_manager, (i % 1000) + 1)
            Workshop.get_by_id(self.db_manager, (i % 5000) + 1)

        end_time = time.time()
        execution_time = end_time - start_time

        print(f"Temps total d'exécution : {execution_time} secondes")
        self.assertLess(execution_time, 10)  # Assurez-vous que l'exécution prend moins de 10 secondes

if __name__ == '__main__':
    unittest.main()