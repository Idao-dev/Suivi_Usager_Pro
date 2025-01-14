import unittest
import sys
import os

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseTestCase
from src.models.user import User
from src.models.workshop import Workshop
from src.utils.date_utils import get_current_date
from datetime import datetime, timedelta
from src.utils.rgpd_manager import RGPDManager

class TestUser(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.rgpd_manager = RGPDManager(self.db_manager)

    def test_user_creation(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        self.assertIsNotNone(user.id)

    def test_get_inactive_users(self):
        # Créer des utilisateurs avec différentes dates d'activité
        user1 = User(nom="Doe", prenom="John", telephone="0123456789")
        user1.save(self.db_manager)
        user2 = User(nom="Smith", prenom="Jane", telephone="9876543210")
        user2.save(self.db_manager)
        user3 = User(nom="Brown", prenom="Bob", telephone="5555555555")
        user3.save(self.db_manager)

        # Simuler une activité récente pour user1 (atelier)
        Workshop(
            user_id=user1.id,
            categorie="Test",
            date=datetime.now().strftime("%Y-%m-%d"),
            conseiller="Conseiller Test"
        ).save(self.db_manager)

        # Simuler une activité ancienne pour user2 (atelier)
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        Workshop(
            user_id=user2.id,
            categorie="Test",
            date=old_date,
            conseiller="Conseiller Test"
        ).save(self.db_manager)

        # Modifier la date de création de user3 pour qu'elle soit ancienne
        user3.date_creation = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        user3.save(self.db_manager)

        # Vérifier les utilisateurs inactifs
        inactive_users = User.get_inactive_users(self.db_manager, 365)
        
        self.assertEqual(len(inactive_users), 2)
        self.assertIn(user2.id, [u.id for u in inactive_users])
        self.assertIn(user3.id, [u.id for u in inactive_users])

    def test_user_update(self):
        user = User(nom="Dupont", prenom="Marie", date_naissance="1990-01-01", telephone="0123456789")
        user.save(self.db_manager)
        
        user.nom = "Martin"
        user.save(self.db_manager)
        
        updated_user = User.get_by_id(self.db_manager, user.id)
        self.assertEqual(updated_user.nom, "Martin")

    def test_user_delete(self):
        user = User(nom="Dupont", prenom="Marie", date_naissance="1990-01-01", telephone="0123456789")
        user.save(self.db_manager)
        
        User.delete(self.db_manager, user.id)
        
        self.assertIsNone(User.get_by_id(self.db_manager, user.id))

    def test_delete_all_inactive_users(self):
        user1 = User(nom="Doe", prenom="John", telephone="0123456789")
        user1.save(self.db_manager)
        user2 = User(nom="Smith", prenom="Jane", telephone="9876543210")
        user2.save(self.db_manager)

        # Simuler une activité récente pour user1
        Workshop(
            user_id=user1.id,
            categorie="Test",
            date=datetime.now().strftime("%Y-%m-%d"),
            conseiller="Conseiller Test"
        ).save(self.db_manager)

        # Simuler une activité ancienne pour user2
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        Workshop(
            user_id=user2.id,
            categorie="Test",
            date=old_date,
            conseiller="Conseiller Test"
        ).save(self.db_manager)

        self.rgpd_manager.delete_all_inactive_users(365)

        self.assertIsNotNone(User.get_by_id(self.db_manager, user1.id))
        self.assertIsNone(User.get_by_id(self.db_manager, user2.id))

    def test_delete_inactive_user(self):
        user = User(nom="Test", prenom="Inactif", telephone="1234567890")
        user.save(self.db_manager)
        
        # Créer un atelier pour cet utilisateur
        workshop = Workshop(user_id=user.id, categorie="Test", date=(datetime.now() - timedelta(days=400)).strftime("%d/%m/%Y"), conseiller="Test")
        workshop.save(self.db_manager)
        
        User.delete(self.db_manager, user.id)
        
        # Vérifier que l'utilisateur a été supprimé
        self.assertIsNone(User.get_by_id(self.db_manager, user.id))
        
        # Vérifier que l'atelier existe toujours mais n'est plus associé à l'utilisateur
        updated_workshop = Workshop.get_by_id(self.db_manager, workshop.id)
        self.assertIsNotNone(updated_workshop)
        self.assertIsNone(updated_workshop.user_id)

class TestWorkshop(BaseTestCase):
    def test_workshop_creation(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        
        workshop = Workshop(user_id=user.id, categorie="Atelier individuel", date="2023-01-01", conseiller="Test Conseiller")
        workshop.save(self.db_manager)
        self.assertIsNotNone(workshop.id)

    def test_get_workshops_for_user(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        
        workshop1 = Workshop(user_id=user.id, categorie="Atelier individuel", date="2023-01-01", conseiller="Test Conseiller")
        workshop1.save(self.db_manager)
        workshop2 = Workshop(user_id=user.id, categorie="Démarche administrative", date="2023-01-02", conseiller="Test Conseiller")
        workshop2.save(self.db_manager)
        
        user_workshops = Workshop.get_by_user(self.db_manager, user.id)
        self.assertEqual(len(user_workshops), 2)

    def test_workshop_update(self):
        user = User(nom="Dupont", prenom="Marie", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel", conseiller="Test Conseiller")
        workshop.save(self.db_manager)

        workshop.description = "Updated Workshop"
        workshop.save(self.db_manager)

        updated_workshop = Workshop.get_by_id(self.db_manager, workshop.id)
        self.assertEqual(updated_workshop.description, "Updated Workshop")

    def test_workshop_delete(self):
        user = User(nom="Dupont", prenom="Marie", telephone="0123456789")
        user.save(self.db_manager)

        workshop = Workshop(user_id=user.id, description="Test Workshop", categorie="Individuel", conseiller="Test Conseiller")
        workshop.save(self.db_manager)

        Workshop.delete(self.db_manager, workshop.id)

        self.assertIsNone(Workshop.get_by_id(self.db_manager, workshop.id))

if __name__ == '__main__':
    unittest.main()
