import os
import hmac
import hashlib
import base64
import json
import time
from typing import Optional, Dict, Any

from app.core.config import settings

def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a unique salt."""
    if not salt:
        salt = os.urandom(16).hex()
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    )
    return f"{salt}:{key.hex()}"

def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verify stored PBKDF2 hash against plain password."""
    try:
        salt, key_hex = stored_hash.split(":")
        computed = hashlib.pbkdf2_hmac(
            'sha256',
            plain_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return hmac.compare_digest(computed.hex(), key_hex)
    except Exception:
        return False

def create_access_token(data: Dict[str, Any], expires_delta_minutes: Optional[int] = None) -> str:
    """Create a URL-safe signed JWT-like token (HMAC-SHA256)."""
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    expire = now + (expires_delta_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60
    
    payload = data.copy()
    payload.update({"iat": now, "exp": expire})
    
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()
    
    signing_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
    encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()
    
    return f"{encoded_header}.{encoded_payload}.{encoded_signature}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify HMAC-SHA256 signed token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        encoded_header, encoded_payload, encoded_signature = parts
        
        # Verify signature
        signing_input = f"{encoded_header}.{encoded_payload}".encode()
        expected_sig = hmac.new(settings.SECRET_KEY.encode(), signing_input, hashlib.sha256).digest()
        
        # Pad base64 if needed
        sig_padding = '=' * (4 - (len(encoded_signature) % 4)) if len(encoded_signature) % 4 else ''
        actual_sig = base64.urlsafe_b64decode(encoded_signature + sig_padding)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        
        # Decode payload
        payload_padding = '=' * (4 - (len(encoded_payload) % 4)) if len(encoded_payload) % 4 else ''
        payload_json = base64.urlsafe_b64decode(encoded_payload + payload_padding).decode()
        payload = json.loads(payload_json)
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None
