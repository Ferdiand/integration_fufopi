"""Switch platform for integration_blueprint."""

import imp
from .const import DEFAULT_NAME, DOMAIN, ICON, SWITCH
from .relay_board import RelayBoardBinarySwitch
from .fridge import FridgePowerSwitch
from .adxl345 import ADXL345PowerSwitch


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            RelayBoardBinarySwitch(coordinator, entry, 0),
            RelayBoardBinarySwitch(coordinator, entry, 1),
            RelayBoardBinarySwitch(coordinator, entry, 2),
            RelayBoardBinarySwitch(coordinator, entry, 3),
            FridgePowerSwitch(coordinator, entry),
            ADXL345PowerSwitch(coordinator, entry),
        ]
    )
