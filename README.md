# Inventory Management System

A Flask-based REST API for managing retail inventory, integrating with OpenFoodFacts to retrieve product information, and providing a command-line interface for inventory operations.

## Features

* Create, retrieve, update, and delete inventory items.
* Search for external product information by barcode or name.
* Import external products into local inventory.
* Interact with the API through a CLI.
* Validate inventory data.
* Run automated tests using pytest.

## Technologies

* Python
* Flask
* Requests
* Pytest
* OpenFoodFacts API
* Git and GitHub

## Installation

1. Clone the repository:

   ```bash
   git clone YOUR_GITHUB_REPOSITORY_URL
   ```

2. Enter the project directory:

   ```bash
   cd inventory-management-system
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv .venv
   ```

4. Activate the environment:

   ```bash
   source .venv/bin/activate
   ```

5. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

Start the Flask server:

```bash
python app.py
```

The API will be available at:

`http://127.0.0.1:5000`

## API Endpoints

| Method | Endpoint                    | Description                |
| ------ | --------------------------- | -------------------------- |
| GET    | `/`                         | Display API information    |
| GET    | `/items`                    | List all inventory items   |
| GET    | `/items/<id>`               | Retrieve an inventory item |
| POST   | `/items`                    | Create an inventory item   |
| PATCH  | `/items/<id>`               | Update an inventory item   |
| DELETE | `/items/<id>`               | Delete an inventory item   |
| GET    | `/search?barcode=<barcode>` | Search by barcode          |
| GET    | `/search?name=<name>`       | Search by name             |
| POST   | `/items/import`             | Import an external product |

## Example API Request

Create an inventory item using JSON:

```json
{
  "name": "Fresh Milk",
  "barcode": "1234567890123",
  "category": "Dairy",
  "price": 120,
  "quantity": 25,
  "description": "Fresh whole milk"
}
```

Send this payload to `POST /items` with the `Content-Type: application/json` header.

## CLI Usage

List all items:

```bash
python cli.py list
```

Add an item:

```bash
python cli.py add --name "Fresh Milk" --price 120 --quantity 25
```

Update an item:

```bash
python cli.py update 1 --quantity 40
```

Delete an item:

```bash
python cli.py delete 1
```

Search by barcode:

```bash
python cli.py search --barcode "5449000000996"
```

Search by name:

```bash
python cli.py search --name "Coca Cola"
```

Import a product:

```bash
python cli.py import --barcode "5449000000996" --price 150 --quantity 20
```

## Running Tests

Run the automated test suite:

```bash
pytest -v
```

Generate a coverage report:

```bash
pytest --cov=app --cov=inventory --cov=external_api --cov-report=term-missing
```

## External API

This project uses OpenFoodFacts to retrieve product information.

Documentation: https://openfoodfacts.github.io/openfoodfacts-server/api/

Product information may be incomplete or unavailable for some barcodes.

## Limitations

The initial implementation uses in-memory storage. Inventory data is not persistent and will be lost when the application restarts.

The system does not yet include user authentication or role-based authorization.

## Future Improvements

* Integrate SQLite or PostgreSQL for persistent storage.
* Add authentication and authorization.
* Implement pagination and inventory filtering.
* Add duplicate barcode detection.
* Improve logging and error monitoring.
* Introduce a web-based administration dashboard.

## License

Add an appropriate license if you intend to distribute the project publicly.
