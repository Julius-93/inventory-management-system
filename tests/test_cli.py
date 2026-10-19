import json
import sys
from unittest.mock import Mock, patch

import requests

from cli import main


def make_response(status_code=200, data=None):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = data if data is not None else {}
    response.text = ""
    response.raise_for_status.return_value = None
    return response


def test_cli_list_inventory(capsys):
    response = make_response(
        data=[{"id": 1, "name": "Milk"}]
    )

    with patch.object(sys, "argv", ["cli.py", "list"]):
        with patch("cli.requests.get", return_value=response) as mock_get:
            main()

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/items",
        timeout=10,
    )

    output = capsys.readouterr().out
    assert "HTTP Status: 200" in output
    assert '"name": "Milk"' in output


def test_cli_add_item():
    response = make_response(
        status_code=201,
        data={"id": 1, "name": "Milk"},
    )

    with patch.object(
        sys,
        "argv",
        [
            "cli.py",
            "add",
            "--name", "Milk",
            "--price", "120",
            "--quantity", "10",
        ],
    ):
        with patch(
            "cli.requests.post",
            return_value=response,
        ) as mock_post:
            main()

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/items",
        json={
            "name": "Milk",
            "price": 120.0,
            "quantity": 10,
            "barcode": "",
            "category": "",
            "description": "",
        },
        timeout=10,
    )


def test_cli_show_item():
    response = make_response(
        data={"id": 5, "name": "Bread"}
    )

    with patch.object(
        sys,
        "argv",
        ["cli.py", "show", "5"],
    ):
        with patch(
            "cli.requests.get",
            return_value=response,
        ) as mock_get:
            main()

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/items/5",
        timeout=10,
    )


def test_cli_update_item():
    response = make_response(
        data={"id": 1, "name": "Whole Milk"}
    )

    with patch.object(
        sys,
        "argv",
        ["cli.py", "update", "1", "--name", "Whole Milk"],
    ):
        with patch(
            "cli.requests.patch",
            return_value=response,
        ) as mock_patch:
            main()

    mock_patch.assert_called_once_with(
        "http://127.0.0.1:5000/items/1",
        json={"name": "Whole Milk"},
        timeout=10,
    )


def test_cli_delete_item():
    response = make_response(data={"message": "Item deleted"})

    with patch.object(
        sys,
        "argv",
        ["cli.py", "delete", "1"],
    ):
        with patch(
            "cli.requests.delete",
            return_value=response,
        ) as mock_delete:
            main()

    mock_delete.assert_called_once_with(
        "http://127.0.0.1:5000/items/1",
        timeout=10,
    )


def test_cli_search_by_barcode():
    response = make_response(
        data={"product": {"product_name": "Milk"}}
    )

    with patch.object(
        sys,
        "argv",
        ["cli.py", "search", "--barcode", "123456789"],
    ):
        with patch(
            "cli.requests.get",
            return_value=response,
        ) as mock_get:
            main()

    mock_get.assert_called_once_with(
        "http://127.0.0.1:5000/search",
        params={"barcode": "123456789"},
        timeout=10,
    )


def test_cli_import_product():
    response = make_response(
        status_code=201,
        data={"id": 1, "name": "Milk"},
    )

    with patch.object(
        sys,
        "argv",
        [
            "cli.py",
            "import",
            "--barcode", "123456789",
            "--price", "120",
            "--quantity", "5",
        ],
    ):
        with patch(
            "cli.requests.post",
            return_value=response,
        ) as mock_post:
            main()

    mock_post.assert_called_once_with(
        "http://127.0.0.1:5000/items/import",
        json={
            "barcode": "123456789",
            "price": 120.0,
            "quantity": 5,
        },
        timeout=10,
    )


def test_cli_handles_connection_error(capsys):
    with patch.object(
        sys,
        "argv",
        ["cli.py", "list"],
    ):
        with patch(
            "cli.requests.get",
            side_effect=requests.ConnectionError("Server unavailable"),
        ):
            main()

    output = capsys.readouterr().out
    assert "Request failed:" in output
    assert "Server unavailable" in output
