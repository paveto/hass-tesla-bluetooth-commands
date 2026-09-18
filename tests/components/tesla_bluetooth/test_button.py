"""Tests for Tesla Local HA Commands buttons."""

from unittest.mock import AsyncMock, MagicMock

from homeassistant.components.tesla_bluetooth.button import (
    TeslaBluetoothUnlockChargeCableButton,
)

COMMAND_OK = {"response": {"result": True, "reason": ""}}


async def test_unlock_charge_cable_button() -> None:
    """Test releasing the charge-port latch."""
    vehicle = MagicMock()
    vehicle.vin = "5YJ3E1EA7KF000000"
    vehicle.model = "Model 3"
    vehicle.charge_port_door_open = AsyncMock(return_value=COMMAND_OK)

    data = MagicMock()
    data.vehicle = vehicle
    data.coordinators.state = MagicMock()

    entity = TeslaBluetoothUnlockChargeCableButton(data)
    entity.wake_up_if_asleep = AsyncMock()
    assert entity.available
    await entity.async_press()

    vehicle.charge_port_door_open.assert_awaited_once_with()
    entity.wake_up_if_asleep.assert_not_awaited()
