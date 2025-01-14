import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import logging
from datetime import datetime, timedelta
from database.db_manager import DatabaseManager
from models.user import User
from models.workshop import Workshop
from utils.config_utils import set_ateliers_entre_paiements

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestPaymentStatus(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager(':memory:')
        self.db_manager.initialize()
        set_ateliers_entre_paiements(5)  # Définir 5 ateliers entre chaque paiement
        logger.info("Base de données initialisée et configuration définie")

    def create_user(self):
        user = User(nom="Dupont", prenom="Jean", telephone="0123456789", 
                    email="jean.dupont@example.com", adresse="123 Rue de la Paix", 
                    date_naissance="01-01-1980")
        user.save(self.db_manager)
        logger.info(f"Utilisateur créé : {user.nom} {user.prenom}")
        return user

    def create_workshop(self, user, date, paid_today):
        workshop = Workshop(user_id=user.id, date=date, categorie="Atelier numérique", 
                            conseiller="Conseiller Test", payant=True, paid_today=paid_today,
                            description="Description de l'atelier")
        workshop.save(self.db_manager)
        logger.info(f"Atelier créé pour {user.nom} {user.prenom} le {date}, payé: {paid_today}")
        return workshop

    def test_payment_status_up_to_date(self):
        user = self.create_user()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Créer 5 ateliers payés
        for i in range(5):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.create_workshop(user, date, True)

        status = user.get_workshop_payment_status(self.db_manager)
        logger.info(f"Statut de paiement pour {user.nom} {user.prenom}: {status}")
        self.assertEqual(status, "À jour")

    def test_payment_status_late(self):
        user = self.create_user()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Créer 6 ateliers, dont seulement 4 payés
        for i in range(6):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.create_workshop(user, date, i < 4)

        status = user.get_workshop_payment_status(self.db_manager)
        logger.info(f"Statut de paiement pour {user.nom} {user.prenom}: {status}")
        self.assertEqual(status, "En retard")

    def test_payment_status_no_workshops(self):
        user = self.create_user()
        status = user.get_workshop_payment_status(self.db_manager)
        logger.info(f"Statut de paiement pour {user.nom} {user.prenom} sans ateliers: {status}")
        self.assertEqual(status, "À jour")

    def test_payment_status_after_update(self):
        user = self.create_user()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Créer 6 ateliers non payés
        for i in range(6):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.create_workshop(user, date, False)

        status_before = user.get_workshop_payment_status(self.db_manager)
        logger.info(f"Statut de paiement avant mise à jour: {status_before}")
        self.assertEqual(status_before, "En retard")

        # Mettre à jour les 5 derniers ateliers comme payés
        workshops = Workshop.get_user_workshops(self.db_manager, user.id)
        for workshop in workshops[:5]:
            workshop.paid_today = True
            workshop.save(self.db_manager)
        logger.info("5 ateliers mis à jour comme payés")

        status_after = user.get_workshop_payment_status(self.db_manager)
        logger.info(f"Statut de paiement après mise à jour: {status_after}")
        self.assertEqual(status_after, "À jour")

if __name__ == '__main__':
    unittest.main()
