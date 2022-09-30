"""Constants for integration_blueprint."""
# Base component constants
NAME = "Integration fufopi"
DOMAIN = "integration_fufopi"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/custom-components/integration_blueprint/issues"

# Icons
ICON = "mdi:format-quote-close"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH]

OPTIONS = ["Simulation"]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
PID_VALUE_LIST = {"0xA060": "SmartSolar MPPT 100|20 48V"}
CS_VALUE_LIST = {
    "0": "Off",
    "2": "Fault",
    "3": "Bulk",
    "4": "Absorption",
    "5": "Float",
    "6": "Storage",
    "7": "Equalize (manual)",
    "9": "Inverting",
    "11": "Power supply",
    "245": "Starting-up",
    "246": "Repeated absorption",
    "247": "Auto equalize / Recondition",
    "248": "BatterySafe",
    "252": "External Control",
}
OR_VALUE_LIST = {
    "0x00000000": "No reason", 
    "0x00000001": "No input power",
    "0x00000002": "Switched off (power switch)",
    "0x00000004": "Switched off (device mode register) ",
    "0x00000008": "Remote input",
    "0x00000010": "Protection active ",
    "0x00000020": "Paygo",
    "0x00000040": "BMS",
    "0x00000080": "Engine shutdown",
    "0x00000100": "Analysing input voltage",
}

MPPT_VALUE_LIST = {
    "0": "Off",
    "1": "Voltage or current limited",
    "2": "MPP Tracker active",
}
