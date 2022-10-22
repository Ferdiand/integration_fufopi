"""Binary sensor platform for integration_blueprint."""
from .const import (
    DOMAIN,
)
from .battery import BatteryStateBinarySensor
from .power_distribution import LoadStateBinarySensor
from .hmc5883L import (
    HCM5883Li2cHighSpeedBinarySensor,
    HCM5883LLockedBinarySensor,
    HCM5883LReadyBinarySensor,
)


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _binary_sensors = []
    _binary_sensors.append(BatteryStateBinarySensor(coordinator, entry))

    _binary_sensors.append(LoadStateBinarySensor(coordinator, entry))

    _binary_sensors.append(HCM5883Li2cHighSpeedBinarySensor(coordinator, entry))
    _binary_sensors.append(HCM5883LLockedBinarySensor(coordinator, entry))
    _binary_sensors.append(HCM5883LReadyBinarySensor(coordinator, entry))

    async_add_devices(_binary_sensors)
