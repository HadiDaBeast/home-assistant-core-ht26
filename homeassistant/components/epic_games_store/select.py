"""Select entity for adding Games to the EGSWishList."""

from typing import override

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EGSConfigEntry
from .entity import EGSWishListEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: EGSConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the wish list game picker."""
    async_add_entities(
        [
            EGSWishListSelect(
                entry.runtime_data.wish_list, entry.entry_id, "add_to_wish_list"
            )
        ]
    )


class EGSWishListSelect(EGSWishListEntity, SelectEntity):
    """Pick a catalog game to add to the wish list."""

    @property
    @override
    def options(self) -> list[str]:
        """Return the catalog games that can still be added."""
        return [game["title"] for game in self._wish_list.available_games]

    @override
    async def async_select_option(self, option: str) -> None:
        """Add the picked game to the wish list."""
        game = next(
            game for game in self._wish_list.available_games if game["title"] == option
        )
        await self._wish_list.async_add(game)
