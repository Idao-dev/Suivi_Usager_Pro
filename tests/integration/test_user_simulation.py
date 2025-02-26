# pour le lancer pytest tests/test_user_simulation.py
import pytest
import customtkinter as ctk
from src.ui.main_window import MainWindow
from src.database.db_manager import DatabaseManager
from src.models.user import User
from src.models.workshop import Workshop
import os
import time

@pytest.fixture
def app():
    ctk.set_appearance_mode("light")
    return ctk.CTk()

@pytest.fixture
def main_window(app, tmp_path):
    db_path = tmp_path / "test_database.db"
    db_manager = DatabaseManager(str(db_path))
    db_manager.initialize()
    
    # Fonction de rappel factice pour mise à jour
    def update_callback():
        pass
    
    window = MainWindow(app, db_manager=db_manager, update_callback=update_callback)
    window.pack(fill="both", expand=True)
    return window

def test_user_workflow(main_window):
    # Simuler l'ajout d'un nouvel utilisateur
    main_window.show_add_user()
    
    # Vérifier que le frame AddUser est affiché
    assert isinstance(main_window.current_frame, main_window.add_user.__class__)
    
    # Remplir le formulaire d'ajout d'utilisateur
    add_user_frame = main_window.current_frame
    add_user_frame.nom_entry.insert(0, "Dupont")
    add_user_frame.prenom_entry.insert(0, "Jean")
    add_user_frame.telephone_entry.insert(0, "0123456789")
    
    # Valider l'ajout de l'utilisateur
    add_user_frame.add_user()
    
    # Attendre un peu pour que l'interface se mette à jour
    time.sleep(0.5)
    
    # Vérifier que l'utilisateur a été ajouté à la base de données
    results = main_window.db_manager.search_users("Dupont")
    assert len(results) > 0, "L'utilisateur 'Dupont' n'a pas été trouvé dans la base de données"
    user = results[0]  # Prendre le premier résultat
    
    # Afficher la liste des utilisateurs
    main_window.show_user_management()
    
    # Attendre un peu pour que l'interface se mette à jour
    time.sleep(0.5)
    
    # Imprimer le contenu de la liste des utilisateurs pour le débogage
    print("Contenu de la liste des utilisateurs:")
    for widget in main_window.user_management.users_frame.winfo_children():
        if isinstance(widget, ctk.CTkFrame):
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    print(child.cget("text"))
    
    # Vérifier la présence de l'utilisateur dans la liste
    user_found = False
    for widget in main_window.user_management.users_frame.winfo_children():
        if isinstance(widget, ctk.CTkFrame):
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "Dupont" in child.cget("text"):
                    user_found = True
                    break
    assert user_found, "L'utilisateur 'Dupont' n'a pas été trouvé dans la liste"
    
    # Simuler l'ouverture de l'édition de l'utilisateur
    results = main_window.db_manager.search_users("Dupont")
    assert len(results) > 0, "L'utilisateur 'Dupont' n'a pas été trouvé dans la base de données"
    user = results[0]  # Prendre le premier résultat
    main_window.edit_user(user)
    
    # Vérifier que le frame UserEditFrame est affiché
    assert isinstance(main_window.current_frame, main_window.user_edit.__class__)
    
    # Simuler l'ajout d'un atelier pour cet utilisateur
    user_edit_frame = main_window.current_frame
    user_edit_frame.open_add_workshop()
    
    # Vérifier que le frame AddWorkshop est affiché
    assert isinstance(main_window.current_frame, main_window.add_workshop.__class__)
    
    add_workshop_frame = main_window.current_frame
    add_workshop_frame.description_entry.insert(0, "Atelier test")
    add_workshop_frame.add_workshop()
    
    # Vérifier que l'atelier a été ajouté
    main_window.show_workshop_history()
    workshop_found = False
    for widget in main_window.workshop_history.history_frame.winfo_children():
        if isinstance(widget, ctk.CTkLabel) and "Atelier test" in widget.cget("text"):
            workshop_found = True
            break
    assert workshop_found, "L'atelier 'Atelier test' n'a pas été trouvé dans l'historique"
    
    # Vérifier les statistiques du tableau de bord
    main_window.show_dashboard()
    dashboard_frame = main_window.current_frame
    assert dashboard_frame.users_count_label.cget("text") == "1"
    assert dashboard_frame.workshops_count_label.cget("text") == "1"
    
    # Vérifier la fonctionnalité de recherche
    main_window.search_entry.insert(0, "Dupont")
    main_window.search_users()
    
    # Attendre un peu pour que l'interface se mette à jour
    time.sleep(0.5)
    
    search_result_found = False
    for widget in main_window.user_management.users_frame.winfo_children():
        if isinstance(widget, ctk.CTkFrame):
            for child in widget.winfo_children():
                if isinstance(child, ctk.CTkLabel) and "Dupont" in child.cget("text") and "Jean" in child.cget("text"):
                    search_result_found = True
                    break
    assert search_result_found, "Le résultat de recherche pour 'Dupont Jean' n'a pas été trouvé"
    
    # Vérifier la fonctionnalité d'exportation CSV
    main_window.show_data_management()
    data_management_frame = main_window.current_frame
    data_management_frame.export_csv()
    
    # Vérifier que le fichier CSV a été créé
    time.sleep(1)  # Attendre un peu pour s'assurer que le fichier a été créé
    assert os.path.exists("export_users.csv")
    
    # Vérifier la gestion RGPD
    data_management_frame.manage_rgpd()
    # Assurez-vous que la fenêtre RGPD s'ouvre (vous devrez adapter ceci en fonction de votre implémentation)
    assert hasattr(main_window, 'rgpd_window')
