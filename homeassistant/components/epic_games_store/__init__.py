"""The Epic Games Store integration."""

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import EGSCalendarUpdateCoordinator, EGSWishlistUpdateCoordinator
from .runtime_data import EGSConfigEntry, EGSRuntimeData

PLATFORMS: list[Platform] = [Platform.CALENDAR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Set up Epic Games Store from a config entry."""

    calendar_coordinator = EGSCalendarUpdateCoordinator(hass, entry)
    wishlist_coordinator = EGSWishlistUpdateCoordinator(hass, entry)
    # Add new wish list custom card
    card = Path(__file__).parent / "www" / "wish-list-card.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/epic_games_store/wish-list-card.js", str(card), False)]
    )
    add_extra_js_url(hass, "/epic_games_store/wish-list-card.js")

    coordinator = EGSCalendarUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    await calendar_coordinator.async_config_entry_first_refresh()
    await wishlist_coordinator.async_config_entry_first_refresh()

    entry.runtime_data = EGSRuntimeData(
        calendar=calendar_coordinator,
        wishlist=wishlist_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
