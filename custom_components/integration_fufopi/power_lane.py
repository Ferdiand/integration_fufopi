""" Power distribution lane """
from decimal import Decimal
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET
from homeassistant.const import (
    ELECTRIC_POTENTIAL_MILLIVOLT,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
)
from RPi import GPIO
from .const import DOMAIN


class PowerLaneEntity(CoordinatorEntity):
    """Power lane entity"""

    def __init__(self, coordinator, config_entry, name, relay_pin, channel_no):
        super().__init__(coordinator)
        self._name = name
        self._sensor_no = channel_no
        self._relay_pin = relay_pin
        self.config_entry = config_entry
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._relay_pin, GPIO.OUT)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "PowerLane" + f"{self._name}"

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.config_entry.entry_id + "PowerLane" + f"{self._name}")
            },
            "name": "PowerLane" + f"{self._name}",
            "manufacturer": "Ermenda",
        }


class PowerLaneCurrentSensor(PowerLaneEntity, SensorEntity):
    """Power lane current sensor"""

    def __init__(self, coordinator, config_entry, name, relay_pin, channel_no):
        super().__init__(coordinator, config_entry, name, relay_pin, channel_no)
        self._attr_name = f"{self._name} current"
        self._attr_native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE
        self._attr_device_class = DEVICE_CLASS_CURRENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _sensor_value = self.coordinator.data[f"ads1115_ch{self._sensor_no}"]
        # sensibility 185 mV/A
        _sensibility = 185

        _raw_value = (_sensor_value - 2500) / _sensibility

        self._attr_native_value = Decimal(_raw_value).quantize(Decimal("0.01"))

        self._attr_extra_state_attributes = {
            "integration": DOMAIN,
            "adschannel": f"ch{self._sensor_no}",
            "sensor_value": _sensor_value,
            "sensor_units": ELECTRIC_POTENTIAL_MILLIVOLT,
            "sensibility": f"{_sensibility} mV/A",
            "raw value": _raw_value,
        }
        self.async_write_ha_state()


class PowerLaneSwitch(PowerLaneEntity, SwitchEntity):
    """Power lane switch"""

    def __init__(self, coordinator, config_entry, name, relay_pin, channel_no):
        super().__init__(coordinator, config_entry, name, relay_pin, channel_no)
        self._attr_name = f"{self._name} switch"
        self._attr_device_class = DEVICE_CLASS_OUTLET

    @property
    def is_on(self) -> bool | None:
        """Return True if entity is on."""
        return GPIO.input(self._pin_no) == 0

    def turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        GPIO.output(self._relay_pin, 0)

    def turn_off(self, **kwargs):
        """Turn the entity off."""
        GPIO.output(self._relay_pin, 1)
