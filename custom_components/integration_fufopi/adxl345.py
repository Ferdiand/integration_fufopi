# ADXL345 Python library for Raspberry Pi
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
#
# This is a Raspberry Pi Python implementation to help you get started with
# the Adafruit Triple Axis ADXL345 breakout board:
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer

from decimal import Decimal
from smbus2 import SMBus
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import SPEED_METERS_PER_SECOND

from .const import DOMAIN, ATTRIBUTION

from homeassistant.components.sensor import SensorEntity


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

    @bandwidth_rate.sette
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

        return round(val, 4)

    def enable_measurement(self):
        """Enables measurement by writing 0x08 to POWER_CTL."""
        self.bus.write_byte_data(self.address, POWER_CTL, 0x08)

    def disable_measurement(self):
        """Disables measurement by writing 0x00 to POWER_CTL."""
        self.bus.write_byte_data(self.address, POWER_CTL, 0x00)


class ADXL345Entity(CoordinatorEntity):
    """Power distribution base entity"""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator)
        self.coordinator = coordinator
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

    @property
    def unique_id(self):
        return super().unique_id + "accX"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.i2c_adxl345.accel_x)

        self.async_write_ha_state()


class ADXL345AccelYSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Accel Y"
        self._attr_native_unit_of_measurement = SPEED_METERS_PER_SECOND + "²"

    @property
    def unique_id(self):
        return super().unique_id + "accY"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.i2c_adxl345.accel_y)

        self.async_write_ha_state()


class ADXL345AccelZSensor(ADXL345Entity, SensorEntity):
    """Fridge voltage sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Accel Z"
        self._attr_native_unit_of_measurement = SPEED_METERS_PER_SECOND + "²"

    @property
    def unique_id(self):
        return super().unique_id + "accZ"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = Decimal(self.coordinator.i2c_adxl345.accel_z)

        self.async_write_ha_state()
