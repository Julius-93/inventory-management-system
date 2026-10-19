import pytest

from app import app
from inventory import reset_inventory


@pytest.fixture
def client():
    reset_inventory()

    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client

    reset_inventory()


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["message"] == "Inventory Management API"


def test_list_empty_inventory(client):
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json == []


def test_create_item(client):
    response = client.post(
        "/items",
        json={
            "name": "Milk",
            "price": 120,
            "quantity": 10
        }
    )

    assert response.status_code == 201
    assert response.json["name"] == "Milk"
    assert response.json["quantity"] == 10


def test_create_item_without_name(client):
    response = client.post(
        "/items",
        json={
            "price": 100,
            "quantity": 5
        }
    )

    assert response.status_code == 400


def test_retrieve_item(client):
    created = client.post(
        "/items",
        json={
            "name": "Bread",
            "price": 70,
            "quantity": 15
        }
    )

    item_id = created.json["id"]

    response = client.get(f"/items/{item_id}")

    assert response.status_code == 200
    assert response.json["name"] == "Bread"


def test_retrieve_missing_item(client):
    response = client.get("/items/999")

    assert response.status_code == 404


def test_patch_item(client):
    created = client.post(
        "/items",
        json={
            "name": "Rice",
            "price": 200,
            "quantity": 20
        }
    )

    item_id = created.json["id"]

    response = client.patch(
        f"/items/{item_id}",
        json={"quantity": 30}
    )

    assert response.status_code == 200
    assert response.json["quantity"] == 30
    assert response.json["name"] == "Rice"


def test_patch_invalid_price(client):
    created = client.post(
        "/items",
        json={
            "name": "Sugar",
            "price": 150,
            "quantity": 10
        }
    )

    item_id = created.json["id"]

    response = client.patch(
        f"/items/{item_id}",
        json={"price": -10}
    )

    assert response.status_code == 400


def test_delete_item(client):
    created = client.post(
        "/items",
        json={
            "name": "Tea",
            "price": 100,
            "quantity": 8
        }
    )

    item_id = created.json["id"]

    response = client.delete(f"/items/{item_id}")

    assert response.status_code == 200

    missing = client.get(f"/items/{item_id}")

    assert missing.status_code == 404


def test_delete_missing_item(client):
    response = client.delete("/items/999")

    assert response.status_code == 404


def test_search_requires_exactly_one_parameter(client):
    response = client.get("/search")

    assert response.status_code == 400