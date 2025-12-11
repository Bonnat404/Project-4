import os
import csv
import sys
from modules import security

FILE_USER = os.path.join("data", "users.csv")

def check_system():
    print("🔍 VÉRIFICATION DU SYSTÈME (MODE NON-DESTRUCTIF)")
    print("=" * 60)

    # --- ÉTAPE 1 : VÉRIFICATION DES FICHIERS ---
    print("1️⃣  Analyse du stockage...")
    if not os.path.exists(FILE_USER):
        print("   ❌ ERREUR : Le fichier users.csv n'existe pas.")
        print("      Lance 'injecter_tests.py' d'abord.")
        return
    
    # Vérification des colonnes
    try:
        with open(FILE_USER, 'r', encoding='utf-8') as f:
            header = next(csv.reader(f))
            if header == ["username", "hash", "salt", "role"]:
                print("   ✅ Fichier users.csv trouvé et structure OK.")
            else:
                print(f"   ⚠️  ATTENTION : Les colonnes semblent incorrectes : {header}")
    except Exception as e:
        print(f"   ❌ Erreur de lecture : {e}")
        return

    # --- ÉTAPE 2 : VÉRIFICATION MATHÉMATIQUE (Interne) ---
    print("\n2️⃣  Test de la cryptographie (security.py)...")
    try:
        test_pass = "TestRapidité123!"
        # On hache
        k, s = security.hash_pw(test_pass)
        # On essaie de vérifier avec le sel généré
        k_verif, _ = security.hash_pw(test_pass, s)
        
        if k == k_verif:
            print("   ✅ Algorithme PBKDF2 fonctionnel (Le hachage est cohérent).")
        else:
            print("   ❌ ERREUR GRAVE : Le hachage ne correspond pas à la vérification !")
            print("      Ton fichier security.py est buggé.")
            return
    except Exception as e:
        print(f"   ❌ Erreur dans le code de sécurité : {e}")
        return

    # --- ÉTAPE 3 : TEST DE CONNEXION MANUEL ---
    print("\n3️⃣  SIMULATION DE CONNEXION")
    print("   (Entrez un utilisateur existant pour voir comment le système le juge)")
    print("-" * 60)
    
    user_input = input("   👤 Identifiant  : ")
    pass_input = input("   🔑 Mot de passe : ")

    print("\n   ⏳ Analyse en cours...")
    
    # Appel réel à la fonction de ton application
    ok, role, status, msg = security.login(user_input, pass_input)

    print("-" * 60)
    if ok:
        print(f"   🎉 CONNEXION RÉUSSIE !")
        print(f"   -----------------------")
        print(f"   🔰 Rôle   : {role.upper()}")
        print(f"   🩺 Santé  : {status.upper()}")
        
        if status == 'ok':
            print("   ✅ Ce compte est SAIN. (Accès direct)")
        elif status == 'weak':
            print("   🟠 Ce compte est FAIBLE. (Déclenche Popup Orange)")
            print(f"      Raison : {msg}")
        elif status == 'pwned':
            print("   🔴 Ce compte est CORROMPU. (Déclenche Popup Rouge)")
            print(f"      Raison : {msg}")
    else:
        print(f"   ❌ ÉCHEC DE CONNEXION")
        print(f"   Raison : {msg}")
        print("   (Vérifiez que cet utilisateur est bien dans le CSV via l'injecteur)")
    print("=" * 60)

if __name__ == "__main__":
    check_system()