import time
import hashlib
import hmac
from core.config import config_manager


SECRET_KEY = config_manager.settings.app_secret_key
TOKEN_EXPIRATION_SECONDS = config_manager.settings.expired_second

def generate_token() -> str:
    timestamp = str(int(time.time()))
    data_to_hash = f"{timestamp}{SECRET_KEY}"
    token = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()[:32]
    return timestamp, token

def verify_token(timestamp_str: str, customize: str,  received_token: str) -> bool:
    """
    验证接收到的 Token 是否有效。
    
    Returns:
        True 如果 Token 有效，否则 False。
    """
    try:
        # 1. 检查时间戳是否在有效期内
        timestamp = int(timestamp_str)
        current_time = int(time.time())
        
        if abs(current_time - timestamp) > TOKEN_EXPIRATION_SECONDS:
            print(f"Token expired. Server time: {current_time}, Token time: {timestamp}")
            return False
            
        data_to_hash = f"{timestamp_str}{customize}{SECRET_KEY}"
        expected_token = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()[:32]
        
        return hmac.compare_digest(expected_token.encode('utf-8'), received_token.encode('utf-8'))

    except (ValueError, TypeError):
        return False
