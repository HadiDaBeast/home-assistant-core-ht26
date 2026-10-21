"""Entity for the todo list EGSWishList."""

from typing import override

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .wish_list import EGSWishList


class EGSWishListEntity(Entity):
    """EGSWishListEntity that is shown in hass areas."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, wish_list: EGSWishList, config_entry_id: str, key: str) -> None:
        """Initialize the entity."""
        self._wish_list = wish_list
        self._attr_translation_key = key
        self._attr_unique_id = f"{config_entry_id}-{key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, config_entry_id)},
            manufacturer="Epic Games Store",
            name="Epic Games Store",
        )

    @override
    async def async_added_to_hass(self) -> None:
        """Update the entity when the wish list changes."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._wish_list.async_add_listener(self.async_write_ha_state)
        )
