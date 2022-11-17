"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from datetime import timedelta
import logging
from operator import xor
from typing import Dict, List, Literal
import serial
import struct

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

        # self.pigpio = pi("172.30.33.0")
        self.relay_board = RelayBoardPigPio()

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

        # self.i2c_adxl345 = ADXL345(i2c_bus=self.i2c_bus)
        # self.i2c_hcm5883 = HCM5883(i2c_bus=self.i2c_bus)
        self.ads1115 = ADS1115weno(i2c=self.i2c_bus)

    async def _async_update_data(self):
        """Update data via serial com"""
        self._data = await self.smart_solar._async_update_data()
        value = await self.ads1115.readADCSingleEnded(0)
        self.logger.warning(f"{value}")
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

        self.bus.write_i2c_block_data(self.address, self.MODE_ADDR, [0x00])

    @property
    def sample_no(self):
        """number of samples averaged (1 to 8) per measurement output.
        00 = 1(Default); 01 = 2; 10 = 4; 11 = 8"""
        _confi_a = self.bus.read_i2c_block_data(self.address, self.CONFIG_A_ADDR, 1)

        val = _confi_a[0] & self.SAMPLE_NO_MASK
        val = val >> 5

        return self.SAMPLE_NO_LIST[val]

    @property
    def output_rate(self):
        """Data Output Rate Bits.
        b000 -> 0.75, b001 -> 1.5, b010 -> 3, b011 -> 7.5, b100 -> 15 (Default), b101 -> 30, b110 -> 75, b111 -> Reserved"""
        _confi_a = self.bus.read_i2c_block_data(self.address, self.CONFIG_A_ADDR, 1)

        val = _confi_a[0] & self.OUTPUT_RATE_MASK
        val = val >> 2

        return self.OUTPUT_RATE_LIST[val]

    @property
    def measurement_mode(self):
        """Measurement Configuration Bits. These bits define the
        measurement flow of the device, specifically whether or not
        to incorporate an applied bias into the measurement."""
        _confi_a = self.bus.read_i2c_block_data(self.address, self.CONFIG_A_ADDR, 1)

        val = _confi_a[0] & self.MEAS_CONFIG_MASK

        return val

    @property
    def gain(self):
        """Gain Configuration Bits. These bits configure the gain for
        the device. The gain configuration is common for all
        channels
        return Gain (LSb/Gauss)"""
        _confi_b = self.bus.read_i2c_block_data(self.address, self.CONFIG_B_ADDR, 1)

        val = _confi_b[0] & self.GAIN_CONFIG_MASK
        val = val >> 5

        return self.GAIN_LIST[val]

    @property
    def sensor_range(self):
        """
        return Recommended Sensor Field Range (Gauss)"""
        _confi_b = self.bus.read_i2c_block_data(self.address, self.CONFIG_B_ADDR, 1)

        val = _confi_b[0] & self.GAIN_CONFIG_MASK
        val = val >> 5

        return self.SENSOR_RANGE_LIST[val]

    @property
    def resolution(self):
        """
        return Digital Resolution (mG/LSb)"""
        _confi_b = self.bus.read_i2c_block_data(self.address, self.CONFIG_B_ADDR, 1)

        val = _confi_b[0] & self.GAIN_CONFIG_MASK
        val = val >> 5

        return self.RESOLUTION_LIST[val]

    @property
    def i2c_high_speed(self):
        """Set this pin to enable High Speed I2C, 3400kHz"""
        _mode = self.bus.read_i2c_block_data(self.address, self.MODE_ADDR, 1)

        val = _mode[0] & self.I2C_HIGH_SPEED_MASK

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

        val = _mode[0] & self.OPERATING_MODE_MASK

        return val

    @operating_mode.setter
    def operating_mode(self, new_mode):
        if new_mode < 0 or new_mode > 3:
            raise ValueError(f"Invalid mode requested [0-3]:{new_mode}")
        else:
            _old_mode = self.bus.read_i2c_block_data(self.address, self.MODE_ADDR, 1)
            self.bus.write_i2c_block_data(self.address, self.MODE_ADDR, [new_mode])

    @property
    def mag_x(self):
        """return the meassurament in X axis"""
        _bytes = self.bus.read_i2c_block_data(self.address, self.X_AXIS_ADDR, 2)

        val = _bytes[0] | (_bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = self._scale(val, (0x07FF, 2047), (0xF800, -2048))

        val = val / self.gain

        return round(val, 4)

    @property
    def mag_y(self):
        """return the meassurament in Y axis"""
        _bytes = self.bus.read_i2c_block_data(self.address, self.Y_AXIS_ADDR, 2)

        val = _bytes[0] | (_bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = self._scale(val, (0x07FF, 2047), (0xF800, -2048))

        val = val / self.gain

        return round(val, 4)

    @property
    def mag_z(self):
        """return the meassurament in Z axis"""
        _bytes = self.bus.read_i2c_block_data(self.address, self.Z_AXIS_ADDR, 2)

        val = _bytes[0] | (_bytes[1] << 8)
        if val & (1 << 16 - 1):
            val = val - (1 << 16)

        val = self._scale(val, (0x07FF, 2047), (0xF800, -2048))

        val = val / self.gain

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

        val = _status[0] & self.STATUS_LOCKED_MASK

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

        val = _status[0] & self.STATUS_READY_MASK

        if val > 0:
            return True

        return False

    def _scale(self, x, upper, lower):
        _x1, _y1 = lower
        _x2, _y2 = upper
        _m = (_y2 - _y1) / (_x2 - _x1)
        _n = _m * _x1 - _y1
        return x * _m - _n


class Mode:
    """An enum-like class representing possible ADC operating modes."""

    # See datasheet "Operating Modes" section
    # values here are masks for setting MODE bit in Config Register
    # pylint: disable=too-few-public-methods
    CONTINUOUS = 0x0000
    """Continuous Mode"""
    SINGLE = 0x0100
    """Single-Shot Mode"""


class ADS1x15:
    """Base functionality for ADS1x15 analog to digital converters.
    :param ~busio.I2C i2c: The I2C bus the device is connected to.
    :param float gain: The ADC gain.
    :param int data_rate: The data rate for ADC conversion in samples per second.
                          Default value depends on the device.
    :param Mode mode: The conversion mode, defaults to `Mode.SINGLE`.
    :param int address: The I2C address of the device.
    """

    _ADS1X15_DEFAULT_ADDRESS = 0x48
    _ADS1X15_POINTER_CONVERSION = 0x00
    _ADS1X15_POINTER_CONFIG = 0x01
    _ADS1X15_CONFIG_OS_SINGLE = 0x8000
    _ADS1X15_CONFIG_MUX_OFFSET = 12
    _ADS1X15_CONFIG_COMP_QUE_DISABLE = 0x0003
    _ADS1X15_CONFIG_GAIN = {
        2 / 3: 0x0000,
        1: 0x0200,
        2: 0x0400,
        4: 0x0600,
        8: 0x0800,
        16: 0x0A00,
    }

    def __init__(
        self,
        i2c_bus: SMBus,
        gain: float = 1,
        data_rate: int = None,
        mode: int = Mode.SINGLE,
        address: int = _ADS1X15_DEFAULT_ADDRESS,
    ):
        # pylint: disable=too-many-arguments
        self._last_pin_read = None
        self.buf = bytearray(3)
        self.gain = gain
        self.data_rate = self._data_rate_default() if data_rate is None else data_rate
        self.mode = mode
        self.bus = i2c_bus
        self.address = address

    @property
    def bits(self) -> int:
        """The ADC bit resolution."""
        raise NotImplementedError("Subclass must implement bits property.")

    @property
    def data_rate(self) -> int:
        """The data rate for ADC conversion in samples per second."""
        return self._data_rate

    @data_rate.setter
    def data_rate(self, rate: int) -> None:
        possible_rates = self.rates
        if rate not in possible_rates:
            raise ValueError("Data rate must be one of: {}".format(possible_rates))
        self._data_rate = rate

    @property
    def rates(self) -> List[int]:
        """Possible data rate settings."""
        raise NotImplementedError("Subclass must implement rates property.")

    @property
    def rate_config(self) -> Dict[int, int]:
        """Rate configuration masks."""
        raise NotImplementedError("Subclass must implement rate_config property.")

    @property
    def gain(self) -> float:
        """The ADC gain."""
        return self._gain

    @gain.setter
    def gain(self, gain: float) -> None:
        possible_gains = self.gains
        if gain not in possible_gains:
            raise ValueError("Gain must be one of: {}".format(possible_gains))
        self._gain = gain

    @property
    def gains(self) -> List[float]:
        """Possible gain settings."""
        g = list(self._ADS1X15_CONFIG_GAIN.keys())
        g.sort()
        return g

    @property
    def mode(self) -> int:
        """The ADC conversion mode."""
        return self._mode

    @mode.setter
    def mode(self, mode: int) -> None:
        if mode not in (Mode.CONTINUOUS, Mode.SINGLE):
            raise ValueError("Unsupported mode.")
        self._mode = mode

    def read(self, pin, is_differential: bool = False) -> int:
        """I2C Interface for ADS1x15-based ADCs reads.
        :param ~microcontroller.Pin pin: individual or differential pin.
        :param bool is_differential: single-ended or differential read.
        """
        pin = pin if is_differential else pin + 0x04
        return self._read(pin)

    def _data_rate_default(self) -> int:
        """Retrieve the default data rate for this ADC (in samples per second).
        Should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _data_rate_default!")

    def _conversion_value(self, raw_adc: int) -> int:
        """Subclasses should override this function that takes the 16 raw ADC
        values of a conversion result and returns a signed integer value.
        """
        raise NotImplementedError("Subclass must implement _conversion_value function!")

    async def _read(self, pin) -> int:
        """Perform an ADC read. Returns the signed integer result of the read."""
        # Immediately return conversion register result if in CONTINUOUS mode
        # and pin has not changed
        if self.mode == Mode.CONTINUOUS and self._last_pin_read == pin:
            return self._conversion_value(self.get_last_result(True))

        # Assign last pin read if in SINGLE mode or first sample in CONTINUOUS mode on this pin
        self._last_pin_read = pin

        # Configure ADC every time before a conversion in SINGLE mode
        # or changing channels in CONTINUOUS mode
        if self.mode == Mode.SINGLE:
            config = self._ADS1X15_CONFIG_OS_SINGLE
        else:
            config = 0
        config |= (pin & 0x07) << self._ADS1X15_CONFIG_MUX_OFFSET
        config |= self._ADS1X15_CONFIG_GAIN[self.gain]
        config |= self.mode
        config |= self.rate_config[self.data_rate]
        config |= self._ADS1X15_CONFIG_COMP_QUE_DISABLE
        self.bus.write_i2c_block_data(
            self.address, self._ADS1X15_POINTER_CONFIG, [config]
        )

        # Wait for conversion to complete
        # ADS1x1x devices settle within a single conversion cycle
        if self.mode == Mode.SINGLE:
            # Continuously poll conversion complete status bit
            while not self._conversion_complete():
                pass
        else:
            # Can't poll registers in CONTINUOUS mode
            # Wait expected time for two conversions to complete
            await asyncio.sleep(2 / self.data_rate)
            # time.sleep(2 / self.data_rate)

        return self._conversion_value(self.get_last_result(False))

    def _conversion_complete(self) -> int:
        """Return status of ADC conversion."""
        # OS is bit 15
        # OS = 0: Device is currently performing a conversion
        # OS = 1: Device is not currently performing a conversion
        return self._read_register(self._ADS1X15_POINTER_CONFIG) & 0x8000

    def get_last_result(self, fast: bool = False) -> int:
        """Read the last conversion result when in continuous conversion mode.
        Will return a signed integer value. If fast is True, the register
        pointer is not updated as part of the read. This reduces I2C traffic
        and increases possible read rate.
        """
        return self._read_register(self._ADS1X15_POINTER_CONVERSION, fast)

    def _write_register(self, reg: int, value: int):
        """Write 16 bit value to register."""
        self.buf[0] = reg
        self.buf[1] = (value >> 8) & 0xFF
        self.buf[2] = value & 0xFF
        self.bus.write_i2c_block_data(self.address, reg, value)
        # with self.i2c_device as i2c:
        #    i2c.write(self.buf)

    def _read_register(self, reg: int, fast: bool = False) -> int:
        """Read 16 bit register value. If fast is True, the pointer register
        is not updated.
        """
        self.bus.read_block_data(self.address, reg, self.buf)
        return self.buf[0] << 8 | self.buf[1]
        # with self.i2c_device as i2c:
        #    if fast:
        #        i2c.readinto(self.buf, end=2)
        #    else:
        #        i2c.write_then_readinto(bytearray([reg]), self.buf, in_end=2)
        # return self.buf[0] << 8 | self.buf[1]


class ADS1115(ADS1x15):
    """Class for the ADS1115 16 bit ADC."""

    # Pins
    P0 = 0
    """Analog Pin 0"""
    P1 = 1
    """Analog Pin 1"""
    P2 = 2
    """Analog Pin 2"""
    P3 = 3
    """Analog Pin 3"""

    # Data sample rates
    _ADS1115_CONFIG_DR = {
        8: 0x0000,
        16: 0x0020,
        32: 0x0040,
        64: 0x0060,
        128: 0x0080,
        250: 0x00A0,
        475: 0x00C0,
        860: 0x00E0,
    }

    @property
    def bits(self) -> Literal[16]:
        """The ADC bit resolution."""
        return 16

    @property
    def rates(self) -> List[int]:
        """Possible data rate settings."""
        r = list(self._ADS1115_CONFIG_DR.keys())
        r.sort()
        return r

    @property
    def rate_config(self) -> Dict[int, int]:
        """Rate configuration masks."""
        return self._ADS1115_CONFIG_DR

    def _data_rate_default(self) -> Literal[128]:
        return 128

    def _conversion_value(self, raw_adc: int) -> int:
        value = struct.unpack(">h", raw_adc.to_bytes(2, "big"))[0]
        return value


class ADS1115weno:
    i2c = None

    # IC Identifiers
    __IC_ADS1115 = 0x01

    # Config Register
    __ADS1115_REG_CONFIG_DR_8SPS = 0x0000  # 8 samples per second
    __ADS1115_REG_CONFIG_DR_16SPS = 0x0020  # 16 samples per second
    __ADS1115_REG_CONFIG_DR_32SPS = 0x0040  # 32 samples per second
    __ADS1115_REG_CONFIG_DR_64SPS = 0x0060  # 64 samples per second
    __ADS1115_REG_CONFIG_DR_128SPS = 0x0080  # 128 samples per second
    __ADS1115_REG_CONFIG_DR_250SPS = 0x00A0  # 250 samples per second (default)
    __ADS1115_REG_CONFIG_DR_475SPS = 0x00C0  # 475 samples per second
    __ADS1115_REG_CONFIG_DR_860SPS = 0x00E0  # 860 samples per second

    __ADS1015_REG_CONFIG_CQUE_MASK = 0x0003
    __ADS1015_REG_CONFIG_CQUE_1CONV = 0x0000  # Assert ALERT/RDY after one conversions
    __ADS1015_REG_CONFIG_CQUE_2CONV = 0x0001  # Assert ALERT/RDY after two conversions
    __ADS1015_REG_CONFIG_CQUE_4CONV = 0x0002  # Assert ALERT/RDY after four conversions
    __ADS1015_REG_CONFIG_CQUE_NONE = (
        0x0003  # Disable the comparator and put ALERT/RDY in high state (default)
    )

    __ADS1015_REG_CONFIG_CMODE_MASK = 0x0010
    __ADS1015_REG_CONFIG_CMODE_TRAD = (
        0x0000  # Traditional comparator with hysteresis (default)
    )
    __ADS1015_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

    __ADS1015_REG_CONFIG_CPOL_MASK = 0x0008
    __ADS1015_REG_CONFIG_CPOL_ACTVLOW = (
        0x0000  # ALERT/RDY pin is low when active (default)
    )
    __ADS1015_REG_CONFIG_CPOL_ACTVHI = 0x0008  # ALERT/RDY pin is high when active

    __ADS1015_REG_CONFIG_CLAT_MASK = (
        0x0004  # Determines if ALERT/RDY pin latches once asserted
    )
    __ADS1015_REG_CONFIG_CLAT_NONLAT = 0x0000  # Non-latching comparator (default)
    __ADS1015_REG_CONFIG_CLAT_LATCH = 0x0004  # Latching comparator

    __ADS1015_REG_CONFIG_MODE_MASK = 0x0100
    __ADS1015_REG_CONFIG_MODE_CONTIN = 0x0000  # Continuous conversion mode
    __ADS1015_REG_CONFIG_MODE_SINGLE = 0x0100  # Power-down single-shot mode (default)

    __ADS1015_REG_CONFIG_PGA_MASK = 0x0E00
    __ADS1015_REG_CONFIG_PGA_6_144V = 0x0000  # +/-6.144V range
    __ADS1015_REG_CONFIG_PGA_4_096V = 0x0200  # +/-4.096V range
    __ADS1015_REG_CONFIG_PGA_2_048V = 0x0400  # +/-2.048V range (default)
    __ADS1015_REG_CONFIG_PGA_1_024V = 0x0600  # +/-1.024V range
    __ADS1015_REG_CONFIG_PGA_0_512V = 0x0800  # +/-0.512V range
    __ADS1015_REG_CONFIG_PGA_0_256V = 0x0A00  # +/-0.256V range

    __ADS1015_REG_CONFIG_MUX_MASK = 0x7000
    __ADS1015_REG_CONFIG_MUX_DIFF_0_1 = (
        0x0000  # Differential P = AIN0, N = AIN1 (default)
    )
    __ADS1015_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __ADS1015_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __ADS1015_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __ADS1015_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __ADS1015_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __ADS1015_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

    # Config Register
    __ADS1015_REG_CONFIG_OS_MASK = 0x8000
    __ADS1015_REG_CONFIG_OS_SINGLE = 0x8000  # Write: Set to start a single-conversion
    __ADS1015_REG_CONFIG_OS_BUSY = (
        0x0000  # Read: Bit = 0 when conversion is in progress
    )
    __ADS1015_REG_CONFIG_OS_NOTBUSY = (
        0x8000  # Read: Bit = 1 when device is not performing a conversion
    )

    # Pointer Register
    __ADS1015_REG_POINTER_MASK = 0x03
    __ADS1015_REG_POINTER_CONVERT = 0x00
    __ADS1015_REG_POINTER_CONFIG = 0x01
    __ADS1015_REG_POINTER_LOWTHRESH = 0x02
    __ADS1015_REG_POINTER_HITHRESH = 0x03

    # Dictionaries with the sampling speed values
    # These simplify and clean the code (avoid the abuse of if/elif/else clauses)
    spsADS1115 = {
        8: __ADS1115_REG_CONFIG_DR_8SPS,
        16: __ADS1115_REG_CONFIG_DR_16SPS,
        32: __ADS1115_REG_CONFIG_DR_32SPS,
        64: __ADS1115_REG_CONFIG_DR_64SPS,
        128: __ADS1115_REG_CONFIG_DR_128SPS,
        250: __ADS1115_REG_CONFIG_DR_250SPS,
        475: __ADS1115_REG_CONFIG_DR_475SPS,
        860: __ADS1115_REG_CONFIG_DR_860SPS,
    }

    # Dictionariy with the programable gains
    pgaADS1x15 = {
        6144: __ADS1015_REG_CONFIG_PGA_6_144V,
        4096: __ADS1015_REG_CONFIG_PGA_4_096V,
        2048: __ADS1015_REG_CONFIG_PGA_2_048V,
        1024: __ADS1015_REG_CONFIG_PGA_1_024V,
        512: __ADS1015_REG_CONFIG_PGA_0_512V,
        256: __ADS1015_REG_CONFIG_PGA_0_256V,
    }

    # Constructor
    def __init__(self, address=0x48, ic=__IC_ADS1115, debug=False, i2c=None):
        self.i2c = i2c
        self.address = address
        self.debug = debug

        # Make sure the IC specified is valid
        self.ic = ic

        # Set pga value, so that getLastConversionResult() can use it,
        # any function that accepts a pga value must update this.
        self.pga = 6144

    async def readADCSingleEnded(self, channel=0, pga=6144, sps=250):
        """
        Gets a single-ended ADC reading from the specified channel in mV.
        The sample rate for this mode (single-shot) can be used to lower the noise
        (low sps) or to lower the power consumption (high sps) by duty cycling,
        see datasheet page 14 for more info.
        The pga must be given in mV, see page 13 for the supported values.
        """

        # With invalid channel return -1
        if channel > 3:
            return -1

        # Disable comparator, Non-latching, Alert/Rdy active low
        # traditional comparator, single-shot mode
        config = (
            self.__ADS1015_REG_CONFIG_CQUE_NONE
            | self.__ADS1015_REG_CONFIG_CLAT_NONLAT
            | self.__ADS1015_REG_CONFIG_CPOL_ACTVLOW
            | self.__ADS1015_REG_CONFIG_CMODE_TRAD
            | self.__ADS1015_REG_CONFIG_MODE_SINGLE
        )

        # Set sample per seconds, defaults to 250sps
        config |= self.spsADS1115.setdefault(sps, self.__ADS1115_REG_CONFIG_DR_250SPS)

        # Set PGA/voltage range, defaults to +-6.144V
        config |= self.pgaADS1x15.setdefault(pga, self.__ADS1015_REG_CONFIG_PGA_6_144V)
        self.pga = pga

        # Set the channel to be converted
        if channel == 3:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_3
        elif channel == 2:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_2
        elif channel == 1:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_1
        else:
            config |= self.__ADS1015_REG_CONFIG_MUX_SINGLE_0

        # Set 'start single-conversion' bit
        config |= self.__ADS1015_REG_CONFIG_OS_SINGLE

        # Write config register to the ADC
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        self.i2c.write_i2c_block_data(
            self.address, self.__ADS1015_REG_POINTER_CONFIG, bytes
        )

        # Wait for the ADC conversion to complete
        # The minimum delay depends on the sps: delay >= 1/sps
        # We add 0.1ms to be sure
        delay = 1.0 / sps + 0.0001
        await asyncio.sleep(delay)

        # Read the conversion results
        result = self.i2c.read_i2c_block_data(
            self.address, self.__ADS1015_REG_POINTER_CONVERT, 2
        )
        # Return a mV value for the ADS1115
        # (Take signed values into account as well)
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            return (val - 0xFFFF) * pga / 32768.0
        else:
            return ((result[0] << 8) | (result[1])) * pga / 32768.0
