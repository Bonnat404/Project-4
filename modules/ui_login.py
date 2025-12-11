import tkinter as tk
from tkinter import messagebox
import modules.ui_client as ui_client
import modules.ui_admin as ui_admin
from modules import security, audit

def show_login(app):
    app.clear()
    app.configure(bg="#000000")
    
    glow_frame = tk.Frame(app, bg="#95a5a6", padx=3, pady=3)
    glow_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    f = tk.Frame(glow_frame, bg="white", padx=40, pady=40)
    f.pack()
    
    tk.Label(f, text="Connexion", font=("Arial", 22, "bold"), bg="white", fg="#333").pack(pady=20)
    tk.Label(f, text="Identifiant", bg="white", fg="gray").pack(anchor="w")
    e_u = tk.Entry(f, width=30, font=("Arial", 12), relief="solid", bd=1); e_u.pack(pady=5)
    tk.Label(f, text="Mot de passe", bg="white", fg="gray").pack(anchor="w")
    e_p = tk.Entry(f, width=30, font=("Arial", 12), show="*", relief="solid", bd=1); e_p.pack(pady=5)
    
    def reset_login_fields():
        e_u.delete(0, 'end')
        e_p.delete(0, 'end')
    
    def process_login_success(username, role, status, msg):
        app.current_role = role
        app.current_user = username
        audit.log_event(username, "LOGIN_SUCCESS", f"Role: {role} | Status: {status}")

        def go_to_interface():
            if role == "admin": ui_admin.show_visu(app)
            else: ui_client.show_client_interface(app)

        if status == 'ok':
            go_to_interface()
        elif status == 'weak':
            show_weak_warning(app, username, msg, go_to_interface, reset_login_fields)
        elif status == 'pwned':
            show_pwned_warning(app, username, msg, reset_login_fields)

    def do_login():
        u, p = e_u.get(), e_p.get()
        ok, role, status, msg = security.login(u, p)
        if ok:
            process_login_success(u, role, status, msg)
        else:
            audit.log_event(u, "LOGIN_FAILED", "Bad credentials")
            messagebox.showerror("Erreur", "Identifiants incorrects")
            e_p.delete(0, 'end')

    tk.Button(f, text="Se Connecter", command=do_login, bg="#27ae60", fg="white", font=("Arial", 11, "bold"), width=28, pady=5, relief="flat").pack(pady=20)
    tk.Frame(f, height=1, bg="#ddd", width=250).pack(pady=10)
    tk.Label(f, text="Nouveau ici ?", bg="white", fg="gray").pack()
    tk.Button(f, text="Créer un compte", command=lambda: show_register_popup(app), bg="white", fg="#2980b9", relief="flat", font=("Arial", 9, "underline")).pack(pady=2)

# --- POPUP : MDP FAIBLE (ORANGE) ---
def show_weak_warning(app, username, msg, callback_continue, callback_cancel):
    top = tk.Toplevel(app)
    top.title("Sécurité - Mot de passe Faible")
    top.geometry("500x350")
    top.configure(bg="#f39c12")
    
    def on_close():
        top.destroy()
        callback_cancel()
    top.protocol("WM_DELETE_WINDOW", on_close)
    
    tk.Label(top, text="⚠️ ATTENTION : MOT DE PASSE FAIBLE", font=("Arial", 16, "bold"), bg="#f39c12", fg="white").pack(pady=20)
    tk.Label(top, text=f"Votre mot de passe actuel est devenu obsolète.\n\nRaison : {msg}", bg="#f39c12", fg="white", font=("Arial", 12)).pack(pady=10)
    
    btn_frame = tk.Frame(top, bg="#f39c12")
    btn_frame.pack(pady=30)
    
    tk.Button(btn_frame, text="Se connecter quand même\n(Non recommandé)", command=lambda: [top.destroy(), callback_continue()], bg="#e67e22", fg="white", font=("Arial", 10), width=25).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Changer le mot de passe\n(Recommandé)", command=lambda: open_change_pw_dialog(app, top, username), bg="white", fg="#d35400", font=("Arial", 10, "bold"), width=25).pack(side="left", padx=10)

# --- POPUP : MDP CORROMPU (ROUGE) ---
def show_pwned_warning(app, username, msg, callback_cancel):
    top = tk.Toplevel(app)
    top.title("ALERTE SÉCURITÉ CRITIQUE")
    top.geometry("500x350")
    top.configure(bg="#c0392b")
    
    def on_close():
        top.destroy()
        callback_cancel()
    top.protocol("WM_DELETE_WINDOW", on_close)
    
    tk.Label(top, text="☠️ MOT DE PASSE CORROMPU", font=("Arial", 18, "bold"), bg="#c0392b", fg="white").pack(pady=20)
    tk.Label(top, text=f"Votre mot de passe a été trouvé dans une fuite de données publique !\nIl n'est plus sûr du tout.\n\n{msg}", bg="#c0392b", fg="white", font=("Arial", 12)).pack(pady=10)
    
    tk.Button(top, text="⚠️CHANGER LE MOT DE PASSE\n(Obligatoire)⚠️", command=lambda: open_change_pw_dialog(app, top, username), bg="white", fg="#c0392b", font=("Arial", 12, "bold"), width=30, pady=10).pack(pady=40)

# --- DIALOGUE CHANGEMENT MDP ---
def open_change_pw_dialog(app, parent_window, username):
    win = tk.Toplevel(parent_window)
    win.title("Mise à jour Sécurité")
    win.geometry("400x350")
    
    tk.Label(win, text="Mise à jour du Compte", font=("Arial", 14, "bold")).pack(pady=10)
    tk.Label(win, text="Utilisateur :").pack(anchor="w", padx=20)
    e_u = tk.Entry(win, width=30); e_u.insert(0, username); e_u.config(state='disabled'); e_u.pack(pady=5)
    tk.Label(win, text="Nouveau Mot de passe (Visible) :").pack(anchor="w", padx=20)
    e_p = tk.Entry(win, width=30); e_p.pack(pady=5)
    
    def save_new_pw():
        new_pass = e_p.get()
        if not new_pass: return
        ok, msg = security.update_credentials(username, username, new_pass)
        if ok:
            messagebox.showinfo("Succès", "Mot de passe mis à jour !\nVous allez être connecté.", parent=win)
            win.destroy()
            parent_window.destroy()
            if app.current_role == "admin": ui_admin.show_visu(app)
            else: ui_client.show_client_interface(app)
        else:
            messagebox.showerror("Erreur", msg, parent=win)

    tk.Button(win, text="Valider & Se connecter", command=save_new_pw, bg="#27ae60", fg="white").pack(pady=20)

# --- INSCRIPTION ---
def show_register_popup(app):
    top = tk.Toplevel(app)
    top.title("Inscription")
    top.geometry("350x300")
    top.configure(bg="#ecf0f1")
    tk.Label(top, text="Créer un compte", font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#2c3e50").pack(pady=15)
    f_in = tk.Frame(top, bg="#ecf0f1"); f_in.pack(pady=5)
    tk.Label(f_in, text="Nom d'utilisateur:", bg="#ecf0f1").pack(anchor="w")
    e_nu = tk.Entry(f_in, width=25, font=("Arial", 11)); e_nu.pack(pady=2)
    tk.Label(f_in, text="Mot de passe:", bg="#ecf0f1").pack(anchor="w", pady=(10,0))
    e_np = tk.Entry(f_in, show="*", width=25, font=("Arial", 11)); e_np.pack(pady=2)
    def process_reg():
        u, p = e_nu.get(), e_np.get()
        if not u or not p: return messagebox.showwarning("!", "Remplissez tout.", parent=top)
        ok, msg = security.register(u, p, "client")
        if ok:
            audit.log_event(u, "REGISTER", "New Client Account")
            messagebox.showinfo("Bienvenue", "Compte créé !", parent=top)
            top.destroy()
        else:
            messagebox.showerror("Erreur", msg, parent=top)
            e_np.delete(0, 'end')
    tk.Button(top, text="S'INSCRIRE", command=process_reg, bg="#2980b9", fg="white", font=("Arial", 10, "bold"), width=20, pady=5).pack(pady=20)