"""Encryption methods for NetEase Cloud Music API.
Ported from the Rust implementation.
"""

import base64
import json
import random
import hashlib
from typing import Dict, Any, Union
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# Constants from the Rust implementation
LINUX_API_KEY = "rFgB&h#%2?^eDg:Q"
EAPIKEY = "e82ckenh8dichen8"
WEAPI_KEY = "0CoJUm6Qyw8W8jud"
IV = "0102030405060708"
RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDgtQn2JZ34ZC28NWYpAUd98iZ3
7BUrX/aKzmFbt7clFSs6sXqHauqKWqdtLkF2KexO40H1YTX8z2lSgBBOAxLsvaklV8k4
cBFK9snQXE9/DDaFt6Rr7iVZMldczhC0JNgTz+SHXT6CBHuX3e9SdB1Ua44oncaTWz7O
BGLbCiK45wIDAQAB
-----END PUBLIC KEY-----"""

def create_key(size: int) -> str:
    """Create a random key string."""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join(random.choice(chars) for _ in range(size))

class Crypto:
    """Encryption methods for different API endpoints."""
    
    @staticmethod
    def _aes_encrypt(text: str, key: str) -> str:
        """AES encryption helper."""
        cipher = AES.new(key.encode(), AES.MODE_CBC, IV.encode())
        encrypted = cipher.encrypt(pad(text.encode(), 16))
        return base64.b64encode(encrypted).decode()

    @staticmethod
    def weapi(params: Dict[str, Any]) -> Dict[str, str]:
        """WeAPI encryption method."""
        text = json.dumps(params)
        secKey = create_key(16)
        
        # First encryption
        encText = Crypto._aes_encrypt(text, WEAPI_KEY)
        # Second encryption
        encText = Crypto._aes_encrypt(encText, secKey)
        
        # RSA encryption for key
        secKey = secKey[::-1].encode()  # Reverse and encode key
        rsa_key = RSA.import_key(RSA_PUBLIC_KEY)
        cipher = PKCS1_v1_5.new(rsa_key)
        secKey = base64.b64encode(cipher.encrypt(secKey)).decode('utf-8')
        
        return {
            'params': encText,
            'encSecKey': secKey
        }

    @staticmethod
    def linux_api(text: Union[Dict[str, Any], str]) -> Dict[str, str]:
        """Linux API encryption method."""
        if isinstance(text, dict):
            text = json.dumps(text)
            
        data = {
            "eparams": Crypto._aes_encrypt(text, LINUX_API_KEY)
        }
        return data

    @staticmethod
    def eapi(input_data: Dict[str, Any]) -> Dict[str, str]:
        """E API encryption method."""
        url = input_data.get('url', '')
        text = json.dumps(input_data.get('params', {}))
        
        message = f"nobody{url}use{text}md5forencrypt"
        digest = hashlib.md5(message.encode()).hexdigest()
        text_to_encrypt = f"{url}-36cd479b6b5-{text}-36cd479b6b5-{digest}"
        
        return {
            "params": Crypto._aes_encrypt(text_to_encrypt, EAPIKEY)
        }
