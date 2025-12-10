import tkinter as tk
from tkinter import ttk
# On importe nos nouveaux modules d'interface
from modules import ui_login, ui_client, ui_admin

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DevSecOps E-Commerce Pro (Modulaire)")
        self.geometry("1200x800")
        
        # Configuration du style global
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook.Tab", font=("Arial", 12, "bold"), padding=[10, 5])
        
        # Données partagées entre les pages
        self.current_role = None
        self.current_user = None
        self.cart = {} 

        # Au démarrage, on lance le module de Login
        ui_login.show_login(self)

    def clear(self):
        """Fonction utilitaire pour vider la fenêtre avant de changer de page"""
        for w in self.winfo_children():
            w.destroy()

    def logout(self):
        """Fonction globale de déconnexion"""
        self.current_role = None
        self.current_user = None
        self.cart = {}
        ui_login.show_login(self)

if __name__ == "__main__":
    app = App()
    app.mainloop()