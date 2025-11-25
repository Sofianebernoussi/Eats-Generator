"""
Uber Eats Account Generator
by @yubunus on discord and telegram

WARNING: This code is for educational purposes only.
Do not use for actual account creation or unauthorized activities.
"""

import json
import uuid
import random
import asyncio
import time
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from curl_cffi import requests
import secrets

from otp import EmailOTPExtractor, IMAPClient
# Assurez-vous que le fichier sms_wrapper.py est dans le même dossier
from sms_wrapper import SMSActivateAPI 

ENDPOINTS = {
    "submit_form": "https://auth.uber.com/v2/submit-form",
    "submit_form_geo": "https://cn-geo1.uber.com/rt/silk-screen/submit-form",
    "apply_promo_code": "https://cn-geo1.uber.com/rt/eats/v1/eater-promos/add"  # Fixed endpoint
}

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer",
    "Michael", "Linda", "William", "Elizabeth", "David", "Barbara",
    "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah",
    "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Pierre", "Sophie", "Thomas", "Marie", "Nicolas", "Camille"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
    "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore",
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard"
]


def generate_device_info():
    with open('config.json', 'r') as f:
        chosen_device = json.load(f)['device']

    BATTERY_STATUSES = ["charging", "discharging"]
    android_id = secrets.token_hex(8)

    shared_info = {
        "batteryLevel": 1.0,
        "batteryStatus": random.choice(BATTERY_STATUSES),
        "carrier": "Orange F",
        "carrierMcc": "208",
        "carrierMnc": "01",
        "course": 0.0,
        "deviceAltitude": 0.0,
        "deviceLatitude": 48.8566,
        "deviceLongitude": 2.3522,
        "emulator": False,
        "horizontalAccuracy": 0.0,
        "ipAddress": f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}",
        "libCount": random.randint(600, 1000),
        "locationServiceEnabled": False,
        "mockGpsOn": False,
        "rooted": False,
        "sourceApp": "eats",
        "specVersion": "2.0",
        "speed": 0.0,
        "systemTimeZone": "Europe/Paris",
        "unknownItems": {"a": []},
        "version": "6.294.10000",
        "versionChecksum": str(uuid.uuid4()).upper(),
        "verticalAccuracy": 0.0,
        "wifiConnected": True
    }

    ios_info = {
        "device_name": "iPhone",
        "device_os_name": "iOS",
        "device_os_version": "26.0",
        "device_model": "iPhone21,4",
        "env_id": uuid.uuid4().hex,
        "env_checksum": str(uuid.uuid4()).upper(),
        "device_ids": {
            "advertiserId": str(uuid.uuid4()),
            "uberId": str(uuid.uuid4()).upper(),
            "perfId": str(uuid.uuid4()).upper(),
            "vendorId": str(uuid.uuid4()).upper()
        },
        "epoch": time.time() * 1000,
    }

    android_info = {
        "deviceModel": "Pixel 9 Pro",
        "deviceOsName": "Android",
        "deviceOsVersion": "16",
        "cpuAbi": "arm64-v8a, armeabi-v7a, armeabi",
        "androidId": android_id,
        "deviceIds": {
            "androidId": android_id,
            "appDeviceId": str(uuid.uuid4()),
            "drmId": str(uuid.uuid4()).upper(),
            "googleAdvertisingId": str(uuid.uuid4()).upper(),
            "installationUuid": str(uuid.uuid4()).upper(),
            "perfId": str(uuid.uuid4()).upper(),
            "udid": str(uuid.uuid4()).upper(),
            "unknownItems": {"a": []}
        },
        "epoch": {"value": time.time() * 1000},
    }

    ios_device_data = {**shared_info, **ios_info}
    android_device_data = {**shared_info, **android_info}

    return ios_device_data if chosen_device == "ios" else android_device_data


class ProxyManager:
    def __init__(self, proxy_file: str = "proxies.txt", cycle: bool = False):
        self.proxy_file = proxy_file
        self.cycle = cycle
        self.proxies: List[str] = []
        self.current_index = 0

    def load_proxies(self) -> bool:
        proxy_path = Path(self.proxy_file)
        if not proxy_path.exists():
            return False
        content = proxy_path.read_text().strip()
        if not content:
            return False
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        self.proxies = [self._parse_proxy(line) for line in lines]
        return len(self.proxies) > 0

    def _parse_proxy(self, line: str) -> str:
        if line.startswith('http://') or line.startswith('https://'):
            return line
        parts = line.split(':')
        if '@' in line:
            if len(parts) == 2:
                auth, host_port = line.split('@')
                return f"http://{auth}@{host_port}"
            return f"http://{line}"
        if len(parts) == 4:
            user, password, ip, port = parts
            return f"http://{user}:{password}@{ip}:{port}"
        elif len(parts) == 2:
            ip, port = parts
            return f"http://{ip}:{port}"
        return f"http://{line}"

    def get_proxy(self) -> Optional[str]:
        if not self.proxies:
            return None
        if self.cycle:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            return proxy
        else:
            return random.choice(self.proxies)


class RequestHandler:
    def __init__(self, proxy_manager: Optional[ProxyManager] = None):
        self.proxy_manager = proxy_manager
        self.session = requests.Session()

    def reset_session(self):
        self.session = requests.Session()

    async def post(self, name: str, url: str, headers: Dict, data: Dict, return_on_error: bool = False) -> Optional[requests.Response]:
        proxies = None
        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                proxies = {'http': proxy, 'https': proxy}

        try:
            print(f"[DEBUG] {name} - POST {url}")
            
            response = self.session.post(
                url,
                headers=headers,
                json=data,
                proxies=proxies,
                timeout=30
            )

            if response.status_code == 200:
                print(f'[✓] {name} request successful')
                return response
            else:
                print(f'[✗] {name} failed: {response.status_code}')
                try:
                    error_json = response.json()
                    print(f'    Error JSON: {json.dumps(error_json, indent=2)}')
                except json.JSONDecodeError:
                    print(f'    Response text: {response.text[:1000]}')
                
                # Return response anyway if requested (for debugging)
                if return_on_error:
                    return response
                return None

        except Exception as e:
            print(f"[!] Request error in {name}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None


class AccountGenerator:
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.proxy_manager = self._init_proxy_manager()
        self.request_handler = RequestHandler(self.proxy_manager)
        self.device_info = generate_device_info()
        self.last_form_response = None  # Store last response for flow analysis
        
        sms_config = self.config.get('sms_activate', {})
        self.sms_api = None
        if sms_config.get('enabled', False):
            print("[*] SMS Activate module enabled")
            self.sms_api = SMSActivateAPI(sms_config.get('api_key', ''))

    def _load_config(self, config_path: str) -> Dict:
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("[!] Config file not found, using defaults")
            return {"proxy_enabled": False, "cycle_proxies": False}

    def _init_proxy_manager(self) -> Optional[ProxyManager]:
        if not self.config.get('proxy_enabled', False):
            return None
        proxy_manager = ProxyManager(cycle=self.config.get('cycle_proxies', False))
        if not proxy_manager.load_proxies():
            print("[!] Proxy enabled but no proxies found in proxies.txt")
            raise FileNotFoundError("Proxies enabled but proxies.txt is empty or missing")
        print(f"[✓] Loaded {len(proxy_manager.proxies)} proxies")
        return proxy_manager

    def generate_user_info(self, domain: str) -> Tuple[str, str]:
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}{last_name.lower()}{random.randint(1000, 9999)}@{domain}"
        return email, name

    def _get_user_agent(self) -> str:
        device = self.config.get('device', 'android').lower()
        if device == 'ios':
            return "Mozilla/5.0 (iPhone; CPU iPhone OS 26_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
        else:
            return "Mozilla/5.0 (Linux; Android 16; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36"

    def _get_headers(self) -> Dict:
        client_app_version = self.device_info.get('version', '6.294.10000')
        device = self.config.get('device', 'android').lower()
        
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Host": "cn-geo1.uber.com",
            "Origin": "https://auth.uber.com",
            "Referer": "https://auth.uber.com/",
            "Sec-Ch-Ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": self._get_user_agent(),
            "Via": "1.1 martian-a6a2b0967dba8230c0eb",
            "X-Uber-Analytics-Session-Id": str(uuid.uuid4()),
            "X-Uber-App-Device-Id": str(uuid.uuid4()),
            "X-Uber-App-Variant": "ubereats",
            "X-Uber-Client-Id": "com.ubercab.eats",
            "X-Uber-Client-Name": "eats",
            "X-Uber-Client-Version": client_app_version,
            "X-Uber-Device-Udid": str(uuid.uuid4()),
        }

    def _analyze_form_response(self, resp_json: Dict) -> Dict:
        """Analyse la réponse du formulaire pour comprendre le flow attendu."""
        analysis = {
            "session_id": resp_json.get('inAuthSessionID'),
            "next_screens": [],
            "flow_type": resp_json.get('form', {}).get('flowType'),
            "raw_form": resp_json.get('form', {})
        }
        
        screens = resp_json.get('form', {}).get('screens', [])
        for screen in screens:
            screen_info = {
                "type": screen.get('screenType'),
                "fields": []
            }
            for field in screen.get('fields', []):
                field_info = {
                    "fieldType": field.get('fieldType'),
                    "hint": field.get('hint'),
                    "label": field.get('label'),
                    "placeholder": field.get('placeholder'),
                    "value": field.get('value'),
                    "options": field.get('options'),
                    "all_keys": list(field.keys())
                }
                screen_info["fields"].append(field_info)
            analysis["next_screens"].append(screen_info)
        
        print(f"[DEBUG] Flow analysis:")
        print(f"  - Session ID: {analysis['session_id'][:50] if analysis['session_id'] else 'None'}...")
        print(f"  - Flow type: {analysis['flow_type']}")
        for i, screen in enumerate(analysis["next_screens"]):
            print(f"  - Screen {i}: {screen['type']}")
            for field in screen["fields"]:
                print(f"    - Field: {field['fieldType']}")
                print(f"      Keys: {field['all_keys']}")
                if field.get('options'):
                    print(f"      Options (first 3): {field['options'][:3] if isinstance(field['options'], list) else field['options']}")
                if field.get('value'):
                    print(f"      Default value: {field['value']}")
        
        # Dump complet des champs pour debug si c'est un écran téléphone
        for screen in screens:
            if 'PHONE' in screen.get('screenType', ''):
                print(f"\n[DEBUG] Full phone screen dump:")
                print(json.dumps(screen, indent=2, default=str)[:2000])
        
        return analysis

    async def email_signup(self, email: str) -> Optional[str]:
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')

        data = {
            "formContainerAnswer": {
                "inAuthSessionID": "",
                "formAnswer": {
                    "flowType": "INITIAL",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isGoogleAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": json.dumps(self.device_info),
                    "codeChallenge": "XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "uslURL": f"https://auth.uber.com/v2?x-uber-device={'iphone' if device == 'ios' else 'android'}&x-uber-client-name=eats&x-uber-client-version={client_app_version}&x-uber-client-id=com.ubercab.UberEats&countryCode=FR&firstPartyClientID=S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z&isiOSCustomTabSessionClose=true&showPasskeys=true&x-uber-app-variant=ubereats&x-uber-hot-launch-id=7AE26A95-AC62-4DB2-BF6E-E36308EBDCFD&socialNative=afg&x-uber-cold-launch-id=2A5D3FCB-0D28-48D5-81D7-5224D5C963C1&x-uber-device-udid=6968C387-69C6-48B6-9600-51986944428C&is_root=false&known_user=true&codeChallenge=XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": "PHONE_NUMBER_INITIAL",
                            "eventType": "TypeInputEmail",
                            "fieldAnswers": [
                                {
                                    "fieldType": "EMAIL_ADDRESS",
                                    "emailAddress": email
                                }
                            ]
                        }
                    ],
                    "appContext": {
                        "socialNative": "afg"
                    }
                }
            }
        }

        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "fr-FR,fr;q=0.9",
            "Content-Type": "application/json",
            "Host": "auth.uber.com",
            "Origin": "https://auth.uber.com",
            "Sec-Ch-Ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": "\"Android\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": self._get_user_agent(),
            "Via": "1.1 martian-a6a2b2967dba8230c0eb",
            "X-Csrf-Token": "x",
            "X-Uber-Analytics-Session-Id": str(uuid.uuid4()),
            "X-Uber-App-Device-Id": str(uuid.uuid4()),
            "X-Uber-App-Variant": "ubereats",
            "X-Uber-Client-Id": "com.ubercab.eats",
            "X-Uber-Client-Name": "eats",
            "X-Uber-Client-Version": client_app_version,
            'X-Uber-Device': 'iphone' if device == 'ios' else 'android',
            "X-Uber-Device-Udid": str(uuid.uuid4()),
        }

        response = await self.request_handler.post(
            "Email Signup",
            ENDPOINTS['submit_form'],
            headers,
            data
        )

        if response:
            resp_json = response.json()
            self._analyze_form_response(resp_json)
            return resp_json.get('inAuthSessionID')
        return None

    async def submit_otp(self, session_id: str, otp: str) -> Tuple[Optional[str], Optional[Dict]]:
        """Retourne (session_id, form_analysis) pour savoir quel écran vient ensuite."""
        data = {
            "formContainerAnswer": {
                "inAuthSessionID": session_id,
                "formAnswer": {
                    "flowType": "SIGN_UP",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "1.107",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": "",
                    "codeChallenge": "eMw_kvmk5MNvtMZkvYWSpZcib4Jvd0M148zSahclT3w",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": "EMAIL_OTP_CODE",
                            "eventType": "TypeEmailOTP",
                            "fieldAnswers": [
                                {
                                    "fieldType": "EMAIL_OTP_CODE",
                                    "emailOTPCode": otp
                                }
                            ]
                        }
                    ]
                }
            }
        }

        response = await self.request_handler.post(
            "Submit OTP",
            ENDPOINTS['submit_form_geo'],
            self._get_headers(),
            data
        )

        if response:
            resp_json = response.json()
            analysis = self._analyze_form_response(resp_json)
            self.last_form_response = resp_json
            return resp_json.get('inAuthSessionID'), analysis
        return None, None

    # --- SMS HANDLING METHODS ---
    async def _add_phone_number(self, session_id: str, phone_number: str, expected_screen_type: str = None) -> Optional[str]:
        """
        Ajoute un numéro de téléphone. Utilise le screenType détecté dynamiquement.
        """
        # Nettoyer le numéro
        clean_number = phone_number
        if phone_number.startswith('+33'):
            clean_number = phone_number[3:]
        elif phone_number.startswith('33'):
            clean_number = phone_number[2:]
        if clean_number.startswith('0'):
            clean_number = clean_number[1:]
        
        # Déterminer le screenType à utiliser
        screen_type = expected_screen_type or "PHONE_NUMBER_PROGRESSIVE"
        
        # Vérifier si on doit utiliser un autre screenType basé sur la dernière réponse
        if self.last_form_response:
            screens = self.last_form_response.get('form', {}).get('screens', [])
            for screen in screens:
                if 'PHONE' in screen.get('screenType', ''):
                    screen_type = screen.get('screenType')
                    print(f"[DEBUG] Using detected screenType: {screen_type}")
                    break
        
        print(f"[*] Adding phone number: +33 {clean_number}")
        print(f"[DEBUG] Using screenType: {screen_type}")
        
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')
        
        data = {
            "formContainerAnswer": {
                "inAuthSessionID": session_id,
                "formAnswer": {
                    "flowType": "PROGRESSIVE_SIGN_UP",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isGoogleAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": json.dumps(self.device_info),
                    "codeChallenge": "XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "uslURL": f"https://auth.uber.com/v2?x-uber-device={'iphone' if device == 'ios' else 'android'}&x-uber-client-name=eats&x-uber-client-version={client_app_version}&x-uber-client-id=com.ubercab.UberEats&countryCode=FR&firstPartyClientID=S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z&isiOSCustomTabSessionClose=true&showPasskeys=true&x-uber-app-variant=ubereats",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": screen_type,
                            "eventType": "TypeInputPhoneNumber",
                            "fieldAnswers": [
                                {
                                    "fieldType": "PHONE_COUNTRY_CODE",
                                    "isoCountryCode": "FR"
                                },
                                {
                                    "fieldType": "PHONE_NUMBER",
                                    "phoneNumber": clean_number
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        headers = self._get_headers()
        response = await self.request_handler.post("Add Phone", ENDPOINTS['submit_form_geo'], headers, data)
        
        if response:
            resp_json = response.json()
            self._analyze_form_response(resp_json)
            self.last_form_response = resp_json
            return resp_json.get('inAuthSessionID')
        return None

    async def _submit_phone_otp(self, session_id: str, sms_code: str) -> Optional[str]:
        """Soumet le code SMS."""
        print(f"[*] Submitting SMS code: {sms_code}")
        
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')
        
        # Détecter le screenType attendu
        screen_type = "PHONE_OTP_CODE"
        if self.last_form_response:
            screens = self.last_form_response.get('form', {}).get('screens', [])
            for screen in screens:
                if 'OTP' in screen.get('screenType', '') or 'SMS' in screen.get('screenType', ''):
                    screen_type = screen.get('screenType')
                    print(f"[DEBUG] Using detected OTP screenType: {screen_type}")
                    break
        
        data = {
            "formContainerAnswer": {
                "inAuthSessionID": session_id,
                "formAnswer": {
                    "flowType": "PROGRESSIVE_SIGN_UP",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isGoogleAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": json.dumps(self.device_info),
                    "codeChallenge": "XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "uslURL": f"https://auth.uber.com/v2?x-uber-device={'iphone' if device == 'ios' else 'android'}&x-uber-client-name=eats&x-uber-client-version={client_app_version}&x-uber-client-id=com.ubercab.UberEats&countryCode=FR",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": screen_type,
                            "eventType": "TypePhoneOTP",
                            "fieldAnswers": [
                                {
                                    "fieldType": "SMS_OTP_CODE",
                                    "smsOTPCode": sms_code
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        headers = self._get_headers()
        response = await self.request_handler.post("Submit SMS OTP", ENDPOINTS['submit_form_geo'], headers, data)
        
        if response:
            resp_json = response.json()
            self._analyze_form_response(resp_json)
            self.last_form_response = resp_json
            return resp_json.get('inAuthSessionID')
        return None

    async def complete_registration(self, email: str, name: str, session_id: str, form_analysis: Dict = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """Complete la registration en analysant le flow dynamiquement."""
        
        # Analyser les écrans attendus
        if form_analysis:
            next_screens = form_analysis.get('next_screens', [])
            print(f"[DEBUG] Expected screens after OTP: {[s['type'] for s in next_screens]}")
        
        sms_enabled = self.config.get('sms_activate', {}).get('enabled', False)
        
        if sms_enabled and self.sms_api:
            country_id = self.config['sms_activate'].get('country_id', '78')
            iso_country = self.config.get('country_code', 'FR').upper()
            
            print(f"[*] Requesting number from SMS-Activate (Country ID: {country_id})...")
            phone_data = self.sms_api.get_number(service='ub', country=country_id)
            
            if phone_data:
                full_number = phone_data['number']
                activation_id = phone_data['id']
                print(f"[✓] Number acquired: +{full_number}")
                
                session_id = await self._add_phone_number(session_id, full_number)
                
                if session_id:
                    sms_code = self.sms_api.wait_for_code(activation_id)
                    if sms_code:
                        print(f"[✓] SMS Code received: {sms_code}")
                        session_id = await self._submit_phone_otp(session_id, sms_code)
                        if session_id:
                            self.sms_api.set_status(activation_id, 6)
                        else:
                            print("[!] Failed to verify SMS code with Uber")
                            self.sms_api.set_status(activation_id, 8)
                            return False, None, None
                    else:
                        print("[!] SMS Timeout or Cancelled")
                        self.sms_api.set_status(activation_id, 8)
                        return False, None, None
                else:
                    print("[!] Failed to submit phone number to Uber")
                    self.sms_api.set_status(activation_id, 8)
                    return False, None, None
            else:
                print("[!] Failed to buy number from SMS Activate. Aborting.")
                return False, None, None
        else:
            print("[*] Skipping phone number (SMS disabled)")
            session_id = await self._skip_submit(session_id)
            if not session_id:
                print("[!] Skip submit failed, trying to continue anyway...")

        session_id = await self._submit_name(session_id, name)
        if not session_id:
            return False, None, None

        session_id, auth_code = await self._submit_legal_confirmation(session_id)
        if not session_id or not auth_code:
            return False, None, None

        result = await self._submit_auth_code(session_id, auth_code, email, name)
        return result

    async def _skip_submit(self, session_id: str) -> Optional[str]:
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')

        data = {
            "formContainerAnswer": {
                "inAuthSessionID": session_id,
                "formAnswer": {
                    "flowType": "PROGRESSIVE_SIGN_UP",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isGoogleAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": json.dumps(self.device_info),
                    "codeChallenge": "XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "uslURL": f"https://auth.uber.com/v2?x-uber-device={'iphone' if device == 'ios' else 'android'}&x-uber-client-name=eats&x-uber-client-version={client_app_version}&x-uber-client-id=com.ubercab.UberEats&countryCode=FR&firstPartyClientID=S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z&isiOSCustomTabSessionClose=true&showPasskeys=true&x-uber-app-variant=ubereats",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": "SKIP",
                            "eventType": "TypeSkip",
                            "fieldAnswers": []
                        }
                    ]
                }
            }
        }

        headers = self._get_headers()
        response = await self.request_handler.post("Skip Submit", ENDPOINTS['submit_form_geo'], headers, data)

        if response:
            resp_json = response.json()
            self._analyze_form_response(resp_json)
            self.last_form_response = resp_json
            return resp_json.get('inAuthSessionID')
        return None

    async def _submit_name(self, session_id: str, name: str) -> Optional[str]:
        first_name, last_name = name.split(' ', 1)
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')

        data = {
            "formContainerAnswer": {
                "inAuthSessionID": session_id,
                "formAnswer": {
                    "flowType": "PROGRESSIVE_SIGN_UP",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isGoogleAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": json.dumps(self.device_info),
                    "codeChallenge": "XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "uslURL": f"https://auth.uber.com/v2?x-uber-device={'iphone' if device == 'ios' else 'android'}&x-uber-client-name=eats&x-uber-client-version={client_app_version}&x-uber-client-id=com.ubercab.UberEats&countryCode=FR&firstPartyClientID=S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": "FULL_NAME_PROGRESSIVE",
                            "eventType": "TypeInputNewUserFullName",
                            "fieldAnswers": [
                                {"fieldType": "FIRST_NAME", "firstName": first_name},
                                {"fieldType": "LAST_NAME", "lastName": last_name}
                            ]
                        }
                    ]
                }
            }
        }

        headers = self._get_headers()
        response = await self.request_handler.post("Submit Name", ENDPOINTS['submit_form_geo'], headers, data)

        if response:
            resp_json = response.json()
            self._analyze_form_response(resp_json)
            self.last_form_response = resp_json
            return resp_json.get('inAuthSessionID')
        return None

    async def _submit_legal_confirmation(self, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')

        data = {
            "formContainerAnswer": {
                "inAuthSessionID": session_id,
                "formAnswer": {
                    "flowType": "SIGN_UP",
                    "standardFlow": True,
                    "accountManagementFlow": False,
                    "daffFlow": False,
                    "productConstraints": {
                        "isEligibleForWebOTPAutofill": False,
                        "uslFELibVersion": "",
                        "uslMobileLibVersion": "",
                        "isWhatsAppAvailable": False,
                        "isPublicKeyCredentialSupported": True,
                        "isFacebookAvailable": False,
                        "isGoogleAvailable": False,
                        "isRakutenAvailable": False,
                        "isKakaoAvailable": False
                    },
                    "additionalParams": {
                        "isEmailUpdatePostAuth": False
                    },
                    "deviceData": json.dumps(self.device_info),
                    "codeChallenge": "XQt42Ii1O9Qzg69ULyVHcQs8uvhvIznGQniUsVI-mEA",
                    "uslURL": f"https://auth.uber.com/v2?x-uber-device={'iphone' if device == 'ios' else 'android'}&x-uber-client-name=eats&x-uber-client-version={client_app_version}&x-uber-client-id=com.ubercab.UberEats&countryCode=FR",
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "screenAnswers": [
                        {
                            "screenType": "LEGAL",
                            "eventType": "TypeSignupLegal",
                            "fieldAnswers": [
                                {"fieldType": "LEGAL_CONFIRMATION", "legalConfirmation": True},
                                {
                                    "fieldType": "LEGAL_CONFIRMATIONS",
                                    "legalConfirmations": {
                                        "legalConfirmations": [
                                            {
                                                "disclosureVersionUUID": "ef1d61c9-b09e-4d44-8cfb-ddfa15cc7523",
                                                "isAccepted": True
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        }

        headers = self._get_headers()
        response = await self.request_handler.post("Submit Legal", ENDPOINTS['submit_form_geo'], headers, data)

        if response:
            resp_json = response.json()
            try:
                fields = resp_json.get('form', {}).get('screens', [{}])[0].get('fields', [])
                auth_code = fields[0].get('authCode') if fields else None
                session_id = resp_json.get('inAuthSessionID')
                return session_id, auth_code
            except (IndexError, KeyError):
                print("[!] Failed to extract auth code")
                return None, None
        return None, None

    async def _submit_auth_code(self, session_id: str, auth_code: str, email: str = '', name: str = '') -> Tuple[bool, Optional[str], Optional[str]]:
        data = {
            "formContainerAnswer": {
                "formAnswer": {
                    "screenAnswers": [
                        {
                            "fieldAnswers": [
                                {
                                    "sessionVerificationCode": auth_code,
                                    "fieldType": "SESSION_VERIFICATION_CODE",
                                    "daffAcrValues": []
                                },
                                {
                                    "codeVerifier": "zZlmodq2L3ly2tJu6GqOa7Yx7AjJpx3TpiXWFfhUDsZ1QSgTObHzgKn5IBLDxtQBd6Gpj8z1BZki6SwEIg2WRg--",
                                    "fieldType": "CODE_VERIFIER",
                                    "daffAcrValues": []
                                }
                            ],
                            "eventType": "TypeVerifySession",
                            "screenType": "SESSION_VERIFICATION"
                        }
                    ],
                    "standardFlow": True,
                    "deviceData": json.dumps(self.device_info),
                    "firstPartyClientID": "S_Fwp1YMY1qAlAf5-yfYbeb7cfJE-50z",
                    "flowType": "SIGN_IN"
                },
                "inAuthSessionID": f"{session_id}.{auth_code}"
            }
        }

        device = self.config.get('device', 'android').lower()
        is_ios = device == 'ios'
        client_app_version = self.device_info.get('version', '6.294.10000')
        
        headers = {
            'Accept': '*/*',
            'X-Uber-Device-Location-Services-Enabled': '0',
            'X-Uber-Device-Language': 'fr_FR',
            'User-Agent': '/iphone/' + client_app_version if is_ios else '/android/' + client_app_version,
            'X-Uber-Eats-App-Installed': '0',
            'X-Uber-App-Lifecycle-State': 'foreground',
            'X-Uber-Request-Uuid': str(uuid.uuid4()),
            'X-Uber-Device-Time-24-Format-Enabled': '1',
            'X-Uber-Device-Location-Provider': 'ios_core' if is_ios else 'network',
            'X-Uber-Markup-Textformat-Version': '1',
            'X-Uber-Device-Voiceover': '0',
            'X-Uber-Device-Model': 'iPhone21,4' if is_ios else 'Pixel 9 Pro',
            'Accept-Language': 'fr-FR;q=1',
            'X-Uber-Redirectcount': '0',
            'X-Uber-Device-Os': '18.0' if is_ios else '16',
            'X-Uber-Network-Classifier': 'fast',
            'X-Uber-Client-Version': client_app_version,
            'X-Uber-App-Variant': 'ubereats',
            'X-Uber-Device-Id-Tracking-Enabled': '0',
            'X-Uber-Client-Id': 'com.ubercab.UberEats',
            'X-Uber-Client-Name': 'eats',
            'Content-Type': 'application/json',
            'X-Uber-Device': 'iphone' if is_ios else 'android',
            'X-Uber-Client-User-Session-Id': str(uuid.uuid4()),
            'X-Uber-Device-Ids': 'aaid:00000000-0000-0000-0000-000000000000',
            'X-Uber-Device-Id': str(uuid.uuid4()),
        }

        response = await self.request_handler.post(
            "Submit Auth Code",
            ENDPOINTS['submit_form_geo'],
            headers,
            data
        )

        # Save account info
        save_info = self.config.get('save_info', {})
        
        try:
            with open('genned_accs.json', 'r') as f:
                accs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            accs = []

        account_information = {}
        if save_info.get('cookies', False):
            account_information['cookies'] = self.request_handler.session.cookies.get_dict()
        if save_info.get('device_data', False):
            account_information['device_data'] = self.device_info
        if save_info.get('account_info', False):
            account_information['account_info'] = {'email': email, 'name': name}

        accs.append(account_information)

        try:
            with open('genned_accs.json', 'w') as f:
                json.dump(accs, f, indent=4)
        except Exception as e:
            print(f"[!] Failed to save account information: {e}")

        if response:
            resp_json = response.json()
            oauth_info = resp_json.get('oAuthInfo')
            access_token = oauth_info.get('accessToken', None) if oauth_info else None
            user_uuid = resp_json.get('userUUID', None)
            
            # Store for promo code usage
            self.last_access_token = access_token
            self.last_user_uuid = user_uuid
            
            return True, access_token, user_uuid
        else:
            return False, None, None

    async def _apply_promo_code(self, auth_code: str, user_uuid: str, promo_code: str) -> bool:
        """Applique un code promo avec le bon endpoint et headers."""
        
        print(f"[*] Applying promo code: {promo_code}")
        print(f"[DEBUG] Using token: {auth_code[:50]}..." if auth_code else "[DEBUG] No token!")
        
        # Endpoint alternatif plus fiable
        endpoints_to_try = [
            "https://cn-geo1.uber.com/rt/eats/v1/eater-promos/add",
            "https://cn-geo1.uber.com/rt/eats/v2/eater-promos/add",
            "https://cn-phx2.cfe.uber.com/rt/delivery/v1/consumer/apply-and-get-savings"
        ]
        
        device = self.config.get('device', 'android').lower()
        client_app_version = self.device_info.get('version', '6.294.10000')
        
        for endpoint in endpoints_to_try:
            print(f"[DEBUG] Trying endpoint: {endpoint}")
            
            # Format du payload selon l'endpoint
            if "eater-promos" in endpoint:
                data = {
                    "promoCode": promo_code
                }
            else:
                data = {
                    'request': {
                        'savingsInfo': {'code': promo_code},
                        'userUuid': user_uuid,
                        'ctaType': 'BROWSE',
                    }
                }
            
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'fr-FR,fr;q=0.9',
                'Authorization': f'Bearer {auth_code}',
                'Content-Type': 'application/json',
                'Host': endpoint.split('/')[2],
                'Origin': 'https://www.ubereats.com',
                'User-Agent': self._get_user_agent(),
                'X-Uber-Device': 'iphone' if device == 'ios' else 'android',
                'X-Uber-Device-Language': 'fr_FR',
                'X-Uber-Device-Model': 'iPhone21,4' if device == 'ios' else 'Pixel 9 Pro',
                'X-Uber-Device-Os': '18.0' if device == 'ios' else '16',
                'X-Uber-Client-Version': client_app_version,
                'X-Uber-App-Variant': 'ubereats',
                'X-Uber-Client-Id': 'com.ubercab.eats',
                'X-Uber-Client-Name': 'eats',
                'X-Uber-Device-Timezone': 'Europe/Paris',
                'X-Uber-Device-Mobile-Iso2': 'FR',
                'X-Uber-Network-Classifier': 'FAST',
                'X-Uber-App-Lifecycle-State': 'foreground',
            }
            
            # Use session cookies
            cookies = self.request_handler.session.cookies.get_dict()
            if cookies:
                print(f"[DEBUG] Using {len(cookies)} session cookies")
            
            try:
                response = self.request_handler.session.post(
                    endpoint,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                print(f"[DEBUG] Promo response status: {response.status_code}")
                
                if response.status_code == 200:
                    resp_json = response.json()
                    print(f"[DEBUG] Promo response: {json.dumps(resp_json, indent=2)[:500]}")
                    
                    if resp_json.get('chocolateChipCookieError'):
                        print(f"[!] Promo error: {resp_json.get('chocolateChipCookieError')}")
                        continue
                    
                    print("[✓] Promo code applied successfully!")
                    return True
                    
                elif response.status_code == 401:
                    print(f"[!] 401 Unauthorized - Token may be invalid or expired")
                    try:
                        error_json = response.json()
                        print(f"    Error: {json.dumps(error_json, indent=2)}")
                    except:
                        print(f"    Response: {response.text[:200]}")
                else:
                    print(f"[!] Promo failed with status {response.status_code}")
                    try:
                        print(f"    Response: {response.json()}")
                    except:
                        print(f"    Response: {response.text[:200]}")
                        
            except Exception as e:
                print(f"[!] Promo request error: {e}")
                continue
        
        return False

    async def create_account(self, domain: str, email_client: IMAPClient, custom_name: Optional[str] = None) -> Optional[str]:
        # Generate new device info
        self.device_info = generate_device_info()
        self.request_handler.reset_session()
        self.last_form_response = None

        email, generated_name = self.generate_user_info(domain)
        name = custom_name if custom_name else generated_name
        
        if domain == 'hotmail.com':
            email = email_client.username

        print(f"\n[*] Creating account for: {email}")
        print(f"[*] Name: {name}")

        session_id = await self.email_signup(email)
        if not session_id:
            print("[!] Failed to initiate signup")
            return None

        if self.config.get('auto_get_otp', True):
            print("[*] Waiting for OTP...")
            await asyncio.sleep(5)
            otp_extractor = EmailOTPExtractor()
            otp = await otp_extractor.get_otp_async(email_client, email)
        else:
            otp = input(f"Please Enter OTP for {email}: ")

        if not otp:
            print("[!] Failed to retrieve OTP")
            return None

        print(f"[✓] OTP received: {otp}")

        # submit_otp now returns form analysis
        session_id, form_analysis = await self.submit_otp(session_id, otp)
        if not session_id:
            print("[!] Failed to verify OTP")
            return None

        success, auth_code, user_uuid = await self.complete_registration(email, name, session_id, form_analysis)
        if not success:
            print("[!] Failed to complete registration")
            return None

        if self.config.get('promos', {}).get('auto_apply', False):
            promo_code = self.config['promos'].get('promo_code', '')
            if promo_code:
                await asyncio.sleep(2)  # Small delay before applying promo
                success = await self._apply_promo_code(auth_code, user_uuid, promo_code)
                if success:
                    print("[✓] Promo code applied successfully!")
                else:
                    print("[!] Failed to apply promo code")
            else:
                print("[!] Promo code not provided")

        print("[✓] Account created successfully!")
        self._save_account(email, name)
        return email

    def _save_account(self, email: str, name: str = ''):
        with open('accounts.txt', 'a') as f:
            f.write(f'{email} | {name}\n')