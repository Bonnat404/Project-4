import tkinter as tk
from tkinter import ttk, messagebox
from modules import data, audit

def show_client_interface(app):
    app.clear()
    app.configure(bg="#000000")
    
    # CHARGEMENT DU PANIER SAUVEGARDÉ
    app.cart = data.get_user_cart(app.current_user)

    # Header
    top = tk.Frame(app, bg="#000000", height=60)
    top.pack(fill="x")
    tk.Label(top, text=f"👤 {app.current_user}", fg="white", bg="#000000", font=("Arial", 12)).pack(side="left", padx=20)
    tk.Button(top, text="Déconnexion", command=app.logout, bg="#e74c3c", fg="white").pack(side="right", padx=20)
    
    app.lbl_header_total = tk.Label(top, text="Panier : 0.00 €", fg="#f1c40f", bg="#000000", font=("Arial", 14, "bold"))
    app.lbl_header_total.pack(side="right", padx=20)

    # Onglets
    app.tabs = ttk.Notebook(app)
    app.tabs.pack(fill="both", expand=True, padx=10, pady=10)
    
    tab_store = tk.Frame(app.tabs, bg="#f5f5f5")
    tab_cart = tk.Frame(app.tabs, bg="#f5f5f5")
    tab_orders = tk.Frame(app.tabs, bg="#f5f5f5")
    
    app.tabs.add(tab_store, text=" 🛍️ Magasin ")
    app.tabs.add(tab_cart, text=" 🛒 Panier ")
    app.tabs.add(tab_orders, text=" 📜 Achats ")
    
    build_store_tab(app, tab_store)
    build_cart_tab(app, tab_cart)
    build_orders_tab(app, tab_orders)
    
    update_header_total(app)
    
    app.tabs.bind("<<NotebookTabChanged>>", lambda e: [
        refresh_cart(app), 
        refresh_orders(app), 
        refresh_store(app)
    ])

    # LANCEMENT DE LA BOUCLE AUTOMATIQUE
    start_auto_refresh(app)

def update_header_total(app):
    total = 0.0
    all_p = {p['id']: p for p in data.get_products()}
    for pid, qty in app.cart.items():
        if str(pid) in all_p:
            total += float(all_p[str(pid)]['prix'].replace('€','').strip()) * qty
    if hasattr(app, 'lbl_header_total'):
        app.lbl_header_total.config(text=f"Panier : {round(total, 2)} €")

# --- BOUCLE AUTOMATIQUE ---
def start_auto_refresh(app):
    if app.current_role != "client": return

    try:
        if app.tabs.index(app.tabs.select()) == 0:
            refresh_store(app)
    except: pass
    
    app.after(3000, lambda: start_auto_refresh(app))

# --- MAGASIN ---
def build_store_tab(app, parent):
    app.tree_store = ttk.Treeview(parent, columns=("id", "nom", "prix", "quantite"), show="headings")
    app.tree_store.heading("id", text="#")
    app.tree_store.heading("nom", text="Produit")
    app.tree_store.heading("prix", text="Prix")
    app.tree_store.heading("quantite", text="Qté")
    
    app.tree_store.column("id", width=50, anchor="center")
    app.tree_store.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    # --- C'EST ICI QUE J'AI MIS LE ROUGE CLAIR (#ff4444) ---
    app.tree_store.tag_configure('rupture', background='#ff4444', foreground='white')
    
    right = tk.Frame(parent, bg="#fff", padx=20, pady=20)
    right.pack(side="right", fill="y", padx=10, pady=10)
    tk.Label(right, text="Quantité :").pack()
    app.spin_qty = tk.Spinbox(right, from_=1, to=100, width=5)
    app.spin_qty.pack()
    tk.Button(right, text="Ajouter 🛒", command=lambda: add_to_cart(app), bg="#FF9800", fg="white").pack(pady=10)
    refresh_store(app)

def refresh_store(app):
    if not hasattr(app, 'tree_store'): return
    
    selected_id = None
    try:
        sel = app.tree_store.selection()
        if sel:
            selected_id = app.tree_store.item(sel[0])['values'][0]
    except: pass

    for i in app.tree_store.get_children(): app.tree_store.delete(i)
    
    for p in data.get_products():
        # Si quantité est 0, on applique le tag 'rupture'
        tag = 'rupture' if int(p['quantite']) == 0 else 'ok'
        item = app.tree_store.insert("", "end", values=(p['id'], p['nom'], p['prix']+" €", p['quantite']), tags=(tag,))
        
        if selected_id is not None and str(p['id']) == str(selected_id):
            app.tree_store.selection_set(item)

def add_to_cart(app):
    sel = app.tree_store.selection()
    if not sel: return
    item = app.tree_store.item(sel[0])
    pid = item['values'][0]
    stock = int(item['values'][3])
    
    if stock == 0: return messagebox.showwarning("!", "Rupture de stock")
    
    try: q = int(app.spin_qty.get())
    except: return
    
    if (app.cart.get(str(pid),0) + q) > stock:
        return messagebox.showwarning("!", "Stock insuffisant")
        
    app.cart[str(pid)] = app.cart.get(str(pid),0) + q
    
    data.save_user_cart(app.current_user, app.cart)
    messagebox.showinfo("OK", "Ajouté")
    update_header_total(app)

# --- PANIER ---
def build_cart_tab(app, parent):
    app.tree_cart = ttk.Treeview(parent, columns=("id", "nom", "qty", "total", "status"), show="headings")
    app.tree_cart.heading("id", text="#")
    app.tree_cart.heading("nom", text="Produit")
    app.tree_cart.heading("qty", text="Quantité")
    app.tree_cart.heading("total", text="Total")
    app.tree_cart.heading("status", text="État")
    
    app.tree_cart.column("id", width=50, anchor="center")
    app.tree_cart.column("status", width=150, anchor="center")
    
    app.tree_cart.pack(fill="both", expand=True, padx=10, pady=10)
    app.tree_cart.tag_configure('error', background='#e74c3c', foreground='white')
    
    app.tree_cart.bind("<<TreeviewSelect>>", lambda e: on_cart_select(app))

    ctrl = tk.LabelFrame(parent, text=" Modifier ", padx=10, pady=10)
    ctrl.pack(pady=5)
    tk.Button(ctrl, text="➖", command=lambda: update_cart_qty(app, -1, True), width=5).pack(side="left", padx=5)
    app.ent_cart_qty = tk.Entry(ctrl, width=10, justify="center")
    app.ent_cart_qty.pack(side="left", padx=5)
    tk.Button(ctrl, text="➕", command=lambda: update_cart_qty(app, 1, True), width=5).pack(side="left", padx=5)
    tk.Button(ctrl, text="Définir", command=lambda: update_cart_qty(app, 0, False), bg="#2196F3", fg="white").pack(side="left", padx=10)

    bottom = tk.Frame(parent, bg="#ddd", height=50); bottom.pack(fill="x", side="bottom")
    app.lbl_total_cart_bottom = tk.Label(bottom, text="Total: 0.00 €", font=("Arial", 16, "bold"), bg="#ddd")
    app.lbl_total_cart_bottom.pack(side="left", padx=20, pady=10)
    tk.Button(bottom, text="PAYER", command=lambda: pay_now(app), bg="#27ae60", fg="white", font=("Arial", 12)).pack(side="right", padx=20, pady=10)

def on_cart_select(app):
    sel = app.tree_cart.selection()
    if sel:
        qty = app.tree_cart.item(sel[0])['values'][2]
        app.ent_cart_qty.delete(0, 'end')
        app.ent_cart_qty.insert(0, qty)

def update_cart_qty(app, value, relative=True):
    sel = app.tree_cart.selection()
    if not sel: return
    pid = str(app.tree_cart.item(sel[0])['values'][0])
    
    all_p = {p['id']: p for p in data.get_products()}
    stock_max = int(all_p[pid]['quantite']) if pid in all_p else 0
    
    current = app.cart.get(pid, 0)
    if relative: new_qty = current + value
    else: 
        try: new_qty = int(app.ent_cart_qty.get())
        except: return

    if new_qty <= 0: 
        del app.cart[pid]
    elif pid in all_p and new_qty > stock_max:
        messagebox.showwarning("Stop", f"Stock insuffisant ({stock_max} dispo).")
        app.cart[pid] = stock_max
    else:
        app.cart[pid] = new_qty
    
    data.save_user_cart(app.current_user, app.cart)
    refresh_cart(app)
    update_header_total(app)

def refresh_cart(app):
    if not hasattr(app, 'tree_cart'): return
    for i in app.tree_cart.get_children(): app.tree_cart.delete(i)
    
    all_p = {p['id']: p for p in data.get_products()}
    total_global = 0.0
    
    for pid, qty in app.cart.items():
        if str(pid) in all_p:
            p = all_p[str(pid)]
            stock_reel = int(p['quantite'])
            tot = float(p['prix'].replace('€','').strip()) * qty
            total_global += tot
            
            if qty > stock_reel:
                status = f"STOCK INSUFFISANT (Max {stock_reel})"
                tag = 'error'
            else:
                status = "OK"
                tag = 'ok'
                
            app.tree_cart.insert("", "end", values=(pid, p['nom'], qty, f"{tot} €", status), tags=(tag,))
        else:
            app.tree_cart.insert("", "end", values=(pid, "SUPPRIMÉ", qty, "0 €", "INDISPONIBLE"), tags=('error',))
            
    app.lbl_total_cart_bottom.config(text=f"Total: {round(total_global, 2)} €")
    update_header_total(app)

def pay_now(app):
    if not app.cart: return
    all_p = {p['id']: p for p in data.get_products()}
    items_valid = []
    
    for pid, qty in app.cart.items():
        if str(pid) not in all_p:
            messagebox.showerror("Erreur", f"Le produit ID {pid} n'existe plus !")
            return
        stock_reel = int(all_p[str(pid)]['quantite'])
        if qty > stock_reel:
            messagebox.showerror("Stock", f"Le produit '{all_p[str(pid)]['nom']}' manque de stock !")
            refresh_cart(app)
            return
        p = all_p[str(pid)]
        items_valid.append({'id': pid, 'nom': p['nom'], 'prix': p['prix'].replace('€','').strip(), 'qty': qty})

    if messagebox.askyesno("?", "Confirmer achat ?"):
        data.record_order(app.current_user, items_valid)
        app.cart = {}
        refresh_cart(app)
        update_header_total(app)
        messagebox.showinfo("Merci", "Achat confirmé")

# --- HISTORIQUE ACHATS ---
def build_orders_tab(app, parent):
    app.tree_orders = ttk.Treeview(parent, columns=("date", "produit", "qty", "total"), show="headings")
    app.tree_orders.heading("date", text="Date")
    app.tree_orders.heading("produit", text="Produit")
    app.tree_orders.heading("qty", text="Qté")
    app.tree_orders.heading("total", text="Total")
    app.tree_orders.pack(fill="both", expand=True)

def refresh_orders(app):
    if not hasattr(app, 'tree_orders'): return
    for i in app.tree_orders.get_children(): app.tree_orders.delete(i)
    for o in data.get_user_orders(app.current_user):
        app.tree_orders.insert("", "end", values=(o['date'], o['produit'], o['quantite'], o['total']+"€"))