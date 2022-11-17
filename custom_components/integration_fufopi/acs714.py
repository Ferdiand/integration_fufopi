# ADXL345 Python library for Raspberry Pi
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
#
# This is a Raspberry Pi Python implementation to help you get started with
# the Adafruit Triple Axis ADXL345 breakout board:
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer

from decimal import Decimal
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    SPEED_METERS_PER_SECOND,
    FREQUENCY_HERTZ,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_POTENTIAL_MILLIVOLT,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET

from .const import DOMAIN, ATTRIBUTION

# from . import FufoPiCoordinator


class ACS712Entity(CoordinatorEntity):
    """ACS712 base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "ACS712"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "ACS712")},
            "name": "ACS712",
            "model": "ACS712ELCTR-05B-T",
            "manufacturer": "Chini",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }

    @property
    def sensibility(self):
        """Return sensor sensibiliti in mV/A"""
        return 185


class ACS712Sensor(ACS712Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry, sensor_no):
        super().__init__(coordinator, config_entry)
        self._sensor_no = sensor_no
        self._attr_name = f"ACS712 Sensor {self._sensor_no}"
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE
        self._attr_device_class = DEVICE_CLASS_CURRENT

    @property
    def unique_id(self):
        return super().unique_id + f"{self._sensor_no}"

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
