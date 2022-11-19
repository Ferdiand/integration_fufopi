"""Sensor platform for integration_blueprint."""
from .const import DOMAIN

from .ads1115 import add_ads1115_sensors

from .acs714 import add_acs712_sensors

from .smart_solar_MPPT import add_smart_solar_mppt_sensors

from .power_lane import add_power_lane_sensors


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup entities platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    sensors = sensors + add_acs712_sensors(coordinator, entry)

    sensors = sensors + add_ads1115_sensors(coordinator, entry)

    add_smart_solar_mppt_sensors(sensors, coordinator, entry)

    add_power_lane_sensors(sensors, coordinator, entry)

    async_add_devices(sensors)
