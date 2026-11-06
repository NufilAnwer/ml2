from web.app import create_app

def test_health_route():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200

def test_home_page():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        response = client.get("/")
        assert response.status_code == 200
        assert b"AI-generated" in response.data
