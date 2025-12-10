import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from modules import data, audit, stats
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- GESTION CENTRALISÉE DU CLIGNOTEMENT ---
def start_global_blinker(app):
    if getattr(app, 'blinker_running', False): 
        return 
    
    app.blinker_running = True
    app.blink_state = False 
    _blink_loop(app)

def _blink_loop(app):
    if app.current_role != "admin":
        app.blinker_running = False
        return

    # On inverse l'état
    app.blink_state = not app.blink_state
    
    # Couleur du clignotement (Alerte Stock Min)
    # ON = Rouge Foncé (#8b0000)
    # OFF = Blanc (#ffffff) - Comme demandé pour remplacer le noir
    bg_alert = '#8b0000' if app.blink_state else '#ffffff'
    fg_alert = 'white' if app.blink_state else 'black' # Texte blanc sur rouge, noir sur blanc

    # 1. MISE A JOUR PAGE VISU (NOIRE)
    if hasattr(app, 'tree_visu') and app.tree_visu.winfo_exists():
        app.tree_visu.tag_configure('alert', background=bg_alert, foreground=fg_alert)

    # 2. MISE A JOUR PAGE DASHBOARD (BLANCHE)
    if hasattr(app, 'tree_dash') and app.tree_dash.winfo_exists():
        app.tree_dash.tag_configure('alert', background=bg_alert, foreground=fg_alert)

    app.after(500, lambda: _blink_loop(app))


# --- PAGE 1 : VISUALISATION LIVE ---
def show_visu(app):
    app.clear()
    app.configure(bg="#000000")
    
    start_global_blinker(app)
    
    header = tk.Frame(app, bg="#000000")
    header.pack(fill="x", pady=20)
    tk.Label(header, text="ADMIN - LIVE", font=("Arial", 24, "bold"), bg="#000000", fg="white").pack()
    
    tk.Button(header, text="📊 STATS & PODIUM", command=lambda: show_advanced_stats(app), bg="#8e44ad", fg="white", font=("Arial", 12)).pack(pady=10)

    tree_frame = tk.Frame(app, bg="#000000", padx=50)
    tree_frame.pack(fill="both", expand=True)
    
    style = ttk.Style()
    style.configure("Visu.Treeview", rowheight=30, font=("Arial", 12))
    
    app.tree_visu = ttk.Treeview(tree_frame, columns=("nom", "prix", "quantite"), show="headings", style="Visu.Treeview")
    app.tree_visu.heading("nom", text="Produit"); app.tree_visu.heading("prix", text="Prix"); app.tree_visu.heading("quantite", text="Stock")
    app.tree_visu.pack(fill="both", expand=True)
    
    # --- COULEURS ---
    # RUPTURE (0) : ROUGE CLAIR (#ff4444) - FIXE
    app.tree_visu.tag_configure('empty', background='#ff4444', foreground='white') 
    
    # ALERTE (Min) : Sera géré par le clignotement (Rouge Foncé <-> Blanc)

    tk.Button(app, text="🔧 GÉRER STOCKS", command=lambda: show_admin_dash(app), bg="#27ae60", fg="white", font=("Arial", 14), padx=20).pack(pady=20)
    tk.Button(app, text="Déconnexion", command=app.logout, bg="#c0392b", fg="white").pack(pady=10)
    
    refresh_visu_loop(app)

def refresh_visu_loop(app):
    if app.current_role != "admin": return
    try:
        if hasattr(app, 'tree_visu') and app.tree_visu.winfo_exists():
            yview = app.tree_visu.yview()
            for i in app.tree_visu.get_children(): app.tree_visu.delete(i)
            
            for p in data.get_products():
                q = int(p['quantite'])
                min_s = int(p.get('min_stock', 10))
                
                if q == 0: tag = 'empty'       # Rouge Clair Fixe
                elif q <= min_s: tag = 'alert' # Clignote (Foncé/Blanc)
                else: tag = 'ok'
                    
                app.tree_visu.insert("", "end", values=(p['nom'], p['prix'] + " €", p['quantite']), tags=(tag,))
            
            app.tree_visu.yview_moveto(yview[0])
    except: pass
    app.after(2000, lambda: refresh_visu_loop(app))


# --- PAGE 2 : GESTION DES STOCKS ---
def show_admin_dash(app):
    app.clear()
    app.configure(bg="#000000")
    
    start_global_blinker(app)
    
    top = tk.Frame(app, bg="#000000", height=60); top.pack(fill="x")
    tk.Button(top, text="⬅ Retour Visu", command=lambda: show_visu(app), bg="#95a5a6", fg="white").pack(side="left", padx=20)
    tk.Label(top, text="GESTION STOCKS", fg="white", bg="#000000", font=("Arial", 12)).pack(side="left")
    tk.Button(top, text="⚠️ RESET SYSTEM", command=lambda: perform_reset(app), bg="red", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=30)
    tk.Button(top, text="💰 CA & Marges", command=show_financials, bg="#27ae60", fg="black").pack(side="right", padx=10)
    tk.Button(top, text="📦 Ventes Produits", command=show_products_sold, bg="#9b5213", fg="white").pack(side="right", padx=10)

    body = tk.Frame(app, bg="#000000"); body.pack(fill="both", expand=True, padx=20, pady=10)
    
    left = tk.LabelFrame(body, text=" Inventaire ", bg="white")
    left.pack(side="left", fill="both", expand=True)
    
    app.tree_dash = ttk.Treeview(left, columns=("id", "nom", "prix", "quantite", "min", "max"), show="headings")
    app.tree_dash.heading("id", text="#"); app.tree_dash.column("id", width=30)
    app.tree_dash.heading("nom", text="Nom")
    app.tree_dash.heading("prix", text="Prix"); app.tree_dash.column("prix", width=60)
    app.tree_dash.heading("quantite", text="Qté"); app.tree_dash.column("quantite", width=60)
    app.tree_dash.heading("min", text="Min Alert"); app.tree_dash.column("min", width=60)
    app.tree_dash.heading("max", text="Max"); app.tree_dash.column("max", width=50)
    app.tree_dash.pack(fill="both", expand=True)
    
    # --- COULEURS ---
    # RUPTURE (0) : ROUGE CLAIR FIXE
    app.tree_dash.tag_configure('empty', background='#ff4444', foreground='white')
    
    app.tree_dash.bind("<<TreeviewSelect>>", lambda e: on_dash_select(app))

    right = tk.Frame(body, bg="#f0f2f5", width=350); right.pack(side="right", fill="y", padx=10)
    
    f_add = tk.LabelFrame(right, text=" Nouveau ", bg="white", padx=10, pady=5); f_add.pack(fill="x", pady=(0, 10))
    r1 = tk.Frame(f_add, bg="white"); r1.pack(fill="x")
    tk.Label(r1, text="Nom:").pack(side="left"); app.e_nom = tk.Entry(r1, width=15); app.e_nom.pack(side="left", padx=5)
    tk.Label(r1, text="Prix:").pack(side="left"); app.e_prix = tk.Entry(r1, width=8); app.e_prix.pack(side="left")
    r2 = tk.Frame(f_add, bg="white"); r2.pack(fill="x", pady=5)
    tk.Label(r2, text="Qté:").pack(side="left"); app.e_qty = tk.Entry(r2, width=5); app.e_qty.pack(side="left", padx=5)
    tk.Label(r2, text="Min:").pack(side="left"); app.e_min = tk.Entry(r2, width=5); app.e_min.insert(0,"10"); app.e_min.pack(side="left")
    tk.Label(r2, text="Max:").pack(side="left"); app.e_max = tk.Entry(r2, width=5); app.e_max.insert(0,"100"); app.e_max.pack(side="left")
    tk.Button(f_add, text="CRÉER", command=lambda: add_prod(app), bg="#27ae60", fg="white").pack(fill="x", pady=5)

    f_mod = tk.LabelFrame(right, text=" Modifier Sélection ", bg="white", padx=10, pady=5); f_mod.pack(fill="x", pady=(0, 10))
    
    tk.Label(f_mod, text="Nom:", bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
    row_nom = tk.Frame(f_mod, bg="white"); row_nom.pack(fill="x", pady=2)
    app.e_mod_nom = tk.Entry(row_nom); app.e_mod_nom.pack(side="left", fill="x", expand=True)
    tk.Button(row_nom, text="Save", command=lambda: save_mod_nom(app), bg="#3498db", fg="white", width=5).pack(side="right")

    tk.Label(f_mod, text="Prix:", bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
    row_prix = tk.Frame(f_mod, bg="white"); row_prix.pack(fill="x", pady=2)
    tk.Button(row_prix, text="-", command=lambda: mod_field_val(app.e_mod_prix, -1), width=2).pack(side="left")
    app.e_mod_prix = tk.Entry(row_prix, justify="center"); app.e_mod_prix.pack(side="left", fill="x", expand=True)
    tk.Button(row_prix, text="+", command=lambda: mod_field_val(app.e_mod_prix, 1), width=2).pack(side="left")
    tk.Button(row_prix, text="Save", command=lambda: save_mod_prix(app), bg="#3498db", fg="white", width=5).pack(side="right")

    tk.Label(f_mod, text="Stock:", bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
    row_qty = tk.Frame(f_mod, bg="white"); row_qty.pack(fill="x", pady=2)
    tk.Button(row_qty, text="-", command=lambda: mod_field_val(app.e_mod_qty, -1), width=2).pack(side="left")
    app.e_mod_qty = tk.Entry(row_qty, justify="center"); app.e_mod_qty.pack(side="left", fill="x", expand=True)
    tk.Button(row_qty, text="+", command=lambda: mod_field_val(app.e_mod_qty, 1), width=2).pack(side="left")
    tk.Button(row_qty, text="Save", command=lambda: save_mod_qty(app), bg="#3498db", fg="white", width=5).pack(side="right")

    tk.Label(f_mod, text="Seuils (Min / Max):", bg="white", font=("Arial", 8, "bold")).pack(anchor="w")
    row_lim = tk.Frame(f_mod, bg="white"); row_lim.pack(fill="x", pady=2)
    app.e_mod_min = tk.Entry(row_lim, width=5); app.e_mod_min.pack(side="left", padx=2)
    app.e_mod_max = tk.Entry(row_lim, width=5); app.e_mod_max.pack(side="left", padx=2)
    tk.Button(row_lim, text="Save Limites", command=lambda: save_mod_limits(app), bg="#9b59b6", fg="white").pack(side="right")

    tk.Button(right, text="Supprimer", command=lambda: del_prod(app), bg="#c0392b", fg="white").pack(fill="x", pady=10)
    
    refresh_dash(app)

# --- LOGIQUE ---

def perform_reset(app):
    if messagebox.askyesno("⚠️ RESET", "Tout effacer (Stocks, Ventes, Paniers) ?"):
        data.reset_all_data(); refresh_dash(app); messagebox.showinfo("Reset", "Remise à zéro effectuée.")

def on_dash_select(app):
    sel = app.tree_dash.selection()
    if sel:
        item = app.tree_dash.item(sel[0]); vals = item['values']
        app.e_mod_nom.delete(0, 'end'); app.e_mod_nom.insert(0, vals[1])
        app.e_mod_prix.delete(0, 'end'); app.e_mod_prix.insert(0, str(vals[2]).replace('€','').strip())
        app.e_mod_qty.delete(0, 'end'); app.e_mod_qty.insert(0, vals[3])
        app.e_mod_min.delete(0, 'end'); app.e_mod_min.insert(0, vals[4])
        app.e_mod_max.delete(0, 'end'); app.e_mod_max.insert(0, vals[5])

def mod_field_val(entry_widget, amount):
    try:
        text_val = entry_widget.get(); clean_val = text_val.replace(',', '.').replace('€', '').strip()
        val = float(clean_val); new_val = val + amount
        if new_val.is_integer(): display_val = str(int(new_val))
        else: display_val = str(round(new_val, 2))
        entry_widget.delete(0, 'end'); entry_widget.insert(0, display_val)
    except: entry_widget.delete(0, 'end'); entry_widget.insert(0, "0")

def get_selected_id(app):
    sel = app.tree_dash.selection()
    if sel: return app.tree_dash.item(sel[0])['values'][0]
    return None

def save_mod_nom(app):
    pid = get_selected_id(app)
    if pid: data.update_product_info(pid, new_nom=app.e_mod_nom.get()); refresh_dash(app)

def save_mod_prix(app):
    pid = get_selected_id(app)
    if pid:
        try: data.update_product_info(pid, new_prix=float(app.e_mod_prix.get().replace(',','.'))); refresh_dash(app)
        except: pass

def save_mod_qty(app):
    pid = get_selected_id(app)
    if pid:
        try: data.update_product_info(pid, new_qty=int(float(app.e_mod_qty.get()))); refresh_dash(app)
        except: pass

def save_mod_limits(app):
    pid = get_selected_id(app)
    if pid:
        try: data.update_product_info(pid, new_min=int(app.e_mod_min.get()), new_max=int(app.e_mod_max.get())); refresh_dash(app)
        except: pass

def refresh_dash(app):
    # Sauvegarde sélection
    sel_id = get_selected_id(app)
    
    for i in app.tree_dash.get_children(): app.tree_dash.delete(i)
    for p in data.get_products():
        q = int(p['quantite'])
        min_s = int(p.get('min_stock', 10))
        max_s = int(p.get('max_stock', 100))
        
        if q == 0: tag = 'empty'       # Rouge Clair Fixe
        elif q <= min_s: tag = 'alert' # Rouge Foncé Clignotant
        else: tag = 'ok'
        
        item = app.tree_dash.insert("", "end", values=(p['id'], p['nom'], p['prix'], p['quantite'], min_s, max_s), tags=(tag,))
        
        if sel_id and str(p['id']) == str(sel_id):
            app.tree_dash.selection_set(item)

def add_prod(app):
    try: 
        n = app.e_nom.get(); p = float(app.e_prix.get().replace(',','.')); q = int(app.e_qty.get())
        mn = int(app.e_min.get()); mx = int(app.e_max.get())
        data.add_product(n, p, q, mn, mx); refresh_dash(app)
        audit.log_event(app.current_user, "ADD_PRODUCT", n)
        app.e_nom.delete(0,'end'); app.e_prix.delete(0,'end'); app.e_qty.delete(0,'end')
    except: pass

def del_prod(app):
    pid = get_selected_id(app)
    if pid: data.delete_product(pid); refresh_dash(app)

def show_financials():
    total_ca = sum([x[1] for x in data.get_stats_dates()])
    messagebox.showinfo("Finances", f"CA Total : {total_ca} €")

def show_products_sold():
    msg = "\n".join([f"{p[0]}: {p[1]}" for p in data.get_stats_products()])
    messagebox.showinfo("Ventes", msg)

# --- STATS AVANCEES ---
def show_advanced_stats(app):
    app.clear()
    app.configure(bg="#000000")
    header = tk.Frame(app, bg="#000000"); header.pack(fill="x", pady=10)
    tk.Button(header, text="⬅ Retour", command=lambda: show_visu(app), bg="#95a5a6", fg="white").pack(side="left", padx=20)
    tk.Label(header, text="STATS", font=("Arial", 20, "bold"), bg="#000000", fg="white").pack(side="left", padx=20)

    tabs = ttk.Notebook(app); tabs.pack(fill="both", expand=True, padx=20, pady=20)
    tab_curve = tk.Frame(tabs); tabs.add(tab_curve, text=" 📈 Ventes ")
    tab_top = tk.Frame(tabs); tabs.add(tab_top, text=" 🏆 Top 5 ")
    tab_cli = tk.Frame(tabs); tabs.add(tab_cli, text=" 🥇 Clients ")

    sales = data.get_stats_dates()
    if sales:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot([x[0] for x in sales], [x[1] for x in sales], marker='o', color='b')
        def currency_fmt(x, pos):
            s = '{:,.0f}'.format(x)
            return s.replace(',', ' ') + ' €'
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
        canvas = FigureCanvasTkAgg(fig, master=tab_curve)
        canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
    
    tree_tp = ttk.Treeview(tab_top, columns=("n","q"), show="headings")
    tree_tp.heading("n", text="Produit"); tree_tp.heading("q", text="Ventes"); tree_tp.pack(fill="both", expand=True)
    for p in data.get_stats_products()[:5]: tree_tp.insert("", "end", values=p)

    tree_cl = ttk.Treeview(tab_cli, columns=("r","u","t"), show="headings")
    tree_cl.heading("r", text="#"); tree_cl.heading("u", text="Client"); tree_cl.heading("t", text="Total"); tree_cl.pack(fill="both", expand=True)
    tree_cl.tag_configure('gold', background='#FFD700'); tree_cl.tag_configure('silver', background='#C0C0C0'); tree_cl.tag_configure('bronze', background='#CD7F32')
    rank = 1
    for c in data.get_stats_clients():
        tag = 'gold' if rank==1 else 'silver' if rank==2 else 'bronze' if rank==3 else ''
        montant_fmt = "{:,.1f}".format(c[1]).replace(",", " ") + " €"
        tree_cl.insert("", "end", values=(rank, c[0], montant_fmt), tags=(tag,)); rank += 1