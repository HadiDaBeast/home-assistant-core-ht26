"""Unit tests for the Epic Games Store wishlist coordinator.

SUT: EGSWishlistUpdateCoordinator. The Epic Games Store API is replaced by a
stub (pre-recorded answers); where the interaction itself is asserted, the
same double is used as a mock.
"""

from unittest.mock import Mock

import pytest

from homeassistant.components.epic_games_store.const import DOMAIN
from homeassistant.components.epic_games_store.coordinator import (
    EGSWishlistUpdateCoordinator,
)
from homeassistant.const import CONF_COUNTRY, CONF_LANGUAGE
from homeassistant.core import HomeAssistant

from .const import MOCK_COUNTRY, MOCK_LANGUAGE

from tests.common import MockConfigEntry


def _store_response(elements: list[dict[str, str]]) -> dict:
    """Wrap catalog elements the way fetch_store_games returns them."""
    return {"data": {"Catalog": {"searchStore": {"elements": elements}}}}


def _create_coordinator(hass: HomeAssistant) -> EGSWishlistUpdateCoordinator:
    """Create the coordinator for a config entry, without setting up the integration."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LANGUAGE: MOCK_LANGUAGE, CONF_COUNTRY: MOCK_COUNTRY},
    )
    entry.add_to_hass(hass)
    return EGSWishlistUpdateCoordinator(hass, entry)


async def test_api_created_with_entry_language_and_country(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the API client is created with the language and country of the entry."""
    # Act
    _create_coordinator(hass)

    # Assert
    service_multiple.assert_called_once_with(MOCK_LANGUAGE, MOCK_COUNTRY)


async def test_refresh_fetches_store_games_for_entry_country(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the catalog is fetched for the country of the entry."""
    # Arrange
    fetch_store_games = service_multiple.return_value.fetch_store_games
    fetch_store_games.return_value = _store_response([])
    coordinator = _create_coordinator(hass)

    # Act
    await coordinator.async_refresh()

    # Assert
    fetch_store_games.assert_called_once_with(
        count=30, start=0, allow_countries=MOCK_COUNTRY
    )


@pytest.mark.parametrize(
    "elements",
    [
        [],
        [{"title": "Game 1", "productSlug": "game-1"}],
    ],
    ids=["zero_games", "one_game"],
)
async def test_refresh_stores_catalog_elements(
    hass: HomeAssistant, service_multiple: Mock, elements: list[dict[str, str]]
) -> None:
    """Test the catalog elements are extracted from the response, for 0 and 1 games."""
    # Arrange
    service_multiple.return_value.fetch_store_games.return_value = _store_response(
        elements
    )
    coordinator = _create_coordinator(hass)

    # Act
    await coordinator.async_refresh()

    # Assert
    assert coordinator.data == elements
