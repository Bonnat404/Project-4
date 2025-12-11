import csv
import os
import sys

# Ajout du chemin pour trouver les modules
sys.path.append(os.getcwd())

from modules.security import hash_pw 

FILE_USER = os.path.join("data", "users.csv")

def injecter():
    print("   [Injecteur] Création des utilisateurs...")

    # CAS 1 : FAIBLE (Orange)
    # Ce mot de passe est UNIQUE (donc pas rouge) mais SANS SYMBOLE (donc orange)
    u1 = "TestFaible"
    p1 = "CeciEstUnTestJusteFaibleSansSymbole2024" 
    k1, s1 = hash_pw(p1)

    # CAS 2 : CORROMPU (Rouge)
    # Connu des pirates -> Corrompu
    u2 = "TestCorrompu"
    p2 = "Password123456!" 
    k2, s2 = hash_pw(p2)

    # Écriture (On écrase le fichier pour être sûr d'avoir les bons hashs)
    with open(FILE_USER, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["username", "hash", "salt", "role"])
        writer.writerow([u1, k1, s1, "client"])
        writer.writerow([u2, k2, s2, "client"])

    print("   [Injecteur] ✅ Fichier users.csv généré.")
    print("-" * 40)
    print(f"🟠 Pour tester l'ORANGE :")
    print(f"   User : {u1}")
    print(f"   Pass : {p1}")
    print("-" * 40)
    print(f"🔴 Pour tester le ROUGE :")
    print(f"   User : {u2}")
    print(f"   Pass : {p2}")

if __name__ == "__main__":
    injecter()