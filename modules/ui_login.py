import tkinter as tk
from tkinter import messagebox
# On importe via l'objet app pour éviter les erreurs, mais on garde les imports locaux si besoin
import modules.ui_client as ui_client
import modules.ui_admin as ui_admin
from modules import security, audit

def show_login(app):
    app.clear()
    # 1. On met un fond SOMBRE pour que le "flou blanc" ressorte
    app.configure(bg="#000000")
    
    # 2. Création de l'effet "Flou/Lueur"
    # On crée un cadre arrière un peu plus grand avec une couleur gris/blanc cassé
    # Cela simule la diffusion de la lumière blanche
    glow_frame = tk.Frame(app, bg="#95a5a6", padx=3, pady=3)
    glow_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # 3. La boîte blanche par-dessus (Le formulaire)
    f = tk.Frame(glow_frame, bg="white", padx=40, pady=40)
    f.pack()
    
    # --- CONTENU DU FORMULAIRE ---
    tk.Label(f, text="Connexion", font=("Arial", 22, "bold"), bg="white", fg="#333").pack(pady=20)
    
    tk.Label(f, text="Identifiant", bg="white", fg="gray").pack(anchor="w")
    e_u = tk.Entry(f, width=30, font=("Arial", 12), relief="solid", bd=1)
    e_u.pack(pady=5)
    
    tk.Label(f, text="Mot de passe", bg="white", fg="gray").pack(anchor="w")
    e_p = tk.Entry(f, width=30, font=("Arial", 12), show="*", relief="solid", bd=1)
    e_p.pack(pady=5)
    
    def do_login():
        u, p = e_u.get(), e_p.get()
        ok, role = security.login(u, p)
        if ok:
            app.current_role = role
            app.current_user = u
            audit.log_event(u, "LOGIN_SUCCESS", f"Role: {role}")
            
            if role == "admin":
                ui_admin.show_visu(app)
            else:
                ui_client.show_client_interface(app)
        else:
            audit.log_event(u, "LOGIN_FAILED", "Bad credentials")
            messagebox.showerror("Erreur", "Identifiants incorrects")

    # Bouton stylisé
    tk.Button(f, text="Se Connecter", command=do_login, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=28, pady=5, relief="flat").pack(pady=20)
    
    tk.Frame(f, height=1, bg="#ddd", width=250).pack(pady=10) # Séparateur
    
    tk.Label(f, text="Nouveau ici ?", bg="white", fg="gray").pack()
    tk.Button(f, text="Créer un compte", command=lambda: show_register_popup(app), bg="white", fg="#2980b9", relief="flat", font=("Arial", 9, "underline")).pack(pady=2)

def show_register_popup(app):
    top = tk.Toplevel(app)
    top.title("Inscription")
    top.geometry("350x300")
    top.configure(bg="#ecf0f1")
    
    tk.Label(top, text="Créer un compte", font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=15)
    
    f_in = tk.Frame(top, bg="#ecf0f1")
    f_in.pack(pady=5)
    
    tk.Label(f_in, text="Nom d'utilisateur:", bg="#ecf0f1").pack(anchor="w")
    e_nu = tk.Entry(f_in, width=25, font=("Arial", 11)); e_nu.pack(pady=2)
    
    tk.Label(f_in, text="Mot de passe:", bg="#ecf0f1").pack(anchor="w", pady=(10,0))
    e_np = tk.Entry(f_in, show="*", width=25, font=("Arial", 11)); e_np.pack(pady=2)
    
    def process_reg():
        u, p = e_nu.get(), e_np.get()
        if not u or not p: return messagebox.showwarning("!", "Remplissez tout.")
        
        ok, msg = security.register(u, p, "client")
        if ok:
            audit.log_event(u, "REGISTER", "New Client Account")
            messagebox.showinfo("Bienvenue", "Compte créé ! Vous pouvez vous connecter.")
            top.destroy()
        else:
            messagebox.showerror("Erreur", msg)
            
    tk.Button(top, text="S'INSCRIRE", command=process_reg, bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=20, pady=5).pack(pady=20)