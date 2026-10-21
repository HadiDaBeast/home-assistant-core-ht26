"""Integration tests for the Epic Games Store wish list to-do entity.

The list is exercised through Home Assistant services, with a stored wish list.
"""

from typing import Any
from unittest.mock import Mock

import pytest

from homeassistant.components.select import ATTR_OPTIONS
from homeassistant.components.todo import (
    ATTR_ITEM,
    ATTR_STATUS,
    DOMAIN as TODO_DOMAIN,
    TodoItemStatus,
    TodoServices,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from .wish_list_common import (
    GAME_A,
    GAME_B,
    SELECT_ENTITY_ID,
    STORAGE_KEY,
    TODO_ENTITY_ID,
    setup_wish_list,
    stored_wish_list,
)


# To-do: items and their status come from storage
async def test_items_come_from_stored_wish_list(
    hass: HomeAssistant, service_multiple: Mock, hass_storage: dict[str, Any]
) -> None:
    """Test the stored games are listed with their completed status."""
    # Arrange
    hass_storage[STORAGE_KEY] = stored_wish_list(
        [{**GAME_A, "completed": True}, GAME_B]
    )
    await setup_wish_list(hass, service_multiple)

    # Act
    result = await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.GET_ITEMS,
        {ATTR_ENTITY_ID: TODO_ENTITY_ID},
        blocking=True,
        return_response=True,
    )

    # Assert
    items = result[TODO_ENTITY_ID]["items"]
    assert [(item["uid"], item["summary"], item["status"]) for item in items] == [
        ("game-a", "Game A", TodoItemStatus.COMPLETED),
        ("game-b", "Game B", TodoItemStatus.NEEDS_ACTION),
    ]
    # Only not completed items are counted in the state
    assert hass.states.get(TODO_ENTITY_ID).state == "1"


# To-do: a status change is saved for that game only
@pytest.mark.parametrize(
    ("status", "completed"),
    [
        pytest.param(TodoItemStatus.COMPLETED, True, id="completed"),
        pytest.param(TodoItemStatus.NEEDS_ACTION, False, id="needs_action"),
    ],
)
async def test_update_item_status_is_stored(
    hass: HomeAssistant,
    service_multiple: Mock,
    hass_storage: dict[str, Any],
    status: TodoItemStatus,
    completed: bool,
) -> None:
    """Test changing the status of one game is saved and leaves the other game as is."""
    # Arrange
    hass_storage[STORAGE_KEY] = stored_wish_list(
        [{**GAME_A, "completed": not completed}, {**GAME_B, "completed": not completed}]
    )
    await setup_wish_list(hass, service_multiple)

    # Act
    await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.UPDATE_ITEM,
        {ATTR_ENTITY_ID: TODO_ENTITY_ID, ATTR_ITEM: "game-a", ATTR_STATUS: status},
        blocking=True,
    )

    # Assert
    assert hass_storage[STORAGE_KEY]["data"] == [
        {**GAME_A, "completed": completed},
        {**GAME_B, "completed": not completed},
    ]


# To-do: removed games leave storage and are offered again
@pytest.mark.parametrize(
    ("removed", "kept", "expected_options"),
    [
        pytest.param(["game-a"], [GAME_B], ["Game A"], id="one_of_two"),
        pytest.param(["game-a", "game-b"], [], ["Game A", "Game B"], id="both"),
    ],
)
async def test_removed_games_can_be_picked_again(
    hass: HomeAssistant,
    service_multiple: Mock,
    hass_storage: dict[str, Any],
    removed: list[str],
    kept: list[dict[str, str]],
    expected_options: list[str],
) -> None:
    """Test removing games keeps the others and offers the removed games again."""
    # Arrange
    hass_storage[STORAGE_KEY] = stored_wish_list([GAME_A, GAME_B])
    await setup_wish_list(hass, service_multiple)

    # Act
    await hass.services.async_call(
        TODO_DOMAIN,
        TodoServices.REMOVE_ITEM,
        {ATTR_ENTITY_ID: TODO_ENTITY_ID, ATTR_ITEM: removed},
        blocking=True,
    )

    # Assert
    assert hass_storage[STORAGE_KEY]["data"] == kept
    assert (
        hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == expected_options
    )
