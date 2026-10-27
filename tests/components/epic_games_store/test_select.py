"""Integration tests for the Epic Games Store wish list game picker.

The picker is exercised through Home Assistant services, so the wish list,
its storage and the to-do entity take part in every test.
"""

from typing import Any
from unittest.mock import Mock

from freezegun.api import FrozenDateTimeFactory
import pytest

from homeassistant.components.epic_games_store.coordinator import SCAN_INTERVAL
from homeassistant.components.select import (
    ATTR_OPTION,
    ATTR_OPTIONS,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .wish_list_common import (
    CATALOG,
    GAME_A,
    GAME_B,
    SELECT_ENTITY_ID,
    STORAGE_KEY,
    product_mapping,
    setup_wish_list,
    stored_wish_list,
)

from tests.common import async_fire_time_changed

GAME_A_DUPLICATE = {"id": "game-a-duplicate", "title": "Game A"}


# Picker: options are the catalog titles (0, 1 and 2 games)
@pytest.mark.parametrize(
    ("catalog", "expected_options"),
    [
        pytest.param([], [], id="zero_games"),
        pytest.param([GAME_A], ["Game A"], id="one_game"),
        pytest.param(CATALOG, ["Game A", "Game B"], id="two_games"),
    ],
)
async def test_options_are_catalog_titles(
    hass: HomeAssistant,
    service_multiple: Mock,
    catalog: list[dict[str, str]],
    expected_options: list[str],
) -> None:
    """Test the picker offers the titles of the fetched catalog."""
    # Act
    await setup_wish_list(hass, service_multiple, catalog)

    # Assert
    state = hass.states.get(SELECT_ENTITY_ID)
    assert state.attributes[ATTR_OPTIONS] == expected_options


# Picker: the chosen game is stored and no longer offered
@pytest.mark.parametrize(
    ("picked", "stored", "remaining"),
    [
        pytest.param("Game A", GAME_A, ["Game B"], id="first"),
        pytest.param("Game B", GAME_B, ["Game A"], id="second"),
    ],
)
async def test_select_adds_game_to_wish_list(
    hass: HomeAssistant,
    service_multiple: Mock,
    hass_storage: dict[str, Any],
    picked: str,
    stored: dict[str, str],
    remaining: list[str],
) -> None:
    """Test picking a game adds exactly that game and stops offering it."""
    # Arrange
    await setup_wish_list(hass, service_multiple)

    # Act
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: SELECT_ENTITY_ID, ATTR_OPTION: picked},
        blocking=True,
    )

    # Assert
    assert hass_storage[STORAGE_KEY]["data"] == [stored]
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == remaining


# Picker: games already on the stored list are not offered
async def test_stored_game_is_not_offered(
    hass: HomeAssistant, service_multiple: Mock, hass_storage: dict[str, Any]
) -> None:
    """Test a game already on the stored wish list is left out of the options."""
    # Arrange
    hass_storage[STORAGE_KEY] = stored_wish_list([GAME_B])

    # Act
    await setup_wish_list(hass, service_multiple)

    # Assert
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == ["Game A"]


# Picker: games sharing a title get distinct options that add the picked game
@pytest.mark.parametrize(
    ("picked", "stored", "remaining"),
    [
        pytest.param("Game A (game-a)", GAME_A, ["Game A", "Game B"], id="first"),
        pytest.param(
            "Game A (game-a-duplicate)",
            GAME_A_DUPLICATE,
            ["Game A", "Game B"],
            id="second",
        ),
    ],
)
async def test_duplicate_titles_add_the_picked_game(
    hass: HomeAssistant,
    service_multiple: Mock,
    hass_storage: dict[str, Any],
    picked: str,
    stored: dict[str, str],
    remaining: list[str],
) -> None:
    """Test catalog games with the same title are added by their own ID."""
    # Arrange
    await setup_wish_list(hass, service_multiple, [GAME_A, GAME_A_DUPLICATE, GAME_B])
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == [
        "Game A (game-a)",
        "Game A (game-a-duplicate)",
        "Game B",
    ]

    # Act
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: SELECT_ENTITY_ID, ATTR_OPTION: picked},
        blocking=True,
    )

    # Assert
    assert hass_storage[STORAGE_KEY]["data"] == [stored]
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == remaining


# Picker: options follow the catalog when the coordinator refreshes
async def test_options_follow_catalog_refresh(
    hass: HomeAssistant, service_multiple: Mock, freezer: FrozenDateTimeFactory
) -> None:
    """Test a game added to the catalog is offered after the next refresh."""
    # Arrange
    await setup_wish_list(hass, service_multiple, [GAME_A])
    service_multiple.return_value.get_product_mapping.return_value = product_mapping(
        CATALOG
    )

    # Act
    freezer.tick(SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    # Assert
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == [
        "Game A",
        "Game B",
    ]
