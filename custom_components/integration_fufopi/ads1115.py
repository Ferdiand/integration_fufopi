""" ADS1115 """
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_POTENTIAL_MILLIVOLT,
)

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


def add_ads1115_sensors(coordinator, config_entry):
    """Add devices"""
    sensors = []
    sensors.append(ADS1115Sensor(coordinator, config_entry, 0))
    sensors.append(ADS1115Sensor(coordinator, config_entry, 1))
    sensors.append(ADS1115Sensor(coordinator, config_entry, 2))
    sensors.append(ADS1115Sensor(coordinator, config_entry, 3))
    return sensors


class ADS1115Entity(CoordinatorEntity):
    """ADS1115 base entity"""

    def __init__(self, coordinator, config_entry, channel_no):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._channel_no = channel_no

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "ADS1115" + f"{self._channel_no}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id + "ADS1115")},
            "name": "ADS1115",
            "model": "ADS1115",
            "manufacturer": "Adafruit",
        }


class ADS1115Sensor(ADS1115Entity, SensorEntity):
    """ADS1115 sensor"""

    def __init__(self, coordinator, config_entry, channel_no):
        super().__init__(coordinator, config_entry, channel_no)
        self._attr_name = f"ADS1115 Channel {self._channel_no}"
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT
        self._attr_device_class = DEVICE_CLASS_VOLTAGE

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data[f"ads1115_ch{self._channel_no}"]

        self.async_write_ha_state()
