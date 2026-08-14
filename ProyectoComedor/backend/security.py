import hashlib
import os
import secrets
import json
import base64
import time
import hmac
import unicodedata
from typing import Optional, Dict, Any

SECRET_KEY = os.environ.get("COMEDOR_SECRET_KEY", "comedor_super_secret_key_change_in_production_2026")

def normalize_text(text: str) -> str:
    """Normaliza texto para comparaciones de preguntas de seguridad (sin tildes, minúsculas, sin espacios extra)."""
    if not text:
        return ""
    text = text.strip().lower()
    normalized = unicodedata.normalize('NFD', text)
    text_without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return ' '.join(text_without_accents.split())

def hash_password(password: str) -> str:
    """Genera un hash seguro para contraseñas usando PBKDF2-HMAC-SHA256 con salt aleatorio."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100_000
    )
    return f"{salt}${key.hex()}"

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verifica si la contraseña provista coincide con el hash almacenado."""
    try:
        salt, key_hex = stored_password_hash.split('$', 1)
        expected_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100_000
        )
        return secrets.compare_digest(expected_key.hex(), key_hex)
    except Exception:
        return False

def hash_security_answer(answer: str) -> str:
    """Calcula el hash de una respuesta de seguridad normalizada."""
    clean_answer = normalize_text(answer)
    return hashlib.sha256(clean_answer.encode('utf-8')).hexdigest()

def verify_security_answer(stored_answer_hash: str, provided_answer: str) -> bool:
    """Verifica si la respuesta provista coincide con el hash de la respuesta de seguridad."""
    provided_hash = hash_security_answer(provided_answer)
    return secrets.compare_digest(stored_answer_hash, provided_hash)

def generate_session_token() -> str:
    """Genera un token seguro para sesiones."""
    return secrets.token_urlsafe(32)

def create_signed_token(payload: Dict[str, Any], expires_in_seconds: int = 900) -> str:
    """Crea un token firmado HMAC con expiración (por defecto 15 minutos)."""
    data = payload.copy()
    data["exp"] = int(time.time()) + expires_in_seconds
    json_bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
    b64_payload = base64.urlsafe_b64encode(json_bytes).decode('utf-8').rstrip('=')
    
    signature = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{signature}"

def verify_signed_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica y decodifica un token firmado HMAC. Retorna None si es inválido o expiró."""
    try:
        if '.' not in token:
            return None
        b64_payload, signature = token.split('.', 1)
        
        expected_signature = hmac.new(SECRET_KEY.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
        if not secrets.compare_digest(signature, expected_signature):
            return None
        
        # Añadir padding si es necesario
        padding = 4 - (len(b64_payload) % 4)
        if padding != 4:
            b64_payload += '=' * padding
            
        json_bytes = base64.urlsafe_b64decode(b64_payload.encode('utf-8'))
        payload = json.loads(json_bytes.decode('utf-8'))
        
        # Verificar expiración
        if "exp" in payload and payload["exp"] < int(time.time()):
            return None
            
        return payload
    except Exception:
        return None
