from ast import Str
from decimal import Decimal

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    DEVICE_CLASS_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    ELECTRIC_CURRENT_AMPERE,
    DEVICE_CLASS_POWER,
    POWER_WATT,
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    DEVICE_CLASS_BATTERY_CHARGING,
)

from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_OUTLET

from homeassistant.components.sensor import SensorEntity

from .const import DOMAIN, ATTRIBUTION
from .SmartSolar import SmartSolarCoordinator


class FridgeEntity(CoordinatorEntity):
    """Power distribution base entity"""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.config_entry = config_entry

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "fridge"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "Drehia")},
            "name": "Drehia CBX-55",
            "model": "CBX-55",
            "manufacturer": "Drehia",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }


class FridgePowerSwitch(FridgeEntity, SwitchEntity):
    """integration_blueprint switch class."""

    def __init__(self, coordinator: SmartSolarCoordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Fridge Power"
        self._attr_device_class = DEVICE_CLASS_OUTLET
        self._relay_index = 1

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return super().unique_id + "power"

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn on the switch."""
        self.coordinator.relay_board.relay[self._relay_index].relay_on()
        # self._attr_is_on = True
        # self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):  # pylint: disable=unused-argument
        """Turn off the switch."""
        self.coordinator.relay_board.relay[self._relay_index].relay_off()
        # self._attr_is_on = False
        # self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.relay_board[self._relay_index].is_on
