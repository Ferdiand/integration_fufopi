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
            IntegrationBlueprintSensor(coordinator, entry, "I"),
            IntegrationBlueprintSensor(coordinator, entry, "IL"),
            IntegrationBlueprintSensor(coordinator, entry, "H19"),
            IntegrationBlueprintSensor(coordinator, entry, "H20"),
            IntegrationBlueprintSensor(coordinator, entry, "H21"),
            IntegrationBlueprintSensor(coordinator, entry, "H22"),
            IntegrationBlueprintSensor(coordinator, entry, "H23"),
        ]
    )


class IntegrationBlueprintSensor(VEDirectEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator, config_entry, key)
        if self.key in ("V", "VPV"):
            self._attr_device_class = "voltage"
            self._attr_native_unit_of_measurement = "V"
        elif self.key in ("PPV", "H21", "H23"):
            self._attr_device_class = "power"
            self._attr_native_unit_of_measurement = "W"
        elif self.key in ("I", "IL"):
            self._attr_device_class = "current"
            self._attr_native_unit_of_measurement = "A"
        elif self.key in ("H19", "H20", "H22"):
            self._attr_device_class = "energy"
            self._attr_native_unit_of_measurement = "kWh"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.coordinator.data[self.key]["name"]

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        if self.key in ("V", "VPV"):
            return self.coordinator.data[self.key]["value"] / Decimal(1000)

        return self.coordinator.data[self.key]["value"]
