import hashlib
import os
import csv
import requests
import string

FILE_USER = os.path.join("data", "users.csv")

def init_users():
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists(FILE_USER):
        with open(FILE_USER, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(["username", "hash", "salt", "role"])

def check_pwned(password):
    sha1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]
    try:
        r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=2)
        if r.status_code == 200:
            for line in r.text.splitlines():
                h, c = line.split(':')
                if h == suffix: return int(c)
    except: pass
    return 0

def get_password_health(password):
    """
    Retourne l'état de santé du mdp: 'ok', 'weak', 'pwned'
    Et un message explicatif.
    """
    # 1. Check Pwned (Priorité Absolue)
    pwned_count = check_pwned(password)
    if pwned_count > 0:
        return 'pwned', f"CORROMPU ({pwned_count} fuites détectées)"

    # 2. Check Faiblesse
    manquements = []
    if len(password) < 14: manquements.append("longueur < 14")
    if not any(c.isalpha() for c in password): manquements.append("pas de lettre")
    if not any(c.isdigit() for c in password): manquements.append("pas de chiffre")
    if not any(c in string.punctuation for c in password): manquements.append("pas de caractère spécial")
    
    if manquements:
        return 'weak', "FAIBLE : " + ", ".join(manquements)
    
    return 'ok', "Sécurisé"

def hash_pw(password, salt=None):
    if not salt:
        salt = os.urandom(32).hex()
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
    return key, salt

def register(username, password, role):
    init_users()
    # On utilise la fonction de santé pour valider l'inscription
    status, msg = get_password_health(password)
    
    # Pour l'inscription, on refuse tout ce qui n'est pas 'ok'
    if status == 'pwned': return False, "Mot de passe CORROMPU ! Refusé."
    if status == 'weak': return False, f"Mot de passe trop faible.\n{msg}"

    with open(FILE_USER, 'r', encoding='utf-8') as f:
        for row in csv.reader(f):
            if row and row[0] == username: return False, "Utilisateur déjà pris"
            
    k, s = hash_pw(password)
    with open(FILE_USER, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([username, k, s, role])
    return True, "Succès"

def login(username, password):
    init_users()
    with open(FILE_USER, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row and row[0] == username:
                stored_hash, stored_salt, role = row[1], row[2], row[3]
                k, _ = hash_pw(password, stored_salt)
                
                if k == stored_hash:
                    # Authentification réussie ! 
                    # MAINTENANT on vérifie la santé pour les warnings
                    status, msg = get_password_health(password)
                    return True, role, status, msg
                    
    return False, None, None, "Identifiants invalides"

def update_credentials(old_username, new_username, new_password):
    """Met à jour le pseudo et le mot de passe"""
    users = []
    updated = False
    
    # Validation du nouveau mot de passe
    status, msg = get_password_health(new_password)
    if status == 'pwned': return False, "Nouveau mot de passe CORROMPU !"
    if status == 'weak': return False, f"Nouveau mot de passe trop faible.\n{msg}"

    # Lecture
    with open(FILE_USER, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if row[0] == old_username:
                # On modifie cette ligne
                new_k, new_s = hash_pw(new_password) # Nouveau sel, nouveau hash
                users.append([new_username, new_k, new_s, row[3]]) # On garde le rôle
                updated = True
            else:
                users.append(row)
    
    # Écriture
    if updated:
        with open(FILE_USER, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if header: writer.writerow(header)
            writer.writerows(users)
        return True, "Mis à jour"
    return False, "Erreur utilisateur non trouvé"