"""Tests for the Epic Games Store wishlist coordinator."""

from unittest.mock import Mock

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.core import HomeAssistant

from .common import setup_platform


async def test_setup_wishlist_coordinator(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the wishlist coordinator fetches and stores the catalog."""
    service_multiple.return_value.get_product_mapping.return_value = {
        "game-id-1": "Game One",
        "game-id-2": "Game Two",
    }
    entry = await setup_platform(hass, CALENDAR_DOMAIN)

    service_multiple.return_value.get_product_mapping.assert_called_once()
    assert entry.runtime_data.wishlist.data == [
        {"id": "game-id-1", "title": "Game One"},
        {"id": "game-id-2", "title": "Game Two"},
    ]
