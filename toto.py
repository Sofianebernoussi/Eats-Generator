import imaplib
import time

# Remplace avec tes identifiants
email = "hcoainkqqt4204@hotmail.com"
password = "8fMQuX2m2u"

print("[*] Test 1: Connection basique sur port 993")
try:
    mail = imaplib.IMAP4_SSL('imap.zmailservice.com', 993, timeout=30)
    print(f"[✓] Connected: {mail.welcome}")
    
    print("\n[*] Test 2: Login")
    status, response = mail.login(email, password)
    print(f"[✓] Login: {status} - {response}")
    
    time.sleep(1)
    
    print("\n[*] Test 3: NOOP (keep-alive)")
    status, response = mail.noop()
    print(f"[✓] NOOP: {status} - {response}")
    
    print("\n[*] Test 4: Select INBOX")
    status, response = mail.select('INBOX')
    print(f"[✓] Select: {status} - {response}")
    
    print("\n[*] Test 5: Search ALL")
    status, response = mail.search(None, 'ALL')
    print(f"[✓] Search: {status} - {response}")
    
    mail.logout()
    print("\n[✓] Logout successful")
    
except Exception as e:
    print(f"[✗] Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("[*] Test 6: Connection sur port 143 (sans SSL)")
try:
    mail = imaplib.IMAP4('imap.zmailservice.com', 143, timeout=30)
    print(f"[✓] Connected: {mail.welcome}")
    
    print("\n[*] Test 7: Login")
    status, response = mail.login(email, password)
    print(f"[✓] Login: {status} - {response}")
    
    time.sleep(1)
    
    print("\n[*] Test 8: NOOP")
    status, response = mail.noop()
    print(f"[✓] NOOP: {status} - {response}")
    
    print("\n[*] Test 9: Select INBOX")
    status, response = mail.select('INBOX')
    print(f"[✓] Select: {status} - {response}")
    
    print("\n[*] Test 10: Search ALL")
    status, response = mail.search(None, 'ALL')
    print(f"[✓] Search: {status} - {response}")
    
    mail.logout()
    print("\n[✓] Logout successful")
    
except Exception as e:
    print(f"[✗] Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
