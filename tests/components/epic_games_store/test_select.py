"""Integration tests for the Epic Games Store wish list game picker.

The picker is exercised through Home Assistant services, so the wish list,
its storage and the to-do entity take part in every test.
"""

from typing import Any
from unittest.mock import Mock

import pytest

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
    setup_wish_list,
    stored_wish_list,
)


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
