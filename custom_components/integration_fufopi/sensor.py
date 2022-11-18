"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from distutils.command.config import config
from .const import DOMAIN

from .ads1115 import add_ads1115_sensors

from .acs714 import add_acs712_sensors

from .power_lane import add_power_lane_sensors


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup entities platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    add_acs712_sensors(sensors, coordinator, entry)

    add_ads1115_sensors(sensors, coordinator, entry)

    add_power_lane_sensors(sensors, coordinator, entry)

    async_add_devices(sensors)
