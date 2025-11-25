import imaplib
import requests
import base64
import json
import ssl

# ==========================================
# PARTIE 1 : TEST PLAIN AUTH (USER/PASS)
# ==========================================

def test_plain_auth(email, password, server="outlook.office365.com", port=993):
    print(f"\n--- TEST PLAIN AUTH : {email} ---")
    print(f"[*] Connexion à {server}:{port}...")
    
    try:
        # Création du contexte SSL (parfois nécessaire pour éviter les erreurs de certificat)
        context = ssl.create_default_context()
        
        # Connexion
        mail = imaplib.IMAP4_SSL(server, port, ssl_context=context)
        print("[*] Serveur connecté. Tentative de login...")
        
        # Login
        mail.login(email, password)
        print(f"[✅] SUCCÈS ! Login réussi pour {email}")
        
        # Test de listing des dossiers pour être sûr
        mail.select("INBOX")
        status, messages = mail.search(None, 'ALL')
        count = len(messages[0].split())
        print(f"[i] Nombre d'emails dans INBOX : {count}")
        
        mail.logout()
        return True

    except imaplib.IMAP4.error as e:
        print(f"[❌] ÉCHEC AUTH : Le serveur a refusé le mot de passe ou l'auth basic est désactivée.")
        print(f"    Erreur : {e}")
    except Exception as e:
        print(f"[❌] ERREUR DE CONNEXION : {e}")
    
    return False


# ==========================================
# PARTIE 2 : TEST OAUTH2 (REFRESH TOKEN)
# ==========================================

def get_access_token(client_id, refresh_token):
    print("[*] Récupération de l'Access Token via Refresh Token...")
    data = {
        'client_id': client_id,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    
    try:
        # Note: endpoint standard Microsoft, parfois redirect_uri est requis selon l'app
        ret = requests.post('https://login.live.com/oauth20_token.srf', data=data)
        
        if ret.status_code == 200:
            token = ret.json().get('access_token')
            print(f"[✓] Token récupéré (début): {token[:20]}...")
            return token
        else:
            print(f"[!] Erreur récupération token : {ret.text}")
            return None
    except Exception as e:
        print(f"[!] Exception HTTP : {e}")
        return None

def generate_auth_string(user, token):
    auth_string = f"user={user}\1auth=Bearer {token}\1\1"
    return auth_string

def test_oauth_imap(email, client_id, refresh_token):
    print(f"\n--- TEST OAUTH2 : {email} ---")
    
    # 1. Obtenir le token frais
    access_token = get_access_token(client_id, refresh_token)
    if not access_token:
        return

    # 2. Connexion IMAP
    try:
        print("[*] Connexion à outlook.office365.com...")
        mail = imaplib.IMAP4_SSL('outlook.office365.com', 993)
        
        # 3. Authentification XOAUTH2
        print("[*] Authentification XOAUTH2...")
        
        # Méthode standard pour passer le token
        auth_str = generate_auth_string(email, access_token)
        mail.authenticate('XOAUTH2', lambda x: auth_str)
        
        print(f"[✅] SUCCÈS ! Login OAuth réussi pour {email}")
        
        mail.select("INBOX")
        status, messages = mail.search(None, 'ALL')
        print(f"[i] IDs des messages : {messages[0]}")
        
        mail.logout()

    except Exception as e:
        print(f"[❌] Erreur OAuth IMAP : {e}")


# ==========================================
# EXECUTION
# ==========================================

if __name__ == "__main__":
    
    # --- CHOIX 1 : Compte avec Mot de passe (Plain) ---
    # Remplacez "imap.zmailservice.com" par "outlook.office365.com" si zmail ne marche pas
    # Mais si vous avez acheté ces comptes, zmailservice est souvent le proxy fourni par le vendeur.
    
    TEST_PLAIN = False
    plain_email = "evaymnan404@hotmail.com"
    plain_pass = "EKuym6HfvIY1i"
    plain_server = "imap.zmailservice.com" # Essayez aussi outlook.office365.com

    if TEST_PLAIN:
        test_plain_auth(plain_email, plain_pass, plain_server)


    # --- CHOIX 2 : Compte avec Token (OAuth) ---
    TEST_OAUTH = True # Mettre à True pour tester le token
    
    oauth_email = "zhiyojw11@hotmail.com"
    client_id = '8b4ba9dd-3ea5-4e5f-86f1-ddba2230dcf2'
    refresh_token = "M.C533_SN1.0.U.-Ckg1QEz0rbGx7l*Es*SCkLYZmiqP85SwPmVRug!krVn94lTj6earlSUHUMezVlI0cefVLnrPTGS08fWZgBroJzg4Qmwy0Lg!qFg4fGpYrHByNI4DY416RHI2m6NkidqI3SNPu4omKO5NM4YlnjufFvyO2MdKRhvyE0Ufv!RuY8wRjJ!SJuKkCRBRa6UHKT9wpqovJ0k0JLze5VqClZp!Jmv16a4gAswwzqFFYrm9tLlHuxYevszm24kACW*WGzq*tL6weSHQEG*i1bCaSztSh6*7FLmj2t3cW7qloy94XgC9lCQPB0DnwxE3JRMS41wFXu42tioas1eJJYXlYIRxiX2hte9pTQ04dnLt5MUjNK2pw7KCF!cTqwoPH8omz6Zwoi74n5PwB1VjHVYWtj8h8O8$"

    if TEST_OAUTH:
        test_oauth_imap(oauth_email, client_id, refresh_token)