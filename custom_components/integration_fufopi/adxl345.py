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
    DEVICE_CLASS_FREQUENCY,
)

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET

from .const import DOMAIN, ATTRIBUTION

# from . import FufoPiCoordinator


class ADXL345Entity(CoordinatorEntity):
    """Power distribution base entity"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.address = 0x53

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "ADXL345"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "ADXL345")},
            "name": "ADXL345",
            "model": "ADXL345",
            "manufacturer": "cHINITO",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class ADXL345AccelXSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Accel X"
        self._attr_native_unit_of_measurement = SPEED_METERS_PER_SECOND + "²"
        self._attr_icon = "mdi:axis-x-arrow"

    @property
    def unique_id(self):
        return super().unique_id + "accX"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.i2c_adxl345.accel_x
        ).quantize(Decimal("1.000"))

        self.async_write_ha_state()


class ADXL345AccelYSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Accel Y"
        self._attr_native_unit_of_measurement = SPEED_METERS_PER_SECOND + "²"
        self._attr_icon = "mdi:axis-y-arrow"

    @property
    def unique_id(self):
        return super().unique_id + "accY"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.i2c_adxl345.accel_y
        ).quantize(Decimal("1.000"))

        self.async_write_ha_state()


class ADXL345AccelZSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Accel Z"
        self._attr_native_unit_of_measurement = SPEED_METERS_PER_SECOND + "²"
        self._attr_icon = "mdi:axis-z-arrow"

    @property
    def unique_id(self):
        return super().unique_id + "accZ"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(
            self.coordinator.i2c_adxl345.accel_z
        ).quantize(Decimal("1.000"))

        self.async_write_ha_state()


class ADXL345PowerSwitch(ADXL345Entity, SwitchEntity):
    """integration_blueprint switch class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "ADXL345 Power"
        self._attr_device_class = DEVICE_CLASS_OUTLET

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return super().unique_id + "power"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self.coordinator.i2c_adxl345.enable_measurement()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self.coordinator.i2c_adxl345.disable_measurement()

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.i2c_adxl345.is_enabled


class ADXL345RangeSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Range"
        self._attr_native_unit_of_measurement = "G"
        self._attr_icon = "mdi:arrow-expand-horizontal"

    @property
    def unique_id(self):
        return super().unique_id + "range"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _range = self.coordinator.i2c_adxl345.range

        if _range == self.coordinator.i2c_adxl345.RANGE_2G:
            self._attr_native_value = Decimal(2)
        elif _range == self.coordinator.i2c_adxl345.RANGE_4G:
            self._attr_native_value = Decimal(4)
        elif _range == self.coordinator.i2c_adxl345.RANGE_8G:
            self._attr_native_value = Decimal(8)
        elif _range == self.coordinator.i2c_adxl345.RANGE_16G:
            self._attr_native_value = Decimal(16)
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()


class ADXL345BandwidthSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Bandwidth rate"
        self._attr_device_class = DEVICE_CLASS_FREQUENCY
        self._attr_native_unit_of_measurement = FREQUENCY_HERTZ

    @property
    def unique_id(self):
        return super().unique_id + "Bandwidth"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _bandwidth = self.coordinator.i2c_adxl345.bandwidth_rate

        if _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_25HZ:
            self._attr_native_value = Decimal(25)
        elif _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_50HZ:
            self._attr_native_value = Decimal(50)
        elif _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_100HZ:
            self._attr_native_value = Decimal(100)
        elif _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_200HZ:
            self._attr_native_value = Decimal(200)
        elif _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_400HZ:
            self._attr_native_value = Decimal(400)
        elif _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_800HZ:
            self._attr_native_value = Decimal(800)
        elif _bandwidth == self.coordinator.i2c_adxl345.BANDWIDTH_RATE_1600HZ:
            self._attr_native_value = Decimal(1600)
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()
