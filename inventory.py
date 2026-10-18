inventory = []

next_id = 1


def get_all_items():
    """Return all inventory items."""
    return inventory


def get_item(item_id):
    """Return an item by ID, or None if it does not exist."""
    return next(
        (item for item in inventory if item["id"] == item_id),
        None
    )


def create_item(data):
    """Validate and create an inventory item."""
    global next_id

    name = data.get("name")
    price = data.get("price")
    quantity = data.get("quantity", 0)

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Name is required.")

    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer.")

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    item = {
        "id": next_id,
        "name": name.strip(),
        "barcode": data.get("barcode", ""),
        "category": data.get("category", ""),
        "price": price,
        "quantity": quantity,
        "description": data.get("description", "")
    }

    inventory.append(item)
    next_id += 1

    return item


def update_item(item_id, updates):
    """Update only the supplied fields of an existing item."""
    item = get_item(item_id)

    if item is None:
        return None

    allowed_fields = {
        "name",
        "barcode",
        "category",
        "price",
        "quantity",
        "description"
    }

    unknown_fields = set(updates) - allowed_fields

    if unknown_fields:
        raise ValueError(
            f"Unknown fields: {', '.join(sorted(unknown_fields))}"
        )

    updated_data = {**item, **updates}

    # Validate the updated record before changing the original.
    name = updated_data.get("name")
    price = updated_data.get("price")
    quantity = updated_data.get("quantity")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Name must be a non-empty string.")

    if isinstance(price, bool) or not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")

    if price < 0:
        raise ValueError("Price cannot be negative.")

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        raise ValueError("Quantity must be an integer.")

    if quantity < 0:
        raise ValueError("Quantity cannot be negative.")

    item.update(updates)

    return item


def delete_item(item_id):
    """Delete an inventory item by ID."""
    item = get_item(item_id)

    if item is None:
        return False

    inventory.remove(item)

    return True


def reset_inventory():
    """Reset inventory state, primarily for automated tests."""
    global next_id

    inventory.clear()
    next_id = 1