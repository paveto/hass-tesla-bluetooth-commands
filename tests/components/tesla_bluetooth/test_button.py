"""Tests for Tesla Local HA Commands buttons."""

from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.tesla_bluetooth.button import (
    BUTTONS,
    TeslaBluetoothUnlockChargeCableButton,
)

COMMAND_OK = {"response": {"result": True, "reason": ""}}


async def test_unlock_charge_cable_button() -> None:
    """Test releasing the charge-port latch."""
    vehicle = MagicMock()
    vehicle.vin = "5YJ3E1EA7KF000000"
    vehicle.model = "Model 3"
    vehicle.charge_port_door_open = AsyncMock(return_value=COMMAND_OK)
    vehicle.disconnect = AsyncMock(return_value=True)

    data = MagicMock()
    data.vehicle = vehicle
    data.coordinators.state = MagicMock()
    data.coordinators.polling_enabled = False

    entity = TeslaBluetoothUnlockChargeCableButton(data)
    entity.wake_up_if_asleep = AsyncMock()
    assert entity.available
    await entity.async_press()

    vehicle.charge_port_door_open.assert_awaited_once_with()
    vehicle.disconnect.assert_awaited_once_with()
    entity.wake_up_if_asleep.assert_not_awaited()


def test_button_catalog_has_unique_commands() -> None:
    """Test that the complete command catalog has stable unique entity keys."""
    keys = [description.key for description in BUTTONS]

    assert len(BUTTONS) >= 49
    assert len(keys) == len(set(keys))
    assert "charge_port_door_open" in {description.command for description in BUTTONS}
    assert "erase_user_data" not in {description.command for description in BUTTONS}
