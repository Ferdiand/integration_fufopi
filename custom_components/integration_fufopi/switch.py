"""Switch platform for integration_blueprint."""
from .const import DOMAIN
from .relay_board import RelayBoardBinarySwitch
from .fridge import FridgePowerSwitch
from .adxl345 import ADXL345PowerSwitch
from .hmc5883L import HCM5883LContinuosModeSwitch
from .power_lane import add_switchs


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    switches = []
    add_switchs(switches, coordinator, entry)
    async_add_devices([switches])
