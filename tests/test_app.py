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

@pytest.mark.parametrize(
    "method, endpoint",
    [
        ("POST", "/items"),
        ("PATCH", "/items/1"),
        ("POST", "/items/import"),
    ],
)
def test_routes_reject_non_object_json(client, method, endpoint):

    response = client.open(
        endpoint,
        method=method,
        json=["invalid", "payload"],
    )

    assert response.status_code == 400
    assert response.json["error"] == "A JSON object is required."


def test_patch_missing_item(client):

    response = client.patch(
        "/items/999",
        json={"quantity": 20},
    )

    assert response.status_code == 404
    assert response.json["error"] == "Item not found."

def test_search_rejects_multiple_parameters(client):

    response = client.get(
        "/search?barcode=123456789&name=milk"
    )

    assert response.status_code == 400
    assert "exactly one" in response.json["error"]


def test_search_by_barcode_success(client, monkeypatch):

    # Simulate a successful response from OpenFoodFacts.
    def fake_search(barcode):
        return {
            "name": "Fresh Milk",
            "barcode": barcode,
        }

    monkeypatch.setattr(
        "app.search_by_barcode",
        fake_search,
    )

    response = client.get(
        "/search?barcode=123456789"
    )

    assert response.status_code == 200
    assert response.json["name"] == "Fresh Milk"
    assert response.json["barcode"] == "123456789"


def test_search_by_barcode_not_found(client, monkeypatch):

    # Simulate an external product that does not exist.
    monkeypatch.setattr(
        "app.search_by_barcode",
        lambda barcode: None,
    )

    response = client.get(
        "/search?barcode=999999999"
    )

    assert response.status_code == 404
    assert response.json["error"] == "Product not found."


def test_search_by_name_success(client, monkeypatch):

    # Simulate multiple products returned by the API.
    fake_products = [
        {"name": "Fresh Milk"},
        {"name": "Long Life Milk"},
    ]

    monkeypatch.setattr(
        "app.search_by_name",
        lambda name: fake_products,
    )

    response = client.get(
        "/search?name=milk"
    )

    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]["name"] == "Fresh Milk"


@pytest.mark.parametrize(
    "error_type, expected_status",
    [
        (ValueError, 400),
        (RuntimeError, 502),
    ],
)
def test_search_by_barcode_errors(
    client,
    monkeypatch,
    error_type,
    expected_status,
):

    # Simulate either an input validation error
    # or an unavailable external service.
    def fake_search(barcode):
        raise error_type("External lookup failed")

    monkeypatch.setattr(
        "app.search_by_barcode",
        fake_search,
    )

    response = client.get(
        "/search?barcode=123456789"
    )

    assert response.status_code == expected_status
    assert response.json["error"] == "External lookup failed"


@pytest.mark.parametrize(
    "error_type, expected_status",
    [
        (ValueError, 400),
        (RuntimeError, 502),
    ],
)
def test_search_by_name_errors(
    client,
    monkeypatch,
    error_type,
    expected_status,
):

    def fake_search(name):
        raise error_type("External lookup failed")

    monkeypatch.setattr(
        "app.search_by_name",
        fake_search,
    )

    response = client.get(
        "/search?name=milk"
    )

    assert response.status_code == expected_status
    assert response.json["error"] == "External lookup failed"

@pytest.mark.parametrize(
    "barcode",
    [
        "",
        "   ",
        123456789,
        None,
    ],
)
def test_import_invalid_barcode(client, barcode):

    response = client.post(
        "/items/import",
        json={"barcode": barcode},
    )

    assert response.status_code == 400
    assert (
        response.json["error"]
        == "A valid product barcode is required."
    )


def test_import_product_not_found(client, monkeypatch):

    # Simulate an unknown barcode.
    monkeypatch.setattr(
        "app.search_by_barcode",
        lambda barcode: None,
    )

    response = client.post(
        "/items/import",
        json={"barcode": "999999999"},
    )

    assert response.status_code == 404
    assert response.json["error"] == "External product not found."


@pytest.mark.parametrize(
    "error_type, expected_status",
    [
        (ValueError, 400),
        (RuntimeError, 502),
    ],
)
def test_import_external_api_errors(
    client,
    monkeypatch,
    error_type,
    expected_status,
):

    def fake_search(barcode):
        raise error_type("Product lookup failed")

    monkeypatch.setattr(
        "app.search_by_barcode",
        fake_search,
    )

    response = client.post(
        "/items/import",
        json={"barcode": "123456789"},
    )

    assert response.status_code == expected_status
    assert response.json["error"] == "Product lookup failed"


def test_import_invalid_inventory_data(client, monkeypatch):

    # Simulate successful external product lookup.
    monkeypatch.setattr(
        "app.search_by_barcode",
        lambda barcode: {
            "name": "Imported Milk",
            "barcode": barcode,
        },
    )

    # Simulate inventory validation rejecting the item.
    def fake_create_item(data):
        raise ValueError("Invalid inventory data")

    monkeypatch.setattr(
        "app.create_item",
        fake_create_item,
    )

    response = client.post(
        "/items/import",
        json={
            "barcode": "123456789",
            "price": -100,
        },
    )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid inventory data"


def test_import_product_success(client, monkeypatch):

    # Simulate the external product information.
    def fake_search(barcode):
        return {
            "name": "Imported Milk",
            "barcode": barcode,
            "price": 100,
        }

    monkeypatch.setattr(
        "app.search_by_barcode",
        fake_search,
    )

    # Simulate a successful inventory insertion.
    # This isolates the Flask route from inventory storage.
    def fake_create_item(data):
        return {
            "id": 1,
            **data,
        }

    monkeypatch.setattr(
        "app.create_item",
        fake_create_item,
    )

    response = client.post(
        "/items/import",
        json={
            "barcode": "123456789",
            "price": 150,
            "quantity": 10,
        },
    )

    assert response.status_code == 201

    assert response.json["id"] == 1
    assert response.json["name"] == "Imported Milk"
    assert response.json["price"] == 150
    assert response.json["quantity"] == 10