"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from distutils.command.config import config
from .const import DOMAIN

from .ads1115 import ADS1115Device

from .acs714 import ACS712Device

from .power_lane import PowerLaneDevice


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup entities platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    devices = []

    ads1115 = ADS1115Device(coordinator, entry)
    ads1115.add_devices(devices)

    acs714 = ACS712Device(coordinator, entry)
    acs714.add_devices(devices)

    power1 = PowerLaneDevice(coordinator, entry, "power 1", 12, 0)
    power1.add_devices(devices)
    power2 = PowerLaneDevice(coordinator, entry, "power 2", 16, 1)
    power2.add_devices(devices)
    power3 = PowerLaneDevice(coordinator, entry, "power 3", 18, 2)
    power3.add_devices(devices)
    power4 = PowerLaneDevice(coordinator, entry, "power 4", 13, 3)
    power4.add_devices(devices)

    async_add_devices(devices)
