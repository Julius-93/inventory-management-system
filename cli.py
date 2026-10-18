import argparse
import json

import requests


BASE_URL = "http://127.0.0.1:5000"


def main():
    parser = argparse.ArgumentParser(
        description="Inventory Management CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # List inventory.
    subparsers.add_parser("list")

    # View one item.
    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("id", type=int)

    # Add an item.
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--price", required=True, type=float)
    add_parser.add_argument("--quantity", type=int, default=0)
    add_parser.add_argument("--barcode", default="")
    add_parser.add_argument("--category", default="")
    add_parser.add_argument("--description", default="")

    # Update an item.
    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("id", type=int)
    update_parser.add_argument("--name")
    update_parser.add_argument("--price", type=float)
    update_parser.add_argument("--quantity", type=int)
    update_parser.add_argument("--category")
    update_parser.add_argument("--description")

    # Delete an item.
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("id", type=int)

    # Search external products.
    search_parser = subparsers.add_parser("search")
    search_parser.add_argument("--barcode")
    search_parser.add_argument("--name")

    # Import an external product.
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("--barcode", required=True)
    import_parser.add_argument("--price", required=True, type=float)
    import_parser.add_argument("--quantity", type=int, default=0)

    args = parser.parse_args()

    try:
        if args.command == "list":
            response = requests.get(f"{BASE_URL}/items", timeout=10)

        elif args.command == "show":
            response = requests.get(
                f"{BASE_URL}/items/{args.id}",
                timeout=10
            )

        elif args.command == "add":
            data = {
                "name": args.name,
                "price": args.price,
                "quantity": args.quantity,
                "barcode": args.barcode,
                "category": args.category,
                "description": args.description
            }

            response = requests.post(
                f"{BASE_URL}/items",
                json=data,
                timeout=10
            )

        elif args.command == "update":
            fields = [
                "name",
                "price",
                "quantity",
                "category",
                "description"
            ]

            data = {
                field: getattr(args, field)
                for field in fields
                if getattr(args, field) is not None
            }

            response = requests.patch(
                f"{BASE_URL}/items/{args.id}",
                json=data,
                timeout=10
            )

        elif args.command == "delete":
            response = requests.delete(
                f"{BASE_URL}/items/{args.id}",
                timeout=10
            )

        elif args.command == "search":
            params = {}

            if args.barcode:
                params["barcode"] = args.barcode

            if args.name:
                params["name"] = args.name

            response = requests.get(
                f"{BASE_URL}/search",
                params=params,
                timeout=10
            )

        elif args.command == "import":
            response = requests.post(
                f"{BASE_URL}/items/import",
                json={
                    "barcode": args.barcode,
                    "price": args.price,
                    "quantity": args.quantity
                },
                timeout=10
            )

        print(f"HTTP Status: {response.status_code}")

        try:
            print(json.dumps(response.json(), indent=2))
        except ValueError:
            print(response.text)

        response.raise_for_status()

    except requests.RequestException as exc:
        print(f"Request failed: {exc}")


if __name__ == "__main__":
    main()