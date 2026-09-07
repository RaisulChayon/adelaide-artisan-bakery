from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "Adelaide Artisan Bakery" in response.text


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_products_page():
    response = client.get("/products")

    assert response.status_code == 200
    assert "Products" in response.text


def test_missing_product():
    response = client.get("/products/999999/edit")

    assert response.status_code == 404


def test_invalid_product():
    response = client.post(
        "/products/new",
        data={
            "name": "",
            "category": "",
            "description": "",
            "price": "-5",
        },
    )

    assert response.status_code == 422
    assert "Product name is required." in response.text
    assert "Price cannot be negative." in response.text


def test_invalid_enquiry():
    response = client.post(
        "/enquiry",
        data={
            "name": "",
            "email": "wrong-email",
            "message": "Hi",
        },
    )

    assert response.status_code == 422
    assert "Name is required." in response.text
    assert "valid email" in response.text
    assert "at least 10 characters" in response.text