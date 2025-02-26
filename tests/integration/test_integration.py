import unittest
import sys
import os

# Ajouter le répertoire racine du projet au chemin d'importation
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseTestCase
from src.models.user import User
from src.models.workshop import Workshop

class TestUserWorkshopIntegration(BaseTestCase):
    def test_user_workshop_creation(self):
        user = User(nom="Dupont", prenom="Jean", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel")
        workshop.save(self.db_manager)

        fetched_user = User.get_by_id(self.db_manager, user.id)
        fetched_workshop = Workshop.get_by_id(self.db_manager, workshop.id)

        self.assertEqual(fetched_user.nom, "Dupont")
        self.assertEqual(fetched_workshop.description, "Test Workshop")
        self.assertEqual(fetched_workshop.user_id, fetched_user.id)

    def test_user_deletion_cascade(self):
        user = User(nom="Dupont", prenom="Jean", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel")
        workshop.save(self.db_manager)

        User.delete(self.db_manager, user.id)

        # Vérifier que l'utilisateur a été supprimé
        self.assertIsNone(User.get_by_id(self.db_manager, user.id))
        
        # Vérifier que l'atelier existe toujours mais avec user_id = NULL
        updated_workshop = Workshop.get_by_id(self.db_manager, workshop.id)
        self.assertIsNotNone(updated_workshop)
        self.assertIsNone(updated_workshop.user_id)
