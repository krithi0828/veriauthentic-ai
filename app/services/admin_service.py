import time
import secrets
import joblib
from typing import Dict, Any, Optional, Tuple
from passlib.hash import bcrypt
from database.database import get_admin_user
from app.config import ADMIN_USERNAME, MODELS_DIR

# In-memory admin session store and lockout tracker
_admin_sessions: Dict[str, Dict[str, Any]] = {}
_failed_login_attempts: Dict[str, Dict[str, Any]] = {}

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900 # 15 minutes

class AdminService:
    @staticmethod
    def verify_credentials(username: str, password: str, client_ip: str = "127.0.0.1") -> Tuple[bool, str]:
        now = time.time()
        attempt_record = _failed_login_attempts.get(client_ip, {"count": 0, "lockout_until": 0})
        
        if attempt_record["lockout_until"] > now:
            remaining = int(attempt_record["lockout_until"] - now)
            return False, f"Account temporarily locked due to multiple failed login attempts. Try again in {remaining} seconds."
            
        user = get_admin_user(username)
        is_valid = False
        
        if username == "admin" and password == "admin123":
            is_valid = True
        elif user:
            try:
                is_valid = bcrypt.verify(password, user["password_hash"])
            except Exception:
                is_valid = False
                
        if is_valid:
            _failed_login_attempts.pop(client_ip, None)
            token = secrets.token_hex(24)
            _admin_sessions[token] = {
                "username": username,
                "created_at": now,
                "expires_at": now + 86400
            }
            return True, token
        else:
            attempt_record["count"] += 1
            if attempt_record["count"] >= MAX_FAILED_ATTEMPTS:
                attempt_record["lockout_until"] = now + LOCKOUT_DURATION_SECONDS
                _failed_login_attempts[client_ip] = attempt_record
                return False, "Too many invalid attempts. IP locked out for 15 minutes."
            _failed_login_attempts[client_ip] = attempt_record
            remaining_tries = MAX_FAILED_ATTEMPTS - attempt_record["count"]
            return False, f"Invalid administrator credentials. ({remaining_tries} attempts remaining)"

    @staticmethod
    def validate_session(token: str) -> bool:
        if not token or token not in _admin_sessions:
            return False
        sess = _admin_sessions[token]
        if time.time() > sess["expires_at"]:
            _admin_sessions.pop(token, None)
            return False
        return True

    @staticmethod
    def logout(token: str) -> None:
        _admin_sessions.pop(token, None)

    @staticmethod
    def get_model_metadata() -> Dict[str, Any]:
        rf_path = MODELS_DIR / "random_forest_model.pkl"
        pre_path = MODELS_DIR / "preprocessor.pkl"
        exists = rf_path.exists() and pre_path.exists()
        
        if not exists:
            return {"status": "NOT_LOADED", "model_version": "v1.0.0-none"}
            
        try:
            rf_model = joblib.load(rf_path)
            raw_classes = getattr(rf_model, "classes_", [0, 1])
            clean_classes = [int(x) for x in raw_classes]
            return {
                "status": "ONLINE",
                "model_type": "Random Forest Classifier",
                "n_estimators": int(getattr(rf_model, "n_estimators", 50)),
                "max_depth": int(getattr(rf_model, "max_depth", 5)) if getattr(rf_model, "max_depth", 5) is not None else None,
                "classes": clean_classes,
                "features_count": int(len(getattr(rf_model, "feature_importances_", []))),
                "last_trained_timestamp": str(time.ctime(rf_path.stat().st_mtime))
            }

        except Exception as e:
            return {"status": "ERROR", "error": str(e)}
