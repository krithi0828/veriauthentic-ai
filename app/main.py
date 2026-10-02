import sys
from pathlib import Path

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import uuid
import io
import csv
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings, DATA_MODE, APP_DIR, OUTPUTS_DIR, BASE_DIR
from database.database import (
    init_db,
    get_analytics_summary,
    get_verification_history,
    get_all_reports
)
from app.services.verification_service import VerificationService
from app.services.registry_service import RegistryService
from app.services.report_service import ReportService
from app.services.admin_service import AdminService

# Initialize database schema
init_db()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_SUBLINE,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount Static Assets & Saved Outputs
app.mount("/assets", StaticFiles(directory=str(APP_DIR / "assets")), name="assets")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

# Setup Jinja2 Templates
templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

def get_session_id(request: Request) -> str:
    sid = request.cookies.get("session_id")
    if not sid:
        sid = str(uuid.uuid4())[:8]
    return sid

# Helper to render HTML with default context variables
def render(template_name: str, request: Request, context: dict = None, active_page: str = "", is_public_page: bool = False):
    ctx = {
        "request": request,
        "app_name": settings.APP_NAME,
        "app_tagline": settings.APP_TAGLINE,
        "app_subline": settings.APP_SUBLINE,
        "data_mode": settings.DATA_MODE,
        "active_page": active_page,
        "is_public_page": is_public_page,
        "session_id": get_session_id(request)
    }
    if context:
        ctx.update(context)
    response = templates.TemplateResponse(request, template_name, ctx)
    if not request.cookies.get("session_id"):
        response.set_cookie(key="session_id", value=ctx["session_id"], max_age=86400*30)
    return response



# ------------------------------------------------------------------
# PUBLIC MARKETING & HELP ROUTES
# ------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return render("index.html", request, is_public_page=True)

@app.get("/help", response_class=HTMLResponse)
async def help_page(request: Request):
    return render("help.html", request, active_page="help", is_public_page=True)

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page(request: Request):
    return render("privacy.html", request, is_public_page=True)

@app.get("/terms", response_class=HTMLResponse)
async def terms_page(request: Request):
    return render("terms.html", request, is_public_page=True)

@app.get("/styleguide", response_class=HTMLResponse)
async def styleguide_page(request: Request):
    return render("styleguide.html", request, active_page="styleguide")

# ------------------------------------------------------------------
# APP WORKSPACE ROUTES
# ------------------------------------------------------------------
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    summary = get_analytics_summary()
    history = get_verification_history(limit=5)
    return render("dashboard.html", request, {"summary": summary, "history": history}, active_page="dashboard")

@app.get("/verify", response_class=HTMLResponse)
async def verify_page(request: Request, mode: str = "a", sample: Optional[str] = None):
    sample_code = "AUTH-NIKE-7712" if sample else ""
    return render("verify.html", request, {"mode": mode, "sample_code": sample_code}, active_page="verify")

@app.get("/result/{result_id}", response_class=HTMLResponse)
async def result_view(request: Request, result_id: str):
    res = VerificationService.get_stored_result(result_id)
    if not res:
        raise HTTPException(status_code=404, detail="Verification result not found or session expired.")
    return render("result.html", request, {"result": res}, active_page="verify")

@app.get("/risk-analysis", response_class=HTMLResponse)
async def risk_analysis_page(request: Request):
    return render("risk_analysis.html", request, active_page="risk_analysis")

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    return render("compare.html", request, active_page="compare")

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    summary = get_analytics_summary()
    return render("analytics.html", request, {"summary": summary}, active_page="analytics")

@app.get("/model-card", response_class=HTMLResponse)
async def model_card_page(request: Request):
    return render("model_card.html", request, active_page="model_card")

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    sid = get_session_id(request)
    history = get_verification_history(session_id=sid, limit=50)
    return render("history.html", request, {"history": history, "session_id": sid}, active_page="history")

@app.get("/report", response_class=HTMLResponse)
async def report_page(request: Request, code: str = "", name: str = ""):
    return render("report.html", request, {"prefill_code": code, "prefill_name": name}, active_page="report")

# ------------------------------------------------------------------
# ADMIN CONSOLE ROUTES
# ------------------------------------------------------------------
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, search: str = ""):
    auth_token = request.cookies.get("admin_token")
    is_admin = AdminService.validate_session(auth_token)
    products = RegistryService.get_products(search=search) if is_admin else []
    return render("admin.html", request, {"is_admin": is_admin, "products": products, "search_query": search}, active_page="admin")

@app.post("/admin/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    client_ip = request.client.host if request.client else "127.0.0.1"
    success, token_or_msg = AdminService.verify_credentials(username, password, client_ip=client_ip)
    if success:
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie(key="admin_token", value=token_or_msg, httponly=True)
        return response
    else:
        return render("admin.html", request, {"is_admin": False, "login_error": token_or_msg}, active_page="admin")

@app.get("/admin/logout")
async def admin_logout(request: Request):
    token = request.cookies.get("admin_token")
    if token:
        AdminService.logout(token)
    response = RedirectResponse(url="/admin", status_code=303)
    response.delete_cookie("admin_token")
    return response

@app.get("/admin/generate-codes")
async def admin_generate_codes(request: Request):
    token = request.cookies.get("admin_token")
    if not AdminService.validate_session(token):
        return RedirectResponse(url="/admin", status_code=303)
    codes = RegistryService.generate_batch_auth_codes(count=10)
    for c in codes:
        RegistryService.create_product({
            "product_id": f"PRD-GEN-{uuid.uuid4().hex[:6]}",
            "product_name": "Generated Registry Item",
            "brand": "Generic Brand",
            "authentication_code": c,
            "reference_price": 150.0
        })
    return RedirectResponse(url="/admin", status_code=303)

@app.get("/admin/delete-product/{product_id}")
async def admin_delete_product(request: Request, product_id: str):
    token = request.cookies.get("admin_token")
    if AdminService.validate_session(token):
        RegistryService.delete_product(product_id)
    return RedirectResponse(url="/admin", status_code=303)

# ------------------------------------------------------------------
# REST API ENDPOINTS (/api/v1/)
# ------------------------------------------------------------------
@app.post("/api/v1/verify/code")
async def api_verify_code(request: Request, auth_code: str = Form(...)):
    sid = get_session_id(request)
    res = VerificationService.verify_code(auth_code, session_id=sid)
    return RedirectResponse(url=f"/result/{res['result_id']}", status_code=303)

@app.post("/api/v1/analyze/listing")
async def api_analyze_listing(
    request: Request,
    product_name: str = Form(...),
    brand: str = Form(...),
    reference_price: float = Form(...),
    listed_price: float = Form(...),
    seller_account_age_days: int = Form(180),
    seller_rating: float = Form(4.0),
    seller_verified: bool = Form(False),
    review_count: int = Form(20),
    average_rating: float = Form(4.0),
    product_description: str = Form(""),
    authentication_code: str = Form("")
):
    sid = get_session_id(request)
    input_data = {
        "product_name": product_name,
        "brand": brand,
        "reference_price": reference_price,
        "listed_price": listed_price,
        "seller_account_age_days": seller_account_age_days,
        "seller_rating": seller_rating,
        "seller_verified": seller_verified,
        "review_count": review_count,
        "average_rating": average_rating,
        "rating_variance": 0.5,
        "extreme_rating_ratio": 0.3,
        "one_star_pct": 5.0,
        "five_star_pct": 70.0,
        "product_description": product_description,
        "authentication_code": authentication_code
    }
    res = VerificationService.analyze_listing(input_data, session_id=sid)
    return RedirectResponse(url=f"/result/{res['result_id']}", status_code=303)

@app.post("/api/v1/verify/combined")
async def api_verify_combined(
    request: Request,
    auth_code: str = Form(...),
    product_name: str = Form(...),
    brand: str = Form(...),
    reference_price: float = Form(...),
    listed_price: float = Form(...),
    product_description: str = Form("")
):
    sid = get_session_id(request)
    input_data = {
        "product_name": product_name,
        "brand": brand,
        "reference_price": reference_price,
        "listed_price": listed_price,
        "seller_account_age_days": 300,
        "seller_rating": 4.5,
        "seller_verified": True,
        "review_count": 100,
        "average_rating": 4.5,
        "product_description": product_description,
        "authentication_code": auth_code
    }
    res = VerificationService.verify_combined(auth_code, input_data, session_id=sid)
    return RedirectResponse(url=f"/result/{res['result_id']}", status_code=303)

@app.post("/api/v1/compare", response_class=HTMLResponse)
async def api_compare(
    request: Request,
    name_a: str = Form(...), list_price_a: float = Form(...), ref_price_a: float = Form(...), seller_age_a: int = Form(...), code_a: str = Form(""),
    name_b: str = Form(...), list_price_b: float = Form(...), ref_price_b: float = Form(...), seller_age_b: int = Form(...), code_b: str = Form("")
):
    sid = get_session_id(request)
    listing_a = {"product_name": name_a, "listed_price": list_price_a, "reference_price": ref_price_a, "seller_account_age_days": seller_age_a, "authentication_code": code_a}
    listing_b = {"product_name": name_b, "listed_price": list_price_b, "reference_price": ref_price_b, "seller_account_age_days": seller_age_b, "authentication_code": code_b}
    
    comp_res = VerificationService.compare_listings(listing_a, listing_b, session_id=sid)
    return render("compare.html", request, {"comparison": comp_res}, active_page="compare")

@app.post("/api/v1/reports")
async def api_create_report(
    request: Request,
    product_name: str = Form(...),
    brand: str = Form(""),
    authentication_code: str = Form(""),
    seller_name: str = Form(""),
    purchase_location: str = Form(...),
    reporter_email: str = Form(...),
    reason: str = Form(...)
):
    rep_data = {
        "product_name": product_name,
        "brand": brand,
        "authentication_code": authentication_code,
        "seller_name": seller_name,
        "purchase_location": purchase_location,
        "reporter_email": reporter_email,
        "reporter_name": reporter_email.split("@")[0],
        "reason": reason,
        "risk_score": 85.0,
        "prediction": 1
    }
    rep_id = ReportService.create_report(rep_data)
    msg = f"✓ Counterfeit report submitted successfully! Reference ID: REP-{rep_id:04d}."
    return render("report.html", request, {"success_msg": msg}, active_page="report")

@app.get("/api/v1/history/export")
async def api_export_history(request: Request):
    sid = get_session_id(request)
    history = get_verification_history(session_id=sid, limit=500)
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Product Name", "Auth Code", "Verification Type", "Prediction", "Risk Score"])
    for h in history:
        writer.writerow([h["created_at"], h["product_name"], h["authentication_code"], h["verification_type"], h["prediction"], h["risk_score"]])
        
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=veri_history_{sid}.csv"}
    )

@app.get("/api/v1/health")
async def api_health():
    model_info = AdminService.get_model_metadata()
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "data_mode": settings.DATA_MODE,
        "model_status": model_info
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8085))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

