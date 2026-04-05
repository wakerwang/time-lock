import json
import os
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets

DATA_FILE = os.environ.get("DATA_FILE", os.path.join(os.path.dirname(__file__), "messages.json"))


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def _load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_data(data: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def encrypt_message(content: str, unlock_date: str, password: str) -> dict:
    """
    加密消息并存储。
    unlock_date 格式: YYYYMMDD
    返回: {"id": str, "unlock_date": str, "created_at": str}
    """
    salt = secrets.token_bytes(16)
    key = _derive_key(password, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(content.encode("utf-8"))

    message_id = secrets.token_hex(8)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = _load_data()
    data[message_id] = {
        "content": base64.b64encode(encrypted).decode("utf-8"),
        "salt": base64.b64encode(salt).decode("utf-8"),
        "unlock_date": unlock_date,
        "created_at": created_at,
    }
    _save_data(data)

    return {
        "id": message_id,
        "unlock_date": unlock_date,
        "created_at": created_at,
    }


def decrypt_message(message_id: str, password: str) -> dict:
    """
    尝试解密消息。
    如果未到解锁日期，返回 {"status": "locked", "remaining": str}
    如果已解锁，返回 {"status": "unlocked", "content": str}
    如果不存在或密码错误，返回 {"status": "error", "message": str}
    """
    data = _load_data()

    if message_id not in data:
        return {"status": "error", "message": "消息不存在"}

    msg = data[message_id]
    unlock_date = datetime.strptime(msg["unlock_date"], "%Y%m%d")
    now = datetime.now()

    if now < unlock_date:
        delta = unlock_date - now
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        remaining = f"{days}天 {hours}小时 {minutes}分钟"
        return {"status": "locked", "remaining": remaining, "unlock_date": msg["unlock_date"]}

    try:
        salt = base64.b64decode(msg["salt"])
        key = _derive_key(password, salt)
        fernet = Fernet(key)
        encrypted = base64.b64decode(msg["content"])
        decrypted = fernet.decrypt(encrypted).decode("utf-8")
        return {"status": "unlocked", "content": decrypted, "created_at": msg["created_at"]}
    except Exception:
        return {"status": "error", "message": "密码错误"}


def list_messages() -> list:
    """列出所有消息（不显示内容）"""
    data = _load_data()
    result = []
    now = datetime.now()
    for msg_id, msg in data.items():
        unlock_date = datetime.strptime(msg["unlock_date"], "%Y%m%d")
        is_unlocked = now >= unlock_date
        result.append({
            "id": msg_id,
            "unlock_date": msg["unlock_date"],
            "created_at": msg["created_at"],
            "is_unlocked": is_unlocked,
        })
    return result
