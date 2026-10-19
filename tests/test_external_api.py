from unittest.mock import Mock, patch

import pytest
import requests

from external_api import search_by_barcode, search_by_name


@patch("external_api.requests.get")
def test_search_by_barcode_success(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "status": 1,
        "product": {
            "product_name": "Chocolate",
            "categories": "Snacks",
            "generic_name": "Milk chocolate"
        }
    }

    mock_get.return_value = mock_response

    result = search_by_barcode("1234567890123")

    assert result["name"] == "Chocolate"
    assert result["barcode"] == "1234567890123"

    mock_get.assert_called_once()


@patch("external_api.requests.get")
def test_search_by_barcode_not_found(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "status": 0,
        "product": None
    }

    mock_get.return_value = mock_response

    assert search_by_barcode("0000000000000") is None


@patch("external_api.requests.get")
def test_search_by_name_success(mock_get):
    mock_response = Mock()

    mock_response.json.return_value = {
        "products": [
            {
                "product_name": "Orange Juice",
                "code": "12345",
                "categories": "Beverages",
                "generic_name": "Orange juice"
            }
        ]
    }

    mock_get.return_value = mock_response

    result = search_by_name("Orange Juice")

    assert len(result) == 1
    assert result[0]["name"] == "Orange Juice"


@patch("external_api.requests.get")
def test_external_api_network_error(mock_get):
    mock_get.side_effect = requests.ConnectionError(
        "Connection failed"
    )

    with pytest.raises(RuntimeError):
        search_by_barcode("1234567890123")