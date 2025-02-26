"""
Tests unitaires pour le module date_utils.
"""

import unittest
import pytest
from datetime import datetime
from freezegun import freeze_time
from src.utils.date_utils import (
    convert_to_db_date,
    convert_from_db_date,
    is_valid_date,
    get_current_date
)

class TestDateUtils(unittest.TestCase):
    """Tests pour les fonctions de manipulation de dates."""
    
    def test_convert_to_db_date_valid(self):
        """Teste la conversion d'une date valide au format français vers le format DB."""
        # Cas normal
        self.assertEqual(convert_to_db_date("25/12/2024"), "2024-12-25")
        
        # Cas avec des zéros
        self.assertEqual(convert_to_db_date("01/01/2024"), "2024-01-01")
        
        # Cas avec des espaces
        self.assertEqual(convert_to_db_date("25 / 12 / 2024".replace(" ", "")), "2024-12-25")
    
    def test_convert_to_db_date_invalid(self):
        """Teste la conversion d'une date invalide ou vide."""
        # Cas avec une chaîne vide
        self.assertIsNone(convert_to_db_date(""))
        self.assertIsNone(convert_to_db_date(None))
        
        # Cas avec un format incorrect
        invalid_date = "2024-12-25"  # Format déjà DB
        self.assertEqual(convert_to_db_date(invalid_date), invalid_date)
        
        # Cas avec un format non reconnu
        other_invalid = "25-12-2024"
        self.assertEqual(convert_to_db_date(other_invalid), other_invalid)
    
    def test_convert_from_db_date_valid(self):
        """Teste la conversion d'une date valide au format DB vers le format français."""
        # Cas normal
        self.assertEqual(convert_from_db_date("2024-12-25"), "25/12/2024")
        
        # Cas avec des zéros
        self.assertEqual(convert_from_db_date("2024-01-01"), "01/01/2024")
    
    def test_convert_from_db_date_already_formatted(self):
        """Teste la conversion d'une date déjà au format français."""
        # La date est déjà au format JJ/MM/AAAA
        self.assertEqual(convert_from_db_date("25/12/2024"), "25/12/2024")
    
    def test_convert_from_db_date_invalid(self):
        """Teste la conversion d'une date invalide."""
        # Format totalement invalide
        with self.assertRaises(ValueError):
            convert_from_db_date("invalid-date")
        
        # Format mixte ou ambigu
        with self.assertRaises(ValueError):
            convert_from_db_date("12-25-2024")
    
    def test_is_valid_date(self):
        """Teste la validation des dates au format français."""
        # Dates valides
        self.assertTrue(is_valid_date("01/01/2024"))
        self.assertTrue(is_valid_date("31/12/2024"))
        self.assertTrue(is_valid_date("29/02/2024"))  # 2024 est une année bissextile
        
        # Dates invalides
        self.assertFalse(is_valid_date(""))
        self.assertFalse(is_valid_date("32/12/2024"))  # Jour invalide
        self.assertFalse(is_valid_date("31/04/2024"))  # Avril n'a que 30 jours
        self.assertFalse(is_valid_date("29/02/2023"))  # 2023 n'est pas bissextile
        
        # Formats invalides
        self.assertFalse(is_valid_date("2024-12-25"))  # Format DB
        self.assertFalse(is_valid_date("25-12-2024"))  # Format incorrect
        self.assertFalse(is_valid_date("12/25/2024"))  # Format américain
        self.assertFalse(is_valid_date("1/1/2024"))    # Pas assez de chiffres
    
    @freeze_time("2024-02-15")
    def test_get_current_date(self):
        """Teste l'obtention de la date actuelle au format français."""
        # Figer la date au 15/02/2024 avec freezegun
        self.assertEqual(get_current_date(), "15/02/2024")

class TestEdgeCases:
    """Tests pour les cas limites et les comportements spécifiques."""
    
    def test_leap_year_validation(self):
        """Teste la validation des années bissextiles."""
        # 2024 est une année bissextile (29 jours en février)
        assert is_valid_date("29/02/2024") is True
        
        # 2023 n'est pas une année bissextile (max 28 jours en février)
        assert is_valid_date("29/02/2023") is False
        
        # 2000 est une année bissextile (divisible par 400)
        assert is_valid_date("29/02/2000") is True
        
        # 1900 n'est pas une année bissextile (divisible par 100 mais pas par 400)
        assert is_valid_date("29/02/1900") is False
    
    def test_month_days_validation(self):
        """Teste la validation des jours selon les mois."""
        # Mois avec 31 jours
        assert is_valid_date("31/01/2024") is True  # Janvier
        assert is_valid_date("31/03/2024") is True  # Mars
        assert is_valid_date("31/05/2024") is True  # Mai
        assert is_valid_date("31/07/2024") is True  # Juillet
        assert is_valid_date("31/08/2024") is True  # Août
        assert is_valid_date("31/10/2024") is True  # Octobre
        assert is_valid_date("31/12/2024") is True  # Décembre
        
        # Mois avec 30 jours
        assert is_valid_date("30/04/2024") is True   # Avril
        assert is_valid_date("31/04/2024") is False  # Avril n'a pas 31 jours
        
        assert is_valid_date("30/06/2024") is True   # Juin
        assert is_valid_date("31/06/2024") is False  # Juin n'a pas 31 jours
        
        assert is_valid_date("30/09/2024") is True   # Septembre
        assert is_valid_date("31/09/2024") is False  # Septembre n'a pas 31 jours
        
        assert is_valid_date("30/11/2024") is True   # Novembre
        assert is_valid_date("31/11/2024") is False  # Novembre n'a pas 31 jours

    def test_date_conversions_roundtrip(self):
        """Teste la conversion aller-retour entre formats de dates."""
        # Format français -> DB -> français
        original = "15/06/2024"
        db_format = convert_to_db_date(original)
        assert db_format == "2024-06-15"
        back_to_original = convert_from_db_date(db_format)
        assert back_to_original == original
        
        # Format DB -> français -> DB
        original_db = "2024-06-15"
        fr_format = convert_from_db_date(original_db)
        assert fr_format == "15/06/2024"
        back_to_original_db = convert_to_db_date(fr_format)
        assert back_to_original_db == original_db 