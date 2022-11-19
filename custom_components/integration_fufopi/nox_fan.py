""" ACS714 """
from decimal import Decimal
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from RPi import GPIO

from homeassistant.const import (
    ELECTRIC_POTENTIAL_MILLIVOLT,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
)

from homeassistant.components.fan import FanEntity, FanEntityFeature

from .const import DOMAIN


def add_nox_fan_fans(fans, coordinator, config_entry):
    """Add devices"""
    fans.append(NoxFanFan(coordinator, config_entry, 15))


class NoxFanEntity(CoordinatorEntity):
    """Nox fan base entity"""

    def __init__(self, coordinator, config_entry, pin_no):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._pin_no = pin_no
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._pin_no, GPIO.OUT)
        self._pwm = GPIO.PWM(self._pin_no, 100)
        self._pwm.start(100)

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "NOXFAN" + f"{self._pin_no}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id + "NOXFAN")},
            "name": "Nox fan",
            "model": "Megachuli",
            "manufacturer": "Nox",
        }


class NoxFanFan(NoxFanEntity, FanEntity):
    """Nox fan fan"""

    def __init__(self, coordinator, config_entry, pin_no):
        super().__init__(coordinator, config_entry, pin_no)
        self._attr_name = f"Nox fan {self._pin_no}"
        self._attr_supported_features = FanEntityFeature.SET_SPEED

    async def async_turn_on(
        self,
        speed: Optional[str] = None,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan."""
        self._pwm.ChangeDutyCycle(percentage)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        self._pwm.ChangeDutyCycle(0)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        self._pwm.ChangeDutyCycle(percentage)
