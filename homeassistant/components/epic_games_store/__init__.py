"""The Epic Games Store integration."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import EGSCalendarUpdateCoordinator, EGSWishlistUpdateCoordinator
from .runtime_data import EGSConfigEntry, EGSRuntimeData

PLATFORMS: list[Platform] = [
    Platform.CALENDAR,
]


async def async_setup_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Set up Epic Games Store from a config entry."""

    calendar_coordinator = EGSCalendarUpdateCoordinator(hass, entry)
    wishlist_coordinator = EGSWishlistUpdateCoordinator(hass, entry)

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
