"""Wish list sensor for Epic Games Store."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import EGSConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EGSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the wish list sensor."""
    async_add_entities([EGSWishListSensor(entry.entry_id)])


class EGSWishListSensor(SensorEntity):
    """Entry point for the wish list popup."""

    _attr_has_entity_name = True
    _attr_translation_key = "wish_list"
    _attr_icon = "mdi:playlist-star"
    _attr_native_value = 1

    def __init__(self, entry_id: str) -> None:
        """Initialize."""
        self._attr_unique_id = f"{entry_id}-wish-list"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Epic Games Store",
            name="Epic Games Store",
        )
