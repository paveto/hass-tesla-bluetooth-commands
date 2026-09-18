"""Button platform for Tesla Local HA Commands."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import TeslaBluetoothConfigEntry
from .entity import TeslaBluetoothStateEntity
from .helpers import handle_vehicle_command
from .models import TeslaBluetoothData

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class TeslaBluetoothButtonDescription(ButtonEntityDescription):
    """Describe a zero-argument local Tesla command."""

    command: str


# Every useful zero-argument action in tesla-fleet-api 1.14.0. Destructive and
# security-sensitive maintenance actions remain available but are disabled by
# default so they cannot accidentally land on a dashboard.
BUTTONS: tuple[TeslaBluetoothButtonDescription, ...] = (
    TeslaBluetoothButtonDescription(
        key="unlock_charge_cable",
        name="Unlock charge cable",
        icon="mdi:ev-plug-tesla",
        command="charge_port_door_open",
    ),
    TeslaBluetoothButtonDescription(
        key="charge_port_close",
        name="Close charge port",
        icon="mdi:ev-plug-tesla",
        command="charge_port_door_close",
    ),
    TeslaBluetoothButtonDescription(
        key="charge_start",
        name="Start charging",
        icon="mdi:ev-station",
        command="charge_start",
    ),
    TeslaBluetoothButtonDescription(
        key="charge_stop",
        name="Stop charging",
        icon="mdi:ev-station",
        command="charge_stop",
    ),
    TeslaBluetoothButtonDescription(
        key="charge_standard",
        name="Standard charge limit",
        icon="mdi:battery-80",
        command="charge_standard",
    ),
    TeslaBluetoothButtonDescription(
        key="charge_max_range",
        name="Maximum charge limit",
        icon="mdi:battery-charging-100",
        command="charge_max_range",
    ),
    TeslaBluetoothButtonDescription(
        key="lock", name="Lock doors", icon="mdi:car-door-lock", command="door_lock"
    ),
    TeslaBluetoothButtonDescription(
        key="unlock", name="Unlock doors", icon="mdi:car-door", command="door_unlock"
    ),
    TeslaBluetoothButtonDescription(
        key="open_front_driver_door",
        name="Open front driver door",
        icon="mdi:car-door",
        command="open_front_driver_door",
    ),
    TeslaBluetoothButtonDescription(
        key="close_front_driver_door",
        name="Close front driver door",
        icon="mdi:car-door-lock",
        command="close_front_driver_door",
    ),
    TeslaBluetoothButtonDescription(
        key="open_front_passenger_door",
        name="Open front passenger door",
        icon="mdi:car-door",
        command="open_front_passenger_door",
    ),
    TeslaBluetoothButtonDescription(
        key="close_front_passenger_door",
        name="Close front passenger door",
        icon="mdi:car-door-lock",
        command="close_front_passenger_door",
    ),
    TeslaBluetoothButtonDescription(
        key="open_rear_driver_door",
        name="Open rear driver door",
        icon="mdi:car-door",
        command="open_rear_driver_door",
    ),
    TeslaBluetoothButtonDescription(
        key="close_rear_driver_door",
        name="Close rear driver door",
        icon="mdi:car-door-lock",
        command="close_rear_driver_door",
    ),
    TeslaBluetoothButtonDescription(
        key="open_rear_passenger_door",
        name="Open rear passenger door",
        icon="mdi:car-door",
        command="open_rear_passenger_door",
    ),
    TeslaBluetoothButtonDescription(
        key="close_rear_passenger_door",
        name="Close rear passenger door",
        icon="mdi:car-door-lock",
        command="close_rear_passenger_door",
    ),
    TeslaBluetoothButtonDescription(
        key="climate_start",
        name="Start climate",
        icon="mdi:fan",
        command="auto_conditioning_start",
    ),
    TeslaBluetoothButtonDescription(
        key="climate_stop",
        name="Stop climate",
        icon="mdi:fan-off",
        command="auto_conditioning_stop",
    ),
    TeslaBluetoothButtonDescription(
        key="flash_lights",
        name="Flash lights",
        icon="mdi:car-light-high",
        command="flash_lights",
    ),
    TeslaBluetoothButtonDescription(
        key="honk_horn", name="Honk horn", icon="mdi:bullhorn", command="honk_horn"
    ),
    TeslaBluetoothButtonDescription(
        key="dashcam_save_clip",
        name="Save dashcam clip",
        icon="mdi:video",
        command="dashcam_save_clip",
    ),
    TeslaBluetoothButtonDescription(
        key="media_play_pause",
        name="Media play or pause",
        icon="mdi:play-pause",
        command="media_toggle_playback",
    ),
    TeslaBluetoothButtonDescription(
        key="media_next_track",
        name="Next track",
        icon="mdi:skip-next",
        command="media_next_track",
    ),
    TeslaBluetoothButtonDescription(
        key="media_previous_track",
        name="Previous track",
        icon="mdi:skip-previous",
        command="media_prev_track",
    ),
    TeslaBluetoothButtonDescription(
        key="media_next_favorite",
        name="Next favorite",
        icon="mdi:heart-arrow-right",
        command="media_next_fav",
    ),
    TeslaBluetoothButtonDescription(
        key="media_previous_favorite",
        name="Previous favorite",
        icon="mdi:heart-arrow-left",
        command="media_prev_fav",
    ),
    TeslaBluetoothButtonDescription(
        key="media_volume_up",
        name="Volume up",
        icon="mdi:volume-plus",
        command="media_volume_up",
    ),
    TeslaBluetoothButtonDescription(
        key="media_volume_down",
        name="Volume down",
        icon="mdi:volume-minus",
        command="media_volume_down",
    ),
    TeslaBluetoothButtonDescription(
        key="remote_start",
        name="Enable keyless driving",
        icon="mdi:key-wireless",
        command="remote_start_drive",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="homelink",
        name="Trigger Homelink",
        icon="mdi:garage-open",
        command="trigger_homelink",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="wake",
        name="Wake vehicle",
        icon="mdi:power",
        command="wake_up",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="ping",
        name="Ping vehicle",
        icon="mdi:bluetooth-connect",
        command="ping",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="cancel_software_update",
        name="Cancel software update",
        icon="mdi:update",
        command="cancel_software_update",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="start_light_show",
        name="Start light show",
        icon="mdi:lightbulb-group",
        command="start_light_show",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="stop_light_show",
        name="Stop light show",
        icon="mdi:lightbulb-group-off",
        command="stop_light_show",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="boombox",
        name="Play boombox sound",
        icon="mdi:volume-high",
        command="remote_boombox",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="open_tonneau",
        name="Open tonneau",
        icon="mdi:truck-cargo-container",
        command="open_tonneau",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="close_tonneau",
        name="Close tonneau",
        icon="mdi:truck-cargo-container",
        command="close_tonneau",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="stop_tonneau",
        name="Stop tonneau",
        icon="mdi:stop",
        command="stop_tonneau",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="auto_secure_vehicle",
        name="Secure vehicle",
        icon="mdi:shield-car",
        command="auto_secure_vehicle",
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="cancel_soh_test",
        name="Cancel battery health test",
        icon="mdi:battery-heart-variant",
        command="cancel_soh_test",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="reset_pin_to_drive",
        name="Reset PIN to drive",
        icon="mdi:form-textbox-password",
        command="reset_pin_to_drive_admin",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="clear_pin_to_drive",
        name="Clear PIN to drive",
        icon="mdi:form-textbox-password",
        command="clear_pin_to_drive_admin",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="reset_pin_to_drive_legacy",
        name="Reset PIN to drive (legacy)",
        icon="mdi:form-textbox-password",
        command="reset_pin_to_drive_pin",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="clear_speed_limit_pin",
        name="Clear speed limit PIN",
        icon="mdi:speedometer",
        command="speed_limit_clear_pin_admin",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="clear_parental_controls_pin",
        name="Clear parental controls PIN",
        icon="mdi:account-child",
        command="parental_controls_clear_pin_admin",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="reset_valet_pin",
        name="Reset valet PIN",
        icon="mdi:account-key",
        command="reset_valet_pin",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="format_usb",
        name="Format USB drive",
        icon="mdi:usb-flash-drive",
        command="format_usb",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
    TeslaBluetoothButtonDescription(
        key="delete_dashcam_clips",
        name="Delete dashcam clips",
        icon="mdi:delete",
        command="delete_dashcam_clips",
        entity_category=EntityCategory.CONFIG,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeslaBluetoothConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Tesla Local HA Commands buttons."""
    async_add_entities(
        TeslaBluetoothCommandButton(entry.runtime_data, description)
        for description in BUTTONS
    )


class TeslaBluetoothCommandButton(TeslaBluetoothStateEntity, ButtonEntity):
    """A button that runs a local zero-argument command."""

    entity_description: TeslaBluetoothButtonDescription

    def __init__(
        self, data: TeslaBluetoothData, description: TeslaBluetoothButtonDescription
    ) -> None:
        """Initialize a command button."""
        self.entity_description = description
        super().__init__(data, description.key)
        self._attr_translation_key = None

    def _async_update_attrs(self) -> None:
        """Buttons do not expose state."""

    @property
    def available(self) -> bool:
        """Commands reconnect on demand even when polling is disabled."""
        return True

    async def async_press(self) -> None:
        """Run the command and release BLE when polling is disabled."""
        command = getattr(self.vehicle, self.entity_description.command)
        await handle_vehicle_command(
            command(),
            vehicle=self.vehicle,
            disconnect_after=not self.coordinators.polling_enabled,
        )


class TeslaBluetoothUnlockChargeCableButton(TeslaBluetoothCommandButton):
    """Compatibility class for the charge-cable button."""

    def __init__(self, data: TeslaBluetoothData) -> None:
        """Initialize the charge-cable release button."""
        super().__init__(data, BUTTONS[0])
