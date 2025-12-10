import csv
import os
import random
from datetime import datetime, timedelta

# Fichiers
FILE_ORDERS = os.path.join("data", "commandes.csv")
FILE_PROD = os.path.join("data", "produits.csv")

# Données factices
CLIENTS = ["client1", "client2", "maxime", "sarah", "admin", "test_user"]
PRODUITS = [
    {"nom": "Iphone 15", "prix": 1000},
    {"nom": "PC Gamer", "prix": 1500},
    {"nom": "Souris", "prix": 50},
    {"nom": "Clavier", "prix": 100},
    {"nom": "Ecran 4K", "prix": 300},
    {"nom": "USB C", "prix": 20}
]

def generer():
    # 1. Créer le dossier data si besoin
    if not os.path.exists("data"): os.makedirs("data")

    print("Génération des fausses ventes en cours...")
    
    # 2. On écrase le fichier commandes.csv avec de nouvelles données
    with open(FILE_ORDERS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["user", "date", "produit", "prix_unit", "quantite", "total"])
        
        # On génère 50 commandes sur les 10 derniers jours
        for _ in range(50):
            # Choisir un jour au hasard dans le passé (entre hier et il y a 10 jours)
            jours_arriere = random.randint(0, 10)
            date_cmd = (datetime.now() - timedelta(days=jours_arriere)).strftime("%Y-%m-%d")
            
            client = random.choice(CLIENTS)
            prod = random.choice(PRODUITS)
            qty = random.randint(1, 3)
            total = prod["prix"] * qty
            
            writer.writerow([client, date_cmd, prod["nom"], str(prod["prix"]), str(qty), str(total)])

    print("✅ 50 Ventes générées avec succès !")
    print("👉 Lance maintenant 'python main.py' et regarde les stats admin.")

if __name__ == "__main__":
    generer()