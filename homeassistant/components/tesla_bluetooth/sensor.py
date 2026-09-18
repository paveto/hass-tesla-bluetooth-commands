"""Sensor platform exposing every Bluetooth vehicle-data field."""

from __future__ import annotations

from dataclasses import dataclass

from google.protobuf.descriptor import FieldDescriptor
from google.protobuf.message import Message
from tesla_fleet_api.tesla.bluetooth import toDict
from tesla_fleet_api.tesla.vehicle.bluetooth import (
    AlertState,
    ChargeScheduleState,
    ChargeState,
    ChildPresenceDetectionState,
    ClimateState,
    ClosuresState,
    DisplayState,
    DriveState,
    GuiSettings,
    LightShowState,
    LocationState,
    MediaDetailState,
    MediaState,
    ParentalControlsState,
    ParkedAccessoryState,
    PreconditioningScheduleState,
    SoftwareUpdateState,
    SohState,
    SuspensionState,
    TirePressureState,
    VehicleConfig,
    VehicleDetailState,
    VehicleState,
    VehicleStatus,
)

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import TeslaBluetoothConfigEntry
from .coordinator import TeslaBluetoothCoordinator
from .entity import TeslaBluetoothEntity
from .models import TeslaBluetoothData

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class TeslaBluetoothFieldDescription(SensorEntityDescription):
    """Describe one top-level protobuf field."""

    coordinator_name: str
    field: FieldDescriptor


ENDPOINTS: tuple[tuple[str, type[Message], str], ...] = (
    ("state", VehicleStatus, "Vehicle security"),
    ("charge", ChargeState, "Charge"),
    ("climate", ClimateState, "Climate"),
    ("closures", ClosuresState, "Closures"),
    ("drive", DriveState, "Drive"),
    ("location", LocationState, "Location"),
    ("charge_schedule", ChargeScheduleState, "Charge schedule"),
    (
        "preconditioning_schedule",
        PreconditioningScheduleState,
        "Preconditioning schedule",
    ),
    ("tire_pressure", TirePressureState, "Tire pressure"),
    ("media", MediaState, "Media"),
    ("media_detail", MediaDetailState, "Media detail"),
    ("software_update", SoftwareUpdateState, "Software update"),
    ("parental_controls", ParentalControlsState, "Parental controls"),
    ("gui_settings", GuiSettings, "GUI settings"),
    ("parked_accessory", ParkedAccessoryState, "Parked accessory"),
    ("legacy_vehicle", VehicleState, "Vehicle"),
    ("vehicle_config", VehicleConfig, "Vehicle config"),
    ("soh", SohState, "Battery health"),
    ("vehicle_detail", VehicleDetailState, "Vehicle detail"),
    ("display", DisplayState, "Display"),
    ("alert", AlertState, "Alert"),
    ("light_show", LightShowState, "Light show"),
    ("suspension", SuspensionState, "Suspension"),
    ("child_presence", ChildPresenceDetectionState, "Child presence"),
)


def _descriptions() -> list[TeslaBluetoothFieldDescription]:
    """Build stable entities from the protobuf schema shipped by the library."""
    return [
        TeslaBluetoothFieldDescription(
            key=f"{coordinator_name}_{field.name}",
            name=f"{title} {field.name.replace('_', ' ')}",
            coordinator_name=coordinator_name,
            field=field,
            entity_category=EntityCategory.DIAGNOSTIC,
            # The complete schema contains many model-specific fields. Keep
            # them opt-in so unsupported fields do not clutter dashboards.
            entity_registry_enabled_default=False,
        )
        for coordinator_name, message_type, title in ENDPOINTS
        for field in message_type.DESCRIPTOR.fields
    ]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TeslaBluetoothConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up all Tesla Bluetooth data sensors."""
    async_add_entities(
        TeslaBluetoothFieldSensor(entry.runtime_data, description)
        for description in _descriptions()
    )


class TeslaBluetoothFieldSensor(TeslaBluetoothEntity, SensorEntity):
    """Sensor backed by one field from a Tesla protobuf state message."""

    entity_description: TeslaBluetoothFieldDescription

    def __init__(
        self,
        data: TeslaBluetoothData,
        description: TeslaBluetoothFieldDescription,
    ) -> None:
        """Initialize a schema-backed sensor."""
        self.entity_description = description
        coordinator: TeslaBluetoothCoordinator = getattr(
            data.coordinators, description.coordinator_name
        )
        super().__init__(data, coordinator, description.key)
        self._attr_translation_key = None

    def _async_update_attrs(self) -> None:
        field = self.entity_description.field
        value = getattr(self.coordinator.data, field.name)
        self._attr_extra_state_attributes = None

        if field.is_repeated:
            values = list(value)
            self._attr_native_value = len(values)
            self._attr_extra_state_attributes = {
                "values": [
                    toDict(item) if isinstance(item, Message) else item
                    for item in values
                ]
            }
        elif field.message_type is not None:
            self._attr_native_value = "available" if value.ListFields() else None
            self._attr_extra_state_attributes = toDict(value)
        elif field.enum_type is not None:
            enum_value = field.enum_type.values_by_number.get(value)
            self._attr_native_value = enum_value.name.lower() if enum_value else value
        elif isinstance(value, bytes):
            self._attr_native_value = value.hex()
        else:
            self._attr_native_value = value
