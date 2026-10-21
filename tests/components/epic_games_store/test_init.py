"""Integration tests for setting up the Epic Games Store config entry."""

from datetime import timedelta
from unittest.mock import Mock

from freezegun.api import FrozenDateTimeFactory

from homeassistant.components.calendar import DOMAIN as CALENDAR_DOMAIN
from homeassistant.components.epic_games_store.coordinator import SCAN_INTERVAL
from homeassistant.core import HomeAssistant

from .common import setup_platform

from tests.common import async_fire_time_changed


async def _tick(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, delta: timedelta
) -> None:
    """Move the clock forward and run the timers that are due."""
    freezer.tick(delta)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_wishlist_with_listener_refreshes_once_per_scan_interval(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, service_multiple: Mock
) -> None:
    """Test a listened-to wishlist is fetched again when the scan interval has passed.

    The coordinator schedules the refresh at a random sub-second offset around
    the interval, so the OFF point (2 s before) and the ON point (1 s after)
    are placed outside that window to keep the test repeatable.
    """
    # Arrange
    fetch_store_games = service_multiple.return_value.fetch_store_games
    fetch_store_games.return_value = {
        "data": {"Catalog": {"searchStore": {"elements": []}}}
    }
    entry = await setup_platform(hass, CALENDAR_DOMAIN)
    entry.async_on_unload(entry.runtime_data.wishlist.async_add_listener(lambda: None))

    # Act + Assert: OFF point
    await _tick(hass, freezer, SCAN_INTERVAL - timedelta(seconds=2))
    assert fetch_store_games.call_count == 1

    # Act + Assert: ON point
    await _tick(hass, freezer, timedelta(seconds=3))
    assert fetch_store_games.call_count == 2
