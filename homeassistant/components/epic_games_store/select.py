"""Select entity for adding Games to the EGSWishList."""

from collections import Counter
from typing import override

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import EGSConfigEntry
from .entity import EGSWishListEntity
from .wish_list import Game


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

    @override
    async def async_added_to_hass(self) -> None:
        """Update the options when the catalog is refreshed."""
        await super().async_added_to_hass()
        self.async_on_remove(
            self._wish_list.coordinator.async_add_listener(self.async_write_ha_state)
        )

    def _games_by_option(self) -> dict[str, Game]:
        """Map each option to its game, adding the ID to titles that repeat."""
        games = self._wish_list.available_games
        title_count = Counter(game["title"] for game in games)
        return {
            (
                game["title"]
                if title_count[game["title"]] == 1
                else f"{game['title']} ({game['id']})"
            ): game
            for game in games
        }

    @property
    @override
    def options(self) -> list[str]:
        """Return the catalog games that can still be added."""
        return list(self._games_by_option())

    @override
    async def async_select_option(self, option: str) -> None:
        """Add the picked game to the wish list."""
        await self._wish_list.async_add(self._games_by_option()[option])
