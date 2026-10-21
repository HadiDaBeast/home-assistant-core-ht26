"""The Epic Games Store integration."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import (
    EGSCalendarUpdateCoordinator,
    EGSConfigEntry,
    EGSWishlistUpdateCoordinator,
)
from .runtime_data import EGSRuntimeData
from .wish_list import EGSWishList, async_remove_wish_list

PLATFORMS: list[Platform] = [
    Platform.CALENDAR,
    Platform.SELECT,
    Platform.TODO,
]


async def async_setup_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Set up Epic Games Store from a config entry."""

    calendar_coordinator = EGSCalendarUpdateCoordinator(hass, entry)
    wishlist_coordinator = EGSWishlistUpdateCoordinator(hass, entry)

    await calendar_coordinator.async_config_entry_first_refresh()
    await wishlist_coordinator.async_config_entry_first_refresh()
    wish_list = EGSWishList(hass, entry.entry_id, wishlist_coordinator)

    entry.runtime_data = EGSRuntimeData(
        calendar=calendar_coordinator,
        wishlist=wishlist_coordinator,
        wish_list=wish_list,
    )

    await wish_list.async_load()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> None:
    """Remove the stored wish list when the config entry is deleted."""
    await async_remove_wish_list(hass, entry.entry_id)
