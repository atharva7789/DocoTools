from app import create_app

def test_home():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200

def test_merge_page():
    app = create_app()
    client = app.test_client()
    response = client.get("/tool/merge")
    assert response.status_code == 200
    assert b"Merge PDF" in response.data
