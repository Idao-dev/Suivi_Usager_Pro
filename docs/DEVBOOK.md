# DEVBOOK – SuiviUsagerPro

## PARTIE 1 : DESCRIPTION ET NOTES TECHNIQUES

### 1. Objectifs du Projet
- Application de bureau pour la gestion des usagers et des ateliers
- Suivi des paiements et des activités
- Interface utilisateur moderne et intuitive
- Gestion des données conforme RGPD

### 2. Stack Technique
- **Langage** : Python 3.x
- **Interface graphique** : CustomTkinter (basé sur Tkinter)
- **Base de données** : SQLite3
- **Gestion de version** : Git
- **Tests** : unittest
- **Dépendances principales** :
  - customtkinter
  - sqlite3
  - faker (pour les données de test)
  - logging

### 3. Architecture Technique

#### 3.1 Structure du Projet
L'application est organisée en plusieurs composants principaux :

- **src/** : Code source principal
  - **database/** : Gestion de la base de données SQLite
  - **models/** : Modèles de données métier
  - **ui/** : Interfaces utilisateur CustomTkinter
  - **utils/** : Utilitaires et helpers

- **tests/** : Tests automatisés
  - Tests unitaires
  - Tests d'intégration
  - Fixtures et utilitaires de test

- **docs/** : Documentation technique et utilisateur

Les fichiers de configuration et de dépendances sont à la racine du projet.

#### 3.2 Base de Données
```sql
-- Tables principales
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    date_naissance TEXT,
    telephone TEXT NOT NULL,
    email TEXT,
    adresse TEXT,
    date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    last_activity_date TEXT,
    last_payment_date TEXT
);

CREATE TABLE workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    description TEXT,
    categorie TEXT,
    payant INTEGER,
    paid INTEGER DEFAULT 0,
    date TEXT,
    conseiller TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

#### 3.3 Patterns de Conception
- **Observer Pattern** : Pour la mise à jour des vues
- **MVC** : Séparation des modèles, vues et contrôleurs
- **Singleton** : Pour la gestion de la base de données
- **Factory** : Pour la création des objets métier

### 4. Standards et Conventions

#### 4.1 Style de Code
- PEP 8 pour le formatage Python
- Docstrings pour la documentation des classes et méthodes
- Nommage en français pour les variables métier
- Logging systématique des opérations importantes

#### 4.2 Gestion des Configurations
- Fichier `config.json` pour les paramètres utilisateur
- Variables d'environnement pour la configuration système
- Thèmes (clair/sombre) personnalisables

#### 4.3 Sécurité
- Validation des entrées utilisateur
- Échappement des requêtes SQL
- Gestion des erreurs avec logging
- Sauvegarde automatique des données

### 5. Gestion des Versions
- Version actuelle : 1.0.2
- Format : MAJOR.MINOR.PATCH
- Branches Git :
  - main : production
  - develop : développement
  - feature/* : nouvelles fonctionnalités

### 6. Interface Utilisateur
- Thème personnalisé (clair/sombre)
- Composants CustomTkinter
- Responsive design
- Validation en temps réel

## PARTIE 2 : PROCESSUS DE DÉVELOPPEMENT

### 2.1 Analyse
- Revue de code avant merge
- Tests unitaires obligatoires
- Documentation à jour
- Validation RGPD

### 2.2 Implémentation
- Développement par fonctionnalité
- Tests en parallèle
- Revue de code systématique
- Documentation continue

### 2.3 Tests & Validation

#### 2.3.1 État des Tests
| Catégorie            | Progression | Dernière MAJ | Statut          |
|----------------------|-------------|--------------|-----------------|
| Tests Unitaires      | 90%         | 2025-01-13   | 🟢 Complété     |
| Tests d'Intégration  | 0%          | YYYY-MM-DD   | 🔴 Non commencé |
| Tests UI             | 65%         | 2024-01-07   | 🟡 En cours     |
| Tests de Performance | 0%          | YYYY-MM-DD   | 🔴 Non commencé |

#### 2.3.2 Détails par Module
| Module   | Tests Unitaires | Tests d'Intégration | Commentaires                                            |
|----------|-----------------|---------------------|---------------------------------------------------------|
| Database | 🟢 Complété     | 🔴 Non commencé     | 8 tests passés avec succès                              |
| Models   | 🟢 Complété     | 🔴 Non commencé     | 10 tests passés avec succès                             |
| UI       | 🟢 Complété     | 🔴 Non commencé     | Tests de navigation, affichage, gestion des usagers et ateliers complétés |
| Utils    | 🟢 Complété     | 🔴 Non commencé     | Tests RGPD, validation des dates et configurations complétés |

#### 2.3.3 Objectifs de Couverture
- Tests Unitaires : 80% minimum
- Tests d'Intégration : 60% minimum
- Tests UI : Tous les parcours critiques
  - ✅ Navigation principale
  - ✅ Affichage des données
  - ✅ Comportement responsive
  - ✅ Mise à jour des composants
  - ✅ Gestion des usagers (liste, ajout, édition, suppression)
  - ✅ Recherche d'usagers (centralisée dans MainWindow)
  - ✅ Gestion des ateliers
    - ✅ Ajout d'atelier avec validation des champs
    - ✅ Gestion des callbacks et transitions
    - ✅ Mise à jour des statuts de paiement
  - ❌ Paramètres
- Tests de Performance : Temps de réponse < 500ms

#### 2.3.4 Validation des Tests
- ✅ Exécution automatique via CI/CD
- ✅ Rapport de couverture généré
- ✅ Tests de non-régression UI
- ✅ Tests de la gestion des usagers
- ✅ Tests de gestion des ateliers
  - ✅ Test des transitions d'interface
  - ✅ Test des callbacks
  - ✅ Test de la destruction des widgets
- ❌ Tests de charge

#### 2.3.5 Prochaines Étapes
1. ✅ Tests unitaires de la base de données
2. ✅ Tests des modèles
3. 🟡 Tests de l'interface utilisateur
   - ✅ Tests de navigation
   - ✅ Tests d'affichage
   - ✅ Tests de comportement responsive
   - ✅ Tests de gestion des usagers
   - ✅ Tests de recherche (MainWindow)
   - ✅ Tests des ateliers
     - ✅ Validation des champs
     - ✅ Gestion des transitions
     - ✅ Exécution des callbacks
   - Implémenter les tests des paramètres
4. Mettre en place les tests d'intégration

### 2.4 Refactoring
- Optimisation des requêtes SQL
- Nettoyage du code
- Amélioration des performances
- Mise à jour de la documentation
- ✅ Correction de la gestion des interfaces
  - ✅ Gestion sécurisée des callbacks
  - ✅ Destruction propre des widgets
  - ✅ Transitions fluides entre interfaces

### 2.5 Création de l'exécutable

#### Prérequis
1. Environnement virtuel activé (`.venv`)
2. Dépendances installées (`requirements.txt`)
3. PyInstaller installé dans l'environnement virtuel

#### Étapes de création
1. Activer l'environnement virtuel :
   ```bash
   .venv/Scripts/activate
   ```

2. Vérifier/installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Installer PyInstaller si nécessaire :
   ```bash
   pip install pyinstaller
   ```

4. Créer l'exécutable avec le fichier spec :
   ```bash
   pyinstaller SuiviUsagerPro.spec --clean
   ```

5. L'exécutable sera créé dans le dossier `dist/`

#### Notes importantes
- Taille approximative : 66 MB
- Exécutable autonome (--onefile)
- Toutes les dépendances incluses
- Structure des ressources :
  - `assets/` : Images et icônes
  - `database/` : Fichiers SQL et schémas
- Création automatique de la base de données et des fichiers de configuration au premier lancement

## PARTIE 3 : SUIVI DU PROJET

### 1. État Actuel
- Version : 1.0.2
- Dernière mise à jour : 2025-01-13
- Fonctionnalités principales implémentées
- Tests en place et validés
- Gestion RGPD complète et testée
- Exécutable fonctionnel avec ressources intégrées

### 2. Métriques
- Couverture de tests : 90%
- Nombre de bugs connus : 0
- Performance : Optimisée pour les requêtes RGPD et la gestion des ressources
- Qualité du code : Tests unitaires complets
- Taille de l'exécutable : 66 MB (optimisé)

### 3. Points d'Attention
- Gestion de la mémoire pour les grandes listes
- Performance des requêtes complexes
- Validation des données utilisateur
- Conformité RGPD :
  - Vérification régulière des périodes d'inactivité
  - Export des données avant suppression
  - Anonymisation des ateliers orphelins
- Gestion des ressources :
  - Chemins d'accès en mode développement et production
  - Intégration des assets dans l'exécutable
  - Accès aux fichiers SQL et configurations

### 4. Journal des Modifications
#### Version 1.0.1
- Interface utilisateur améliorée
- Correction de bugs mineurs
- Optimisation des performances
- Mise à jour de la documentation

## ANNEXES

### A. Commandes Utiles
```bash
# Installation des dépendances
pip install -r requirements.txt

# Lancement des tests
python -m unittest discover tests

# Génération des données de test
python generate_test_data.py

# Construction de l'exécutable
pyinstaller main.py
```

### B. Ressources
- Documentation CustomTkinter
- Documentation SQLite
- Guide style PEP 8
- Réglementation RGPD

### C. Contacts
- Support technique : [À définir]
- Équipe de développement : [À définir]
- Communauté : Discord (https://discord.gg/FD4DdWEQ) 