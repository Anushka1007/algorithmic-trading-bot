import pytest
from unittest.mock import patch, MagicMock
from backend.data.twelve_data import TwelveDataClient
from fastapi import HTTPException

@pytest.fixture
def client():
    return TwelveDataClient(api_key="test_api_key")

@pytest.mark.asyncio
@patch("backend.data.twelve_data.httpx.AsyncClient.get")
async def test_get_quote_success(mock_get, client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "symbol": "AAPL",
        "close": "150.00",
        "timestamp": 1631822400,
        "is_market_open": True
    }
    mock_get.return_value = mock_response

    quote = await client.get_quote("AAPL")
    
    assert quote.symbol == "AAPL"
    assert quote.price == 150.00
    assert quote.timestamp == 1631822400
    assert quote.is_live is True
    assert quote.source == "Twelve Data"

@pytest.mark.asyncio
@patch("backend.data.twelve_data.httpx.AsyncClient.get")
async def test_get_quote_api_error(mock_get, client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "status": "error",
        "message": "You have reached your API limit.",
        "code": 429
    }
    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as excinfo:
        await client.get_quote("AAPL")
    assert excinfo.value.status_code == 400
    assert "limit" in excinfo.value.detail

@pytest.mark.asyncio
@patch("backend.data.twelve_data.httpx.AsyncClient.get")
async def test_get_history_success_and_cache(mock_get, client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "meta": {"symbol": "AAPL", "interval": "1day"},
        "values": [
            {
                "datetime": "2021-09-16",
                "open": "148.0",
                "high": "149.0",
                "low": "147.0",
                "close": "148.5",
                "volume": "10000"
            }
        ],
        "status": "ok"
    }
    mock_get.return_value = mock_response

    # First call (cache miss)
    history = await client.get_history("AAPL", "1day", 1)
    
    assert history.symbol == "AAPL"
    assert history.interval == "1day"
    assert len(history.data) == 1
    assert history.data[0].open == 148.0
    assert history.data[0].volume == 10000
    assert history.is_cached is False
    assert mock_get.call_count == 1

    # Second call (cache hit)
    history2 = await client.get_history("AAPL", "1day", 1)
    assert history2.is_cached is True
    assert mock_get.call_count == 1  # Should not increase

@pytest.mark.asyncio
@patch("backend.data.twelve_data.httpx.AsyncClient.get")
async def test_get_history_malformed_data(mock_get, client):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "meta": {"symbol": "AAPL", "interval": "1day"},
        "values": [
            {
                "datetime": "2021-09-16",
                "open": "INVALID",
                "high": "149.0",
                "low": "147.0",
                "close": "148.5"
            }
        ],
        "status": "ok"
    }
    mock_get.return_value = mock_response

    with pytest.raises(HTTPException) as excinfo:
        # Avoid cache hit from previous tests if run in same process
        await client.get_history("INVALID_DATA_SYMBOL", "1day", 1)
    assert excinfo.value.status_code == 502

@pytest.mark.asyncio
async def test_dummy_api_key():
    dummy_client = TwelveDataClient(api_key="dummy_key")
    with pytest.raises(HTTPException) as excinfo:
        await dummy_client.get_quote("AAPL")
    assert excinfo.value.status_code == 500
