"""Live API contract checks for public (no-token) endpoints.

These tests intentionally hit the real Vistopia API to verify that the
observed response shapes still match our pydantic models.
"""

from urllib.parse import urljoin

import requests

from vistopia.models import Catalog, ContentShow, SearchResult, SubscriptionsList, validate_model


BASE_URL = "https://api.vistopia.com.cn/api/v1/"
TIMEOUT = 20


def _get_data(uri: str, **params):
    query = {"api_token": ""}
    query.update(params)
    response = requests.get(urljoin(BASE_URL, uri), params=query, timeout=TIMEOUT)
    payload = response.json()
    assert payload["status"] == "success"
    assert "data" in payload
    return payload["data"]


def test_live_catalog_endpoint_matches_model():
    data = _get_data("content/catalog/18")
    model = validate_model(Catalog, data)
    assert model.title
    assert model.catalog
    assert model.catalog[0].part


def test_live_content_show_endpoint_matches_model():
    data = _get_data("content/content-show/18")
    model = validate_model(ContentShow, data)
    assert model.title
    assert model.author


def test_live_search_endpoint_matches_model():
    data = _get_data("search/web", keyword="八分")
    model = validate_model(SearchResult, data)
    assert isinstance(model.data, list)
    assert len(model.data) > 0


def test_live_subscriptions_endpoint_matches_model():
    data = _get_data("user/subscriptions-list")
    model = validate_model(SubscriptionsList, data)
    assert isinstance(model.data, list)
