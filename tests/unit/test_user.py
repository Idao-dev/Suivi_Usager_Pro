"""
Tests unitaires pour la classe User.
"""

import pytest
from src.models.user import User
from src.models.workshop import Workshop

class TestUser:
    """Tests pour les méthodes de User qui ne nécessitent pas de base de données."""
    
    def test_user_initialization(self):
        """Teste l'initialisation d'un utilisateur."""
        user = User(
            id=1,
            nom="Dupont",
            prenom="Jean",
            date_naissance="01/01/1990",
            email="jean.dupont@example.com",
            telephone="0123456789",
            adresse="123 Rue de la Paix",
            date_creation="01/01/2023",
            last_activity_date="01/02/2023",
            last_payment_date="01/01/2023"
        )
        
        assert user.id == 1
        assert user.nom == "Dupont"
        assert user.prenom == "Jean"
        assert user.date_naissance == "01/01/1990"
        assert user.email == "jean.dupont@example.com"
        assert user.telephone == "0123456789"
        assert user.adresse == "123 Rue de la Paix"
        assert user.date_creation == "01/01/2023"
        assert user.last_activity_date == "01/02/2023"
        assert user.last_payment_date == "01/01/2023"
    
    def test_user_required_fields(self):
        """Teste l'initialisation d'un utilisateur avec seulement les champs obligatoires."""
        user = User(
            nom="Dupont",
            prenom="Jean"
        )
        
        assert user.id is None
        assert user.nom == "Dupont"
        assert user.prenom == "Jean"
        assert user.date_naissance is None
        assert user.email is None
        assert user.adresse is None

@pytest.mark.usefixtures("db_manager")
class TestUserDB:
    """Tests pour les méthodes de User qui interagissent avec la base de données."""
    
    def test_save_new(self, db_manager):
        """Teste la sauvegarde d'un nouvel utilisateur."""
        user = User(
            nom="Dupont",
            prenom="Jean",
            date_naissance="01/01/1990",
            email="jean.dupont@example.com"
        )
        
        # Sauvegarder l'utilisateur
        user_id = user.save(db_manager)
        
        # Vérifier que l'ID a été attribué
        assert user_id is not None
        assert user.id == user_id
        
        # Récupérer l'utilisateur de la base de données
        saved_user = User.get_by_id(db_manager, user_id)
        
        # Vérifier que les données sont correctes
        assert saved_user.nom == "Dupont"
        assert saved_user.prenom == "Jean"
        assert saved_user.date_naissance == "01/01/1990"
        assert saved_user.email == "jean.dupont@example.com"
    
    def test_update_user(self, db_manager):
        """Teste la mise à jour d'un utilisateur existant."""
        # Créer et sauvegarder un utilisateur
        user = User(
            nom="Dupont",
            prenom="Jean",
            email="jean.dupont@example.com"
        )
        user_id = user.save(db_manager)
        
        # Modifier et sauvegarder l'utilisateur
        user.nom = "Martin"
        user.email = "jean.martin@example.com"
        user.save(db_manager)
        
        # Récupérer l'utilisateur mis à jour
        updated_user = User.get_by_id(db_manager, user_id)
        
        # Vérifier que les modifications ont été enregistrées
        assert updated_user.nom == "Martin"
        assert updated_user.email == "jean.martin@example.com"
    
    def test_get_by_id_not_found(self, db_manager):
        """Teste la récupération d'un utilisateur inexistant."""
        user = User.get_by_id(db_manager, 999)
        assert user is None
    
    def test_delete_user(self, db_manager):
        """Teste la suppression d'un utilisateur."""
        # Créer et sauvegarder un utilisateur
        user = User(
            nom="Dupont",
            prenom="Jean"
        )
        user_id = user.save(db_manager)
        
        # Vérifier que l'utilisateur existe
        assert User.get_by_id(db_manager, user_id) is not None
        
        # Supprimer l'utilisateur
        User.delete(db_manager, user_id)
        
        # Vérifier que l'utilisateur n'existe plus
        assert User.get_by_id(db_manager, user_id) is None
    
    def test_search_users(self, db_manager):
        """Teste la recherche d'utilisateurs."""
        # Créer des utilisateurs pour le test
        user1 = User(
            nom="Dupont",
            prenom="Jean",
            adresse="Paris"
        )
        user1.save(db_manager)
        
        user2 = User(
            nom="Martin",
            prenom="Pierre",
            adresse="Lyon"
        )
        user2.save(db_manager)
        
        user3 = User(
            nom="Durand",
            prenom="Paul",
            adresse="Paris"
        )
        user3.save(db_manager)
        
        # Rechercher par nom
        results = db_manager.search_users("Dup")
        assert len(results) > 0
        assert any(u.nom == "Dupont" for u in results)
        
        # Rechercher par prénom
        results = db_manager.search_users("Pierre")
        assert len(results) > 0
        assert any(u.prenom == "Pierre" for u in results)
    
    def test_get_all(self, db_manager):
        """Teste la récupération de tous les utilisateurs."""
        # Supprimer tous les utilisateurs existants
        for user in User.get_all(db_manager):
            User.delete(db_manager, user.id)
        
        # Créer des utilisateurs pour le test
        user1 = User(nom="Dupont", prenom="Jean")
        user1.save(db_manager)
        
        user2 = User(nom="Martin", prenom="Pierre")
        user2.save(db_manager)
        
        user3 = User(nom="Durand", prenom="Paul")
        user3.save(db_manager)
        
        # Récupérer tous les utilisateurs
        all_users = User.get_all(db_manager)
        
        # Vérifier qu'il y a exactement trois utilisateurs
        assert len(all_users) == 3
        
        # Vérifier que les utilisateurs sont bien présents
        noms = [u.nom for u in all_users]
        assert "Dupont" in noms
        assert "Martin" in noms
        assert "Durand" in noms
    
    def test_get_workshops(self, db_manager):
        """Teste la récupération des ateliers d'un utilisateur."""
        # Créer un utilisateur
        user = User(
            nom="Dupont",
            prenom="Jean"
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
        
        # Récupérer les ateliers de l'utilisateur
        workshops = user.get_workshops(db_manager)
        
        # Vérifier qu'il y a exactement deux ateliers
        assert len(workshops) == 2
        
        # Vérifier que ce sont les bons ateliers
        descriptions = [w.description for w in workshops]
        assert "Atelier 1" in descriptions
        assert "Atelier 2" in descriptions 