"""Test integration_blueprint switch."""
from unittest.mock import call, patch

from homeassistant.components.switch import SERVICE_TURN_OFF, SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.integration_fufopi import async_setup_entry
from custom_components.integration_fufopi.const import DEFAULT_NAME, DOMAIN, SWITCH

from .const import MOCK_CONFIG
