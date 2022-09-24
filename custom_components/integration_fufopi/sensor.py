"""Sensor platform for integration_blueprint."""
from homeassistant.components.sensor import SensorEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([IntegrationBlueprintSensor(coordinator, entry, "V")])


class IntegrationBlueprintSensor(VEDirectEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator, config_entry, key)
        if self.key == "V":
            self._attr_device_class = "voltage"
            self._attr_native_unit_of_measurement = "V"

    @property
    def name(self):
        """Return the name of the sensor."""
        if self.key == "V":
            return "Battery Voltage"
        else:
            return f"{DEFAULT_NAME}_{SENSOR}_" + self.key

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data[self.key]["value"]
