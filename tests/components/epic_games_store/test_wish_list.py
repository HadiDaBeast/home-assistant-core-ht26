"""Integration tests for the Epic Games Store wish list storage and lifecycle."""

from typing import Any
from unittest.mock import Mock, patch

import pytest

from homeassistant.components.epic_games_store.const import DOMAIN
from homeassistant.components.select import (
    ATTR_OPTION,
    ATTR_OPTIONS,
    DOMAIN as SELECT_DOMAIN,
    SERVICE_SELECT_OPTION,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_COUNTRY,
    CONF_LANGUAGE,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant

from .const import MOCK_COUNTRY, MOCK_LANGUAGE
from .wish_list_common import (
    GAME_A,
    SELECT_ENTITY_ID,
    STORAGE_KEY,
    TODO_ENTITY_ID,
    setup_wish_list,
)

from tests.common import MockConfigEntry


async def _pick(hass: HomeAssistant, entity_id: str, title: str) -> None:
    """Pick a game in the given wish list picker."""
    await hass.services.async_call(
        SELECT_DOMAIN,
        SERVICE_SELECT_OPTION,
        {ATTR_ENTITY_ID: entity_id, ATTR_OPTION: title},
        blocking=True,
    )


# Lifecycle: the wish list survives a reload
async def test_wish_list_survives_reload(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the wish list is loaded from storage again after a reload."""
    # Arrange
    entry = await setup_wish_list(hass, service_multiple)
    await _pick(hass, SELECT_ENTITY_ID, "Game A")

    # Act
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()

    # Assert
    assert hass.states.get(TODO_ENTITY_ID).state == "1"
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == ["Game B"]


# Lifecycle: unloading detaches the entities from the wish list
async def test_unload_entry_detaches_wish_list_entities(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test unloading makes the entities unavailable and stops listening to the wish list."""
    # Arrange
    entry = await setup_wish_list(hass, service_multiple)
    wish_list = entry.runtime_data.wish_list

    # Act
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()

    # Assert
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert hass.states.get(SELECT_ENTITY_ID).state == STATE_UNAVAILABLE
    assert hass.states.get(TODO_ENTITY_ID).state == STATE_UNAVAILABLE
    # White-box on purpose: a leaked listener is not observable, because writes
    # to removed entities are ignored, so the subscription is checked directly
    assert not wish_list._listeners


# Storage: a failed save leaves the entities unchanged
async def test_failed_save_does_not_update_entities(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the entities keep their state when the wish list cannot be saved."""
    # Arrange
    await setup_wish_list(hass, service_multiple)

    # Act
    with (
        patch(
            "homeassistant.components.epic_games_store.wish_list.Store.async_save",
            side_effect=OSError,
        ),
        pytest.raises(OSError),
    ):
        await _pick(hass, SELECT_ENTITY_ID, "Game A")

    # Assert
    assert hass.states.get(SELECT_ENTITY_ID).attributes[ATTR_OPTIONS] == [
        "Game A",
        "Game B",
    ]


# Setup: a failed first catalog fetch retries the setup
async def test_catalog_fetch_failure_retries_setup(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test setup is retried, without entities, when the first catalog fetch fails."""
    # Arrange
    service_multiple.return_value.get_product_mapping.side_effect = Exception

    # Act
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LANGUAGE: MOCK_LANGUAGE, CONF_COUNTRY: MOCK_COUNTRY},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    # Assert
    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert hass.states.get(SELECT_ENTITY_ID) is None


# Storage: removing the entry deletes the stored wish list
async def test_removing_entry_deletes_stored_wish_list(
    hass: HomeAssistant, service_multiple: Mock, hass_storage: dict[str, Any]
) -> None:
    """Test the stored wish list is deleted together with the config entry."""
    # Arrange
    entry = await setup_wish_list(hass, service_multiple)
    await _pick(hass, SELECT_ENTITY_ID, "Game A")
    assert hass_storage[STORAGE_KEY]["data"] == [GAME_A]

    # Act
    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    # Assert
    assert STORAGE_KEY not in hass_storage
