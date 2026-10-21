"""The Epic Games Store integration."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import EGSCalendarUpdateCoordinator, EGSConfigEntry, EGSData
from .wish_list import EGSWishList, async_remove_wish_list

PLATFORMS: list[Platform] = [
    Platform.CALENDAR,
    Platform.SELECT,
    Platform.TODO,
]


async def async_setup_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Set up Epic Games Store from a config entry."""

    coordinator = EGSCalendarUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    # Create / Setup wishlist entity
    wish_list = EGSWishList(hass, entry.entry_id)
    await wish_list.async_load()

    entry.runtime_data = EGSData(coordinator, wish_list)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: EGSConfigEntry) -> None:
    """Remove the stored wish list when the config entry is deleted."""
    await async_remove_wish_list(hass, entry.entry_id)
