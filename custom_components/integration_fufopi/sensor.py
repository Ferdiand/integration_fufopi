"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from homeassistant.components.sensor import SensorEntity

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _sensors = []
    for key in list(coordinator.data.keys()):
        _sensors.append(IntegrationBlueprintSensor(coordinator, entry, key))
    async_add_devices(_sensors)


class IntegrationBlueprintSensor(VEDirectEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator, config_entry, key)
        _data = self.coordinator.data[self.key]
        if "device_class" in _data.keys():
            self._attr_device_class = _data["device_class"]
        if "unit_meassurement" in _data.keys():
            self._attr_native_unit_of_measurement = _data["unit_meassurement"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.coordinator.data[self.key]["name"]

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        _data = self.coordinator.data[self.key]
        if isinstance(_data["value"], Decimal):
            return _data["value"] * _data["unit_conversion"]

        return self.coordinator.data[self.key]["value"]
