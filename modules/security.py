import hashlib
import os
import csv
import requests

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

def hash_pw(password, salt=None):
    if not salt: salt = os.urandom(32).hex()
    key = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return key, salt

def register(username, password, role):
    init_users()
    if len(password) < 4: return False, "Mot de passe trop court"
    
    pwned = check_pwned(password)
    if pwned > 0: return False, f"Mot de passe COMPROMIS ({pwned} fois)"
    
    with open(FILE_USER, 'r', encoding='utf-8') as f:
        for row in csv.reader(f):
            if row and row[0] == username: return False, "Utilisateur pris"
            
    k, s = hash_pw(password)
    with open(FILE_USER, 'a', newline='', encoding='utf-8') as f:
        csv.writer(f).writerow([username, k, s, role])
    return True, "Succès"

def login(username, password):
    init_users()
    with open(FILE_USER, 'r', encoding='utf-8') as f:
        next(csv.reader(f), None)
        for row in csv.reader(f):
            if row and row[0] == username:
                k, _ = hash_pw(password, row[2])
                if k == row[1]: return True, row[3]
    return False, "Echec"
