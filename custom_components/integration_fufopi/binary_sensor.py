"""Binary sensor platform for integration_blueprint."""
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_BATTERY_CHARGING,
)

from decimal import Decimal

from .const import (
    DOMAIN,
)
from .entity import VEDirectEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup binary_sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([BatteryStateBinarySensor(coordinator, entry)])


class BatteryStateBinarySensor(VEDirectEntity, BinarySensorEntity):
    """battery state binary_sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry, "BS")
        self._attr_device_class = DEVICE_CLASS_BATTERY_CHARGING

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return f"Battery is charging"

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self.coordinator.data["I"]["value"] > Decimal(0)
