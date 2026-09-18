# Tesla Local HA Commands

Home Assistant integration for sending local commands to Tesla vehicles over Bluetooth Low Energy (BLE).

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=paveto&repository=hass-tesla-bluetooth-commands)

## Installation

Add `https://github.com/paveto/hass-tesla-bluetooth-commands` as a custom
integration repository in HACS and install **Tesla Local HA Commands**. The
integration is stored directly in `custom_components/tesla_bluetooth`, so a
GitHub release is not required. Restart Home Assistant after installation or
updating.

## Important Notice

This integration will keep your vehicle awake constantly while connected. If you want your vehicle to sleep, I recommend creating an automation to enable and disable the included "polling" switch.

The recommended logic is:
- Trigger status is On: Switch Polling On
- Trigger sentry mode, charging, user present, where all are off: Switch Polling Off

## Unlocking the charge cable

The integration provides an **Unlock charge cable** button entity. Pressing it
sends Tesla's local `charge_port_door_open` command over BLE. When a charging
cable is connected, the same command releases the charge-port latch so the
cable can be removed.

You can call this button from a Home Assistant automation connected to a
physical button on the charging handle. Keep the Bluetooth adapter or proxy
close enough to the vehicle for the command to connect reliably.

## Limitations

- Tesla vehicles only support 3 BLE connections, which includes the mobile app, watch app, and Powerwall when Charge On Solar is enabled.
- This will not work with legacy (pre-2021) Model S and Model X vehicles.
- This will not work if the Tesla Fleet, Tessie, or Teslemetry (core version) integrations are configured in Home Assistant.
- It will work alongside the latest Teslemetry Custom (HACS version) integration, but both need to be kept up to date to ensure library compatibility.
- This is a work in progress, lower your expectations.

## Known Issues

Initial setup may fail after the virtual key is installed. Simply retry the setup and the pairing step will be skipped.

The entities will go unavailable if your vehicle is not connected or the communication otherwise fails in an unexpected way.

## Troubleshooting a vehicle not being discovered.

- Ensure the Bluetooth integration is configured.
- Ensure your Bluetooth hardware is close enough to your vehicle. Using Bluetooth proxies near the vehicle is recommended
- Ensure you do not have more than 2 other active BLE connections. Turn Bluetooth off on devices running the Tesla or Tessie app including watches.
- Be patient, discovery won't be instantaneous.
