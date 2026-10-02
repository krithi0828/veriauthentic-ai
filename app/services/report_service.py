from typing import List, Dict, Any, Optional
from database.database import add_report, get_all_reports, update_report_status

class ReportService:
    @staticmethod
    def create_report(data: Dict[str, Any]) -> int:
        return add_report(data)

    @staticmethod
    def get_reports(status_filter: Optional[str] = None, search: str = "") -> List[Dict[str, Any]]:
        return get_all_reports(status_filter=status_filter, search=search)

    @staticmethod
    def update_status(report_id: int, status: str) -> bool:
        valid_statuses = {"PENDING", "UNDER_REVIEW", "VERIFIED_COUNTERFEIT", "DISMISSED"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}")
        return update_report_status(report_id, status)
