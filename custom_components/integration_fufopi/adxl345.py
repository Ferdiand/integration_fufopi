# ADXL345 Python library for Raspberry Pi
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
#
# This is a Raspberry Pi Python implementation to help you get started with
# the Adafruit Triple Axis ADXL345 breakout board:
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer

from decimal import Decimal
from unicodedata import decimal
from smbus2 import SMBus
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    SPEED_METERS_PER_SECOND,
    FREQUENCY_HERTZ,
    DEVICE_CLASS_FREQUENCY,
)

from .const import DOMAIN, ATTRIBUTION

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET
from homeassistant.components.input_select import InputSelect

# ADXL345 constants
EARTH_GRAVITY_MS2 = 9.80665
# This is the typical scale factor in g/LSB as given in the datasheet (page 4)
SCALE_MULTIPLIER = 0.0039

DATA_FORMAT = 0x31
BANDWIDTH_RATE_REG = 0x2C
POWER_CTL = 0x2D

BANDWIDTH_RATE_1600HZ = 0x0F
BANDWIDTH_RATE_800HZ = 0x0E
BANDWIDTH_RATE_400HZ = 0x0D
BANDWIDTH_RATE_200HZ = 0x0C
BANDWIDTH_RATE_100HZ = 0x0B
BANDWIDTH_RATE_50HZ = 0x0A
BANDWIDTH_RATE_25HZ = 0x09

RANGE_2G = 0x00
RANGE_4G = 0x01
RANGE_8G = 0x02
RANGE_16G = 0x03

MEASURE = 0x08
AXES_DATA = 0x32

DATAX0 = 0x32
DATAX1 = 0x33
DATAY0 = 0x34
DATAY1 = 0x35
DATAZ0 = 0x36
DATAZ1 = 0x37


class ADXL345:
    """adxl class"""

    address = None

    def __init__(self, i2c_bus: SMBus, address=0x53):
        self.address = address
        self.bus = i2c_bus
        self.bandwidth_rate = BANDWIDTH_RATE_100HZ
        self.range = RANGE_2G
        self.enable_measurement()

    @property
    def is_enabled(self):
        """Reads POWER_CTL.
        Returns the read value.
        """
        if self.bus.read_byte_data(self.address, POWER_CTL) == 0x00:
            return False

        return True

    @property
    def bandwidth_rate(self):
        """Reads BANDWIDTH_RATE_REG.
        Returns the read value.
        """
        raw_bandwidth_rate = self.bus.read_byte_data(self.address, BANDWIDTH_RATE_REG)
        return raw_bandwidth_rate & 0x0F

    @bandwidth_rate.setter
    def bandwidth_rate(self, new_rate):
        """Changes the bandwidth rate by writing rate to BANDWIDTH_RATE_REG.
        rate -- the bandwidth rate the ADXL345 will be set to. Using a
        pre-defined rate is advised.
        """
        self.bus.write_byte_data(self.address, BANDWIDTH_RATE_REG, new_rate)

    @property
    def range(self):
        """Reads the range the ADXL345 is currently set to.
        return a hexadecimal value.
        """
        return self.bus.read_byte_data(self.address, DATA_FORMAT)

    @range.setter
    def range(self, new_range):
        """Changes the range of the ADXL345.
        range -- the range to set the accelerometer to. Using a pre-defined
        range is advised.
        """
        value = None

        value = self.bus.read_byte_data(self.address, DATA_FORMAT)

        value &= ~0x0F
        value |= new_range
        value |= 0x08

        self.bus.write_byte_data(self.address, DATA_FORMAT, value)

    @property
    def accel_x(self):
        """Reads accel x and returns it."""
        bytes = self.bus.read_i2c_block_data(self.address, DATAX0, 2)

        val = bytes[0] | (bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * SCALE_MULTIPLIER

        return round(val, 4)

    @property
    def accel_y(self):
        """Reads accel y and returns it."""
        bytes = self.bus.read_i2c_block_data(self.address, DATAY0, 2)

        val = bytes[0] | (bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * SCALE_MULTIPLIER

        return round(val, 4)

    @property
    def accel_z(self):
        """Reads accel z and returns it."""
        bytes = self.bus.read_i2c_block_data(self.address, DATAZ0, 2)

        val = bytes[0] | (bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * SCALE_MULTIPLIER

        return val

    def enable_measurement(self):
        """Enables measurement by writing 0x08 to POWER_CTL."""
        self.bus.write_byte_data(self.address, POWER_CTL, 0x08)

    def disable_measurement(self):
        """Disables measurement by writing 0x00 to POWER_CTL."""
        self.bus.write_byte_data(self.address, POWER_CTL, 0x00)


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
        self._attr_unit_of_measurement = "G"
        self._attr_icon = " "

    @property
    def unique_id(self):
        return super().unique_id + "range"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _range = self.coordinator.i2c_adxl345.range

        if _range == RANGE_2G:
            self._attr_native_value = Decimal(2)
        elif _range == RANGE_4G:
            self._attr_native_value = Decimal(4)
        elif _range == RANGE_8G:
            self._attr_native_value = Decimal(8)
        elif _range == RANGE_16G:
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
        self._attr_unit_of_measurement = FREQUENCY_HERTZ

    @property
    def unique_id(self):
        return super().unique_id + "Bandwidth"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _bandwidth = self.coordinator.i2c_adxl345.bandwidth_rate

        if _bandwidth == BANDWIDTH_RATE_25HZ:
            self._attr_native_value = Decimal(25)
        elif _bandwidth == BANDWIDTH_RATE_50HZ:
            self._attr_native_value = Decimal(50)
        elif _bandwidth == BANDWIDTH_RATE_100HZ:
            self._attr_native_value = Decimal(100)
        elif _bandwidth == BANDWIDTH_RATE_200HZ:
            self._attr_native_value = Decimal(200)
        elif _bandwidth == BANDWIDTH_RATE_400HZ:
            self._attr_native_value = Decimal(400)
        elif _bandwidth == BANDWIDTH_RATE_800HZ:
            self._attr_native_value = Decimal(800)
        elif _bandwidth == BANDWIDTH_RATE_1600HZ:
            self._attr_native_value = Decimal(1600)
        else:
            self._attr_native_value = Decimal(0)

        self.async_write_ha_state()
