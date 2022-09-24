"""
Custom integration to integrate integration_blueprint with Home Assistant.

For more details about this integration, please refer to
https://github.com/custom-components/integration_blueprint
"""
import asyncio
from base64 import encode
from dataclasses import field
from datetime import timedelta
import logging
import serial
import time

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    PLATFORMS,
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

    coordinator = VEDirectCoordinator(
        hass=hass, logger=_LOGGER, name="Victron Solar", update_interval=timedelta(2)
    )
    await coordinator.async_refresh()

    if not coordinator.last_update_success or not coordinator.config_ready():
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # for platform in PLATFORMS:
    #    if entry.options.get(platform, True):
    #        coordinator.platforms.append(platform)
    #        hass.async_add_job(#
    #         hass.config_entries.async_forward_entry_setup(entry, platform)
    #        )

    # entry.async_on_unload(entry.add_update_listener(async_reload_entry))
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

        try:
            self._serial = serial.Serial("/dev/ttyUSB0", baudrate=19200, timeout=1)
            self.simulation = False
        except:
            self.simulation = True

        self.data = {
            "PID": {"value": "", "last_update": time.time()},
            "FW": {"value": "", "last_update": time.time()},
            "SER#": {"value": "", "last_update": time.time()},
            "V": {"value": "", "last_update": time.time()},
            "I": {"value": "", "last_update": time.time()},
            "VPV": {"value": "", "last_update": time.time()},
            "PPV": {"value": "", "last_update": time.time()},
            "CS": {"value": "", "last_update": time.time()},
            "MPPT": {"value": "", "last_update": time.time()},
            "OR": {"value": "", "last_update": time.time()},
            "ERR": {"value": "", "last_update": time.time()},
            "LOAD": {"value": "", "last_update": time.time()},
            "H19": {"value": "", "last_update": time.time()},
            "H20": {"value": "", "last_update": time.time()},
            "H21": {"value": "", "last_update": time.time()},
            "H22": {"value": "", "last_update": time.time()},
            "H23": {"value": "", "last_update": time.time()},
            "HSDS": {"value": "", "last_update": time.time()},
            "Checksum": {"value": "", "last_update": time.time()},
            "IL": {"value": "", "last_update": time.time()},
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
            self.data["PID"]["value"] is not ""
            and self.data["FW"]["value"] is not ""
            and self.data["SER#"]["value"] is not ""
        )

    def simulate_buffer(self):
        """return simulated buffer"""
        return [
            "PID\t0x000",
            "FW\t156",
            "SER#\t453646543643",
            "V\t12000",
            "I\t10000",
            "VPV\t19000",
            "PPV\t50",
            "CS\t0",
            "MPPT\t0",
            "OR\t0x0000",
            "ERR\t0",
            "LOAD\tON",
            "H19\t15",
            "H20\t33",
            "H21\t34",
            "H22\t34",
            "H23\t45",
            "HSDS\t69",
            "Checksum\tb",
            "IL\t500",
        ]


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
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
