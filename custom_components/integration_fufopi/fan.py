"""Sensor platform for integration_blueprint."""
from .const import DOMAIN

from .nox_fan import add_nox_fan_fans


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup entities platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    fans = []

    add_nox_fan_fans(fans, coordinator, entry)

    async_add_devices(fans)
