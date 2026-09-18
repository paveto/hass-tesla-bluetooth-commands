"""Tesla Bluetooth helper functions."""

from collections.abc import Awaitable
from typing import Any

from bleak.exc import BleakError
from tesla_fleet_api.exceptions import TeslaFleetError
from tesla_fleet_api.tesla.vehicle.bluetooth import VehicleBluetooth

from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, LOGGER


async def handle_vehicle_command(
    command: Awaitable,
    *,
    vehicle: VehicleBluetooth | None = None,
    disconnect_after: bool = False,
) -> bool:
    """Handle a vehicle command."""
    try:
        result: dict[str, Any] = await command
    except TimeoutError as e:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="command_timeout",
        ) from e
    except TeslaFleetError as e:
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="command_failed",
            translation_placeholders={"message": e.message},
        ) from e
    finally:
        if disconnect_after and vehicle is not None:
            try:
                await vehicle.disconnect()
            except (BleakError, TimeoutError) as err:
                LOGGER.debug("Failed to disconnect idle BLE link: %s", err)
    if (response := result.get("response")) is None:
        if error := result.get("error"):
            # No response with error
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_error",
                translation_placeholders={"error": error},
            )
        # No response without error (unexpected)
        raise HomeAssistantError(f"Unknown response: {response}")
    if (result := response.get("result")) is not True:
        if reason := response.get("reason"):
            if reason in ("already_set", "not_charging", "requested"):
                # Reason is acceptable
                return result
            # Result of false with reason
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_reason",
                translation_placeholders={"reason": reason},
            )
        # Result of false without reason (unexpected)
        raise HomeAssistantError(
            translation_domain=DOMAIN,
            translation_key="command_no_reason",
        )
    # Response with result of true
    return result
