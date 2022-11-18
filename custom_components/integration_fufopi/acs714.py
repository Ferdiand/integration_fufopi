""" ACS714 """
from decimal import Decimal
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    ELECTRIC_POTENTIAL_MILLIVOLT,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
)

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN


def add_acs712_sensors(coordinator, config_entry):
    """Add devices"""
    sensors = []
    sensors.append(ACS712Sensor(coordinator, config_entry, 0))
    sensors.append(ACS712Sensor(coordinator, config_entry, 1))
    sensors.append(ACS712Sensor(coordinator, config_entry, 2))
    sensors.append(ACS712Sensor(coordinator, config_entry, 3))
    return sensors


class ACS712Entity(CoordinatorEntity):
    """ACS712 base entity"""

    def __init__(self, coordinator, config_entry, sensor_no):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._attr_assumed_state = True
        self._sensor_no = sensor_no
        # self._attr_entity_picture =

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "ACS712" + f"{self._sensor_no}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id + "ACS712")},
            "name": "ACS712",
            "model": "ACS712ELCTR-05B-T",
            "manufacturer": "Chini",
        }

    @property
    def extra_state_attributes(self):
        return self._attr_extra_state_attributes

    @property
    def sensibility(self):
        """Return sensor sensibiliti in mV/A"""
        return 185


class ACS712Sensor(ACS712Entity, SensorEntity):
    """ACS712 sensor"""

    def __init__(self, coordinator, config_entry, sensor_no):
        super().__init__(coordinator, config_entry, sensor_no)
        self._attr_name = f"ACS712 Sensor {self._sensor_no}"
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE
        self._attr_device_class = DEVICE_CLASS_CURRENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _sensor_value = self.coordinator.data[f"ads1115_ch{self._sensor_no}"]

        _raw_value = (_sensor_value - 2500) / self.sensibility

        self._attr_native_value = Decimal(_raw_value).quantize(Decimal("0.01"))

        self._attr_extra_state_attributes = {
            "integration": DOMAIN,
            "adschannel": f"ch{self._sensor_no}",
            "sensor_value": _sensor_value,
            "sensor_units": ELECTRIC_POTENTIAL_MILLIVOLT,
            "sensibility": f"{self.sensibility} mV/A",
            "raw value": _raw_value,
        }
        self.async_write_ha_state()
