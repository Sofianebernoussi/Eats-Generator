#!/usr/bin/env python3
import requests
import time
import json
from datetime import datetime

# Configuration
API_URL = "https://gapi.hotmail007.com/api/mail/getMail"
OUTPUT_FILE = "acc.txt"
LOG_FILE = "api_responses.log"
INTERVAL = 30  # secondes

# Gestion dynamique de la quantité
current_quantity = 1

def fetch_and_save():
    global current_quantity
    
    try:
        # Paramètres avec quantité dynamique
        params = {
            "clientKey": "7c168bb6ebea434bba4eb880829c2cc8519559",
            "mailType": "hotmail Trusted",
            "quantity": str(current_quantity)
        }
        
        # Appel API
        response = requests.get(API_URL, params=params, timeout=10)
        data = response.json()
        
        # Logger la réponse brute dans le fichier de log
        with open(LOG_FILE, "a") as log:
            log.write(f"\n{'='*60}\n")
            log.write(f"[{datetime.now()}] Quantité demandée: {current_quantity}\n")
            log.write(f"Status Code: {response.status_code}\n")
            log.write(f"Réponse brute:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
        
        # Vérifier si le code est 0
        if data.get("code") == 0 and data.get("success") == True:
            # Extraire les données
            accounts = data.get("data", [])
            
            if accounts:
                received_count = len(accounts)
                print(f"[{datetime.now()}] {received_count} compte(s) reçu(s) (quantité demandée: {current_quantity})")
                
                # Parser et sauvegarder
                with open(OUTPUT_FILE, "a") as f:
                    for account in accounts:
                        # Extraire email:password (2 premiers éléments séparés par :)
                        parts = account.split(":")
                        if len(parts) >= 2:
                            credential = f"{parts[0]}:{parts[1]}"
                            f.write(credential + "\n")
                            print(f"  ✓ {parts[0]}")
                
                # Augmenter la quantité si on a reçu ce qu'on a demandé
                if received_count >= current_quantity:
                    if current_quantity == 1:
                        current_quantity = 10
                        print(f"[{datetime.now()}] 🚀 Passage à {current_quantity} comptes par requête")
                    elif current_quantity == 10:
                        current_quantity = 100
                        print(f"[{datetime.now()}] 🚀 Passage à {current_quantity} comptes par requête")
                
            else:
                print(f"[{datetime.now()}] Code 0 mais pas de données")
        else:
            print(f"[{datetime.now()}] Code: {data.get('code')} - En attente...")
            
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] Erreur réseau: {e}")
        # Logger l'erreur
        with open(LOG_FILE, "a") as log:
            log.write(f"\n[{datetime.now()}] ERREUR RÉSEAU: {e}\n")
    except json.JSONDecodeError as e:
        print(f"[{datetime.now()}] Erreur JSON: {e}")
        # Logger l'erreur et la réponse brute
        with open(LOG_FILE, "a") as log:
            log.write(f"\n[{datetime.now()}] ERREUR JSON: {e}\n")
            log.write(f"Réponse brute: {response.text}\n")
    except Exception as e:
        print(f"[{datetime.now()}] Erreur: {e}")
        # Logger l'erreur
        with open(LOG_FILE, "a") as log:
            log.write(f"\n[{datetime.now()}] ERREUR: {e}\n")

def main():
    print("Démarrage du polling API...")
    print(f"Intervalle: {INTERVAL}s")
    print(f"Fichier de sortie: {OUTPUT_FILE}")
    print(f"Fichier de logs: {LOG_FILE}")
    print(f"Quantité initiale: {current_quantity}")
    print("-" * 50)
    
    while True:
        fetch_and_save()
        time.sleep(INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nArrêt du script.")
