""" Smart Solar """
import logging
import random
import serial

from homeassistant.core import callback

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)
from homeassistant.core import Config, HomeAssistant
from homeassistant.components.sensor import (
    SensorEntity,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
)

from datetime import timedelta
from pigpio import pi
from .relay_board import RelayBoardPigPio
from .const import DOMAIN, ATTRIBUTION


PID_VALUE_LIST = {"0xA060": "SmartSolar MPPT 100|20 48V"}

CS_VALUE_LIST = {
    "0": "Off",
    "2": "Fault",
    "3": "Bulk",
    "4": "Absorption",
    "5": "Float",
    "6": "Storage",
    "7": "Equalize (manual)",
    "9": "Inverting",
    "11": "Power supply",
    "245": "Starting-up",
    "246": "Repeated absorption",
    "247": "Auto equalize / Recondition",
    "248": "BatterySafe",
    "252": "External Control",
}

MPPT_VALUE_LIST = {
    "0": "Off",
    "1": "Voltage or current limited",
    "2": "MPP Tracker active",
}

OR_VALUE_LIST = {
    "0x00000000": "No reason",
    "0x00000001": "No input power",
    "0x00000002": "Switched off (power switch)",
    "0x00000004": "Switched off (device mode register) ",
    "0x00000008": "Remote input",
    "0x00000010": "Protection active ",
    "0x00000020": "Paygo",
    "0x00000040": "BMS",
    "0x00000080": "Engine shutdown",
    "0x00000100": "Analysing input voltage",
}

ERR_VALUE_LIST = {
    "0": "No error",
    "2": "Battery voltage too high",
    "17": "Charger temperature too high",
    "18": "Charger over current",
    "19": "Charger current reversed",
    "20": "Bulk time limit exceeded",
    "21": "Current sensor issue (sensor bias/sensor broken)",
    "26": "Terminals overheated",
    "28": "Converter issue (dual converter models only)",
    "33": "Input voltage too high (solar panel)",
    "34": "Input current too high (solar panel)",
    "38": "Input shutdown (due to excessive battery voltage)",
    "39": "Input shutdown (due to current flow during off mode)",
    "65": "Lost communication with one of devices",
    "66": "Synchronised charging device configuration issue",
    "67": "BMS connection lost",
    "68": "Network misconfigured",
    "116": "Factory calibration data lost",
    "117": "Invalid/incompatible firmware",
    "119": "User settings invalid",
}


class SmartSolarCoordinator(DataUpdateCoordinator):
    """Victron Smart Solar charger coordinator"""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        name: str,
        update_interval: timedelta,
    ) -> None:
        super().__init__(hass, logger, name=name, update_interval=update_interval)

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

        self.relay_board = RelayBoardPigPio(pi("172.30.33.0"))

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


class SmartSolarEntity(CoordinatorEntity):
    """VE Direct base entity"""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "SmartSolar"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "HQ2129WD7QV")},
            "name": "SmartSolar MPPT 100|20 48V",
            "model": "HQ2129WD7QV",
            "manufacturer": "Victron Energy",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class SmartSolarProductIDSensor(SmartSolarEntity, SensorEntity):
    """Smart solar Product ID Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Product ID"
        self._attr_icon = "mdi:identifier"

    @property
    def unique_id(self):
        return super().unique_id + "PID"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.product_id

        self.async_write_ha_state()


class SmartSolarFirmwareSensor(SmartSolarEntity, SensorEntity):
    """Smart solar Firmware Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Firmware Version"
        self._attr_icon = "mdi:identifier"

    @property
    def unique_id(self):
        return super().unique_id + "FW"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.firmware

        self.async_write_ha_state()


class SmartSolarSerialNumberSensor(SmartSolarEntity, SensorEntity):
    """Smart solar serial number Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Serial Number"
        self._attr_icon = "mdi:music-accidental-sharp"

    @property
    def unique_id(self):
        return super().unique_id + "SER#"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.serial_number

        self.async_write_ha_state()


class SmartSolarCSSensor(SmartSolarEntity, SensorEntity):
    """Smart solar operation state Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "State of operation"
        self._attr_icon = "mdi:car-turbocharger"

    @property
    def unique_id(self):
        return super().unique_id + "CS"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.state_of_operation

        self.async_write_ha_state()


class SmartSolarMPPTSensor(SmartSolarEntity, SensorEntity):
    """Smart solar tracker op mode Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Tracker operation mode"
        self._attr_icon = "mdi:radar"

    @property
    def unique_id(self):
        return super().unique_id + "MPPT"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.tracker_operation_mode

        self.async_write_ha_state()


class SmartSolarORSensor(SmartSolarEntity, SensorEntity):
    """Smart solar off reason Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Off Reason"
        self._attr_icon = "mdi:playlist-remove"

    @property
    def unique_id(self):
        return super().unique_id + "OR"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.off_reason

        self.async_write_ha_state()


class SmartSolarHSDSSensor(SmartSolarEntity, SensorEntity):
    """Smart solar day seq number Sensor class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Day seq number"

    @property
    def unique_id(self):
        return super().unique_id + "HSDS"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.coordinator.day_seq_number

        self.async_write_ha_state()
