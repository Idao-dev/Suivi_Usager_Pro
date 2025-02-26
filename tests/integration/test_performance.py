import unittest
import time
import sys
import os

# Ajouter le répertoire racine du projet au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseTestCase
from src.models.user import User
from src.models.workshop import Workshop

class TestPerformance(BaseTestCase):
    def test_bulk_operations(self):
        start_time = time.time()

        # Créer 100 utilisateurs (réduit pour des tests plus rapides)
        for i in range(100):
            user = User(nom=f"User{i}", prenom=f"Test{i}", telephone=f"0123456{i:03d}")
            user.save(self.db_manager)

        # Créer 500 ateliers (réduit pour des tests plus rapides)
        for i in range(500):
            workshop = Workshop(user_id=(i % 100) + 1, description=f"Workshop{i}", categorie="Test")
            workshop.save(self.db_manager)

        # Effectuer 100 recherches (réduit pour des tests plus rapides)
        for i in range(100):
            User.get_by_id(self.db_manager, (i % 100) + 1)
            Workshop.get_by_id(self.db_manager, (i % 500) + 1)

        end_time = time.time()
        execution_time = end_time - start_time

        print(f"Temps total d'exécution : {execution_time} secondes")
        # Ajuster le seuil de temps pour des tests plus rapides
        self.assertLess(execution_time, 5)  # Assurez-vous que l'exécution prend moins de 5 secondes

if __name__ == '__main__':
    unittest.main()