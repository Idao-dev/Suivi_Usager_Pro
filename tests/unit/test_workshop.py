"""
Tests unitaires pour la classe Workshop.
"""

import unittest
import pytest
from datetime import datetime
from src.models.workshop import Workshop
from src.models.user import User

class TestWorkshop(unittest.TestCase):
    """Tests pour la classe Workshop."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        pass
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        pass
    
    def test_workshop_initialization(self):
        """Teste l'initialisation d'un atelier."""
        workshop = Workshop(
            id=1,
            user_id=2,
            description="Atelier de test",
            categorie="Informatique",
            payant=True,
            paid=False,
            date="2023-01-01",
            conseiller="Dupont"
        )
        
        self.assertEqual(workshop.id, 1)
        self.assertEqual(workshop.user_id, 2)
        self.assertEqual(workshop.description, "Atelier de test")
        self.assertEqual(workshop.categorie, "Informatique")
        self.assertTrue(workshop.payant)
        self.assertFalse(workshop.paid)
        self.assertEqual(workshop.date, "2023-01-01")
        self.assertEqual(workshop.conseiller, "Dupont")
    
    def test_to_dict(self):
        """Teste la conversion en dictionnaire."""
        workshop = Workshop(
            id=1,
            user_id=2,
            description="Atelier de test",
            categorie="Informatique",
            payant=True,
            paid=False,
            date="2023-01-01",
            conseiller="Dupont"
        )
        
        expected_dict = {
            'id': 1,
            'user_id': 2,
            'description': "Atelier de test",
            'categorie': "Informatique",
            'payant': True,
            'paid': False,
            'date': "2023-01-01",
            'conseiller': "Dupont"
        }
        
        self.assertEqual(workshop.to_dict(), expected_dict)
    
    def test_from_db(self):
        """Teste la création d'un atelier depuis une ligne de base de données."""
        row = {
            'id': 1,
            'user_id': 2,
            'description': "Atelier de test",
            'categorie': "Informatique",
            'payant': True,
            'paid': False,
            'date': "2023-01-01",
            'conseiller': "Dupont"
        }
        
        workshop = Workshop.from_db(row)
        
        self.assertEqual(workshop.id, 1)
        self.assertEqual(workshop.user_id, 2)
        self.assertEqual(workshop.description, "Atelier de test")
        self.assertEqual(workshop.categorie, "Informatique")
        self.assertTrue(workshop.payant)
        self.assertFalse(workshop.paid)
        self.assertEqual(workshop.date, "2023-01-01")
        self.assertEqual(workshop.conseiller, "Dupont")
    
    def test_from_db_with_none_user_id(self):
        """Teste la création d'un atelier depuis une ligne avec user_id à None."""
        row = {
            'id': 1,
            'user_id': None,
            'description': "Atelier de test",
            'categorie': "Informatique",
            'payant': True,
            'paid': False,
            'date': "2023-01-01",
            'conseiller': "Dupont"
        }
        
        workshop = Workshop.from_db(row)
        
        self.assertEqual(workshop.id, 1)
        self.assertIsNone(workshop.user_id)
        self.assertEqual(workshop.description, "Atelier de test")
    
    def test_get_state(self):
        """Teste la méthode get_state."""
        workshop = Workshop(
            id=1,
            user_id=2,
            description="Atelier de test",
            categorie="Informatique",
            payant=True,
            paid=False,
            date="2023-01-01",
            conseiller="Dupont"
        )
        
        expected_state = {
            'id': 1,
            'user_id': 2,
            'description': "Atelier de test",
            'categorie': "Informatique",
            'payant': True,
            'paid': False,
            'date': "2023-01-01",
            'conseiller': "Dupont"
        }
        
        self.assertEqual(workshop.get_state(), expected_state)

@pytest.mark.usefixtures("db_manager")
class TestWorkshopDB:
    """Tests pour les méthodes de Workshop qui interagissent avec la base de données."""
    
    def test_save_new(self, db_manager):
        """Teste la sauvegarde d'un nouvel atelier."""
        workshop = Workshop(
            description="Nouvel atelier",
            categorie="Test",
            payant=True,
            paid=False,
            date="2023-01-01",
            conseiller="Dupont"
        )
        
        # Sauvegarder l'atelier
        workshop_id = workshop.save(db_manager)
        
        # Vérifier que l'ID a été attribué
        assert workshop_id is not None
        assert workshop.id == workshop_id
        
        # Récupérer l'atelier de la base de données
        saved_workshop = Workshop.get_by_id(db_manager, workshop_id)
        
        # Vérifier que les données sont correctes
        assert saved_workshop.description == "Nouvel atelier"
        assert saved_workshop.categorie == "Test"
        assert bool(saved_workshop.payant) == True
        assert bool(saved_workshop.paid) == False
        assert saved_workshop.date == "2023-01-01"
        assert saved_workshop.conseiller == "Dupont"
    
    def test_save_update(self, db_manager):
        """Teste la mise à jour d'un atelier existant."""
        # Créer et sauvegarder un atelier
        workshop = Workshop(
            description="Atelier initial",
            categorie="Test",
            payant=True,
            paid=False,
            date="2023-01-01",
            conseiller="Dupont"
        )
        workshop_id = workshop.save(db_manager)
        
        # Modifier et sauvegarder l'atelier
        workshop.description = "Atelier modifié"
        workshop.paid = True
        workshop.save(db_manager)
        
        # Récupérer l'atelier mis à jour
        updated_workshop = Workshop.get_by_id(db_manager, workshop_id)
        
        # Vérifier que les modifications ont été enregistrées
        assert updated_workshop.description == "Atelier modifié"
        assert bool(updated_workshop.paid) == True
    
    def test_get_by_id_not_found(self, db_manager):
        """Teste la récupération d'un atelier inexistant."""
        workshop = Workshop.get_by_id(db_manager, 999)
        assert workshop is None
    
    def test_delete(self, db_manager):
        """Teste la suppression d'un atelier."""
        # Créer et sauvegarder un atelier
        workshop = Workshop(
            description="Atelier à supprimer",
            categorie="Test",
            date="2023-01-01"
        )
        workshop_id = workshop.save(db_manager)
        
        # Vérifier que l'atelier existe
        assert Workshop.get_by_id(db_manager, workshop_id) is not None
        
        # Supprimer l'atelier
        Workshop.delete(db_manager, workshop_id)
        
        # Vérifier que l'atelier n'existe plus
        assert Workshop.get_by_id(db_manager, workshop_id) is None
    
    def test_get_by_user(self, db_manager):
        """Teste la récupération des ateliers d'un utilisateur."""
        # Créer un utilisateur
        user = User(
            nom="Doe",
            prenom="John",
            date_naissance="1990-01-01",
            email="john.doe@example.com"
        )
        user_id = user.save(db_manager)
        
        # Créer des ateliers pour cet utilisateur
        workshop1 = Workshop(
            user_id=user_id,
            description="Atelier 1",
            date="2023-01-01"
        )
        workshop1.save(db_manager)
        
        workshop2 = Workshop(
            user_id=user_id,
            description="Atelier 2",
            date="2023-01-02"
        )
        workshop2.save(db_manager)
        
        # Créer un atelier pour un autre utilisateur
        workshop3 = Workshop(
            user_id=None,
            description="Atelier 3",
            date="2023-01-03"
        )
        workshop3.save(db_manager)
        
        # Récupérer les ateliers de l'utilisateur
        user_workshops = Workshop.get_by_user(db_manager, user_id)
        
        # Vérifier qu'il y a exactement deux ateliers pour cet utilisateur
        assert len(user_workshops) == 2
        assert user_workshops[0].description == "Atelier 2"  # Le plus récent en premier
        assert user_workshops[1].description == "Atelier 1"
    
    def test_get_orphan_workshops(self, db_manager):
        """Teste la récupération des ateliers sans utilisateur associé."""
        # Créer des ateliers sans utilisateur
        workshop1 = Workshop(
            user_id=None,
            description="Atelier orphelin 1",
            date="2023-01-01"
        )
        workshop1.save(db_manager)
        
        workshop2 = Workshop(
            user_id=None,
            description="Atelier orphelin 2",
            date="2023-01-02"
        )
        workshop2.save(db_manager)
        
        # Créer un atelier avec un utilisateur
        user = User(
            nom="Doe",
            prenom="John",
            date_naissance="1990-01-01"
        )
        user_id = user.save(db_manager)
        
        workshop3 = Workshop(
            user_id=user_id,
            description="Atelier avec utilisateur",
            date="2023-01-03"
        )
        workshop3.save(db_manager)
        
        # Récupérer les ateliers orphelins
        orphan_workshops = Workshop.get_orphan_workshops(db_manager)
        
        # Vérifier qu'il y a exactement deux ateliers orphelins
        assert len(orphan_workshops) == 2
        descriptions = [w.description for w in orphan_workshops]
        assert "Atelier orphelin 1" in descriptions
        assert "Atelier orphelin 2" in descriptions
    
    def test_get_user(self, db_manager):
        """Teste la méthode get_user."""
        # Créer un utilisateur
        user = User(
            nom="Dupont",
            prenom="Jean",
            date_naissance="1990-01-01"
        )
        user_id = user.save(db_manager)
        
        # Créer un atelier associé à cet utilisateur
        workshop = Workshop(
            user_id=user_id,
            description="Atelier test get_user",
            date="2023-01-01"
        )
        workshop.save(db_manager)
        
        # Récupérer l'utilisateur associé à l'atelier
        retrieved_user = workshop.get_user(db_manager)
        
        # Vérifier que c'est le bon utilisateur
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.nom == "Dupont"
        assert retrieved_user.prenom == "Jean"
        
    def test_get_user_none(self, db_manager):
        """Teste la méthode get_user quand il n'y a pas d'utilisateur associé."""
        workshop = Workshop(
            user_id=None,
            description="Atelier sans utilisateur",
            date="2023-01-01"
        )
        workshop.save(db_manager)
        
        # Récupérer l'utilisateur associé à l'atelier
        retrieved_user = workshop.get_user(db_manager)
        
        # Vérifier qu'il n'y a pas d'utilisateur
        assert retrieved_user is None 