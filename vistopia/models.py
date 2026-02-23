"""API schema models for key Vistopia endpoints.

These models serve two goals:
1) Runtime validation/parsing of API payloads used by the app.
2) Human-readable schema documentation of observed endpoint fields,
   including fields not currently consumed by business logic.

Relevant endpoints:
- content/catalog/{id}
- content/content-show/{id}
- search/web
- user/subscriptions-list
"""

from typing import Any, List, Optional

from pydantic import BaseModel, Field


class VistopiaModel(BaseModel):
    """Shared base model for Vistopia API schemas."""
    class Config:
        extra = "allow"
        allow_population_by_field_name = True


class Article(VistopiaModel):
    """Episode/article item from `content/catalog/{id}` -> `catalog[].part[]`."""
    article_id: str
    catalog_id: Optional[int] = None
    comment_count: Optional[int] = None
    content_id: Optional[int] = None
    content_media_type_en: Optional[str] = None
    content_url: Optional[str] = None
    duration: Optional[str] = None
    sort_number: str
    title: str
    duration_str: str
    is_finished: Optional[bool] = None
    is_listened: Optional[bool] = None
    is_trial: Optional[bool] = None
    listen_percent: Optional[int] = None
    listen_time: Optional[int] = None
    media_files: Optional[Any] = None
    media_key: Optional[str] = None
    media_key_full_url: Optional[str] = None
    media_type: Optional[str] = None
    media_type_en: Optional[str] = None
    optional_media_key_full_url: Optional[str] = None
    sample_media_full_url: Optional[str] = None
    sample_media_key: Optional[str] = None
    sample_vid: Optional[str] = None
    share_desc: Optional[str] = None
    share_url: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    vid: Optional[str] = None
    video_poster: Optional[str] = None


class CatalogPart(VistopiaModel):
    """Catalog section from `content/catalog/{id}` -> `catalog[]`."""
    catalog_id: Optional[int] = None
    catalog_number: Optional[str] = None
    catalog_title: Optional[str] = None
    part: List[Article]


class Catalog(VistopiaModel):
    """Response data model for `content/catalog/{id}`."""
    id: Optional[int] = None
    author: str
    title: str
    type: str
    background_img: Optional[str] = None
    small_background_img: Optional[str] = None
    catalog_type: Optional[str] = None
    complete_class_price: Optional[str] = None
    is_limited_free: Optional[bool] = None
    is_promotion: Optional[bool] = None
    is_purchased: Optional[bool] = None
    is_subscribed: Optional[bool] = None
    is_vip_expired: Optional[bool] = None
    is_vip_free: Optional[bool] = None
    is_vip_only: Optional[bool] = None
    media_type: Optional[str] = None
    media_type_en: Optional[str] = None
    old_vip_type: Optional[str] = None
    promotion_desc: Optional[str] = None
    promotion_price: Optional[str] = None
    vip_type: Optional[str] = None
    catalog: List[CatalogPart]


class ContentShow(VistopiaModel):
    """Response data model for `content/content-show/{id}`."""
    article_count: Optional[int] = None
    author: str
    author_id: Optional[int] = None
    author_ids: Optional[Any] = None
    authors: Optional[Any] = None
    avatar: Optional[str] = None
    background_img: Optional[str] = None
    catalog: Optional[Any] = None
    catalog_type: Optional[str] = None
    comment_count: Optional[int] = None
    complete_class_price: Optional[str] = None
    content_id: Optional[int] = None
    content_url: Optional[str] = None
    cron_price: Optional[str] = None
    cron_price_end_time: Optional[str] = None
    cron_price_start_time: Optional[str] = None
    discount_price: Optional[str] = None
    friend_vip_price: Optional[str] = None
    friend_vip_price_home: Optional[str] = None
    gift_num: Optional[int] = None
    gift_url: Optional[str] = None
    intro_txt: Optional[str] = None
    introduction: Optional[str] = None
    is_audiobook: Optional[bool] = None
    is_can_subscribed: Optional[bool] = None
    is_cancel_subscribed: Optional[bool] = None
    is_channel_promotion: Optional[bool] = None
    is_coupon: Optional[bool] = None
    is_cron_price: Optional[bool] = None
    is_favorite: Optional[bool] = None
    is_friend_vip: Optional[bool] = None
    is_gift_created: Optional[bool] = None
    is_limited_free: Optional[bool] = None
    is_pending_update: Optional[bool] = None
    is_promotion: Optional[bool] = None
    is_purchased: Optional[bool] = None
    is_salon_act: Optional[bool] = None
    is_show_input: Optional[bool] = None
    is_show_question: Optional[bool] = None
    is_show_view: Optional[bool] = None
    is_subscribed: Optional[bool] = None
    is_vip_expired: Optional[bool] = None
    is_vip_free: Optional[bool] = None
    is_vip_only: Optional[bool] = None
    limited_free_days: Optional[int] = None
    link_url: Optional[str] = None
    main_tab: Optional[str] = None
    media_type: Optional[str] = None
    media_type_en: Optional[str] = None
    nice_id: Optional[str] = None
    old_vip_type: Optional[str] = None
    pending_update_time: Optional[str] = None
    popup: Optional[Any] = None
    promotion_desc: Optional[str] = None
    promotion_price: Optional[str] = None
    question_tips: Optional[str] = None
    range: Optional[str] = None
    relate_content: Optional[Any] = None
    relate_contents: Optional[Any] = None
    relate_image: Optional[str] = None
    set_count: Optional[int] = None
    share_desc: Optional[str] = None
    share_poster: Optional[str] = None
    share_poster_scale: Optional[str] = None
    share_url: Optional[str] = None
    small_background_img: Optional[str] = None
    sponsor_img: Optional[str] = None
    status: Optional[str] = None
    status_desc: Optional[str] = None
    subtitle: Optional[str] = None
    title: str
    total_set: Optional[int] = None
    trial_articles: Optional[Any] = None
    type: Optional[str] = None
    update_time: Optional[str] = None
    user_collection: Optional[Any] = None
    user_data: Optional[Any] = None
    video: Optional[Any] = None
    video_img: Optional[str] = None
    video_poster: Optional[str] = None
    video_title: Optional[str] = None
    video_url: Optional[str] = None
    view_image_url: Optional[str] = None
    view_url: Optional[str] = None
    vip_type: Optional[str] = None


class SubscriptionItem(VistopiaModel):
    """Single subscription item from `user/subscriptions-list` pagination."""
    content_id: int
    title: str
    subtitle: Optional[str] = ""
    type: Optional[str] = None
    share_desc: Optional[str] = None
    media_type_en: Optional[str] = None
    icon: Optional[str] = None


class PaginationMeta(VistopiaModel):
    """Common pagination fields used by list endpoints."""
    current_page: Optional[int] = None
    from_: Optional[int] = Field(default=None, alias="from")
    last_page: Optional[int] = None
    next_page_url: Optional[str] = None
    per_page: Optional[int] = None
    prev_page_url: Optional[str] = None
    to: Optional[int] = None
    total: Optional[int] = None


class SearchItem(VistopiaModel):
    """Single search item from `search/web` pagination."""
    id: int
    author: str
    title: str
    share_desc: str
    data_type: str
    subtitle: Optional[str] = None
    type: Optional[str] = None
    media_type_en: Optional[str] = None
    icon: Optional[str] = None
    index: Optional[int] = None
    top: Optional[int] = None
    weight: Optional[int] = None
    friend_vip_price: Optional[str] = None
    is_friend_vip: Optional[bool] = None
    is_limited_free: Optional[bool] = None
    is_presell: Optional[bool] = None
    is_promotion: Optional[bool] = None
    is_purchased: Optional[bool] = None
    is_subscribed: Optional[bool] = None
    is_vip_free: Optional[bool] = None
    is_vip_only: Optional[bool] = None
    origin_price: Optional[str] = None
    presell_time: Optional[str] = None
    price: Optional[str] = None
    promotion_desc: Optional[str] = None
    promotion_price: Optional[str] = None
    sale_price: Optional[str] = None
    vip_type: Optional[str] = None


class SearchPage(PaginationMeta):
    """Paginated `data` object returned by `search/web`."""
    data: List[SearchItem]


class SubscriptionsPage(PaginationMeta):
    """Paginated `data` object returned by `user/subscriptions-list`."""
    data: List[SubscriptionItem]


class SearchResult(VistopiaModel):
    """Top-level `search/web` payload (`data` is a pagination object)."""
    data: SearchPage


class SubscriptionsList(VistopiaModel):
    """Top-level `user/subscriptions-list` payload (`data` is pagination)."""
    data: SubscriptionsPage


def validate_model(model_cls, payload):
    if hasattr(model_cls, "model_validate"):
        return model_cls.model_validate(payload)
    return model_cls.parse_obj(payload)


def dump_model(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()
