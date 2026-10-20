"""Tests for the Epic Games Store wishlist coordinator."""

from unittest.mock import Mock

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.core import HomeAssistant

from .common import setup_platform


async def test_setup_wishlist_coordinator(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the wishlist coordinator fetches and stores the product mapping."""
    product_mapping = {
        "product-namespace-1": "game-slug-1",
        "product-namespace-2": "game-slug-2",
    }
    service_multiple.return_value.get_product_mapping.return_value = product_mapping
    entry = await setup_platform(hass, CALENDAR_DOMAIN)

    service_multiple.return_value.get_product_mapping.assert_called_once()
    assert entry.runtime_data.wishlist.data == product_mapping
