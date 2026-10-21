"""Wish list sensor for Epic Games Store."""

from typing import override

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import CATALOG_KEY, DOMAIN
from .coordinator import EGSConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EGSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the wish list sensor."""
    async_add_entities([EGSWishListSensor(entry.runtime_data.wishlist, entry.entry_id)])


class EGSWishListSensor(
    CoordinatorEntity[DataUpdateCoordinator[list[dict[str, str]]]], SensorEntity
):
    """Entry point for the wish list popup."""

    _attr_has_entity_name = True
    _attr_translation_key = "wish_list"
    _attr_icon = "mdi:playlist-star"
    _attr_native_value = 1

    def __init__(
        self,
        coordinator: DataUpdateCoordinator[list[dict[str, str]]],
        entry_id: str,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}-wish-list"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, entry_id)},
            manufacturer="Epic Games Store",
            name="Epic Games Store",
        )

    @property
    @override
    def extra_state_attributes(self) -> dict[str, list[dict[str, str]]]:
        """Return the game catalog."""
        return {CATALOG_KEY: self.coordinator.data}
