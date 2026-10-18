from flask import Flask, jsonify, request

from inventory import (
    create_item,
    delete_item,
    get_all_items,
    get_item,
    update_item
)

from external_api import (
    search_by_barcode,
    search_by_name
)


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Inventory Management API",
        "endpoints": {
            "items": "/items",
            "search": "/search",
            "import": "/items/import"
        }
    }), 200


@app.route("/items", methods=["GET"])
def list_items():
    return jsonify(get_all_items()), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def retrieve_item(item_id):
    item = get_item(item_id)

    if item is None:
        return jsonify({"error": "Item not found."}), 404

    return jsonify(item), 200


@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    try:
        item = create_item(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(item), 201


@app.route("/items/<int:item_id>", methods=["PATCH"])
def modify_item(item_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    try:
        item = update_item(item_id, data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    if item is None:
        return jsonify({"error": "Item not found."}), 404

    return jsonify(item), 200


@app.route("/items/<int:item_id>", methods=["DELETE"])
def remove_item(item_id):
    if not delete_item(item_id):
        return jsonify({"error": "Item not found."}), 404

    return jsonify({
        "message": "Item deleted successfully."
    }), 200


@app.route("/search", methods=["GET"])
def search_products():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if bool(barcode) == bool(name):
        return jsonify({
            "error": "Provide exactly one of barcode or name."
        }), 400

    try:
        if barcode:
            product = search_by_barcode(barcode)

            if product is None:
                return jsonify({
                    "error": "Product not found."
                }), 404

            return jsonify(product), 200

        products = search_by_name(name)

        return jsonify(products), 200

    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502


@app.route("/items/import", methods=["POST"])
def import_product():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    barcode = data.get("barcode")

    if not isinstance(barcode, str) or not barcode.strip():
        return jsonify({
            "error": "A valid product barcode is required."
        }), 400

    try:
        product = search_by_barcode(barcode)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 502

    if product is None:
        return jsonify({
            "error": "External product not found."
        }), 404

    # Employee-supplied fields take precedence over external data.
    item_data = {
        **product,
        "price": data.get("price"),
        "quantity": data.get("quantity", 0)
    }

    try:
        item = create_item(item_data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(item), 201


if __name__ == "__main__":
    app.run(debug=True)