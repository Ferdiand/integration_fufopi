"""Switch platform for integration_blueprint."""
from .const import DOMAIN
from .relay_board import RelayBoardBinarySwitch
from .fridge import FridgePowerSwitch
from .adxl345 import ADXL345PowerSwitch
from .hmc5883L import HCM5883LContinuosModeSwitch
from .power_lane import PowerLaneSwitch


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            PowerLaneSwitch(coordinator, entry, "Power1", 12, 0),
            PowerLaneSwitch(coordinator, entry, "Power2", 16, 1),
            PowerLaneSwitch(coordinator, entry, "Power3", 18, 2),
            PowerLaneSwitch(coordinator, entry, "Power4", 13, 3),
            RelayBoardBinarySwitch(coordinator, entry, 0),
            RelayBoardBinarySwitch(coordinator, entry, 1),
            RelayBoardBinarySwitch(coordinator, entry, 2),
            RelayBoardBinarySwitch(coordinator, entry, 3),
            FridgePowerSwitch(coordinator, entry),
            # ADXL345PowerSwitch(coordinator, entry),
            # HCM5883LContinuosModeSwitch(coordinator, entry),
        ]
    )
