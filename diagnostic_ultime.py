import os
import time

# Chemin du fichier
REL_PATH = os.path.join("data", "users.csv")
ABS_PATH = os.path.abspath(REL_PATH)

def kill_csv():
    print("-" * 50)
    print("💀 MISSION : DESTRUCTION DU CSV")
    print("-" * 50)
    
    print(f"📍 Je cherche le fichier ici :")
    print(f"   -> {ABS_PATH}")

    # 1. EST-CE QU'IL EXISTE ?
    if not os.path.exists(ABS_PATH):
        print("\n❌ Le fichier n'existe pas à cet endroit.")
        print("   Soit il est déjà supprimé, soit ton dossier 'data' n'est pas là.")
        
        # Vérif dossier
        dossier = os.path.dirname(ABS_PATH)
        if os.path.exists(dossier):
            print(f"   (Le dossier '{dossier}' existe bien).")
        else:
            print(f"   (Le dossier '{dossier}' N'EXISTE PAS !)")
        return

    print("\n✅ Fichier trouvé !")

    # 2. TENTATIVE DE SUPPRESSION
    print("💥 Tentative de suppression...")
    try:
        os.remove(ABS_PATH)
        print("\n🎉 SUCCÈS ! Fichier users.csv supprimé.")
        print("   Tu peux maintenant lancer l'injecteur.")
    except PermissionError:
        print("\n⛔ STOP ! ACCÈS REFUSÉ (PermissionError)")
        print("   Le fichier est VERROUILLÉ par un autre programme.")
        print("   Causes possibles :")
        print("   1. Excel est ouvert ?")
        print("   2. Une fenêtre Python (Tkinter) est encore ouverte en fond ?")
        print("   3. Un terminal est bloqué ?")
    except Exception as e:
        print(f"\n❌ ERREUR INCONNUE : {e}")

if __name__ == "__main__":
    kill_csv()
    print("-" * 50)
    input("Appuie sur Entrée pour quitter...")