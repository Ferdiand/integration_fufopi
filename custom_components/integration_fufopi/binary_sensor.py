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
from .power_distribution import LoadStateBinarySensor


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _binary_sensors = []
    _binary_sensors.append(BatteryStateBinarySensor(coordinator, entry))
    _binary_sensors.append(LoadStateBinarySensor(coordinator, entry))
    async_add_devices([BatteryStateBinarySensor(coordinator, entry)])
