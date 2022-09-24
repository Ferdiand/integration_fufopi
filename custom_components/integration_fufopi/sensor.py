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

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{DEFAULT_NAME}_{SENSOR}_" + self.key

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data[self.key]["value"]
