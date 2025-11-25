import time
import requests

class SMSActivateAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.sms-activate.io/stubs/handler_api.php"
    
    def get_balance(self):
        params = {
            'api_key': self.api_key,
            'action': 'getBalance'
        }
        try:
            response = requests.get(self.base_url, params=params)
            return response.text
        except Exception as e:
            print(f"[!] SMS API Error: {e}")
            return None

    def get_number(self, service='ub', country='0'):
        """
        service 'ub' = Uber
        country '0' = Russia, '22' = India, etc. (Check SMS-Activate ID list)
        """
        params = {
            'api_key': self.api_key,
            'action': 'getNumber',
            'service': service,
            'country': country
        }
        try:
            response = requests.get(self.base_url, params=params)
            # Response format: ACCESS_NUMBER:$ID:$NUMBER
            text = response.text
            if "ACCESS_NUMBER" in text:
                parts = text.split(':')
                return {'id': parts[1], 'number': parts[2]}
            else:
                print(f"[!] Failed to get number: {text}")
                return None
        except Exception as e:
            print(f"[!] Request Error: {e}")
            return None

    def get_status(self, activation_id):
        params = {
            'api_key': self.api_key,
            'action': 'getStatus',
            'id': activation_id
        }
        try:
            response = requests.get(self.base_url, params=params)
            return response.text
        except Exception as e:
            return None

    def wait_for_code(self, activation_id, timeout=120):
        print(f"[*] Waiting for SMS code (ID: {activation_id})...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status(activation_id)
            if status and "STATUS_OK" in status:
                code = status.split(':')[1]
                return code
            elif status == "STATUS_CANCEL":
                return None
            time.sleep(3)
        
        # If timeout, cancel activation
        self.set_status(activation_id, 8) # 8 = Cancel
        return None

    def set_status(self, activation_id, status):
        """
        1 = Ready
        3 = Request another code
        6 = Complete
        8 = Cancel
        """
        params = {
            'api_key': self.api_key,
            'action': 'setStatus',
            'id': activation_id,
            'status': status
        }
        requests.get(self.base_url, params=params)