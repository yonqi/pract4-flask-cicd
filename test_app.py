from app import create_app


def test_health():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_index():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == "Flask CI/CD application"


def test_environment():
    app = create_app()
    client = app.test_client()

    response = client.get("/env")

    assert response.status_code == 200
    assert "environment" in response.json
