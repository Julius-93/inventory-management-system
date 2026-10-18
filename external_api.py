import requests


BASE_URL = "https://world.openfoodfacts.org"


def search_by_barcode(barcode):
    """Retrieve product details using a barcode."""
    if not barcode or not barcode.strip():
        raise ValueError("Barcode is required.")

    url = f"{BASE_URL}/api/v2/product/{barcode.strip()}.json"

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "InventoryManagementSystem/1.0"
            },
            timeout=10
        )
        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            "Unable to connect to OpenFoodFacts."
        ) from exc

    data = response.json()

    if data.get("status") != 1 or not data.get("product"):
        return None

    product = data["product"]

    return {
        "name": product.get("product_name", ""),
        "barcode": barcode.strip(),
        "category": product.get("categories", ""),
        "description": product.get("generic_name", ""),
        "image_url": product.get("image_front_url", "")
    }


def search_by_name(name):
    """Search for products using their names."""
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Product name is required.")

    try:
        response = requests.get(
            f"{BASE_URL}/api/v2/search",
            params={
                "search_terms": name.strip(),
                "page_size": 10,
                "fields": (
                    "code,product_name,categories,"
                    "generic_name,image_front_url"
                )
            },
            headers={
                "User-Agent": "InventoryManagementSystem/1.0"
            },
            timeout=10
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise RuntimeError(
            "Unable to connect to OpenFoodFacts."
        ) from exc

    data = response.json()

    return [
        {
            "name": product.get("product_name", ""),
            "barcode": product.get("code", ""),
            "category": product.get("categories", ""),
            "description": product.get("generic_name", ""),
            "image_url": product.get("image_front_url", "")
        }
        for product in data.get("products", [])
    ]