import csv
import os
from datetime import datetime

FILE_PROD = os.path.join("data", "produits.csv")
FILE_ORDERS = os.path.join("data", "commandes.csv")
FILE_CARTS = os.path.join("data", "paniers.csv")

def init_db():
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists(FILE_PROD):
        with open(FILE_PROD, 'w', newline='', encoding='utf-8') as f:
            # AJOUT DES COLONNES MIN ET MAX
            csv.writer(f).writerow(["id", "nom", "prix", "quantite", "min_stock", "max_stock"])
    if not os.path.exists(FILE_ORDERS):
        with open(FILE_ORDERS, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["user", "date", "produit", "prix_unit", "quantite", "total"])
    if not os.path.exists(FILE_CARTS):
        with open(FILE_CARTS, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["user", "product_id", "qty"])

# --- PRODUITS ---
def get_products():
    init_db()
    data = []
    try:
        with open(FILE_PROD, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Sécurités si anciennes données
                if 'min_stock' not in row: row['min_stock'] = '10'
                if 'max_stock' not in row: row['max_stock'] = '100'
                data.append(row)
    except: pass
    return data

def save_products(products):
    with open(FILE_PROD, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "nom", "prix", "quantite", "min_stock", "max_stock"])
        for p in products:
            # On s'assure que les clés existent
            min_s = p.get('min_stock', '10')
            max_s = p.get('max_stock', '100')
            writer.writerow([p['id'], p['nom'], p['prix'], p['quantite'], min_s, max_s])

def add_product(nom, prix, qty, min_s=10, max_s=100):
    init_db()
    prods = get_products()
    new_id = 1
    if prods:
        ids = [int(p['id']) for p in prods if p['id'].isdigit()]
        if ids: new_id = max(ids) + 1
    with open(FILE_PROD, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([new_id, nom, prix, qty, min_s, max_s])

def update_product_info(pid, new_nom=None, new_prix=None, new_qty=None, new_min=None, new_max=None):
    prods = get_products()
    updated = False
    for p in prods:
        if p['id'] == str(pid):
            if new_nom is not None: p['nom'] = new_nom
            if new_prix is not None: p['prix'] = str(new_prix)
            if new_qty is not None: 
                q = int(new_qty)
                if q < 0: q = 0
                p['quantite'] = str(q)
            if new_min is not None: p['min_stock'] = str(new_min)
            if new_max is not None: p['max_stock'] = str(new_max)
            updated = True
    if updated: save_products(prods)
    return updated

def update_stock(pid, amount):
    prods = get_products()
    current_qty = 0
    for p in prods:
        if p['id'] == str(pid):
            current_qty = int(p['quantite'])
            break
    update_product_info(pid, new_qty=current_qty + amount)

def delete_product(pid):
    prods = get_products()
    new_list = [p for p in prods if p['id'] != str(pid)]
    save_products(new_list)

# --- COMMANDES ---
def record_order(user, cart_items):
    init_db()
    date_str = datetime.now().strftime("%Y-%m-%d") 
    for item in cart_items:
        update_stock(item['id'], -int(item['qty']))
    
    with open(FILE_ORDERS, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for item in cart_items:
            total = float(item['prix']) * int(item['qty'])
            writer.writerow([user, date_str, item['nom'], item['prix'], item['qty'], round(total, 2)])
    save_user_cart(user, {})

def get_user_orders(username):
    init_db()
    orders = []
    try:
        with open(FILE_ORDERS, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row['user'] == username: orders.append(row)
    except: pass
    return orders

# --- PANIER ---
def save_user_cart(user, cart_dict):
    init_db()
    all_carts = []
    try:
        with open(FILE_CARTS, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user'] != user: all_carts.append(row)
    except: pass
    for pid, qty in cart_dict.items():
        all_carts.append({"user": user, "product_id": pid, "qty": qty})
    with open(FILE_CARTS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["user", "product_id", "qty"])
        writer.writeheader()
        writer.writerows(all_carts)

def get_user_cart(user):
    init_db()
    cart = {}
    try:
        with open(FILE_CARTS, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['user'] == user: cart[str(row['product_id'])] = int(row['qty'])
    except: pass
    return cart

# --- STATS ---
def get_all_orders():
    init_db(); orders = []
    try:
        with open(FILE_ORDERS, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f): orders.append(row)
    except: pass
    return orders

def get_stats_clients():
    orders = get_all_orders(); stats = {}
    for o in orders:
        u = o['user']; montant = float(o['total'])
        stats[u] = stats.get(u, 0) + montant
    return sorted(stats.items(), key=lambda x: x[1], reverse=True)

def get_stats_products():
    orders = get_all_orders(); stats = {}
    for o in orders:
        p = o['produit']; q = int(o['quantite'])
        stats[p] = stats.get(p, 0) + q
    return sorted(stats.items(), key=lambda x: x[1], reverse=True)

def get_stats_dates():
    orders = get_all_orders(); stats = {}
    for o in orders:
        d = o['date']; montant = float(o['total'])
        stats[d] = stats.get(d, 0) + montant
    return sorted(stats.items())

# --- RESET TOTAL ---
def reset_all_data():
    init_db()
    with open(FILE_PROD, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["id", "nom", "prix", "quantite", "min_stock", "max_stock"])
    with open(FILE_ORDERS, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["user", "date", "produit", "prix_unit", "quantite", "total"])
    with open(FILE_CARTS, 'w', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow(["user", "product_id", "qty"])