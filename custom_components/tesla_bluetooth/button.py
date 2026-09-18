"""Button platform for Tesla Local HA Commands."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import TeslaBluetoothConfigEntry
from .entity import TeslaBluetoothStateEntity
from .helpers import handle_vehicle_command
from .models import TeslaBluetoothData

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeslaBluetoothConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tesla Local HA Commands buttons."""
    async_add_entities([TeslaBluetoothUnlockChargeCableButton(entry.runtime_data)])


class TeslaBluetoothUnlockChargeCableButton(TeslaBluetoothStateEntity, ButtonEntity):
    """Button that releases a connected charge cable."""

    def __init__(self, data: TeslaBluetoothData) -> None:
        """Initialize the charge cable release button."""
        super().__init__(data, "unlock_charge_cable")

    def _async_update_attrs(self) -> None:
        """Update button attributes."""

    @property
    def available(self) -> bool:
        """Keep the button callable so it can reconnect after a BLE drop."""
        return True

    async def async_press(self) -> None:
        """Release the charge-port latch over Bluetooth."""
        # This is a VCSEC command and reconnects to BLE when needed. It does not
        # need the slower infotainment wake-up sequence.
        await handle_vehicle_command(self.vehicle.charge_port_door_open())
