import random
from datetime import datetime, timedelta
from models.user import User
from models.workshop import Workshop

def generate_test_data(db_manager):
    # Générer des utilisateurs
    users = [
        User(nom="Dupont", prenom="Jean", date_naissance="01/01/1980", telephone="0123456789", email="jean@example.com", adresse="123 Rue de Paris", date_creation="01/01/2023", last_activity_date="01/01/2023"),
        User(nom="Martin", prenom="Marie", date_naissance="15/05/1990", telephone="0987654321", email="marie@example.com", adresse="456 Avenue des Champs", date_creation="02/01/2024", last_activity_date="02/01/2024"),
        User(nom="SansAtelier", prenom="Pierre", date_naissance="30/06/1985", telephone="0567891234", email="pierre@example.com", adresse="789 Boulevard du Soleil", date_creation="03/08/2024", last_activity_date="03/08/2024"),
        User(nom="Bernard", prenom="Paul", telephone="0654321987", last_activity_date=datetime.now().strftime("%d/%m/%Y")),
    ]
    
    for user in users:
        user.save(db_manager)
    
    # Générer des ateliers
    categories = ["Informatique", "Administratif", "Emploi", "Santé"]
    descriptions = ["Initiation", "Perfectionnement", "Assistance", "Formation"]
    
    for _ in range(20):  # Créer 20 ateliers
        user = random.choice(users)
        Workshop(
            user_id=user.id,
            description=f"{random.choice(descriptions)} en {random.choice(categories)}",
            categorie=random.choice(categories),
            payant=random.choice([True, False]),
            date=(datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%d/%m/%Y"),
            conseiller=random.choice(["Conseiller1", "Conseiller2", "Conseiller3"])
        ).save(db_manager)
    
    # Créer quelques utilisateurs sans ateliers
    for _ in range(3):
        User(nom=f"SansAtelier{_}", prenom="Test").save(db_manager)
    
    # Créer quelques ateliers associés à un utilisateur existant (par exemple, le premier)
    user_id_for_orphan_workshops = users[0].id
    for _ in range(3):
        Workshop(
            user_id=user_id_for_orphan_workshops,
            description="Atelier sans utilisateur spécifique",
            categorie=random.choice(categories),
            payant=False,
            date=datetime.now().strftime("%d/%m/%Y"),
            conseiller="ConseillerTest"
        ).save(db_manager)

    return users
