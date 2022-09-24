"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from homeassistant.components.sensor import SensorEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices(
        [
            IntegrationBlueprintSensor(coordinator, entry, "V"),
            IntegrationBlueprintSensor(coordinator, entry, "VPV"),
            IntegrationBlueprintSensor(coordinator, entry, "PPV"),
        ]
    )


class IntegrationBlueprintSensor(VEDirectEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator, config_entry, key)
        if self.key in ("V", "VPV"):
            self._attr_device_class = "voltage"
            self._attr_native_unit_of_measurement = "V"
        elif self.key in ("PPV"):
            self._attr_device_class = "power"
            self._attr_native_unit_of_measurement = "W"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.coordinator.data[self.key]["name"]

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        if self.key in ("V", "VPV"):
            return self.coordinator.data[self.key]["value"] / 1000

        return self.coordinator.data[self.key]["value"]
