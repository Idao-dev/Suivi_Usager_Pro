# Structure du Projet SuiviUsagerPro

```
SuiviUsagerPro/
│
├── src/                              # Code source principal
│   ├── __init__.py
│   ├── main.py                       # Point d'entrée de l'application
│   ├── config.py                     # Configuration globale
│   │
│   ├── database/                     # Gestion de la base de données
│   │   ├── __init__.py
│   │   ├── db_manager.py            # Gestionnaire de base de données
│   │   └── schema.sql               # Structure de la base de données
│   │
│   ├── models/                       # Modèles de données
│   │   ├── __init__.py
│   │   ├── user.py                  # Modèle Utilisateur
│   │   └── workshop.py              # Modèle Atelier
│   │
│   ├── ui/                          # Interface utilisateur
│   │   ├── __init__.py
│   │   ├── main_window.py          # Fenêtre principale
│   │   ├── dashboard.py            # Tableau de bord
│   │   ├── add_user.py            # Ajout d'utilisateur
│   │   ├── add_workshop.py        # Ajout d'atelier
│   │   ├── user_management.py     # Gestion des utilisateurs
│   │   ├── user_edit.py          # Édition d'utilisateur
│   │   ├── edit_workshop.py      # Édition d'atelier
│   │   ├── workshop_history.py   # Historique des ateliers
│   │   ├── settings.py          # Paramètres
│   │   └── data_management.py   # Gestion des données
│   │
│   └── utils/                    # Utilitaires
│       ├── __init__.py
│       ├── config_utils.py      # Utilitaires de configuration
│       ├── csv_import_export.py # Import/Export CSV
│       ├── date_utils.py       # Manipulation des dates
│       ├── observer.py        # Pattern Observer
│       ├── rgpd_manager.py   # Gestion RGPD
│       └── theme.py         # Gestion des thèmes
│
├── tests/                     # Tests
│   ├── __init__.py
│   ├── test_base.py         # Classe de base pour les tests
│   ├── test_setup.py       # Configuration des tests
│   │
│   ├── conftest.py/        # Configuration pytest
│   │
│   ├── fixtures/           # Données de test
│   │   └── __init__.py
│   │
│   ├── unit/              # Tests unitaires
│   │   ├── __init__.py
│   │   ├── test_config.py           # Tests de configuration
│   │   ├── test_settings.py         # Tests des paramètres
│   │   ├── test_utils.py            # Tests des utilitaires
│   │   ├── test_models.py           # Tests des modèles
│   │   ├── test_database.py         # Tests de la base de données
│   │   ├── test_rgpd_manager.py     # Tests du gestionnaire RGPD
│   │   └── test_data_generator.py   # Tests du générateur de données
│   │
│   └── integration/                 # Tests d'intégration
│       ├── __init__.py
│       ├── test_integration.py      # Tests d'intégration généraux
│       ├── test_navigation.py       # Tests de navigation
│       ├── test_ui.py              # Tests d'interface
│       ├── test_performance.py      # Tests de performance
│       ├── test_user_simulation.py  # Tests de simulation utilisateur
│       ├── test_workshop_history.py # Tests historique ateliers
│       ├── test_csv_import.py      # Tests import/export CSV
│       ├── test_data_management.py # Tests gestion données
│       └── test_payment_status.py  # Tests statut paiement
│
├── data/                    # Données de l'application
│   ├── exports/            # Exports CSV, etc.
│   └── suivi_usager.db    # Base de données SQLite
│
├── docs/                   # Documentation
│   ├── specifications/    # Spécifications techniques
│   │   └── Structure.md  # Ce fichier
│   ├── DEVBOOK.md       # Documentation développeur
│   └── CDC.md          # Cahier des charges
│
├── setup.py              # Configuration du package
├── requirements.txt      # Dépendances Python
├── .gitignore           # Fichiers ignorés par Git
├── README.md            # Documentation principale
└── CHANGELOG.md         # Journal des modifications
```

## Description des composants principaux

### Source (`src/`)
- **main.py** : Point d'entrée, initialise l'application
- **database/** : Gestion de la base de données SQLite
- **models/** : Classes de modèles de données
- **ui/** : Composants d'interface utilisateur
- **utils/** : Fonctions et classes utilitaires

### Tests (`tests/`)
- **unit/** : Tests unitaires isolés
- **integration/** : Tests d'intégration système
- **fixtures/** : Données de test réutilisables
- **conftest.py/** : Configuration pytest

### Documentation (`docs/`)
- **specifications/** : Documentation technique
- **DEVBOOK.md** : Guide du développeur
- **CDC.md** : Cahier des charges

### Données (`data/`)
- **exports/** : Fichiers d'export
- **suivi_usager.db** : Base de données principale

### Configuration
- **setup.py** : Configuration du package Python
- **requirements.txt** : Dépendances du projet