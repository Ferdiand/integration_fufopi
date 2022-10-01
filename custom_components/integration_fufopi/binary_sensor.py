"""Binary sensor platform for integration_blueprint."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_BATTERY_CHARGING,
)

from decimal import Decimal

from .const import (
    DOMAIN,
)
from .battery import BatteryStateBinarySensor


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([BatteryStateBinarySensor(coordinator, entry)])
