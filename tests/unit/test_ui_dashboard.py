import unittest
import sys
import os
from datetime import datetime
import customtkinter as ctk

# Ajouter le répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tests.test_base import BaseUITestCase
from src.ui.dashboard import Dashboard
from src.models.user import User
from src.models.workshop import Workshop

class TestDashboard(BaseUITestCase):
    def setUp(self):
        super().setUp()
        self.dashboard = Dashboard(self.root, self.db_manager)

    def test_init_components(self):
        """Test l'initialisation des composants du tableau de bord"""
        # Vérifier la présence des frames principaux
        self.assertIsNotNone(self.dashboard.stats_frame)
        self.assertIsNotNone(self.dashboard.graph_frame)
        self.assertIsNotNone(self.dashboard.recent_activities_frame)
        
        # Vérifier les widgets de statistiques
        self.assertIsNotNone(self.dashboard.users_count_label)
        self.assertIsNotNone(self.dashboard.workshops_count_label)
        self.assertIsNotNone(self.dashboard.active_users_label)
        
        # Vérifier les éléments du graphique
        self.assertIsNotNone(self.dashboard.graph_canvas)
        
        # Vérifier la liste des activités récentes
        self.assertIsNotNone(self.dashboard.activities_list)

    def test_stats_display(self):
        """Test l'affichage des statistiques"""
        # Créer des données de test
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)
        
        workshop = Workshop(
            user_id=user.id,
            categorie="Test",
            date=datetime.now().strftime("%Y-%m-%d"),
            conseiller="Test"
        )
        workshop.save(self.db_manager)
        
        # Mettre à jour les statistiques
        self.dashboard.update_stats()
        self.root.update()
        
        # Vérifier les valeurs affichées
        self.assertEqual(self.dashboard.users_count_label.cget("text"), "1")
        self.assertEqual(self.dashboard.workshops_count_label.cget("text"), "1")

    def test_recent_activities_display(self):
        """Test l'affichage des activités récentes"""
        # Créer plusieurs activités
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)
        
        for i in range(3):
            workshop = Workshop(
                user_id=user.id,
                categorie=f"Test {i}",
                date=datetime.now().strftime("%Y-%m-%d"),
                conseiller="Test"
            )
            workshop.save(self.db_manager)
        
        # Mettre à jour l'affichage
        self.dashboard.update_recent_activities()
        self.root.update()
        
        # Vérifier l'affichage des activités
        activities = self.dashboard.get_activities_list()
        self.assertEqual(len(activities), 3)

    def test_graph_display(self):
        """Test l'affichage du graphique"""
        # Créer des données pour le graphique
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)
        
        dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        for date in dates:
            workshop = Workshop(
                user_id=user.id,
                categorie="Test",
                date=date,
                conseiller="Test"
            )
            workshop.save(self.db_manager)
        
        # Mettre à jour le graphique
        self.dashboard.update_graph()
        self.root.update()
        
        # Vérifier que le graphique est créé
        self.assertTrue(self.dashboard.graph_canvas.winfo_exists())
        self.assertGreater(len(self.dashboard.graph_canvas.find_all()), 0)

    def test_responsive_behavior(self):
        """Test le comportement responsive du dashboard"""
        # Test avec une petite fenêtre
        self.root.geometry("400x300")
        self.root.update()
        self.wait_for(lambda: self.dashboard.winfo_width() == 400)
        
        # Vérifier l'adaptation des composants
        self.assertLessEqual(self.dashboard.stats_frame.winfo_width(), 400)
        self.assertLessEqual(self.dashboard.graph_frame.winfo_width(), 400)
        
        # Test avec une grande fenêtre
        self.root.geometry("1200x800")
        self.root.update()
        self.wait_for(lambda: self.dashboard.winfo_width() == 1200)
        
        # Vérifier l'adaptation des composants
        self.assertLessEqual(self.dashboard.stats_frame.winfo_width(), 1200)
        self.assertLessEqual(self.dashboard.graph_frame.winfo_width(), 1200)

    def test_refresh_behavior(self):
        """Test le comportement lors du rafraîchissement"""
        # État initial
        initial_stats = self.dashboard.get_current_stats()
        
        # Ajouter des données
        user = User(nom="Test", prenom="User", telephone="0123456789")
        user.save(self.db_manager)
        
        # Rafraîchir le dashboard
        self.dashboard.refresh_dashboard()
        self.root.update()
        
        # Vérifier la mise à jour
        updated_stats = self.dashboard.get_current_stats()
        self.assertNotEqual(initial_stats, updated_stats)

    def tearDown(self):
        self.dashboard.destroy()
        super().tearDown()

if __name__ == '__main__':
    unittest.main() 