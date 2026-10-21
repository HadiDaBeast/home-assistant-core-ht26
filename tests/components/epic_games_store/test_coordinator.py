"""Unit tests for the Epic Games Store wishlist coordinator.

SUT: EGSWishlistUpdateCoordinator. The Epic Games Store API is replaced by a
stub (pre-recorded answers); where the interaction itself is asserted, the
same double is used as a mock. Many games are covered by
test_wishlist_coordinator.py.
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


@pytest.mark.parametrize(
    "product_mapping",
    [
        {},
        {"namespace-1": "game-slug-1"},
    ],
    ids=["zero_games", "one_game"],
)
async def test_refresh_stores_product_mapping(
    hass: HomeAssistant, service_multiple: Mock, product_mapping: dict[str, str]
) -> None:
    """Test the product mapping from the API is stored unchanged, for 0 and 1 games."""
    # Arrange
    service_multiple.return_value.get_product_mapping.return_value = product_mapping
    coordinator = _create_coordinator(hass)

    # Act
    await coordinator.async_refresh()

    # Assert
    assert coordinator.data == product_mapping
