"""BlueprintEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, PID_VALUE_LIST, VERSION, ATTRIBUTION


class VEDirectEntity(CoordinatorEntity):
    """VE Direct base entity"""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator)
        self.config_entry = config_entry
        self.key = key

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + self.key

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.coordinator.data["SER#"]["value"])},
            "name": PID_VALUE_LIST[self.coordinator.data["PID"]["value"]],
            "model": self.coordinator.data["SER#"]["value"],
            "manufacturer": "Victron Energy",
        }

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.unique_id,
            "integration": DOMAIN,
        }
