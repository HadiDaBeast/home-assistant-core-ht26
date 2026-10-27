"""Wish list storage for the Epic Games Store integration."""

from typing import NotRequired, TypedDict

from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.helpers.storage import Store

# from homeassistant.components.epic_games_store import coordinator
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

STORAGE_VERSION = 1


class Game(TypedDict):
    """A game object from the Epic Games Store catalog."""

    id: str
    title: str
    completed: NotRequired[bool]


def _store(hass: HomeAssistant, entry_id: str) -> Store[list[Game]]:
    """Return the store holding the wish list of a config entry."""
    return Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry_id}")


async def async_remove_wish_list(hass: HomeAssistant, entry_id: str) -> None:
    """Remove the stored wish list of a config entry."""
    await _store(hass, entry_id).async_remove()


class EGSWishList:
    """EGS Wishlist for storing, adding and removing games."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry_id: str,
        coordinator: DataUpdateCoordinator[list[dict[str, str]]],
    ) -> None:
        """Initialize."""
        self._store = _store(hass, entry_id)
        self._listeners: list[CALLBACK_TYPE] = []
        self.games: list[Game] = []
        self.coordinator = coordinator

    async def async_load(self) -> None:
        """Load the stored wish list."""
        self.games = await self._store.async_load() or []

    @property
    def catalog(self) -> list[Game]:
        """Return the catalog games from the latest coordinator refresh."""
        return [
            Game(id=game["id"], title=game["title"])
            for game in sorted(self.coordinator.data, key=lambda game: game["title"])
        ]

    @property
    def available_games(self) -> list[Game]:
        """Return the catalog games that are not on the wish list yet."""
        wishlisted = {game["id"] for game in self.games}
        return [game for game in self.catalog if game["id"] not in wishlisted]

    async def async_add(self, game: Game) -> None:
        """Add a game to the wish list."""
        self.games.append(game)
        await self._async_save()

    async def async_set_completed(self, game_id: str, state: bool) -> None:
        """Set wishlisted game as completed or not."""
        for game in self.games:
            if game["id"] == game_id:
                game["completed"] = state
        await self._async_save()

    async def async_remove(self, game_ids: set[str]) -> None:
        """Remove games from the wish list."""
        self.games = [game for game in self.games if game["id"] not in game_ids]
        await self._async_save()

    async def _async_save(self) -> None:
        """Store the wish list and notify the entities."""
        await self._store.async_save(self.games)
        for update_callback in self._listeners:
            update_callback()

    @callback
    def async_add_listener(self, update_callback: CALLBACK_TYPE) -> CALLBACK_TYPE:
        """Listen for wish list changes."""
        self._listeners.append(update_callback)

        @callback
        def remove_listener() -> None:
            self._listeners.remove(update_callback)

        return remove_listener
