"""Switch platform for integration_blueprint."""
from .const import DOMAIN
from .power_lane import add_power_lane_switches


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    switches = []
    add_power_lane_switches(switches, coordinator, entry)
    async_add_devices(switches)
