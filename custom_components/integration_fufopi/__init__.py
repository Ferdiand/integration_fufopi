"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from datetime import timedelta
import logging
import serial

import random
from pigpio import pi
from smbus2 import SMBus

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .relay_board import RelayBoardPigPio
from .SmartSolar import (
    CS_VALUE_LIST,
    MPPT_VALUE_LIST,
    OR_VALUE_LIST,
    ERR_VALUE_LIST,
    PID_VALUE_LIST,
)


from .const import (
    DOMAIN,
    STARTUP_MESSAGE,
)

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    coordinator = FufoPiCoordinator(
        hass=hass,
        logger=_LOGGER,
        name="Victron Solar",
        update_interval=timedelta(seconds=2),
    )
    # await coordinator.async_refresh()

    # if not coordinator.last_update_success or not coordinator.config_ready():
    #    raise ConfigEntryNotReady

    # coordinator.platforms.append("sensor")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "switch"))
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(entry, "binary_sensor")
    )

    # for platform in PLATFORMS:
    #    if entry.options.get(platform, True):
    #        coordinator.platforms.append(platform)
    #        hass.async_add_job(#
    #         hass.config_entries.async_forward_entry_setup(entry, platform)
    #        )

    # entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in ["sensor", "switch", "binary_sensor"]
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class FufoPiCoordinator(DataUpdateCoordinator):
    """FufoPi coordinator"""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        name: str,
        update_interval: timedelta,
    ) -> None:
        super().__init__(hass, logger, name=name, update_interval=update_interval)

        self.smart_solar = SmartSolar(logger=logger)

        self.pigpio = pi("172.30.33.0")
        self.relay_board = RelayBoardPigPio(self.pigpio)

        # select the correct i2c bus for this revision of Raspberry Pi
        revision = (
            [
                l[12:-1]
                for l in open("/proc/cpuinfo", "r").readlines()
                if l[:8] == "Revision"
            ]
            + ["0000"]
        )[0]
        self.i2c_bus = SMBus(1 if int(revision, 16) >= 4 else 0)

        self.i2c_adxl345 = ADXL345(i2c_bus=self.i2c_bus)
        self.i2c_hcm5883 = HCM5883(i2c_bus=self.i2c_bus)

    async def _async_update_data(self):
        """Update data via serial com"""
        self._data = await self.smart_solar._async_update_data()

        return self._data


class SmartSolar:
    """Smart solar VE Direct comm"""

    def __init__(self, logger: logging.Logger) -> None:
        self._data = {
            "PID": "0xA060",
            "FW": "156",
            "SER#": "HQ2129WD7QV",
            "CS": f"{random.choice(list(CS_VALUE_LIST.keys()))}",
            "MPPT": f"{random.choice(list(MPPT_VALUE_LIST.keys()))}",
            "OR": f"{random.choice(list(OR_VALUE_LIST.keys()))}",
            "HSDS": f"{random.randrange(0,365)}",
            "Checksum": "ABCDE",
            "IL": "0",
            "ERR": f"{random.choice(list(ERR_VALUE_LIST.keys()))}",
            "LOAD": "ON",
            "V": "0",
            "VPV": "0",
            "PPV": "0",
            "I": "0",
            "H19": "0",
            "H20": "0",
            "H21": "0",
            "H22": "0",
            "H23": "0",
        }

        self.logger = logger

        try:
            self._serial = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)
            self.simulation = False
        except:
            self.simulation = True

    @property
    def product_id(self):
        """return product ID"""
        _raw = self._data["PID"]
        if _raw in list(PID_VALUE_LIST.keys()):
            return PID_VALUE_LIST[_raw]

        return None

    @property
    def firmware(self):
        """return firmware version"""
        return self._data["FW"]

    @property
    def serial_number(self):
        """return serial number"""
        return self._data["SER#"]

    @property
    def state_of_operation(self):
        """return state of operation"""
        _raw = self._data["CS"]
        if _raw in list(CS_VALUE_LIST.keys()):
            return CS_VALUE_LIST[_raw]

        return None

    @property
    def tracker_operation_mode(self):
        """return tracker operation mode"""
        _raw = self._data["MPPT"]
        if _raw in list(MPPT_VALUE_LIST.keys()):
            return MPPT_VALUE_LIST[_raw]

        return None

    @property
    def off_reason(self):
        """return off reason"""
        _raw = self._data["OR"]
        if _raw in list(OR_VALUE_LIST.keys()):
            return OR_VALUE_LIST[_raw]

        return None

    @property
    def day_seq_number(self):
        """return day sequence number"""
        return self._data["HSDS"]

    @property
    def checksum(self):
        """return checksum"""
        return self._data["Checksum"]

    @property
    def load_current(self):
        """return load current in mA"""
        return self._data["IL"]

    @property
    def error_reason(self):
        """return the error reason"""
        _raw = self._data["ERR"]
        if _raw in list(ERR_VALUE_LIST.keys()):
            return ERR_VALUE_LIST[_raw]

        return None

    @property
    def load_state(self):
        """return the load state"""
        return self._data["LOAD"]

    @property
    def battery_voltage(self):
        """return the battery voltage in mV"""
        return self._data["V"]

    @property
    def panel_voltage(self):
        """return the panel voltage in mV"""
        return self._data["VPV"]

    @property
    def panel_power(self):
        """return the panel power in W"""
        return self._data["PPV"]

    @property
    def battery_current(self):
        """return the battery current in mA"""
        return self._data["I"]

    @property
    def yield_total(self):
        """return the yield total in 0.01kWh"""
        return self._data["H19"]

    @property
    def yield_today(self):
        """return the yield today in 0.01kWh"""
        return self._data["H20"]

    @property
    def max_power_today(self):
        """return the max power today in W"""
        return self._data["H21"]

    @property
    def yield_yesterday(self):
        """return the yield yesterday in 0.01kWh"""
        return self._data["H22"]

    @property
    def max_power_yesterday(self):
        """return the max power yesterday in W"""
        return self._data["H23"]

    async def _async_update_data(self):
        """Update data via serial com"""
        if self.simulation is True:
            return self._data

        _buffer = self._serial.read_all().decode("ascii", "ignore").split("\r\n")
        # remove last item, may be corrupt
        _buffer.pop(-1)

        for _line in _buffer:
            _field = _line.split("\t")
            if len(_field) > 1:
                _key = _field[0]
                _value = _field[1]
                if _key in list(self._data.keys()):
                    self._data[_key] = _value
                else:
                    self.logger.warning(f"Key not defined {_field}")
            else:
                self.logger.warning(f"Field structure not valid: {_field}")

        return self._data


class ADXL345:
    """adxl class"""

    address = None

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

    def __init__(self, i2c_bus: SMBus, address=0x53):
        self.address = address
        self.bus = i2c_bus
        self.bandwidth_rate = self.BANDWIDTH_RATE_100HZ
        self.range = self.RANGE_2G
        self.enable_measurement()

    @property
    def is_enabled(self):
        """Reads POWER_CTL.
        Returns the read value.
        """
        if self.bus.read_byte_data(self.address, self.POWER_CTL) == 0x00:
            return False

        return True

    @property
    def bandwidth_rate(self):
        """Reads BANDWIDTH_RATE_REG.
        Returns the read value.
        """
        raw_bandwidth_rate = self.bus.read_byte_data(
            self.address, self.BANDWIDTH_RATE_REG
        )
        return raw_bandwidth_rate

    @bandwidth_rate.setter
    def bandwidth_rate(self, new_rate):
        """Changes the bandwidth rate by writing rate to BANDWIDTH_RATE_REG.
        rate -- the bandwidth rate the ADXL345 will be set to. Using a
        pre-defined rate is advised.
        """
        self.bus.write_byte_data(self.address, self.BANDWIDTH_RATE_REG, new_rate)

    @property
    def range(self):
        """Reads the range the ADXL345 is currently set to.
        return a hexadecimal value.
        """
        return self.bus.read_byte_data(self.address, self.DATA_FORMAT)

    @range.setter
    def range(self, new_range):
        """Changes the range of the ADXL345.
        range -- the range to set the accelerometer to. Using a pre-defined
        range is advised.
        """
        value = None

        value = self.bus.read_byte_data(self.address, self.DATA_FORMAT)

        value &= ~0x0F
        value |= new_range
        value |= 0x08

        self.bus.write_byte_data(self.address, self.DATA_FORMAT, value)

    @property
    def accel_x(self):
        """Reads accel x and returns it."""
        bytes = self.bus.read_i2c_block_data(self.address, self.DATAX0, 2)

        val = bytes[0] | (bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * self.SCALE_MULTIPLIER * self.EARTH_GRAVITY_MS2

        return round(val, 4)

    @property
    def accel_y(self):
        """Reads accel y and returns it."""
        bytes = self.bus.read_i2c_block_data(self.address, self.DATAY0, 2)

        val = bytes[0] | (bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * self.SCALE_MULTIPLIER * self.EARTH_GRAVITY_MS2

        return round(val, 4)

    @property
    def accel_z(self):
        """Reads accel z and returns it."""
        bytes = self.bus.read_i2c_block_data(self.address, self.DATAZ0, 2)

        val = bytes[0] | (bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * self.SCALE_MULTIPLIER * self.EARTH_GRAVITY_MS2

        return val

    def enable_measurement(self):
        """Enables measurement by writing 0x08 to POWER_CTL."""
        self.bus.write_byte_data(self.address, self.POWER_CTL, 0x08)

    def disable_measurement(self):
        """Disables measurement by writing 0x00 to POWER_CTL."""
        self.bus.write_byte_data(self.address, self.POWER_CTL, 0x00)


class HCM5883:
    """Class for coordinator HCM5883 sensor"""

    CONFIG_A_ADDR = 0x00  # Address of Configuration register A
    CONFIG_B_ADDR = 0x01  # Address of Configuration register B
    MODE_ADDR = 0x02  # Address of mode register

    X_AXIS_ADDR = 0x03  # Address of X-axis MSB data register
    Y_AXIS_ADDR = 0x05  # Address of Y-axis MSB data register
    Z_AXIS_ADDR = 0x07  # Address of Y-axis MSB data register

    STATUS_ADDR = 0x09  ## Address of status register
    ID_ADDR = 0x10  ## Start addres of identification register

    # Config A register masks
    SAMPLE_NO_MASK = 0x60
    SAMPLE_NO_LIST = [1, 2, 4, 8]  # 00 = 1(Default); 01 = 2; 10 = 4; 11 = 8
    OUTPUT_RATE_MASK = 0x1C
    OUTPUT_RATE_LIST = [
        0.75,
        1.5,
        3.0,
        7.5,
        15.0,
        30.0,
        75.0,
        8080,
    ]  # b000 -> 0.75, b001 -> 1.5, b010 -> 3, b011 -> 7.5, b100 -> 15 (Default), b101 -> 30, b110 -> 75, b111 -> Reserved"""
    MEAS_CONFIG_MASK = 0x03

    # Config B register masks
    GAIN_CONFIG_MASK = 0xE0
    GAIN_LIST = [
        1370,
        1090,
        820,
        660,
        440,
        390,
        330,
        230,
    ]  # Gain (LSb/Gauss)

    SENSOR_RANGE_LIST = [
        0.88,
        1.3,
        1.9,
        2.5,
        4.0,
        4.7,
        5.6,
        8.1,
    ]  # Sensor range (Gauss)

    RESOLUTION_LIST = [
        0.73,
        0.92,
        1.22,
        1.52,
        2.27,
        2.56,
        3.03,
        4.35,
    ]  # Digital Resolution (mG/LSb)

    # Mode register masks
    I2C_HIGH_SPEED_MASK = 0x80
    OPERATING_MODE_MASK = 0x03

    # Status register masks
    STATUS_LOCKED_MASK = 0x02
    STATUS_READY_MASK = 0x01

    def __init__(self, i2c_bus: SMBus, address=0x1E):
        self.address = address
        self.bus = i2c_bus

    @property
    def sample_no(self):
        """number of samples averaged (1 to 8) per measurement output.
        00 = 1(Default); 01 = 2; 10 = 4; 11 = 8"""
        _confi_a = self.bus.read_i2c_block_data(self.address, self.CONFIG_A_ADDR, 1)

        val = _confi_a & self.SAMPLE_NO_MASK
        val = val >> 5

        return self.SAMPLE_NO_LIST[val]

    @property
    def output_rate(self):
        """Data Output Rate Bits.
        b000 -> 0.75, b001 -> 1.5, b010 -> 3, b011 -> 7.5, b100 -> 15 (Default), b101 -> 30, b110 -> 75, b111 -> Reserved"""
        _confi_a = self.bus.read_i2c_block_data(self.address, self.CONFIG_A_ADDR, 1)

        val = _confi_a & self.OUTPUT_RATE_MASK
        val = val >> 2

        return self.OUTPUT_RATE_LIST[val]

    @property
    def measurement_mode(self):
        """Measurement Configuration Bits. These bits define the
        measurement flow of the device, specifically whether or not
        to incorporate an applied bias into the measurement."""
        _confi_a = self.bus.read_i2c_block_data(self.address, self.CONFIG_A_ADDR, 1)

        val = _confi_a & self.MEAS_CONFIG_MASK

        return val

    @property
    def gain(self):
        """Gain Configuration Bits. These bits configure the gain for
        the device. The gain configuration is common for all
        channels
        return Gain (LSb/Gauss)"""
        _confi_b = self.bus.read_i2c_block_data(self.address, self.CONFIG_B_ADDR, 1)

        val = _confi_b & self.GAIN_CONFIG_MASK
        val = val >> 5

        return self.GAIN_LIST[val]

    @property
    def sensor_range(self):
        """
        return Recommended Sensor Field Range (Gauss)"""
        _confi_b = self.bus.read_i2c_block_data(self.address, self.CONFIG_B_ADDR, 1)

        val = _confi_b & self.GAIN_CONFIG_MASK
        val = val >> 5

        return self.SENSOR_RANGE_LIST[val]

    @property
    def resolution(self):
        """
        return Digital Resolution (mG/LSb)"""
        _confi_b = self.bus.read_i2c_block_data(self.address, self.CONFIG_B_ADDR, 1)

        val = _confi_b & self.GAIN_CONFIG_MASK
        val = val >> 5

        return self.RESOLUTION_LIST[val]

    @property
    def i2c_high_speed(self):
        """Set this pin to enable High Speed I2C, 3400kHz"""
        _mode = self.bus.read_i2c_block_data(self.address, self.MODE_ADDR, 1)

        val = _mode & self.I2C_HIGH_SPEED_MASK

        if val > 0:
            return True

        return False

    @property
    def operating_mode(self):
        """Mode Select Bits. These bits select the operation mode of this device.
        0 -> Continuous-Measurement Mode. In continuous-measurement mode,
        the device continuously performs measurements and places the
        result in the data register. RDY goes high when new data is placed
        in all three registers. After a power-on or a write to the mode or
        configuration register, the first measurement set is available from all
        three data output registers after a period of 2/fDO and subsequent
        measurements are available at a frequency of fDO, where fDO is the
        frequency of data output.
        1 -> Single-Measurement Mode (Default). When single-measurement
        mode is selected, device performs a single measurement, sets RDY
        high and returned to idle mode. Mode register returns to idle mode
        bit values. The measurement remains in the data output register and
        RDY remains high until the data output register is read or another
        measurement is performed.
        2 -> Idle Mode. Device is placed in idle mode.
        3 -> Idle Mode. Device is placed in idle mode."""
        _mode = self.bus.read_i2c_block_data(self.address, self.MODE_ADDR, 1)

        val = _mode & self.OPERATING_MODE_MASK

        return val

    @property
    def mag_x(self):
        """return the meassurament in X axis"""
        _bytes = self.bus.read_i2c_block_data(self.address, self.X_AXIS_ADDR, 2)

        val = _bytes[0] | (_bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * self.resolution

        return round(val, 4)

    @property
    def mag_y(self):
        """return the meassurament in Y axis"""
        _bytes = self.bus.read_i2c_block_data(self.address, self.Y_AXIS_ADDR, 2)

        val = _bytes[0] | (_bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * self.resolution

        return round(val, 4)

    @property
    def mag_z(self):
        """return the meassurament in Z axis"""
        _bytes = self.bus.read_i2c_block_data(self.address, self.Z_AXIS_ADDR, 2)

        val = _bytes[0] | (_bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = val * self.resolution

        return round(val, 4)

    @property
    def is_locked(self):
        """Data output register lock. This bit is set when:
        1.some but not all for of the six data output registers have been read,
        2. Mode register has been read.
            When this bit is set, the six data output registers are locked
            and any new data will not be placed in these register until
            one of these conditions are met:
            1. all six bytes have been read, 2. the mode register is changed,
            3. the measurement configuration (CRA) is changed,
            4. power is reset"""

        _status = self.bus.read_i2c_block_data(self.address, self.MODE_ADDR, 1)

        val = _status & self.STATUS_LOCKED_MASK

        if val > 0:
            return True

        return False

    @property
    def is_ready(self):
        """Ready Bit. Set when data is written to all six data registers.
        Cleared when device initiates a write to the data output
        registers and after one or more of the data output registers
        are written to. When RDY bit is clear it shall remain cleared
        for a 250 μs. DRDY pin can be used as an alternative to
        the status register for monitoring the device for
        measurement data."""

        _status = self.bus.read_i2c_block_data(self.address, self.MODE_ADDR, 1)

        val = _status & self.STATUS_READY_MASK

        if val > 0:
            return True

        return False
