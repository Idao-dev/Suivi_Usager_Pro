-- Schéma de la base de données SQLite
-- Définit la structure des tables pour le suivi des usagers et des ateliers

-- Table des utilisateurs
-- Stocke les informations personnelles et le suivi des activités
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique auto-incrémenté
    nom TEXT NOT NULL,                     -- Nom de famille (obligatoire)
    prenom TEXT NOT NULL,                  -- Prénom (obligatoire)
    date_naissance TEXT,                   -- Date de naissance (format YYYY-MM-DD)
    telephone TEXT NOT NULL,               -- Numéro de téléphone (obligatoire)
    email TEXT,                            -- Adresse email (optionnel)
    adresse TEXT,                          -- Adresse postale (optionnel)
    date_creation TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),  -- Date de création du compte
    last_activity_date TEXT,               -- Date de dernière activité
    last_payment_date TEXT                 -- Date du dernier paiement
);

-- Table des ateliers
-- Enregistre les ateliers et leur association avec les utilisateurs
CREATE TABLE IF NOT EXISTS workshops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identifiant unique auto-incrémenté
    user_id INTEGER,                       -- Référence vers l'utilisateur (peut être NULL)
    description TEXT,                      -- Description de l'atelier
    categorie TEXT,                        -- Catégorie de l'atelier
    payant INTEGER,                        -- Indique si l'atelier est payant (0/1)
    paid INTEGER DEFAULT 0,                -- Indique si l'atelier a été payé (0/1)
    date TEXT,                             -- Date de l'atelier (format YYYY-MM-DD)
    conseiller TEXT,                       -- Nom du conseiller
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL  -- Lien vers la table users
);
