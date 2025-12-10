import tkinter as tk
from tkinter import ttk
import csv
import os

# Chemin vers le fichier de données (le même que celui utilisé par main.py)
FILE_PROD = os.path.join("data", "produits.csv")

class PublicScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔴 STOCK EN TEMPS RÉEL")
        self.geometry("800x600")
        self.configure(bg="#2c3e50") # Fond sombre pour faire "écran d'affichage"

        # Titre
        tk.Label(self, text="DISPONIBILITÉ DES PRODUITS", font=("Arial", 24, "bold"), bg="#2c3e50", fg="white").pack(pady=20)

        # Tableau
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="#ecf0f1", 
                        fieldbackground="#ecf0f1", 
                        foreground="black", 
                        rowheight=30, 
                        font=("Arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))

        self.tree = ttk.Treeview(self, columns=("nom", "prix", "quantite"), show="headings")
        
        self.tree.heading("nom", text="Produit")
        self.tree.column("nom", anchor="center")
        
        self.tree.heading("prix", text="Prix Unitaire")
        self.tree.column("prix", anchor="center", width=150)
        
        self.tree.heading("quantite", text="En Stock")
        self.tree.column("quantite", anchor="center", width=150)
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=20)

        # Zone de statut (bas de page)
        self.lbl_info = tk.Label(self, text="Mise à jour automatique...", bg="#2c3e50", fg="#bdc3c7", font=("Arial", 10))
        self.lbl_info.pack(pady=10)

        # LANCEMENT DE LA BOUCLE DE MISE À JOUR
        self.auto_refresh()

    def get_data(self):
        """Lit le fichier CSV sans le bloquer"""
        data = []
        if os.path.exists(FILE_PROD):
            try:
                with open(FILE_PROD, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        data.append(row)
            except:
                pass # Si le fichier est en cours d'écriture par l'admin, on attend la prochaine fois
        return data

    def auto_refresh(self):
        """Fonction qui se relance toute seule toutes les 2 secondes"""
        # 1. On vide le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 2. On récupère les données fraîches
        produits = self.get_data()
        
        # 3. On remplit le tableau
        for p in produits:
            # Petite logique visuelle : Si stock faible (<5), on peut colorier (optionnel)
            nom = p.get('nom', 'N/A')
            prix = p.get('prix', '0') + " €"
            qty = p.get('quantite', '0')
            
            self.tree.insert("", "end", values=(nom, prix, qty))

        # 4. LA MAGIE : On demande à tkinter de relancer cette fonction dans 2000ms (2 secondes)
        self.after(2000, self.auto_refresh)

if __name__ == "__main__":
    app = PublicScreen()
    app.mainloop()