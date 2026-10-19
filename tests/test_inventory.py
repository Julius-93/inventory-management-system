import pytest

from inventory import (
    create_item,
    delete_item,
    get_all_items,
    get_item,
    reset_inventory,
    update_item,
)


@pytest.fixture(autouse=True)
def clean_inventory():
    reset_inventory()


def sample_item():
    return {
        "name": "Milk",
        "price": 120.0,
        "quantity": 10,
        "barcode": "123456789",
        "category": "Dairy",
        "description": "Fresh milk",
    }


def test_inventory_starts_empty():
    assert get_all_items() == []


def test_create_item_success():
    item = create_item(sample_item())

    assert item["id"] == 1
    assert item["name"] == "Milk"
    assert item["price"] == 120.0
    assert item["quantity"] == 10


def test_create_item_assigns_incrementing_ids():
    first = create_item(sample_item())
    second = create_item({
        **sample_item(),
        "name": "Bread",
    })

    assert first["id"] == 1
    assert second["id"] == 2


@pytest.mark.parametrize(
    "data",
    [
        {"name": "", "price": 10, "quantity": 1},
        {"name": "   ", "price": 10, "quantity": 1},
        {"name": "Milk", "price": -1, "quantity": 1},
        {"name": "Milk", "price": "invalid", "quantity": 1},
        {"name": "Milk", "price": 10, "quantity": -1},
        {"name": "Milk", "price": 10, "quantity": 1.5},
    ],
)
def test_create_item_rejects_invalid_data(data):
    with pytest.raises(ValueError):
        create_item(data)

    assert get_all_items() == []


def test_get_item_returns_existing_item():
    created = create_item(sample_item())

    assert get_item(created["id"]) == created


def test_get_item_returns_none_for_missing_item():
    assert get_item(999) is None


def test_update_item_success():
    created = create_item(sample_item())

    updated = update_item(
        created["id"],
        {"name": "Whole Milk", "quantity": 15},
    )

    assert updated["name"] == "Whole Milk"
    assert updated["quantity"] == 15
    assert updated["price"] == 120.0


def test_update_missing_item_returns_none():
    assert update_item(999, {"name": "Bread"}) is None


@pytest.mark.parametrize(
    "updates",
    [
        {"name": ""},
        {"price": -10},
        {"price": "invalid"},
        {"quantity": -1},
        {"quantity": 1.5},
        {"unknown_field": "value"},
    ],
)
def test_update_item_rejects_invalid_data(updates):
    created = create_item(sample_item())
    original = created.copy()

    with pytest.raises(ValueError):
        update_item(created["id"], updates)

    assert get_item(created["id"]) == original


def test_delete_item_success():
    created = create_item(sample_item())

    assert delete_item(created["id"]) is True
    assert get_item(created["id"]) is None
    assert get_all_items() == []


def test_delete_missing_item_returns_false():
    assert delete_item(999) is False


def test_reset_inventory_clears_items_and_resets_ids():
    create_item(sample_item())

    reset_inventory()

    assert get_all_items() == []

    created = create_item(sample_item())
    assert created["id"] == 1
