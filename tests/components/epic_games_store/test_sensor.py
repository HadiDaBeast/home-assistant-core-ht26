"""Tests for the Epic Games Store wish list sensor."""

from unittest.mock import Mock

from homeassistant.components.epic_games_store.const import DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.const import CONF_COUNTRY, CONF_LANGUAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.setup import async_setup_component

from .common import setup_platform
from .const import MOCK_COUNTRY, MOCK_LANGUAGE

from tests.common import MockConfigEntry

ENTITY_ID = "sensor.epic_games_store_wish_list"


async def test_wish_list_sensor_state(
    hass: HomeAssistant, service_multiple: Mock
) -> None:
    """Test the wish list sensor is created with its name, icon and state."""
    # Act
    await setup_platform(hass, SENSOR_DOMAIN)

    # Assert
    state = hass.states.get(ENTITY_ID)
    assert state.name == "Epic Games Store Wish List"
    assert state.attributes["icon"] == "mdi:playlist-star"
    assert state.state == "1"


async def test_wish_list_registry_entry_matches_card(
    hass: HomeAssistant, entity_registry: er.EntityRegistry, service_multiple: Mock
) -> None:
    """Test the registry entry has the platform and translation key the card looks for."""
    # Act
    entry = await setup_platform(hass, SENSOR_DOMAIN)

    # Assert
    registry_entry = entity_registry.async_get(ENTITY_ID)
    assert registry_entry.platform == DOMAIN
    assert registry_entry.translation_key == "wish_list"
    assert registry_entry.unique_id == f"{entry.entry_id}-wish-list"


async def test_wish_list_on_same_device_as_calendars(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    service_multiple: Mock,
) -> None:
    """Test the integration's own platforms put the sensor on the calendars' device."""
    # Arrange
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_LANGUAGE: MOCK_LANGUAGE, CONF_COUNTRY: MOCK_COUNTRY},
    )
    entry.add_to_hass(hass)

    # Act
    assert await async_setup_component(hass, DOMAIN, {})
    await hass.async_block_till_done()

    # Assert
    devices = dr.async_entries_for_config_entry(device_registry, entry.entry_id)
    entities = er.async_entries_for_config_entry(entity_registry, entry.entry_id)
    assert len(devices) == 1
    assert {entity.device_id for entity in entities} == {devices[0].id}
    assert len(entities) == 3
