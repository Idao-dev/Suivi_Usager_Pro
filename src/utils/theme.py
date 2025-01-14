"""
Module de gestion des thèmes de l'application.
Définit les couleurs et styles pour les modes sombre et clair.
Utilise customtkinter pour une interface moderne et cohérente.

Les couleurs sont définies en paires [mode_clair, mode_sombre] pour chaque composant.
"""

import customtkinter as ctk

def set_dark_theme():
    """
    Configure le thème sombre de l'application.
    
    Définit les couleurs pour tous les composants de l'interface en mode sombre :
    - Fond principal : Gris foncé (#2B2B2B)
    - Texte : Blanc (#FFFFFF)
    - Boutons : Bleu foncé (#1F6AA5) avec effet hover plus sombre
    - Entrées : Gris moyen (#4A4A4A) avec texte blanc
    - Menus : Bleu foncé assorti aux boutons
    """
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Définir les couleurs personnalisées
    ctk.ThemeManager.theme["CTk"]["fg_color"] = ["#2B2B2B", "#2B2B2B"]  # Fond principal
    ctk.ThemeManager.theme["CTk"]["text"] = ["#FFFFFF", "#FFFFFF"]      # Texte général
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = ["#383838", "#383838"]  # Fond des cadres
    
    # Configuration des boutons
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = ["#1F6AA5", "#1F6AA5"]  # Bleu principal
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = ["#144870", "#144870"]  # Effet hover
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"] = ["#7F7F7F", "#7F7F7F"]
    ctk.ThemeManager.theme["CTkButton"]["fg_color_disabled"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color_disabled"] = ["#404040", "#404040"]
    
    # Configuration des labels et entrées
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkEntry"]["placeholder_text_color"] = ["#AAAAAA", "#AAAAAA"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color_disabled"] = ["#7F7F7F", "#7F7F7F"]
    ctk.ThemeManager.theme["CTkEntry"]["fg_color_disabled"] = ["#404040", "#404040"]
    ctk.ThemeManager.theme["CTkEntry"]["border_color_disabled"] = ["#4A4A4A", "#4A4A4A"]
    
    # Configuration des menus et switches
    ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color"] = ["#1F6AA5", "#1F6AA5"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"] = ["#144870", "#144870"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color"] = ["#0D2F4B", "#0D2F4B"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["text_color_disabled"] = ["#7F7F7F", "#7F7F7F"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color_disabled"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_color_disabled"] = ["#404040", "#404040"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color_disabled"] = ["#383838", "#383838"]
    
    ctk.ThemeManager.theme["CTkSwitch"]["progress_color"] = ["#1F6AA5", "#1F6AA5"]
    ctk.ThemeManager.theme["CTkSwitch"]["button_hover_color"] = ["#144870", "#144870"]

    # Configuration des cases à cocher
    ctk.ThemeManager.theme["CTkCheckBox"]["text_color_disabled"] = ["#7F7F7F", "#7F7F7F"]
    ctk.ThemeManager.theme["CTkCheckBox"]["fg_color_disabled"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkCheckBox"]["hover_color_disabled"] = ["#404040", "#404040"]
    ctk.ThemeManager.theme["CTkCheckBox"]["checkmark_color_disabled"] = ["#7F7F7F", "#7F7F7F"]

    # Configuration des zones de texte
    ctk.ThemeManager.theme["CTkTextbox"]["text_color_disabled"] = ["#7F7F7F", "#7F7F7F"]
    ctk.ThemeManager.theme["CTkTextbox"]["fg_color_disabled"] = ["#404040", "#404040"]
    ctk.ThemeManager.theme["CTkTextbox"]["border_color_disabled"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkTextbox"]["scrollbar_button_color"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkTextbox"]["scrollbar_button_hover_color"] = ["#404040", "#404040"]

    # Configuration des cadres défilables
    ctk.ThemeManager.theme["CTkScrollableFrame"]["label_text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkScrollableFrame"]["scrollbar_button_color"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkScrollableFrame"]["scrollbar_button_hover_color"] = ["#404040", "#404040"]

def set_light_theme():
    """
    Configure le thème clair de l'application.
    
    Définit les couleurs pour tous les composants de l'interface en mode clair :
    - Fond principal : Gris très clair (#F0F0F0)
    - Texte : Noir (#000000)
    - Boutons : Bleu moyen (#3A7EBF) avec effet hover plus foncé
    - Entrées : Blanc (#FFFFFF) avec texte noir
    - Menus : Bleu assorti aux boutons
    """
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Définir les couleurs personnalisées pour le thème clair
    ctk.ThemeManager.theme["CTk"]["fg_color"] = ["#F0F0F0", "#F0F0F0"]  # Fond principal
    ctk.ThemeManager.theme["CTk"]["text"] = ["#000000", "#000000"]      # Texte général
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = ["#E0E0E0", "#E0E0E0"]  # Fond des cadres
    
    # Configuration des boutons
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = ["#3A7EBF", "#3A7EBF"]  # Bleu principal
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = ["#2A5F8F", "#2A5F8F"]  # Effet hover
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"] = ["#A0A0A0", "#A0A0A0"]
    ctk.ThemeManager.theme["CTkButton"]["fg_color_disabled"] = ["#D0D0D0", "#D0D0D0"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color_disabled"] = ["#C0C0C0", "#C0C0C0"]
    
    # Configuration des labels et entrées
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = ["#000000", "#000000"]
    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = ["#000000", "#000000"]
    ctk.ThemeManager.theme["CTkEntry"]["placeholder_text_color"] = ["#7F7F7F", "#7F7F7F"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color_disabled"] = ["#A0A0A0", "#A0A0A0"]
    ctk.ThemeManager.theme["CTkEntry"]["fg_color_disabled"] = ["#F0F0F0", "#F0F0F0"]
    ctk.ThemeManager.theme["CTkEntry"]["border_color_disabled"] = ["#D0D0D0", "#D0D0D0"]
    
    # Configuration des menus et switches
    ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color"] = ["#3A7EBF", "#3A7EBF"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"] = ["#2A5F8F", "#2A5F8F"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color"] = ["#1A4F7F", "#1A4F7F"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["text_color_disabled"] = ["#A0A0A0", "#A0A0A0"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color_disabled"] = ["#D0D0D0", "#D0D0D0"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_color_disabled"] = ["#C0C0C0", "#C0C0C0"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color_disabled"] = ["#B0B0B0", "#B0B0B0"]
    
    ctk.ThemeManager.theme["CTkSwitch"]["progress_color"] = ["#3A7EBF", "#3A7EBF"]
    ctk.ThemeManager.theme["CTkSwitch"]["button_hover_color"] = ["#2A5F8F", "#2A5F8F"]

    # Configuration des cases à cocher
    ctk.ThemeManager.theme["CTkCheckBox"]["text_color_disabled"] = ["#A0A0A0", "#A0A0A0"]
    ctk.ThemeManager.theme["CTkCheckBox"]["fg_color_disabled"] = ["#D0D0D0", "#D0D0D0"]
    ctk.ThemeManager.theme["CTkCheckBox"]["hover_color_disabled"] = ["#C0C0C0", "#C0C0C0"]
    ctk.ThemeManager.theme["CTkCheckBox"]["checkmark_color_disabled"] = ["#A0A0A0", "#A0A0A0"]

    # Configuration des zones de texte
    ctk.ThemeManager.theme["CTkTextbox"]["text_color_disabled"] = ["#A0A0A0", "#A0A0A0"]
    ctk.ThemeManager.theme["CTkTextbox"]["fg_color_disabled"] = ["#F0F0F0", "#F0F0F0"]
    ctk.ThemeManager.theme["CTkTextbox"]["border_color_disabled"] = ["#D0D0D0", "#D0D0D0"]
    ctk.ThemeManager.theme["CTkTextbox"]["scrollbar_button_color"] = ["#D0D0D0", "#D0D0D0"]
    ctk.ThemeManager.theme["CTkTextbox"]["scrollbar_button_hover_color"] = ["#C0C0C0", "#C0C0C0"]

    # Configuration des cadres défilables
    ctk.ThemeManager.theme["CTkScrollableFrame"]["label_text_color"] = ["#000000", "#000000"]
    ctk.ThemeManager.theme["CTkScrollableFrame"]["scrollbar_button_color"] = ["#D0D0D0", "#D0D0D0"]
    ctk.ThemeManager.theme["CTkScrollableFrame"]["scrollbar_button_hover_color"] = ["#C0C0C0", "#C0C0C0"]
