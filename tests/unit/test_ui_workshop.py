import unittest
import sys
import os
from datetime import datetime
from unittest.mock import MagicMock

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseUITestCase
from src.ui.add_workshop import AddWorkshop, get_workshop_types
from src.models.workshop import Workshop
from src.models.user import User
from src.utils.date_utils import convert_to_db_date

class TestWorkshopUI(BaseUITestCase):
    def setUp(self):
        super().setUp()
        # Créer un utilisateur de test
        self.test_user = User(
            nom="Dupont",
            prenom="Jean",
            telephone="0123456789",
            email="jean.dupont@test.com"
        )
        self.test_user.id = self.db_manager.add_user(self.test_user)
        
        # Créer un atelier de test
        self.test_workshop = Workshop(
            user_id=self.test_user.id,
            description="Atelier test",
            categorie="Test",
            payant=True,
            date=datetime.now().strftime("%Y-%m-%d"),
            conseiller="Test Conseiller"
        )
        self.test_workshop.id = self.db_manager.add_workshop(self.test_workshop)
        
        def update_callback():
            pass  # Callback vide pour les tests
            
        def show_user_edit_callback():
            pass  # Callback vide pour les tests
            
        self.window = AddWorkshop(self.root, self.db_manager, self.test_user, show_user_edit_callback, update_callback)

    def tearDown(self):
        super().tearDown()
        self.window.destroy()

    def test_init(self):
        """Test l'initialisation de la fenêtre d'atelier"""
        self.assertIsNotNone(self.window)
        # Vérifier la présence des composants principaux
        self.assertTrue(hasattr(self.window, "date_entry"))
        self.assertTrue(hasattr(self.window, "workshop_type_var"))
        self.assertTrue(hasattr(self.window, "conseiller_entry"))
        self.assertTrue(hasattr(self.window, "paid_var"))
        self.assertTrue(hasattr(self.window, "description_entry"))

    def test_add_workshop(self):
        """Test l'ajout d'un nouvel atelier"""
        # Remplir les champs
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.window.date_entry.delete(0, "end")
        self.window.date_entry.insert(0, current_date)
        self.window.workshop_type_var.set(get_workshop_types()[0])
        self.window.conseiller_entry.delete(0, "end")
        self.window.conseiller_entry.insert(0, "Conseiller test")
        self.window.paid_var.set(True)
        self.window.description_entry.delete("1.0", "end")
        self.window.description_entry.insert("1.0", "Description test")
        
        # Simuler le clic sur le bouton de sauvegarde
        self.window.add_workshop()
        
        # Vérifier que l'atelier a été ajouté
        workshops = self.db_manager.get_user_workshops(self.test_user.id)
        found = False
        for w in workshops:
            if (w.conseiller == "Conseiller test" and 
                w.description.strip() == "Description test" and
                w.date == convert_to_db_date(current_date)):
                found = True
                break
        self.assertTrue(found, "L'atelier n'a pas été trouvé dans la base de données")

    def test_validation(self):
        """Test la validation des champs obligatoires"""
        # Tester la sauvegarde sans conseiller
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.window.date_entry.delete(0, "end")
        self.window.date_entry.insert(0, current_date)
        self.window.workshop_type_var.set(get_workshop_types()[0])
        self.window.description_entry.delete("1.0", "end")
        self.window.description_entry.insert("1.0", "Description test")
        
        # La sauvegarde devrait échouer car le conseiller est manquant
        result = self.window.add_workshop()
        self.assertFalse(result, "L'ajout de l'atelier aurait dû échouer car le conseiller est manquant")
        
        # Vérifier qu'aucun atelier n'a été ajouté
        initial_count = len(self.db_manager.get_user_workshops(self.test_user.id))
        self.window.add_workshop()
        final_count = len(self.db_manager.get_user_workshops(self.test_user.id))
        self.assertEqual(initial_count, final_count, "Un atelier a été ajouté alors qu'il manque le conseiller")

    def test_payment_status(self):
        """Test la gestion du statut de paiement"""
        # Vérifier l'état initial
        self.assertFalse(self.window.paid_var.get())
        
        # Changer le statut
        self.window.paid_var.set(True)
        
        # Vérifier que le changement est pris en compte
        self.assertTrue(self.window.paid_var.get()) 