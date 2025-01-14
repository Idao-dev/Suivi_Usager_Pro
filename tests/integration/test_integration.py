import unittest
from ..test_base import BaseTestCase
from models.user import User
from models.workshop import Workshop

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

        self.assertIsNone(User.get_by_id(self.db_manager, user.id))
        self.assertIsNone(Workshop.get_by_id(self.db_manager, workshop.id))
