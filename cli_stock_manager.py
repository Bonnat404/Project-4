import csv
import os
import sys
import getpass

# --- CONFIGURATION & FICHIERS ---
FILE_PROD = os.path.join("data", "produits.csv") 
MIN_REQUIRED_ROLE = "admin"

# --- IMPORT DU MODULE DE SÉCURITÉ ---
try:
    from modules.security import login, init_users 
except ImportError:
    print("⚠️ ERREUR CRITIQUE : Le module 'modules.security' est introuvable.")
    
    def init_users(): pass
    def login(username, password):
        if username.lower() == "admin" and password == "admin":
            return True, "admin", "ok", "Mode secours"
        return False, None, "error", "Module manquant"

# --- GESTION DES FICHIERS PRODUITS ---
def init_produits_file():
    """Assure que le fichier produits.csv existe avec l'en-tête."""
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists(FILE_PROD):
        with open(FILE_PROD, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["id", "nom", "prix", "quantite", "min_stock", "max_stock"])

class StockManager:
    """Classe pour gérer les opérations CRUD sur le fichier de stock."""

    def __init__(self):
        init_produits_file()
        self.data = self._read_all()
        self.next_id = self._get_next_id()

    def _read_all(self):
        data = []
        if os.path.exists(FILE_PROD):
            with open(FILE_PROD, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        row['id'] = int(row['id'])
                        row['prix'] = float(row['prix'])
                        row['quantite'] = int(row['quantite'])
                        row['min_stock'] = int(row.get('min_stock', 10))
                        row['max_stock'] = int(row.get('max_stock', 100))
                        data.append(row)
                    except ValueError:
                        continue 
        return data

    def _write_all(self):
        with open(FILE_PROD, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["id", "nom", "prix", "quantite", "min_stock", "max_stock"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)

    def _get_next_id(self):
        if not self.data: return 1
        return max(p['id'] for p in self.data) + 1

    # --- CLI ACTIONS (MODIFIÉE POUR LES ICÔNES) ---
    def list_products(self):
        if not self.data:
            print("\nℹ️ Le stock est vide.")
            return

        total_value = sum(p['prix'] * p['quantite'] for p in self.data)
        
        print("\n--- Stock Actuel ---")
        # J'ai élargi la première colonne 'ÉTAT' pour que les émojis s'alignent bien
        print(f"{'ÉTAT':<6} {'ID':<4} {'Nom du Produit':<30} {'Prix (€)':>10} {'Qté':>5} {'Min/Max':>10} {'Valeur':>18}")
        print("-" * 90)
        
        for p in self.data:
            val = round(p['prix'] * p['quantite'], 2)
            qty = p['quantite']
            min_s = p['min_stock']
            
            # --- LOGIQUE DES ICÔNES ---
            if qty == 0:
                # Si stock à 0 -> Croix Rouge
                icon = "❌"
            elif qty <= min_s:
                # Si stock entre 1 et le Min -> Attention Jaune
                icon = "⚠️"
            else:
                # Si stock OK -> Rien (ou un espace pour garder l'alignement)
                icon = "  "
            
            limits = f"{min_s}/{p['max_stock']}"
            
            # Affichage avec l'icône
            print(f"{icon:<6} {p['id']:<4} {p['nom']:<30} {p['prix']:>10.2f} {qty:>5} {limits:>10} {val:>18.2f}")
        
        print("-" * 90)
        print(f"Valeur Totale : {total_value:>80.2f} €")

    def add_product(self, name, price, quantity, min_s, max_s):
        new_product = {
            'id': self.next_id, 'nom': name, 'prix': price, 
            'quantite': quantity, 'min_stock': min_s, 'max_stock': max_s
        }
        self.data.append(new_product)
        self._write_all()
        self.next_id += 1
        print(f"✅ Produit ajouté : {name}")

    def update_quantity(self, product_id, new_quantity):
        for p in self.data:
            if p['id'] == product_id:
                p['quantite'] = new_quantity
                self._write_all()
                print(f"✅ Stock mis à jour.")
                return
        print("❌ ID introuvable.")

    def update_stock_limits(self, product_id, new_min, new_max):
        for p in self.data:
            if p['id'] == product_id:
                p['min_stock'] = new_min
                p['max_stock'] = new_max
                self._write_all()
                print(f"✅ Seuils mis à jour.")
                return
        print("❌ ID introuvable.")

    def delete_product(self, product_id):
        initial_len = len(self.data)
        self.data = [p for p in self.data if p['id'] != product_id]
        if len(self.data) < initial_len:
            self._write_all()
            print(f"✅ Produit supprimé.")
        else:
            print("❌ ID introuvable.")

    def reset_products(self):
        self.data = []
        self.next_id = 1
        self._write_all()
        print("✅ Stock vidé.")

# --- INTERFACE UTILISATEUR (CLI) ---

def show_menu():
    print("\n--- ADMIN PANEL ---")
    print("1. Lister Stock (Voir États)")
    print("2. Ajouter Produit")
    print("3. Modifier Quantité")
    print("4. Modifier Seuils")
    print("5. Supprimer Produit")
    print("6. RESET TOTAL")
    print("0. Quitter")

def main_cli():
    # 1. INITIALISATION
    init_users()
    
    print("\n🔒 ACCÈS RESTREINT : ADMINISTRATEURS UNIQUEMENT 🔒")
    
    logged_in_user = None
    
    # 2. CONNEXION
    while logged_in_user is None:
        try:
            username = input("Utilisateur : ")
            password = getpass.getpass("Mot de passe : ")
        except EOFError:
            sys.exit(0)

        success, role, status, msg = login(username, password)

        if success:
            if role == "admin":
                print(f"\n✅ Bienvenue Admin {username}.")
                logged_in_user = username
            else:
                print(f"\n⛔ Accès refusé. Rôle '{role}' non autorisé.")
        else:
            print(f"\n❌ Erreur : {msg}")

    # 3. MANAGER
    manager = StockManager()

    while True:
        show_menu()
        choice = input("Choix : ")

        if choice == '1': manager.list_products()
        elif choice == '2':
            try:
                n = input("Nom : ")
                p = float(input("Prix : "))
                q = int(input("Qté : "))
                mn = int(input("Min : "))
                mx = int(input("Max : "))
                manager.add_product(n, p, q, mn, mx)
            except: print("Erreur de saisie.")
        elif choice == '3':
            try: manager.update_quantity(int(input("ID : ")), int(input("Qté : ")))
            except: print("Erreur.")
        elif choice == '4':
            try: manager.update_stock_limits(int(input("ID : ")), int(input("Min : ")), int(input("Max : ")))
            except: print("Erreur.")
        elif choice == '5':
            try: manager.delete_product(int(input("ID : ")))
            except: print("Erreur.")
        elif choice == '6':
            if input("Confirmer (OUI) ? ") == "OUI": manager.reset_products()
        elif choice == '0':
            break

if __name__ == '__main__':
    main_cli()