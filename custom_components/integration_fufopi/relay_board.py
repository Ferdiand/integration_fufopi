from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.switch import SwitchEntity, is_on
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, ATTRIBUTION

from pigpio import OUTPUT, pi


class RelayBoardPigPio:
    """PigPio relay board class"""

    def __init__(self, pi) -> None:
        # Initialite pigpio pi
        self.pig = pi
        self.relay = [
            RelayPigPio(18, self.pig, True),
            RelayPigPio(23, self.pig, True),
            RelayPigPio(17, self.pig, True),
            RelayPigPio(27, self.pig, True),
        ]

    @property
    def is_conected(self):
        """return if pigpio is connected"""
        return self.pig.connected


class RelayPigPio:
    """Pigpio relay class"""

    def __init__(self, pin_no, pi, inverted=False) -> None:
        pi.set_mode(pin_no, OUTPUT)
        self._pin_no = pin_no
        self._pi = pi
        self._inverted = inverted
        self.relay_off()

    @property
    def is_on(self):
        """Return if relay is on or not"""
        if self._pi.read(self._pin_no) == 1:
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
            self._pi.write(self._pin_no, 0)
        else:
            self._pi.write(self._pin_no, 1)

    def relay_off(self):
        """Switch relay off"""
        if self._inverted is True:
            self._pi.write(self._pin_no, 1)
        else:
            self._pi.write(self._pin_no, 0)


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


class RelayBoardBinarySwitch(RelayBoardEntity, SwitchEntity):
    """integration_blueprint switch class."""

    def turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self.coordinator.relay_board.relay[self.relay_index].relay_on()

    def turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self.coordinator.relay_board.relay[self.relay_index].relay_off()

    @property
    def name(self):
        """Return the name of the switch."""
        return f"Relay_{self.relay_index}"

    @property
    def is_on(self) -> bool | None:
        return is_on(self.coordinator.hass, self.entity_id)
