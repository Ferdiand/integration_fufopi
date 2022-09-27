"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from base64 import encode
from dataclasses import field
from datetime import timedelta
from decimal import Decimal
import logging
from unicodedata import decimal
import serial
import time
import random


from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .relay_board import RelayBoardPigPio
from homeassistant.components.sensor import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
)

from .const import (
    DOMAIN,
    PLATFORMS,
    STARTUP_MESSAGE,
    PID_VALUE_LIST,
    CS_VALUE_LIST,
    MPPT_VALUE_LIST,
    OR_VALUE_LIST,
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

    coordinator = VEDirectCoordinator(
        hass=hass,
        logger=_LOGGER,
        name="Victron Solar",
        update_interval=timedelta(seconds=2),
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success or not coordinator.config_ready():
        raise ConfigEntryNotReady

    # coordinator.platforms.append("sensor")

    hass.data[DOMAIN][entry.entry_id] = coordinator

    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "sensor"))
    hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, "switch"))

    # for platform in PLATFORMS:
    #    if entry.options.get(platform, True):
    #        coordinator.platforms.append(platform)
    #        hass.async_add_job(#
    #         hass.config_entries.async_forward_entry_setup(entry, platform)
    #        )

    # entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


class VEDirectCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Victron VE Direct"""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        name: str,
        update_interval: timedelta,
    ) -> None:
        super().__init__(hass, logger, name=name, update_interval=update_interval)

        self.relay_board = RelayBoardPigPio()

        try:
            self._serial = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)
            self.simulation = False
        except:
            self.simulation = True

        self.data = {
            "PID": {
                "name": "Product ID",
                "value": "",
                "last_update": time.time(),
                "value_list": PID_VALUE_LIST,
                "icon": "mdi:identifier",
            },
            "FW": {
                "name": "Firmware Version",
                "value": "",
                "last_update": time.time(),
                "icon": "mdi:identifier",
            },
            "SER#": {
                "name": "Serial Number",
                "value": "",
                "last_update": time.time(),
                "icon": "mdi:music-accidental-sharp",
            },
            "V": {
                "name": "Battery Voltage",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.001),
                "unit_meassurement": "V",
                "device_class": DEVICE_CLASS_VOLTAGE,
            },
            "I": {
                "name": "Battery Current",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.001),
                "unit_meassurement": "A",
                "device_class": DEVICE_CLASS_CURRENT,
            },
            "VPV": {
                "name": "Panel Voltage",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.001),
                "unit_meassurement": "V",
                "device_class": DEVICE_CLASS_VOLTAGE,
            },
            "PPV": {
                "name": "Panel Power",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(1.0),
                "unit_meassurement": "W",
                "device_class": DEVICE_CLASS_POWER,
            },
            "CS": {
                "name": "State of operation",
                "value": "",
                "last_update": time.time(),
                "value_list": CS_VALUE_LIST,
                "icon": "mdi:car-turbocharger",
            },
            "MPPT": {
                "name": "Tracker operation mode",
                "value": "",
                "last_update": time.time(),
                "value_list": MPPT_VALUE_LIST,
                "icon": "mdi:radar",
            },
            "OR": {
                "name": "Off Reason",
                "value": "",
                "last_update": time.time(),
                "value_list": OR_VALUE_LIST,
                "icon": "mdi:playlist-remove",
            },
            "H19": {
                "name": "Yield total",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.01),
                "unit_meassurement": "kWh",
                "device_class": DEVICE_CLASS_ENERGY,
            },
            "H20": {
                "name": "Yield today",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.01),
                "unit_meassurement": "kWh",
                "device_class": DEVICE_CLASS_ENERGY,
            },
            "H22": {
                "name": "Yield yesterday",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.01),
                "unit_meassurement": "kWh",
                "device_class": DEVICE_CLASS_ENERGY,
            },
            "H21": {
                "name": "Max power today",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(1.0),
                "unit_meassurement": "W",
                "device_class": DEVICE_CLASS_POWER,
            },
            "H23": {
                "name": "Max power yesterday",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(1.0),
                "unit_meassurement": "W",
                "device_class": DEVICE_CLASS_POWER,
            },
            "HSDS": {
                "name": "Day seq number",
                "value": "",
                "last_update": time.time(),
            },
            "Checksum": {
                "name": "CheckSum",
                "value": "",
                "last_update": time.time(),
            },
            "IL": {
                "name": "Load Current",
                "value": Decimal(),
                "last_update": time.time(),
                "unit_conversion": Decimal(0.001),
                "unit_meassurement": "A",
                "device_class": DEVICE_CLASS_POWER,
            },
        }

    async def _async_update_data(self):
        """Update data via library."""
        _data_cpy = {}
        _data_cpy = self.data
        if self.simulation is False:
            _buffer = self._serial.readlines()
        else:
            _buffer = self.simulate_buffer()
        self.logger.warning(f"{_buffer}")
        for line in _buffer:
            _field = line.split("\t")
            if len(_field) > 1:
                _key = _field[0]
                _value = _field[1]
                if _key in _data_cpy.keys():
                    if isinstance(_data_cpy[_key]["value"], Decimal):
                        _data_cpy[_key]["value"] = Decimal(_value)
                    else:
                        _data_cpy[_key]["value"] = _value
                    _data_cpy[_key]["last_update"] = time.time()
                else:
                    self.logger.warning(f"Key not defined {_field}")
            else:
                self.logger.warning(f"Field structure not valid: {_field}")

        return _data_cpy

    def config_ready(self):
        """retrun true if configuration is ready to finish"""
        return (
            self.data["PID"]["value"] != ""
            and self.data["FW"]["value"] != ""
            and self.data["SER#"]["value"] != ""
        )

    def simulate_buffer(self):
        """return simulated buffer"""
        _buff = []
        for _key in list(self.data.keys()):
            if _key == "PID":
                _buff.append(f"{_key}\t0xA060")
            elif _key == "FW":
                _buff.append(f"{_key}\t156")
            elif _key == "SER#":
                _buff.append(f"{_key}\t1234567890")
            elif _key == "V":
                _buff.append(f"{_key}\t{random.randrange(9000,14500)}")
            elif _key == "I":
                _buff.append(f"{_key}\t{random.randrange(-5000,5000)}")
            elif _key == "IL":
                _buff.append(f"{_key}\t{random.randrange(0,5000)}")
            elif _key == "VPV":
                _buff.append(f"{_key}\t{random.randrange(0,20000)}")
            elif _key == "PPV":
                _buff.append(f"{_key}\t{random.randrange(0,100)}")
            elif _key in ("H19", "H20", "H21", "H22", "H23"):
                _buff.append(f"{_key}\t{random.randrange(0,200)}")
            elif "value_list" in list(self.data[_key].keys()):
                _list = list(self.data[_key]["value_list"].keys())
                # self.logger.warning(f"value list:{_key} ::: {_list}")
                _buff.append(f"{_key}\t{random.choice(_list)}")
        return _buff


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in ["sensor"]
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
