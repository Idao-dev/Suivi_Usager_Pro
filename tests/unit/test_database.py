from ..test_base import BaseTestCase
from src.models.user import User
from src.models.workshop import Workshop
from datetime import datetime

class TestDatabaseManager(BaseTestCase):
    def test_connection(self):
        # Vérifiez simplement que la connexion peut être établie
        with self.db_manager.get_connection() as conn:
            self.assertIsNotNone(conn)

    def test_create_tables(self):
        # Ce test reste inchangé
        pass

    def test_insert_and_fetch(self):
        self.db_manager.execute("INSERT INTO users (nom, prenom, telephone, date_creation) VALUES (?, ?, ?, ?)", 
                                ('Doe', 'John', '0123456789', datetime.now().strftime("%Y-%m-%d")))
        
        result = self.db_manager.fetch_one("SELECT * FROM users WHERE nom = ?", ('Doe',))
        self.assertIsNotNone(result)
        self.assertEqual(result['nom'], 'Doe')
        self.assertEqual(result['prenom'], 'John')

    def test_create_user(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        
        retrieved_user = User.get_by_id(self.db_manager, user.id)
        self.assertEqual(retrieved_user.nom, "Doe")
        self.assertEqual(retrieved_user.prenom, "John")

    def test_create_workshop(self):
        user = User(nom="Doe", prenom="John", telephone="0123456789")
        user.save(self.db_manager)
        
        workshop = Workshop(user_id=user.id, categorie="Atelier individuel", date="2023-01-01", conseiller="Test Conseiller")
        workshop.save(self.db_manager)
        
        retrieved_workshop = Workshop.get_by_id(self.db_manager, workshop.id)
        self.assertEqual(retrieved_workshop.categorie, "Atelier individuel")
        self.assertEqual(retrieved_workshop.date, "2023-01-01")
        self.assertEqual(retrieved_workshop.conseiller, "Test Conseiller")

    def test_search_users_methods(self):
        """
        Test des différentes méthodes de recherche d'utilisateurs :
        1. Recherche exacte + Soundex pour les noms
        2. Recherche partielle (LIKE)
        3. Recherche avec Levenshtein à différentes distances
        """
        # Création des utilisateurs de test avec plus de variations
        test_users = [
            ("Dubois", "Pierre", "0123456789"),
            ("Dupont", "Marie", "0234567890"),
            ("Martin", "Jean", "0345678901"),
            ("Durand", "Sophie", "0456789012"),
            ("Petit", "Lucas", "0567890123"),
            ("Dupond", "Paul", "0678901234"),     # Variante phonétique de Dupont
            ("Duboi", "Thomas", "0789012345"),    # Distance 1 de Dubois
            ("Duboit", "Alice", "0890123456"),    # Distance 1 de Dubois
            ("Dubua", "Claire", "0901234567"),    # Distance 2 de Dubois
            ("Duboas", "Marc", "0012345678"),     # Distance 2 de Dubois
            ("Duboix", "Julie", "1234567890"),    # Distance 1 de Dubois
        ]
        
        for nom, prenom, tel in test_users:
            user = User(nom=nom, prenom=prenom, telephone=tel)
            user.save(self.db_manager)

        # Test 1: Recherche par numéro de téléphone (exacte uniquement)
        results = self.db_manager.search_users("0123456789")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].telephone, "0123456789")

        # Test 2: Recherche de nom avec Soundex
        # Devrait trouver Dupont et Dupond car même code Soundex
        results = self.db_manager.search_users("Dupond")
        exact_match = next(u for u in results if u.nom == "Dupond")
        soundex_matches = [u for u in results if u.nom != "Dupond" and self.db_manager._soundex(u.nom) == self.db_manager._soundex("Dupond")]
        self.assertIsNotNone(exact_match)
        self.assertEqual(len(soundex_matches), 1)
        self.assertTrue(any(u.nom == "Dupont" for u in soundex_matches))

        # Test 3: Recherche avec faute de frappe (Levenshtein)
        # Test 3.1: Distance 1 - Recherche de "Duboi"
        results = self.db_manager.search_users("Duboi")
        # Vérifier que le résultat exact est en premier
        self.assertEqual(results[0].nom, "Duboi")
        # Vérifier que les résultats à distance 1 sont inclus
        distance_1_matches = [u for u in results if self.db_manager._levenshtein_distance(u.nom.lower(), "Duboi".lower()) <= 1]
        self.assertGreaterEqual(len(distance_1_matches), 2)  # Au moins "Duboi" et "Dubois"
        self.assertTrue(any(u.nom == "Dubois" for u in distance_1_matches))
        
        # Test 3.2: Vérification de l'ordre des résultats pour "Dubois"
        results = self.db_manager.search_users("Dubois")
        # Le résultat exact doit être en premier
        self.assertEqual(results[0].nom, "Dubois")
        # Les distances doivent être croissantes
        distances = [self.db_manager._levenshtein_distance(r.nom.lower(), "Dubois".lower()) for r in results]
        self.assertEqual(distances, sorted(distances))
        
        # Test 3.3: Limite du nombre de résultats
        self.assertLessEqual(len(results), 4)
        
        # Test 3.4: Recherche avec distance 2
        results = self.db_manager.search_users("Dubua")
        self.assertEqual(results[0].nom, "Dubua")  # Correspondance exacte d'abord
        # Vérifier que les résultats à distance 2 sont inclus après les distance 1
        for i in range(1, len(results)):
            dist = self.db_manager._levenshtein_distance(results[i].nom.lower(), "Dubua".lower())
            self.assertLessEqual(dist, 2)  # Distance maximale de 2

        # Test 4: Recherche partielle
        # Devrait trouver les 4 premiers noms commençant par "Du"
        results = self.db_manager.search_users("Du")
        du_matches = [u for u in results if u.nom.startswith("Du")]
        self.assertEqual(len(du_matches), 4)  # Limite aux 4 premiers résultats
        # Vérifier que tous les résultats commencent bien par "Du"
        self.assertTrue(all(u.nom.startswith("Du") for u in results))

    def test_soundex(self):
        """Test de la méthode Soundex"""
        # Test des cas basiques
        self.assertEqual(self.db_manager._soundex("Robert"), "R163")
        self.assertEqual(self.db_manager._soundex("Rupert"), "R163")
        self.assertEqual(self.db_manager._soundex("Dupont"), "D153")
        self.assertEqual(self.db_manager._soundex("Dupond"), "D153")
        
        # Test des cas spéciaux
        self.assertEqual(self.db_manager._soundex(""), "0000")
        self.assertEqual(self.db_manager._soundex("123"), "0000")
        self.assertEqual(self.db_manager._soundex("A"), "A000")

    def test_levenshtein(self):
        """Test de la méthode de distance de Levenshtein"""
        # Test des cas basiques
        self.assertEqual(self.db_manager._levenshtein_distance("chat", "chats"), 1)
        self.assertEqual(self.db_manager._levenshtein_distance("Dubois", "Duboi"), 1)
        self.assertEqual(self.db_manager._levenshtein_distance("Martin", "Marten"), 1)
        
        # Test des cas extrêmes
        self.assertEqual(self.db_manager._levenshtein_distance("", ""), 0)
        self.assertEqual(self.db_manager._levenshtein_distance("abc", ""), 3)
        self.assertEqual(self.db_manager._levenshtein_distance("", "abc"), 3)
        self.assertEqual(self.db_manager._levenshtein_distance("abc", "def"), 3)
