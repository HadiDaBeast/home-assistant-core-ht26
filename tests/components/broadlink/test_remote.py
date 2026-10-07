"""Tests for Broadlink remotes."""

import asyncio
from base64 import b64decode
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

from broadlink.exceptions import BroadlinkException, ReadError
from freezegun.api import FrozenDateTimeFactory
import pytest

from homeassistant.components.broadlink.const import DOMAIN
from homeassistant.components.broadlink.remote import BroadlinkRemote
from homeassistant.components.broadlink.updater import BroadlinkRMUpdateManager
from homeassistant.components.remote import (
    DOMAIN as REMOTE_DOMAIN,
    SERVICE_LEARN_COMMAND,
    SERVICE_SEND_COMMAND,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
)
from homeassistant.const import (
    ATTR_FRIENDLY_NAME,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from . import get_device

from tests.common import async_fire_time_changed, async_get_persistent_notifications

REMOTE_DEVICES = ["Entrance", "Living Room", "Office", "Garage"]

IR_PACKET = (
    "JgBGAJKVETkRORA6ERQRFBEUERQRFBE5ETkQOhAVEBUQFREUEBUQ"
    "OhEUERQRORE5EBURFBA6EBUQOhE5EBUQFRA6EDoRFBEADQUAAA=="
)


async def test_remote_setup_works(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test a successful setup with all remotes."""
    for device in map(get_device, REMOTE_DEVICES):
        mock_setup = await device.setup_entry(hass)

        device_entry = device_registry.async_get_device_by_identifier(
            (DOMAIN, mock_setup.entry.unique_id), mock_setup.entry.entry_id
        )
        entries = er.async_entries_for_device(entity_registry, device_entry.id)
        remotes = [entry for entry in entries if entry.domain == Platform.REMOTE]
        assert len(remotes) == 1

        remote = remotes[0]
        assert (
            hass.states.get(remote.entity_id).attributes[ATTR_FRIENDLY_NAME]
            == device.name
        )
        assert hass.states.get(remote.entity_id).state == STATE_ON
        assert mock_setup.api.auth.call_count == 1


async def test_remote_send_command(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test sending a command with all remotes."""
    for device in map(get_device, REMOTE_DEVICES):
        mock_setup = await device.setup_entry(hass)

        device_entry = device_registry.async_get_device_by_identifier(
            (DOMAIN, mock_setup.entry.unique_id), mock_setup.entry.entry_id
        )
        entries = er.async_entries_for_device(entity_registry, device_entry.id)
        remotes = [entry for entry in entries if entry.domain == Platform.REMOTE]
        assert len(remotes) == 1

        remote = remotes[0]
        await hass.services.async_call(
            REMOTE_DOMAIN,
            SERVICE_SEND_COMMAND,
            {"entity_id": remote.entity_id, "command": "b64:" + IR_PACKET},
            blocking=True,
        )

        assert mock_setup.api.send_data.call_count == 1
        assert mock_setup.api.send_data.call_args == call(b64decode(IR_PACKET))
        assert mock_setup.api.auth.call_count == 1


@pytest.mark.parametrize(
    ("error", "ticks_to_unavailable"),
    [
        # OSError flips availability on the first failure (fast path).
        (OSError("connection refused"), 1),
        # A generic BroadlinkException keeps the entity available across the
        # first three failed cycles and only flips once SCAN_INTERVAL * 3 has
        # elapsed since the last successful update.
        (BroadlinkException("update failed"), 4),
    ],
)
async def test_remote_availability(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
    error: Exception,
    ticks_to_unavailable: int,
) -> None:
    """Test the remote becomes unavailable on disconnect and recovers on reconnect."""
    device = get_device("Garage")
    mock_setup = await device.setup_entry(hass)

    device_entry = device_registry.async_get_device_by_identifier(
        (DOMAIN, mock_setup.entry.unique_id), mock_setup.entry.entry_id
    )
    entries = er.async_entries_for_device(entity_registry, device_entry.id)
    remote = next(entry for entry in entries if entry.domain == Platform.REMOTE)

    assert hass.states.get(remote.entity_id).state == STATE_ON

    mock_setup.api.check_sensors.side_effect = error

    for _ in range(ticks_to_unavailable - 1):
        freezer.tick(BroadlinkRMUpdateManager.SCAN_INTERVAL)
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
        assert hass.states.get(remote.entity_id).state == STATE_ON

    freezer.tick(BroadlinkRMUpdateManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert hass.states.get(remote.entity_id).state == STATE_UNAVAILABLE

    mock_setup.api.check_sensors.side_effect = None

    freezer.tick(BroadlinkRMUpdateManager.SCAN_INTERVAL)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    assert hass.states.get(remote.entity_id).state == STATE_ON


async def test_remote_turn_off_turn_on(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Test we do not send commands if the remotes are off."""
    for device in map(get_device, REMOTE_DEVICES):
        mock_setup = await device.setup_entry(hass)

        device_entry = device_registry.async_get_device_by_identifier(
            (DOMAIN, mock_setup.entry.unique_id), mock_setup.entry.entry_id
        )
        entries = er.async_entries_for_device(entity_registry, device_entry.id)
        remotes = [entry for entry in entries if entry.domain == Platform.REMOTE]
        assert len(remotes) == 1

        remote = remotes[0]
        await hass.services.async_call(
            REMOTE_DOMAIN,
            SERVICE_TURN_OFF,
            {"entity_id": remote.entity_id},
            blocking=True,
        )
        assert hass.states.get(remote.entity_id).state == STATE_OFF

        await hass.services.async_call(
            REMOTE_DOMAIN,
            SERVICE_SEND_COMMAND,
            {"entity_id": remote.entity_id, "command": "b64:" + IR_PACKET},
            blocking=True,
        )
        assert mock_setup.api.send_data.call_count == 0

        await hass.services.async_call(
            REMOTE_DOMAIN,
            SERVICE_TURN_ON,
            {"entity_id": remote.entity_id},
            blocking=True,
        )
        assert hass.states.get(remote.entity_id).state == STATE_ON

        await hass.services.async_call(
            REMOTE_DOMAIN,
            SERVICE_SEND_COMMAND,
            {"entity_id": remote.entity_id, "command": "b64:" + IR_PACKET},
            blocking=True,
        )
        assert mock_setup.api.send_data.call_count == 1
        assert mock_setup.api.send_data.call_args == call(b64decode(IR_PACKET))
        assert mock_setup.api.auth.call_count == 1


def _fake_sleep(freezer: FrozenDateTimeFactory):
    """Return an asyncio.sleep replacement that advances the clock on 1 s polls."""
    real_sleep = asyncio.sleep

    async def fake_sleep(delay: float) -> None:
        if delay == 1:
            freezer.tick(1)
            # Yield to the event loop so asyncio.timeout can expire.
            await real_sleep(0)
            return
        await real_sleep(delay)

    return fake_sleep


async def _setup_learning_remote(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
):
    """Set up a remote and return its mock setup and entity id."""
    device = get_device("Entrance")
    mock_setup = await device.setup_entry(hass)
    entity_id = next(
        entry.entity_id
        for entry in er.async_entries_for_config_entry(
            entity_registry, mock_setup.entry.entry_id
        )
        if entry.domain == Platform.REMOTE
    )
    mock_setup.api.enter_learning.return_value = None
    return mock_setup, entity_id


async def _learn_turn_on(hass: HomeAssistant, entity_id: str) -> None:
    """Call the learn_command service for the "tv" / "turn_on" command."""
    await hass.services.async_call(
        REMOTE_DOMAIN,
        SERVICE_LEARN_COMMAND,
        {
            "entity_id": entity_id,
            "device": "tv",
            "command": "turn_on",
            "command_type": "ir",
        },
        blocking=True,
    )


async def test_remote_learn_ir_command_retries_on_read_error(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
    hass_storage: dict,
) -> None:
    """Test a learned IR code is stored after the device first reports no data."""
    mock_setup, entity_id = await _setup_learning_remote(hass, entity_registry)
    mock_setup.api.check_data.side_effect = [ReadError(), b64decode(IR_PACKET)]

    with patch(
        "homeassistant.components.broadlink.remote.asyncio.sleep",
        _fake_sleep(freezer),
    ):
        await _learn_turn_on(hass, entity_id)

    assert mock_setup.api.check_data.call_count == 2
    codes_key = f"broadlink_remote_{mock_setup.entry.unique_id}_codes"
    assert hass_storage[codes_key]["data"] == {"tv": {"turn_on": IR_PACKET}}


async def test_remote_poll_ir_code_retries_until_code(
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test the IR polling helper keeps polling until the device returns a code."""
    api = MagicMock()
    api.check_data.side_effect = [ReadError(), ReadError(), b64decode(IR_PACKET)]
    device = SimpleNamespace(
        api=api, async_request=AsyncMock(side_effect=lambda func, *args: func(*args))
    )
    remote = SimpleNamespace(_device=device)

    with patch(
        "homeassistant.components.broadlink.remote.asyncio.sleep",
        _fake_sleep(freezer),
    ):
        code = await BroadlinkRemote._async_poll_ir_code(remote)

    assert code == IR_PACKET
    assert api.check_data.call_count == 3


async def test_remote_learn_ir_command_timeout_dismisses_notification(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
    hass_storage: dict,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a learning timeout is logged, stores nothing and dismisses the notification."""
    mock_setup, entity_id = await _setup_learning_remote(hass, entity_registry)
    mock_setup.api.check_data.side_effect = ReadError()

    with patch(
        "homeassistant.components.broadlink.remote.asyncio.sleep",
        _fake_sleep(freezer),
    ):
        await _learn_turn_on(hass, entity_id)

    assert "Failed to learn 'turn_on'" in caplog.text
    assert "No infrared code received within 30.0 seconds" in caplog.text
    assert "learn_command" not in async_get_persistent_notifications(hass)
    codes_key = f"broadlink_remote_{mock_setup.entry.unique_id}_codes"
    assert codes_key not in hass_storage


async def test_remote_learn_ir_command_device_timeout_is_not_relabelled(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    freezer: FrozenDateTimeFactory,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test a timeout raised by the device keeps its own message."""
    mock_setup, entity_id = await _setup_learning_remote(hass, entity_registry)
    mock_setup.api.check_data.side_effect = TimeoutError("device socket timed out")

    with patch(
        "homeassistant.components.broadlink.remote.asyncio.sleep",
        _fake_sleep(freezer),
    ):
        await _learn_turn_on(hass, entity_id)

    assert "Failed to learn 'turn_on': device socket timed out" in caplog.text
    assert "No infrared code received" not in caplog.text
