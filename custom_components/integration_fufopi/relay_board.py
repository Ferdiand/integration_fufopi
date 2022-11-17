from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.switch import SwitchEntity

import RPi.GPIO as GPIO

from .const import DOMAIN, ATTRIBUTION


class RelayBoardPigPio:
    """PigPio relay board class"""

    def __init__(self) -> None:
        # Initialite pigpio pi
        GPIO.setmode(GPIO.BOARD)
        self.relay = [
            RelayPigPio(18, True),
            RelayPigPio(23, True),
            RelayPigPio(24, True),
            RelayPigPio(27, True),
        ]


class RelayPigPio:
    """Pigpio relay class"""

    def __init__(self, pin_no, inverted=False) -> None:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_no, GPIO.OUT)
        self._pin_no = pin_no
        self._inverted = inverted
        self.relay_off()

    @property
    def is_on(self):
        """Return if relay is on or not"""
        if GPIO.input(self._pin_no) == 1:
            if self._inverted is True:
                return False
            else:
                return True
        else:
            if self._inverted is True:
                return True
            else:
                return False

    def relay_on(self):
        """Switch relay on"""
        if self._inverted is True:
            GPIO.output(self._pin_no, 0)
        else:
            GPIO.output(self._pin_no, 1)

    def relay_off(self):
        """Switch relay off"""
        if self._inverted is True:
            GPIO.output(self._pin_no, 1)
        else:
            GPIO.output(self._pin_no, 0)


class RelayBoardEntity(CoordinatorEntity):
    """Relay board base entity"""

    def __init__(self, coordinator, config_entry, relay_index):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.relay_index = relay_index

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + f"{self.relay_index}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "relay board")},
            "name": "relay board",
            "model": "4x",
            "manufacturer": "Algun chino",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }

    @property
    def available(self) -> bool:
        _pig = self.coordinator.relay_board.pig
        return _pig.connected


class RelayBoardBinarySwitch(RelayBoardEntity, SwitchEntity):
    """integration_blueprint switch class."""

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self.coordinator.relay_board.relay[self.relay_index].relay_on()
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self.coordinator.relay_board.relay[self.relay_index].relay_off()
        self._attr_is_on = False
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"Relay_{self.relay_index}"
