from pydantic import ValidationError
import pytest

from vistopia.models import (
    Article,
    Catalog,
    CatalogPart,
    ContentShow,
    SearchPage,
    SearchItem,
    SearchResult,
    SubscriptionsPage,
    SubscriptionItem,
    SubscriptionsList,
    validate_model,
)


def _field_names(model_cls):
    if hasattr(model_cls, "model_fields"):
        return set(model_cls.model_fields.keys())
    return set(model_cls.__fields__.keys())


def test_models_cover_all_keys_used_by_runtime_code():
    # Keys referenced in vistopia/main.py and vistopia/visitor.py.
    assert {"author", "title", "type", "background_img", "catalog"} <= _field_names(Catalog)
    assert {"catalog_number", "catalog_title", "part"} <= _field_names(CatalogPart)
    assert {"sort_number", "title", "duration_str", "media_key_full_url", "content_url", "article_id"} <= _field_names(Article)
    assert {"author", "title"} <= _field_names(ContentShow)
    assert {"data"} <= _field_names(SubscriptionsList)
    assert {"content_id", "title", "subtitle"} <= _field_names(SubscriptionItem)
    assert {"data"} <= _field_names(SearchResult)
    assert {"data", "current_page", "from_", "last_page"} <= _field_names(SearchPage)
    assert {"data", "current_page", "from_", "last_page"} <= _field_names(SubscriptionsPage)
    assert {"id", "author", "title", "share_desc", "data_type", "subtitle"} <= _field_names(SearchItem)


def test_catalog_model_parses_nested_structure():
    payload = {
        "author": "Author A",
        "title": "Show A",
        "type": "charge",
        "catalog": [
            {
                "catalog_number": "01",
                "catalog_title": "Part One",
                "part": [
                    {
                        "sort_number": "00",
                        "title": "Episode 1",
                        "duration_str": "1:00",
                        "media_key_full_url": "https://example.com/a.mp3",
                        "content_url": "https://example.com/a",
                        "article_id": "100",
                    }
                ],
            }
        ],
    }

    model = validate_model(Catalog, payload)
    assert model.title == "Show A"
    assert model.catalog[0].catalog_number == "01"
    assert model.catalog[0].part[0].sort_number == "00"


def test_search_result_coerces_numeric_id_from_string():
    payload = {
        "data": {
            "current_page": 1,
            "from": 1,
            "last_page": 1,
            "next_page_url": None,
            "per_page": 20,
            "prev_page_url": None,
            "to": 1,
            "total": 1,
            "data": [
                {
                    "id": "11",
                    "author": "梁文道",
                    "title": "八分",
                    "share_desc": "知识只求八分饱",
                    "data_type": "content",
                    "subtitle": "",
                }
            ],
        }
    }

    model = validate_model(SearchResult, payload)
    assert model.data.data[0].id == 11
    assert model.data.from_ == 1


def test_catalog_model_raises_on_missing_required_fields():
    with pytest.raises(ValidationError):
        validate_model(Catalog, {"title": "missing-author-and-catalog"})
