from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductModel:
    product_id: str
    product_name: str
    brand: str
    product_category: str
    authentication_code: str
    batch_number: Optional[str] = "BATCH-001"
    manufacturing_date: Optional[str] = "2024-01-01"
    origin_country: Optional[str] = "USA"
    reference_price: float = 0.0
    is_registered: bool = True
    id: Optional[int] = None

@dataclass
class ReportModel:
    product_name: str
    brand: str
    authentication_code: str
    seller_name: str
    purchase_location: str
    reason: str
    reporter_name: str
    reporter_email: str
    risk_score: float
    prediction: int
    status: str = "PENDING"
    id: Optional[int] = None

@dataclass
class VerificationHistoryModel:
    session_id: str
    product_name: str
    authentication_code: str
    prediction: int
    risk_score: float
    verification_type: str
    id: Optional[int] = None
