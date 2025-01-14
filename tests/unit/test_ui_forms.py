import unittest
import sys
import os
from datetime import datetime
import customtkinter as ctk

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseUITestCase
from src.ui.add_user import AddUser
from src.ui.user_edit import UserEditFrame
from src.ui.add_workshop import AddWorkshop
from src.ui.edit_workshop import EditWorkshop
from src.models.user import User
from src.models.workshop import Workshop

class TestUIForms(BaseUITestCase):
    def setUp(self):
        super().setUp()
        # Créer un utilisateur de test
        self.test_user = User(
            nom="Test",
            prenom="User",
            telephone="0123456789",
            email="test@example.com",
            adresse="123 Test St"
        )
        self.test_user.save(self.db_manager)
        
        # Créer un atelier de test
        self.test_workshop = Workshop(
            user_id=self.test_user.id,
            description="Test Workshop",
            categorie="Test",
            date=datetime.now().strftime("%Y-%m-%d"),
            conseiller="Test Conseiller"
        )
        self.test_workshop.save(self.db_manager)

    def test_add_user_form_init(self):
        """Test l'initialisation du formulaire d'ajout d'utilisateur"""
        def on_submit():
            pass
        
        form = AddUser(self.root, self.db_manager, on_submit)
        self.root.update()
        
        # Vérifier la présence des champs requis
        self.assertIsNotNone(form.nom_entry)
        self.assertIsNotNone(form.prenom_entry)
        self.assertIsNotNone(form.telephone_entry)
        self.assertIsNotNone(form.email_entry)
        self.assertIsNotNone(form.adresse_entry)
        self.assertIsNotNone(form.submit_button)

    def test_add_user_form_validation(self):
        """Test la validation du formulaire d'ajout d'utilisateur"""
        # Mock du callback
        submitted = False
        def mock_submit():
            nonlocal submitted
            submitted = True
            
        # Créer le formulaire avec le mock
        form = AddUser(self.root, self.db_manager, mock_submit)
        
        # Remplir les champs requis
        form.nom_entry.insert(0, "Dupont")
        form.prenom_entry.insert(0, "Jean")
        form.date_naissance_entry.insert(0, "01/01/1990")
        form.telephone_entry.insert(0, "0123456789")
        form.email_entry.insert(0, "jean.dupont@email.com")
        
        # Simuler le clic sur le bouton de soumission
        self.simulate_click(form.submit_button)
        
        # Vérifier que le callback a été appelé
        self.assertTrue(submitted)

    def test_edit_user_form_init(self):
        """Test l'initialisation du formulaire d'édition d'utilisateur"""
        def on_submit():
            pass
        def show_user_management():
            pass
        def show_add_workshop():
            pass
        def edit_workshop():
            pass
        
        form = UserEditFrame(
            self.root, 
            self.db_manager, 
            self.test_user,
            show_user_management,
            show_add_workshop,
            edit_workshop,
            on_submit
        )
        self.root.update()
        
        # Vérifier que les champs sont pré-remplis
        self.assertEqual(form.nom_entry.get(), "Test")
        self.assertEqual(form.prenom_entry.get(), "User")
        self.assertEqual(form.telephone_entry.get(), "0123456789")
        self.assertEqual(form.email_entry.get(), "test@example.com")
        self.assertEqual(form.adresse_entry.get(), "123 Test St")

    def test_edit_user_form_update(self):
        """Test la mise à jour d'un utilisateur via le formulaire"""
        updated = False
        def on_submit():
            nonlocal updated
            updated = True
        def show_previous_page():
            pass

        form = UserEditFrame(self.root, self.db_manager, self.test_user, show_previous_page, lambda x: None, lambda x: None, on_submit)

        # Modifier les champs
        form.nom_entry.delete(0, 'end')
        form.nom_entry.insert(0, "Nouveau Nom")
        form.prenom_entry.delete(0, 'end')
        form.prenom_entry.insert(0, "Nouveau Prénom")
        form.telephone_entry.delete(0, 'end')
        form.telephone_entry.insert(0, "0123456789")

        # Simuler le clic sur le bouton de sauvegarde
        self.simulate_click(form.save_button)
        self.root.update()

        # Vérifier que la mise à jour a été effectuée
        self.assertTrue(updated)

        # Vérifier les modifications en base
        updated_user = User.get_by_id(self.db_manager, self.test_user.id)
        self.assertEqual(updated_user.nom, "Nouveau Nom")
        self.assertEqual(updated_user.prenom, "Nouveau Prénom")
        self.assertEqual(updated_user.telephone, "0123456789")

    def test_add_workshop_form_init(self):
        """Test l'initialisation du formulaire d'ajout d'atelier"""
        def on_submit():
            pass
        def show_user_edit():
            pass
        
        form = AddWorkshop(self.root, self.db_manager, self.test_user, show_user_edit, on_submit)
        self.root.update()
        
        # Vérifier la présence des champs requis
        self.assertIsNotNone(form.date_entry)
        self.assertIsNotNone(form.workshop_type_var)
        self.assertIsNotNone(form.conseiller_entry)
        self.assertIsNotNone(form.description_entry)
        self.assertIsNotNone(form.submit_button)

    def test_add_workshop_form_validation(self):
        """Test la validation du formulaire d'ajout d'atelier"""
        # Mock des callbacks
        submitted = False
        def mock_submit():
            nonlocal submitted
            submitted = True
            
        def mock_show_user_edit():
            pass
            
        # Créer le formulaire avec les mocks
        form = AddWorkshop(self.root, self.db_manager, self.test_user, mock_show_user_edit, mock_submit)
        
        # Remplir les champs requis
        form.date_entry.insert(0, "01/01/2024")
        form.conseiller_entry.insert(0, "Jean Conseiller")
        form.workshop_type_var.set("Atelier numérique")
        form.paid_var.set(1)
        
        # Simuler le clic sur le bouton de soumission
        self.simulate_click(form.submit_button)
        
        # Vérifier que le callback a été appelé
        self.assertTrue(submitted)

    def test_edit_workshop_form_init(self):
        """Test l'initialisation du formulaire d'édition d'atelier"""
        def on_submit():
            pass
        def show_previous_page():
            pass
        
        form = EditWorkshop(self.root, self.db_manager, self.test_workshop, on_submit, show_previous_page)
        self.root.update()
        
        # Vérifier que les champs sont pré-remplis
        self.assertEqual(form.description_entry.get("1.0", "end-1c"), "Test Workshop")
        self.assertEqual(form.categorie_entry.get(), "Test")
        self.assertEqual(form.conseiller_entry.get(), "Test Conseiller")

    def test_edit_workshop_form_update(self):
        """Test la mise à jour d'un atelier via le formulaire"""
        updated = False
        def on_submit():
            nonlocal updated
            updated = True
        def show_previous_page():
            pass

        form = EditWorkshop(self.root, self.db_manager, self.test_workshop, on_submit, show_previous_page)

        # Modifier les champs
        form.date_entry.delete(0, 'end')
        form.date_entry.insert(0, "02/01/2024")
        form.conseiller_entry.delete(0, 'end')
        form.conseiller_entry.insert(0, "Nouveau Conseiller")
        form.categorie_entry.delete(0, 'end')
        form.categorie_entry.insert(0, "Atelier numérique")  # Changer la catégorie
        form.paid_var.set(1)  # Marquer comme payé

        # Simuler le clic sur le bouton de mise à jour
        self.simulate_click(form.submit_button)
        self.root.update()

        # Vérifier que la mise à jour a été effectuée
        self.assertTrue(updated)

        # Vérifier les modifications en base
        updated_workshop = Workshop.get_by_id(self.db_manager, self.test_workshop.id)
        self.assertEqual(updated_workshop.conseiller, "Nouveau Conseiller")
        self.assertEqual(updated_workshop.categorie, "Atelier numérique")
        self.assertTrue(updated_workshop.paid)

    def test_form_responsive_behavior(self):
        """Test le comportement responsive des formulaires"""
        # Créer une fenêtre dédiée pour le test
        test_window = ctk.CTk()
        test_window.grid_columnconfigure(0, weight=1)
        test_window.grid_rowconfigure(0, weight=1)
        
        # Initialiser avec une taille fixe
        test_window.geometry("800x600")
        test_window.update()
        test_window.after(500)  # Attendre que la taille initiale soit appliquée
        test_window.update()
        
        form = AddUser(test_window, self.db_manager, lambda: None)
        form.grid(row=0, column=0, sticky="nsew")
        test_window.update()
        test_window.after(500)  # Attendre que le formulaire soit affiché
        test_window.update()
        
        # Vérifier la taille initiale
        form_initial_width = form.winfo_width()
        self.assertGreater(form_initial_width, 0, "La largeur initiale doit être positive")
        
        # Redimensionner la fenêtre
        test_window.geometry("400x600")
        test_window.update()
        test_window.after(500)  # Attendre que le redimensionnement soit appliqué
        test_window.update()
        
        # Vérifier que le formulaire s'est adapté
        form_final_width = form.winfo_width()
        self.assertLess(form_final_width, form_initial_width, 
                       f"La largeur finale ({form_final_width}) devrait être inférieure à la largeur initiale ({form_initial_width})")
        
        # Nettoyer
        test_window.destroy()

    def tearDown(self):
        super().tearDown()

if __name__ == '__main__':
    unittest.main() 