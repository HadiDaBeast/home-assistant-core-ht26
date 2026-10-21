"""Tests for the Epic Games Store wishlist coordinator."""

from unittest.mock import Mock

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.components.epic_games_store.const import CATALOG_KEY
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.core import HomeAssistant

from .common import setup_platform


async def test_setup_wishlist_coordinator(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the wishlist coordinator fetches and stores the catalog."""
    catalog_data = [
        {"id": "game-id-1", "title": "Game One", "namespace": "game-namespace-1"},
        {"id": "game-id-2", "title": "Game Two", "namespace": "game-namespace-2"},
    ]
    catalog = [
        {"id": "game-id-1", "title": "Game One"},
        {"id": "game-id-2", "title": "Game Two"},
    ]
    service_multiple.return_value.fetch_store_games.return_value = {
        "data": {"Catalog": {"searchStore": {"elements": catalog_data}}}
    }
    entry = await setup_platform(hass, CALENDAR_DOMAIN)

    service_multiple.return_value.fetch_store_games.assert_called_once()
    assert entry.runtime_data.wishlist.data == catalog


async def test_wishlist_catalog_attribute(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the wishlist sensor exposes the catalog."""
    catalog_data = [
        {"id": "game-id-1", "title": "Game One", "namespace": "game-namespace-1"}
    ]
    catalog = [{"id": "game-id-1", "title": "Game One"}]
    service_multiple.return_value.fetch_store_games.return_value = {
        "data": {"Catalog": {"searchStore": {"elements": catalog_data}}}
    }
    await setup_platform(hass, SENSOR_DOMAIN)

    states = hass.states.async_all(SENSOR_DOMAIN)
    assert len(states) == 1
    assert states[0].attributes[CATALOG_KEY] == catalog
