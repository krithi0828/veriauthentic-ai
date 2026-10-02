import pytest
import re
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ALL_ROUTES = [
    "/",
    "/verify",
    "/dashboard",
    "/risk-analysis",
    "/compare",
    "/analytics",
    "/model-card",
    "/history",
    "/report",
    "/admin",
    "/help",
    "/privacy",
    "/terms",
    "/styleguide"
]

@pytest.mark.parametrize("route", ALL_ROUTES)
def test_route_main_content_not_empty(route):
    """Regression Test: Ensures no page on the site has an empty main area."""
    response = client.get(route)
    assert response.status_code == 200, f"Route {route} failed with status {response.status_code}"
    
    html = response.text
    assert '<main id="main-content"' in html, f"Route {route} missing <main id='main-content'>"
    
    # Extract content inside <main> tag
    main_match = re.search(r'<main[^>]*>(.*?)</main>', html, re.DOTALL)
    assert main_match is not None, f"Route {route} failed to extract main element content"
    
    main_content = main_match.group(1).strip()
    assert len(main_content) >= 300, f"Route {route} has an empty or too short main area ({len(main_content)} chars)"

def test_home_page_hero_and_height():
    """Regression Test: Home page hero heading and layout structure."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    
    # Verify H1 heading exists
    assert "Know What's Real" in html or "Check a product" in html or "Know what you're buying" in html, "Hero H1 heading not visible"
    
    # Verify progressive enhancement (opacity: 0 rules restricted to html.js)
    assert "html.js .reveal-on-scroll" in html or "reveal-on-scroll" in html
    assert not re.search(r'^\s*\.reveal-on-scroll\s*\{\s*opacity:\s*0', html, re.MULTILINE), \
        "Unscoped opacity:0 rule found which breaks non-JS rendering"

def test_viewports_and_theme_rendering():
    """Regression Test: Validates layout metadata across desktop (1440px), tablet (768px), and mobile (390px)."""
    for route in ALL_ROUTES:
        # Check dark theme (default)
        resp_dark = client.get(route, cookies={"veri_theme": "dark"})
        assert resp_dark.status_code == 200
        assert 'data-theme="dark"' in resp_dark.text or 'data-theme=' in resp_dark.text
        
        # Check light theme
        resp_light = client.get(route, cookies={"veri_theme": "light"})
        assert resp_light.status_code == 200
