import customtkinter as ctk
from ui.settings import Settings

def setup_test_environment(self):
    self.root = ctk.CTk()
    self.root.update_appearance = lambda: None
    self.root.update_conseiller_dropdown = self.mock_update_conseiller_dropdown
    self.settings = Settings(self.root, self.db_manager, self.root)