"""Shared setup for the Epic Games Store wish list tests."""

from typing import Any
from unittest.mock import Mock

from homeassistant.components.epic_games_store.const import DOMAIN
from homeassistant.const import CONF_COUNTRY, CONF_LANGUAGE
from homeassistant.core import HomeAssistant

from .const import MOCK_COUNTRY, MOCK_LANGUAGE

from tests.common import MockConfigEntry

ENTRY_ID = "egs_entry"
STORAGE_KEY = f"{DOMAIN}.{ENTRY_ID}"
SELECT_ENTITY_ID = "select.epic_games_store_add_to_wish_list"
TODO_ENTITY_ID = "todo.epic_games_store_wish_list"

GAME_A = {"id": "game-a", "title": "Game A"}
GAME_B = {"id": "game-b", "title": "Game B"}
CATALOG = [GAME_A, GAME_B]


def product_mapping(games: list[dict[str, str]]) -> dict[str, str]:
    """Return catalog games the way get_product_mapping returns them."""
    return {game["id"]: game["title"] for game in games}


def stored_wish_list(games: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a wish list as it is saved by the storage helper."""
    return {"version": 1, "minor_version": 1, "key": STORAGE_KEY, "data": games}


async def setup_wish_list(
    hass: HomeAssistant,
    service: Mock,
    catalog: list[dict[str, str]] | None = None,
    entry_id: str = ENTRY_ID,
    country: str = MOCK_COUNTRY,
) -> MockConfigEntry:
    """Set up a config entry with all its platforms and the given catalog."""
    if catalog is None:
        catalog = CATALOG
    service.return_value.get_product_mapping.return_value = product_mapping(catalog)
    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id=entry_id,
        data={CONF_LANGUAGE: MOCK_LANGUAGE, CONF_COUNTRY: country},
        unique_id=f"freegames-{MOCK_LANGUAGE}-{country}",
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
