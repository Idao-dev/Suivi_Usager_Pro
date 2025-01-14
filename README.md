# SuiviUsagerPro

Application de gestion des usagers et des ateliers pour les professionnels de l'accompagnement social.

## 📋 Description

SuiviUsagerPro est une application desktop développée en Python avec CustomTkinter qui permet de :
- Gérer les dossiers des usagers
- Planifier et suivre les ateliers
- Générer des rapports et statistiques
- Exporter/Importer des données
- Assurer la conformité RGPD

## 🚀 Installation

### Prérequis
- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (pour le clonage du dépôt)

### Installation pour le développement

1. Cloner le dépôt
```bash
git clone [URL_DU_DEPOT]
cd SuiviUsagerPro
```

2. Créer un environnement virtuel
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
pip install -e .
```

### Installation pour l'utilisation

1. Télécharger la dernière version depuis la page des releases
2. Exécuter l'installateur (.exe pour Windows)
3. Suivre les instructions d'installation

## 🏃 Démarrage rapide

### Lancement en mode développement
```bash
# Depuis la racine du projet
python src/main.py
# OU avec le package installé
suiviusagerpro
```

### Premier démarrage
1. Configurer les paramètres initiaux dans l'interface
2. Créer un premier conseiller
3. Commencer à ajouter des usagers

## 🛠️ Développement

### Structure du projet
```
SuiviUsagerPro/
├── src/                  # Code source
├── tests/               # Tests
├── data/               # Données
├── docs/              # Documentation
└── [autres fichiers de config]
```

### Commandes utiles

#### Tests
```bash
# Lancer tous les tests
pytest

# Lancer les tests unitaires uniquement
pytest tests/unit

# Lancer les tests d'intégration
pytest tests/integration
```

#### Build
```bash
# Créer un exécutable
pyinstaller src/main.py

# Construire le package
python setup.py build

# Créer une distribution
python setup.py sdist bdist_wheel
```

#### Nettoyage
```bash
# Nettoyer les fichiers de build
Remove-Item -Recurse -Force build/, dist/, .pytest_cache/
```

### Installation de l'environnement de développement
1. Cloner le dépôt
2. Créer un environnement virtuel : `python -m venv .venv`
3. Activer l'environnement virtuel : `.venv/Scripts/activate`
4. Installer les dépendances : `pip install -r requirements.txt`

### Tests
- Exécuter les tests : `pytest tests/`
- Vérifier la couverture : `pytest --cov=src tests/`

### Création de l'exécutable
Voir les instructions détaillées dans `docs/DEVBOOK.md` section 2.5.

Points importants :
- Utilisation d'un fichier spec personnalisé
- Structure des ressources optimisée
- Taille de l'exécutable : ~66 MB
- Création automatique des dossiers et fichiers nécessaires au premier lancement

## 📊 Base de données

- SQLite3 utilisé comme SGBD
- Base stockée dans `data/suivi_usager.db`
- Schéma disponible dans `src/database/schema.sql`

## 🔒 Sécurité et RGPD

- Données stockées localement uniquement
- Export des données possible au format CSV
- Fonction de suppression conforme RGPD
- Pas de données sensibles en clair

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Guidelines de contribution
- Suivre les conventions de code Python (PEP 8)
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation
- Vérifier que tous les tests passent

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des versions.

## 📄 Licence

Ce projet est sous licence [À DÉFINIR] - voir le fichier LICENSE pour plus de détails.

## 👥 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Rejoindre le serveur Discord : [Lien Discord]
- Contacter l'équipe de développement

## ✨ Remerciements

- Équipe de développement
- Contributeurs
- Utilisateurs pour leurs retours

---
Développé avec ❤️ pour améliorer le suivi des usagers
