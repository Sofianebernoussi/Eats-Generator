#!/usr/bin/env python3
import imaplib
import socks
import socket

original_socket = socket.socket

# Essayer avec HTTP proxy au lieu de SOCKS5
print("Configuration HTTP proxy...")
socks.set_default_proxy(
    socks.HTTP,  # HTTP au lieu de SOCKS5
    "brd.superproxy.io",
    33335,  # Port HTTP
    username="brd-customer-hl_c408bb10-zone-residential_proxy1",
    password="evzdu73yycp6"
)
socket.socket = socks.socksocket

try:
    imap_ip = "172.239.57.117"
    
    print(f"Connexion IMAP via HTTP proxy à {imap_ip}...")
    mail = imaplib.IMAP4_SSL(imap_ip, 993, timeout=30)
    print("✅ Connecté!")
    
    print("Login...")
    mail.login("wgothtmvc8165@hotmail.com", "pXsS2dCxmqxg")
    print("✅ Login OK!")
    
    mail.select("INBOX")
    typ, data = mail.search(None, 'ALL')
    num_msgs = len(data[0].split()) if data[0] else 0
    print(f"✅ {num_msgs} messages dans INBOX")
    
    mail.logout()
    print("✅ Test réussi!")
    
except Exception as e:
    print(f"❌ Erreur: {type(e).__name__}: {e}")
finally:
    socket.socket = original_socket