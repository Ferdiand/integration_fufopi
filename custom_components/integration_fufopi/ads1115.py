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
)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET

from .const import DOMAIN, ATTRIBUTION

# from . import FufoPiCoordinator


class ADS1115Entity(CoordinatorEntity):
    """Power distribution base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "ADS1115"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "ADS1115")},
            "name": "ADS1115",
            "model": "ADS1115",
            "manufacturer": "Adafruit",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class ADS1115Channel0(ADS1115Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Channel 0"
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT
        self._attr_device_class = DEVICE_CLASS_VOLTAGE

    @property
    def unique_id(self):
        return super().unique_id + "adsch0"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["ads1115_ch0"]

        self.async_write_ha_state()


class ADS1115Channel1(ADS1115Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Channel 1"
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT
        self._attr_device_class = DEVICE_CLASS_VOLTAGE

    @property
    def unique_id(self):
        return super().unique_id + "adsch1"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["ads1115_ch1"]

        self.async_write_ha_state()


class ADS1115Channel2(ADS1115Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Channel 2"
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT
        self._attr_device_class = DEVICE_CLASS_VOLTAGE

    @property
    def unique_id(self):
        return super().unique_id + "adsch2"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["ads1115_ch2"]

        self.async_write_ha_state()


class ADS1115Channel3(ADS1115Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Channel 3"
        self._attr_native_unit_of_measurement = ELECTRIC_POTENTIAL_MILLIVOLT
        self._attr_device_class = DEVICE_CLASS_VOLTAGE

    @property
    def unique_id(self):
        return super().unique_id + "adsch3"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.data["ads1115_ch3"]

        self.async_write_ha_state()
