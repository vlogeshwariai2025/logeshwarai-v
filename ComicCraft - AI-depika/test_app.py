import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_endpoints():
    print("==================================================")
    print("Testing ComicCraft FastAPI Application Endpoints")
    print("==================================================")

    # 1. Test Health Check
    print("\n1. Testing GET /health...")
    res = client.get("/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("   [PASS] /health response:", res.json())

    # 2. Test Homepage GET /
    print("\n2. Testing GET / (Homepage)...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Create Your Comic" in res.text, "Homepage did not contain expected title"
    print("   [PASS] Homepage rendered successfully with comic form.")

    # 3. Test Direct Image Generation GET /test-image
    print("\n3. Testing GET /test-image...")
    res = client.get("/test-image?prompt=A+futuristic+cyberpunk+city+at+dusk")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.json()
    assert "path" in data, "Path missing from /test-image response"
    print("   [PASS] Image generated at:", data["path"])

    # 4. Test Full Comic Generation via JSON API POST /generate-comic/json
    print("\n4. Testing POST /generate-comic/json (Full Pipeline)...")
    payload = {
        "prompt": "A courageous fox exploring an ancient enchanted forest.",
        "character_name": "Free",
        "setting": "forest",
        "tone": "dramatic",
        "style": "anime"
    }
    res = client.post("/generate-comic/json", json=payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    json_data = res.json()
    assert json_data["status"] == "success", "Generation status not successful"
    assert len(json_data["layout"]) == 5, f"Expected 5 panels, got {len(json_data['layout'])}"
    assert os.path.exists(json_data["pdf_path"].lstrip("/\\")), f"PDF file does not exist: {json_data['pdf_path']}"
    print(f"   [PASS] 5-Panel comic created! Exported PDF: {json_data['pdf_path']}")

    # 5. Test PDF Download GET /download
    print("\n5. Testing GET /download for generated PDF...")
    pdf_path = json_data["pdf_path"]
    res = client.get(f"/download?path={pdf_path}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000, "Downloaded PDF is too small or empty"
    print(f"   [PASS] PDF downloaded successfully ({len(res.content)} bytes).")

    # 6. Test Form Submission POST /generate (HTML Preview response)
    print("\n6. Testing POST /generate (Form Submission)...")
    form_data = {
        "prompt": "A funny raccoon trying to bake pizza in a spaceship.",
        "character_name": "Bandit",
        "setting": "space",
        "tone": "funny",
        "style": "comic book"
    }
    res = client.post("/generate", data=form_data)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Your Comic Preview" in res.text, "Comic preview page not rendered"
    assert "Download Your Comic as PDF" in res.text, "PDF download button missing"
    print("   [PASS] Form submission generated preview page with panels & download CTA.")

    # 7. Test Export Success Page GET /export-success
    print("\n7. Testing GET /export-success...")
    res = client.get(f"/export-success?pdf_path={pdf_path}")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Comic Exported Successfully!" in res.text
    print("   [PASS] Export success page confirmed.")

    print("\n==================================================")
    print("ALL TESTS PASSED SUCCESSFULLY! (7/7)")
    print("==================================================")

if __name__ == "__main__":
    test_endpoints()
