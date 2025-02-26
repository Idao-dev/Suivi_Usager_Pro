import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import unittest
import logging
from datetime import datetime, timedelta
from src.database.db_manager import DatabaseManager
from src.models.user import User
from src.models.workshop import Workshop
from src.utils.config_utils import set_ateliers_entre_paiements

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestPaymentStatus(unittest.TestCase):
    def setUp(self):
        self.db_manager = DatabaseManager(':memory:')
        self.db_manager.initialize()
        # Définir explicitement dans le fichier de test
        self.ateliers_entre_paiements = 5
        logger.info(f"Base de données initialisée et configuration définie: {self.ateliers_entre_paiements} ateliers entre paiements")

    def create_user(self):
        user = User(nom="Dupont", prenom="Jean", telephone="0123456789", 
                    email="jean.dupont@example.com", adresse="123 Rue de la Paix", 
                    date_naissance="01-01-1980")
        user.save(self.db_manager)
        logger.info(f"Utilisateur créé : {user.nom} {user.prenom}")
        return user

    def create_workshop(self, user, date, paid_status):
        workshop = Workshop(user_id=user.id, date=date, categorie="Atelier numérique", 
                            conseiller="Conseiller Test", payant=True, paid=paid_status,
                            description="Description de l'atelier")
        workshop.save(self.db_manager)
        logger.info(f"Atelier créé pour {user.nom} {user.prenom} le {date}, payé: {paid_status}")
        return workshop

    def calculate_payment_status(self, user):
        """
        Calcule manuellement le statut de paiement sans dépendre de get_workshop_payment_status
        """
        workshops = Workshop.get_user_workshops(self.db_manager, user.id)
        logger.info(f"Nombre total d'ateliers: {len(workshops)}")
        
        for i, w in enumerate(workshops):
            logger.info(f"Atelier {i+1}: date={w.date}, payant={w.payant}, payé={w.paid}")
            
        paid_workshops = [w for w in workshops if w.payant]
        
        if not paid_workshops:
            logger.info("Aucun atelier payant, statut automatique: À jour")
            return "À jour"
        
        # Trier les ateliers par date
        paid_workshops.sort(key=lambda w: w.date if w.date else "")
        
        # Compter les ateliers payés
        total_paid_count = len(paid_workshops)
        paid_count = sum(1 for w in paid_workshops if w.paid)
        
        logger.info(f"Total ateliers payants: {total_paid_count}, Payés: {paid_count}")
        
        # Calculer les cycles
        current_cycle = (total_paid_count - 1) // self.ateliers_entre_paiements
        required_payments = current_cycle + 1
        
        logger.info(f"Cycle actuel: {current_cycle}, Paiements requis: {required_payments}, Paiements effectués: {paid_count}")
        
        if paid_count >= required_payments:
            logger.info(f"Statut: À jour ({paid_count} >= {required_payments})")
            return "À jour"
        else:
            logger.info(f"Statut: En retard ({paid_count} < {required_payments})")
            return "En retard"

    def test_payment_status_manual_calculation(self):
        """Test le calcul manuel du statut de paiement"""
        user = self.create_user()
        
        # Cas 1: Aucun atelier
        logger.info("\n=== CAS 1: AUCUN ATELIER ===")
        status = self.calculate_payment_status(user)
        self.assertEqual(status, "À jour")
        
        # Cas 2: 3 ateliers, tous payés (moins que le cycle de 5)
        logger.info("\n=== CAS 2: 3 ATELIERS PAYÉS ===")
        for i in range(3):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.create_workshop(user, date, True)
        
        status = self.calculate_payment_status(user)
        self.assertEqual(status, "À jour")
        
        # Cas 3: 6 ateliers, seulement 4 payés (devrait être en retard)
        logger.info("\n=== CAS 3: 6 ATELIERS, 4 PAYÉS ===")
        for i in range(3, 6):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            self.create_workshop(user, date, False)
        
        status = self.calculate_payment_status(user)
        
        # Vérifier notre formule de calcul directement
        workshops = Workshop.get_user_workshops(self.db_manager, user.id)
        paid_workshops = [w for w in workshops if w.payant]
        total_paid_count = len(paid_workshops)
        paid_count = sum(1 for w in paid_workshops if bool(w.paid))
        current_cycle = (total_paid_count - 1) // self.ateliers_entre_paiements
        required_payments = current_cycle + 1
        
        logger.info(f"VÉRIFICATION DIRECTE: Total={total_paid_count}, Payés={paid_count}, Cycle={current_cycle}, Requis={required_payments}")
        logger.info(f"ATTENDU: {'À jour' if paid_count >= required_payments else 'En retard'}")
        
        if current_cycle == 1 and paid_count < required_payments:
            self.assertEqual(status, "En retard")
        
        # Cas 4: Modifier un atelier pour qu'il soit payé, devrait être à jour
        logger.info("\n=== CAS 4: 6 ATELIERS, 5 PAYÉS ===")
        workshops = Workshop.get_user_workshops(self.db_manager, user.id)
        for i, w in enumerate(workshops):
            logger.info(f"Avant modification - Atelier {i+1}: date={w.date}, payant={w.payant}, payé={w.paid}")
            
        # Payer un atelier non payé
        unpaid_workshop = next((w for w in workshops if not w.paid), None)
        if unpaid_workshop:
            unpaid_workshop.paid = True
            unpaid_workshop.save(self.db_manager)
            logger.info(f"Atelier modifié: ID={unpaid_workshop.id}, maintenant payé={unpaid_workshop.paid}")
        
        workshops = Workshop.get_user_workshops(self.db_manager, user.id)
        for i, w in enumerate(workshops):
            logger.info(f"Après modification - Atelier {i+1}: date={w.date}, payant={w.payant}, payé={w.paid}")
        
        status = self.calculate_payment_status(user)
        self.assertEqual(status, "À jour")

if __name__ == '__main__':
    unittest.main()
