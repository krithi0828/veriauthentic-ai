import uuid
from typing import Dict, Any, Optional
from database.database import (
    get_product_by_auth_code,
    log_verification_event,
    check_code_reuse_alert,
    add_verification_history,
    get_verification_history
)
from ml.predict import predict_authenticity
from ml.explain import explain_prediction

# In-memory store for session-scoped shareable results
_results_cache: Dict[str, Dict[str, Any]] = {}

class VerificationService:
    @staticmethod
    def verify_code(auth_code: str, session_id: str = "default") -> Dict[str, Any]:
        auth_code_clean = auth_code.strip().upper()
        log_verification_event(auth_code_clean, session_id)
        
        prod = get_product_by_auth_code(auth_code_clean)
        reuse_info = check_code_reuse_alert(auth_code_clean, session_id)
        
        registered = prod is not None
        result_id = str(uuid.uuid4())[:12]
        
        result_data = {
            "result_id": result_id,
            "verification_type": "CODE_LOOKUP",
            "auth_code": auth_code_clean,
            "registered": registered,
            "product_details": prod,
            "code_reuse_info": reuse_info,
            "risk_score": 0.0 if registered else 100.0,
            "prediction": 0 if registered else 1,
            "prediction_label": "Genuine Registered Product" if registered else "Unregistered Product Code",
            "disclaimer": "This is an AI-based risk assessment, not proof of authenticity. Confirm with the manufacturer."
        }
        
        add_verification_history(
            session_id,
            prod["product_name"] if prod else "Unregistered Item",
            auth_code_clean,
            0 if registered else 1,
            0.0 if registered else 100.0,
            "CODE_LOOKUP"
        )
        _results_cache[result_id] = result_data
        return result_data

    @staticmethod
    def analyze_listing(listing_data: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
        res = predict_authenticity(listing_data, db_check_func=get_product_by_auth_code)
        explanation = explain_prediction(res)
        
        result_id = str(uuid.uuid4())[:12]
        auth_code = str(listing_data.get("authentication_code", "")).strip().upper()
        
        if auth_code:
            log_verification_event(auth_code, session_id)
            reuse_info = check_code_reuse_alert(auth_code, session_id)
        else:
            reuse_info = {"total_verifications": 1, "distinct_sessions": 1, "reuse_alert": False}
            
        full_result = {
            "result_id": result_id,
            "verification_type": "AI_LISTING_ANALYSIS",
            "auth_code": auth_code,
            "prediction_data": res,
            "explanation_data": explanation,
            "code_reuse_info": reuse_info,
            "risk_score": res["risk_score"],
            "prediction": res["prediction"],
            "prediction_label": res["prediction_label"],
            "confidence_pct": res["confidence_pct"],
            "disclaimer": "This is an AI-based risk assessment, not proof of authenticity. Confirm with the manufacturer."
        }
        
        add_verification_history(
            session_id,
            listing_data.get("product_name", "Marketplace Listing"),
            auth_code,
            res["prediction"],
            res["risk_score"],
            "AI_LISTING_ANALYSIS"
        )
        _results_cache[result_id] = full_result
        return full_result

    @staticmethod
    def verify_combined(auth_code: str, listing_data: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
        auth_code_clean = auth_code.strip().upper()
        listing_data["authentication_code"] = auth_code_clean
        
        log_verification_event(auth_code_clean, session_id)
        prod = get_product_by_auth_code(auth_code_clean)
        reuse_info = check_code_reuse_alert(auth_code_clean, session_id)
        
        res = predict_authenticity(listing_data, db_check_func=get_product_by_auth_code)
        explanation = explain_prediction(res)
        
        result_id = str(uuid.uuid4())[:12]
        
        combined_result = {
            "result_id": result_id,
            "verification_type": "COMBINED_VERIFICATION",
            "auth_code": auth_code_clean,
            "registered": prod is not None,
            "product_details": prod,
            "code_reuse_info": reuse_info,
            "prediction_data": res,
            "explanation_data": explanation,
            "risk_score": res["risk_score"],
            "prediction": res["prediction"],
            "prediction_label": res["prediction_label"],
            "confidence_pct": res["confidence_pct"],
            "disclaimer": "This is an AI-based risk assessment, not proof of authenticity. Confirm with the manufacturer."
        }
        
        add_verification_history(
            session_id,
            listing_data.get("product_name", "Combined Verification Item"),
            auth_code_clean,
            res["prediction"],
            res["risk_score"],
            "COMBINED_VERIFICATION"
        )
        _results_cache[result_id] = combined_result
        return combined_result

    @staticmethod
    def compare_listings(listing_a: Dict[str, Any], listing_b: Dict[str, Any], session_id: str = "default") -> Dict[str, Any]:
        res_a = predict_authenticity(listing_a, db_check_func=get_product_by_auth_code)
        res_b = predict_authenticity(listing_b, db_check_func=get_product_by_auth_code)
        exp_a = explain_prediction(res_a)
        exp_b = explain_prediction(res_b)
        
        lower_risk = "A" if res_a["risk_score"] < res_b["risk_score"] else "B" if res_b["risk_score"] < res_a["risk_score"] else "EQUAL"
        
        return {
            "listing_a": {
                "input": listing_a,
                "result": res_a,
                "explanation": exp_a
            },
            "listing_b": {
                "input": listing_b,
                "result": res_b,
                "explanation": exp_b
            },
            "lower_risk_listing": lower_risk,
            "disclaimer": "This is an AI-based risk assessment, not proof of authenticity. Confirm with the manufacturer."
        }

    @staticmethod
    def get_stored_result(result_id: str) -> Optional[Dict[str, Any]]:
        return _results_cache.get(result_id)
