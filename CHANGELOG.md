# Journal des modifications

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Ajouté
  - Ajout de tests unitaires complémentaires pour améliorer la couverture du code :
    - Tests unitaires pour le pattern Observer (test_observer.py) - 5/5 tests réussis
    - Tests unitaires pour le gestionnaire de thèmes (test_theme.py) - 3/3 tests réussis
    - Tests unitaires pour le module principal (test_main.py) - 8/8 tests réussis
    - Tests unitaires pour le tableau de bord (test_dashboard.py) - 9/9 tests réussis
    - Tests unitaires pour la gestion des utilisateurs (test_user_management.py) - 15/15 tests réussis
    - Tests unitaires partiels pour le module d'importation/exportation CSV (test_csv_export.py)
  - Création d'un script run_unit_tests.py pour exécuter de manière sélective les tests unitaires
  - Mise à jour du rapport de tests (RAPPORT_TESTS.md) avec l'état actuel et les problèmes identifiés
  - Amélioration significative de la couverture de tests de 38% à 52%

### Problèmes identifiés
  - Difficultés avec le mocking de datetime.now() dans les tests unitaires CSV
  - Problèmes avec l'implémentation des tests d'interface utilisateur

## [1.0.2] - 2025-01-13

### Ajouté
  - Implémentation d'une recherche intelligente multi-étapes :
    - Recherche exacte pour les correspondances précises
    - Recherche phonétique avec Soundex pour les noms similaires
    - Recherche approximative avec Levenshtein pour les fautes de frappe
    - Recherche partielle pour les résultats complémentaires
  - Tests unitaires complets pour la recherche avancée
  - Tests unitaires complets pour la gestion RGPD :
    - Test de détection des utilisateurs inactifs
    - Test de suppression sécurisée des données
    - Test d'export sélectif des données
    - Test de configuration de la période d'inactivité
  - Configuration optimisée pour la création de l'exécutable :
    - Gestion améliorée des chemins de ressources
    - Structure de dossiers adaptée pour PyInstaller
    - Support des assets dans l'exécutable final

### Modifié
  - Restructuration majeure du projet
  - Séparation du code source dans src/
  - Centralisation de la documentation dans docs/
  - Réorganisation des tests dans src/tests/
    - Documentation complète du code source :
    - Ajout de docstrings en français pour tous les fichiers Python
    - Documentation détaillée des classes et méthodes
    - Commentaires explicatifs dans le schéma de la base de données
  - Amélioration de l'interface utilisateur :
    - Correction du fond du graphique dans le tableau de bord en mode sombre/clair
    - Refonte des tableaux d'historique des ateliers
    - Harmonisation du style entre les différents tableaux de l'application
  - Optimisation de la recherche d'utilisateurs :
    - Limitation à 4 résultats maximum pour une meilleure lisibilité
    - Priorisation des résultats selon leur pertinence
    - Amélioration des performances avec mise en cache des résultats
  - Amélioration de la gestion RGPD :
    - Optimisation de la détection des utilisateurs inactifs
    - Export sélectif des données avant suppression
    - Uniformisation du format des dates dans les requêtes SQL
  - Optimisation de la gestion des ressources :
    - Nouveau système de gestion des chemins
    - Support amélioré des assets dans l'exécutable
    - Correction des chemins pour les images et fichiers SQL

### Corrigé
  - Correction des résultats de recherche pour éviter les doublons
  - Amélioration de la précision des recherches phonétiques
  - Optimisation des performances pour les grandes bases de données
  - Correction des bugs dans la gestion RGPD :
    - Correction de la détection des utilisateurs inactifs
    - Correction de l'export des données spécifiques
    - Correction du format des dates dans les requêtes SQL
  - Résolution des problèmes de chemins dans l'exécutable
  - Correction de l'accès aux ressources en mode développement et production
  - Amélioration de la gestion des assets dans l'application packagée

## [1.0.1] - 2024-11-20

### Ajouté
- Thème sombre/clair personnalisable
- Système de pagination pour les listes d'ateliers
- Nouvelles statistiques dans le tableau de bord

### Modifié
- Amélioration des performances de la recherche
- Interface utilisateur plus intuitive
- Optimisation du chargement des données

### Corrigé
- Correction du calcul des statuts de paiement
- Résolution des problèmes d'affichage sur certaines résolutions
- Correction des erreurs de sauvegarde des paramètres

## [1.0.0] - 2024-11-19

### Ajouté
- Interface graphique complète avec CustomTkinter
- Gestion des usagers (création, modification, suppression)
- Gestion des ateliers avec suivi des paiements
- Tableau de bord avec statistiques
- Export/Import des données en CSV
- Système de configuration des conseillers
- Gestion des données conforme RGPD
- Documentation utilisateur et technique

### Fonctionnalités principales
- Système de suivi des usagers
- Gestion des ateliers et paiements
- Interface moderne et intuitive
- Base de données SQLite
- Sauvegarde automatique
- Protection des données RGPD

[1.0.1]: https://github.com/username/SuiviUsagerPro/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/username/SuiviUsagerPro/releases/tag/v1.0.0 