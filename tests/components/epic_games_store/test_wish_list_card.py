"""Tests for serving and registering the wish list card in the frontend."""

from http import HTTPStatus
from unittest.mock import Mock

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.core import HomeAssistant

from .common import setup_platform

from tests.typing import ClientSessionGenerator

CARD_URL = "/epic_games_store/wish-list-card.js"


async def test_card_is_served(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    service_multiple: Mock,
) -> None:
    """Test the card script is served on its URL."""
    # Arrange
    await setup_platform(hass, SENSOR_DOMAIN)
    client = await hass_client_no_auth()

    # Act
    response = await client.get(CARD_URL)

    # Assert
    assert response.status == HTTPStatus.OK
    assert "hass-more-info" in await response.text()


async def test_only_the_card_is_served(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    service_multiple: Mock,
) -> None:
    """Test no other file next to the card is reachable."""
    # Arrange
    await setup_platform(hass, SENSOR_DOMAIN)
    client = await hass_client_no_auth()

    # Act
    response = await client.get("/epic_games_store/manifest.json")

    # Assert
    assert response.status == HTTPStatus.NOT_FOUND


async def test_card_is_loaded_by_frontend(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the card URL is added to the extra modules the frontend loads."""
    # Act
    await setup_platform(hass, SENSOR_DOMAIN)

    # Assert
    assert CARD_URL in hass.data[DATA_EXTRA_MODULE_URL].urls
