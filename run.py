#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de lancement pour SuiviUsagerPro.
Ajoute automatiquement le répertoire racine au PYTHONPATH.
"""

import os
import sys

# Ajouter le répertoire racine au PYTHONPATH
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

if __name__ == "__main__":
    # Importer et exécuter la fonction main de src/main.py
    from src.main import main
    main() 