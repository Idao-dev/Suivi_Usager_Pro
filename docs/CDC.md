# Cahier des Charges - SuiviUsagerPro

## 1. Présentation du Projet

### 1.1 Contexte
SuiviUsagerPro est une application de bureau destinée à la gestion et au suivi des usagers dans un contexte professionnel. Elle permet de gérer efficacement les ateliers, les paiements et le suivi des participants.

### 1.2 Objectifs
- Simplifier la gestion quotidienne des usagers et des ateliers
- Assurer un suivi précis des paiements et des participations
- Fournir des statistiques et des indicateurs de performance
- Faciliter l'exportation et l'importation des données

## 2. Description Fonctionnelle

### 2.1 Fonctionnalités Principales

#### Gestion des Usagers
- Création et modification des fiches usagers avec :
  - Informations personnelles (nom, prénom, date de naissance)
  - Coordonnées (téléphone, email, adresse)
  - Date de création automatique
  - Suivi des dernières activités
  - Historique des paiements
- Système de statut de paiement automatique :
  - Calcul du statut "À jour" ou "En retard"
  - Basé sur le nombre d'ateliers entre paiements
  - Prise en compte des ateliers payants uniquement
- Gestion des usagers inactifs :
  - Détection automatique basée sur la période d'inactivité
  - Possibilité de suppression des usagers inactifs
  - Conservation de l'historique des ateliers

#### Gestion des Ateliers
- Création et modification d'ateliers avec :
  - Description détaillée
  - Catégorisation (individuel, administratif)
  - Statut de paiement (payant/non-payant)
  - État du paiement (payé/non-payé)
  - Date de l'atelier
  - Attribution d'un conseiller
- Fonctionnalités avancées :
  - Pagination des listes d'ateliers
  - Filtrage par usager
  - Historique complet
  - Gestion des ateliers orphelins (sans usager)
- Système de paiement :
  - Types d'ateliers payants configurables
  - Suivi des paiements par cycle
  - Mise à jour automatique des statuts

#### Tableau de Bord
- Vue d'ensemble des activités
- Statistiques en temps réel :
  - Nombre total d'usagers
  - Nombre d'ateliers
  - Usagers actifs
  - Ateliers du mois
- Graphiques de suivi :
  - Répartition par type d'atelier
  - Évolution mensuelle
  - Taux de participation
  - Statuts des paiements

#### Gestion des Données
- Exportation des données :
  - Format CSV standardisé
  - Sélection des données à exporter
  - Horodatage des exports
- Importation de données :
  - Validation des formats
  - Gestion des erreurs
  - Fusion des données
- Protection des données :
  - Sauvegarde automatique
  - Gestion des doublons
  - Validation des données

### 2.2 Interfaces Utilisateur

#### Interface Principale
- Barre latérale de navigation avec :
  - Tableau de bord
  - Gestion des usagers
  - Ajout d'usager
  - Gestion des ateliers
  - Historique
  - Paramètres
- Barre supérieure avec :
  - Recherche globale
  - Sélection du conseiller actif
  - Accès rapide aux fonctions
- Zone de contenu principal :
  - Affichage adaptatif
  - Navigation intuitive
  - Mise en page responsive

#### Formulaires
- Saisie intuitive des informations
- Validation en temps réel :
  - Formats de dates
  - Numéros de téléphone
  - Adresses email
  - Champs obligatoires
- Messages d'erreur explicites
- Suggestions automatiques

## 3. Spécifications Techniques

### 3.1 Architecture
- Application de bureau autonome
- Base de données SQLite :
  - Tables principales : users, workshops
  - Relations optimisées
  - Indexation performante
- Interface graphique CustomTkinter
- Structure modulaire :
  - Modèles (User, Workshop)
  - Vues (Dashboard, Forms)
  - Utilitaires

### 3.2 Sécurité
- Protection des données personnelles :
  - Stockage local sécurisé
  - Pas de données sensibles en clair
- Gestion sécurisée des paiements :
  - Traçabilité complète
  - Historique des modifications
- Sauvegarde automatique :
  - Base de données locale
  - Exports réguliers
- Conformité RGPD :
  - Droit à l'oubli
  - Exportation des données
  - Suppression sécurisée

### 3.3 Performance
- Temps de réponse rapide :
  - Requêtes optimisées
  - Cache intelligent
- Gestion efficace de la mémoire :
  - Chargement pagination
  - Nettoyage automatique
- Interface fluide :
  - Actualisation asynchrone
  - Transitions douces

## 4. Contraintes et Exigences

### 4.1 Techniques
- Compatibilité Windows 10 et versions ultérieures
- Espace disque minimal requis : 100 Mo
- Mémoire RAM recommandée : 4 Go
- Résolution d'écran minimale : 1024x768

### 4.2 Fonctionnelles
- Interface en français
- Temps de démarrage < 5 secondes
- Sauvegarde automatique des données
- Export des données au format standard

### 4.3 Légales
- Conformité RGPD
- Protection des données personnelles
- Conditions d'utilisation claires
- Politique de confidentialité

## 5. Maintenance et Évolution

### 5.1 Maintenance
- Mises à jour régulières
- Corrections de bugs
- Optimisations de performance
- Sauvegardes automatiques

### 5.2 Évolutions Futures
- Nouvelles fonctionnalités planifiées
- Améliorations de l'interface
- Intégrations supplémentaires
- Retours utilisateurs

## 6. Support et Documentation

### 6.1 Support Utilisateur
- Guide d'utilisation intégré
- Support technique par email
- Communauté Discord
- Documentation en ligne

### 6.2 Formation
- Tutoriels intégrés
- Guide de prise en main
- Bonnes pratiques
- Mises à jour documentées

## 7. Annexes

### 7.1 Glossaire
- **Usager** : Personne suivie dans le système
- **Atelier** : Session de travail avec un usager
- **Conseiller** : Professionnel accompagnant les usagers
- **Dashboard** : Tableau de bord avec les indicateurs clés
- **Cycle de paiement** : Nombre d'ateliers entre deux paiements
- **Atelier orphelin** : Atelier sans usager associé
- **Statut de paiement** : État des paiements (À jour/En retard)

### 7.2 Contacts
- Support technique : [À définir]
- Communauté : Discord (https://discord.gg/FD4DdWEQ)
- Développement : [À définir] 



