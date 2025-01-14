from ..test_base import BaseTestCase
from src.utils.rgpd_manager import RGPDManager
from src.models.user import User
from src.models.workshop import Workshop
from datetime import datetime, timedelta
import tempfile
import os

class TestRGPDManager(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.rgpd_manager = RGPDManager(self.db_manager)

    def test_get_inactive_users(self):
        # Créer un utilisateur inactif avec un ancien atelier
        user = User(nom="Test", prenom="Inactif")
        user.save(self.db_manager)
        
        # Créer un atelier ancien (plus de 365 jours)
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        Workshop(user_id=user.id, categorie="Test", date=old_date, conseiller="Test").save(self.db_manager)
        
        inactive_users = self.rgpd_manager.get_inactive_users(365)
        self.assertGreater(len(inactive_users), 0)
        self.assertEqual(inactive_users[0].id, user.id)

    def test_delete_inactive_user(self):
        user = User(nom="Test", prenom="Inactif")
        user.save(self.db_manager)
        
        # Créer un atelier pour cet utilisateur
        workshop = Workshop(
            user_id=user.id, 
            categorie="Test", 
            date=(datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d"),
            conseiller="Test"
        )
        workshop_id = workshop.save(self.db_manager)
        
        self.rgpd_manager.delete_inactive_user(user)
        
        # Vérifier que l'utilisateur a été supprimé
        self.assertIsNone(User.get_by_id(self.db_manager, user.id))
        
        # Vérifier que l'atelier existe toujours mais n'est plus associé à l'utilisateur
        updated_workshop = Workshop.get_by_id(self.db_manager, workshop_id)
        self.assertIsNotNone(updated_workshop)
        self.assertIsNone(updated_workshop.user_id)

    def test_delete_all_inactive_users(self):
        user1 = User(nom="Doe", prenom="John", telephone="0123456789")
        user1.save(self.db_manager)
        user2 = User(nom="Smith", prenom="Jane", telephone="9876543210")
        user2.save(self.db_manager)

        # Ajouter un atelier récent pour user1
        recent_date = datetime.now().strftime("%Y-%m-%d")
        Workshop(user_id=user1.id, categorie="Test", date=recent_date, conseiller="Conseiller Test").save(self.db_manager)

        # Ajouter un atelier ancien pour user2
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        Workshop(user_id=user2.id, categorie="Test", date=old_date, conseiller="Conseiller Test").save(self.db_manager)

        self.rgpd_manager.delete_all_inactive_users(365)

        self.assertIsNotNone(User.get_by_id(self.db_manager, user1.id))
        self.assertIsNone(User.get_by_id(self.db_manager, user2.id))

    def test_export_inactive_users(self):
        """Test l'export des utilisateurs inactifs avant leur suppression."""
        # Créer des utilisateurs de test
        user1 = User(nom="Actif", prenom="User", telephone="0123456789")
        user1.save(self.db_manager)
        user2 = User(nom="Inactif", prenom="User", telephone="9876543210")
        user2.save(self.db_manager)

        # Simuler une activité récente pour user1
        Workshop(
            user_id=user1.id,
            categorie="Test",
            date=datetime.now().strftime("%Y-%m-%d"),
            conseiller="Test"
        ).save(self.db_manager)

        # Simuler une ancienne activité pour user2
        old_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        Workshop(
            user_id=user2.id,
            categorie="Test",
            date=old_date,
            conseiller="Test"
        ).save(self.db_manager)

        # Créer un fichier temporaire pour l'export
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp_file:
            export_path = tmp_file.name

        try:
            # Exporter les utilisateurs inactifs
            self.rgpd_manager.export_inactive_users(365, export_path)

            # Vérifier que le fichier existe et contient les bonnes données
            self.assertTrue(os.path.exists(export_path))
            with open(export_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("Inactif,User", content)
                self.assertNotIn("Actif,User", content)
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(export_path):
                os.unlink(export_path)

    def test_inactivity_period_config(self):
        """Test que la période d'inactivité configurée est bien prise en compte."""
        from src.utils.config_utils import set_inactivity_period, get_inactivity_period
        
        # Créer trois utilisateurs avec différentes dates d'activité
        user1 = User(nom="Recent", prenom="User")  # Activité < 12 mois
        user2 = User(nom="Moyen", prenom="User")   # Activité entre 12 et 24 mois
        user3 = User(nom="Ancien", prenom="User")  # Activité > 24 mois
        
        for user in [user1, user2, user3]:
            user.save(self.db_manager)
        
        # Créer des ateliers avec différentes dates
        Workshop(
            user_id=user1.id,
            categorie="Test",
            date=(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),  # 6 mois
            conseiller="Test"
        ).save(self.db_manager)
        
        Workshop(
            user_id=user2.id,
            categorie="Test",
            date=(datetime.now() - timedelta(days=540)).strftime("%Y-%m-%d"),  # 18 mois
            conseiller="Test"
        ).save(self.db_manager)
        
        Workshop(
            user_id=user3.id,
            categorie="Test",
            date=(datetime.now() - timedelta(days=900)).strftime("%Y-%m-%d"),  # 30 mois
            conseiller="Test"
        ).save(self.db_manager)
        
        # Test avec période de 12 mois
        set_inactivity_period(12)
        inactive_users_12m = self.rgpd_manager.get_inactive_users(365)  # 365 jours = 12 mois
        self.assertNotIn(user1.id, [u.id for u in inactive_users_12m])  # user1 devrait être actif
        self.assertIn(user2.id, [u.id for u in inactive_users_12m])     # user2 devrait être inactif
        self.assertIn(user3.id, [u.id for u in inactive_users_12m])     # user3 devrait être inactif
        
        # Test avec période de 24 mois
        set_inactivity_period(24)
        inactive_users_24m = self.rgpd_manager.get_inactive_users(730)  # 730 jours = 24 mois
        self.assertNotIn(user1.id, [u.id for u in inactive_users_24m])  # user1 devrait être actif
        self.assertNotIn(user2.id, [u.id for u in inactive_users_24m])  # user2 devrait être actif
        self.assertIn(user3.id, [u.id for u in inactive_users_24m])     # user3 devrait être inactif
