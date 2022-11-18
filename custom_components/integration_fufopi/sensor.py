"""Sensor platform for integration_blueprint."""
from decimal import Decimal
from distutils.command.config import config
from unicodedata import decimal
from homeassistant.components.sensor import (
    SensorEntity,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
    TEMP_CELSIUS,
)

from .const import DEFAULT_NAME, DOMAIN, ICON, SENSOR
from .entity import VEDirectEntity, ClimaDHTEntity

from .SmartSolar import (
    SmartSolarCSSensor,
    SmartSolarFirmwareSensor,
    SmartSolarHSDSSensor,
    SmartSolarORSensor,
    SmartSolarMPPTSensor,
    SmartSolarProductIDSensor,
    SmartSolarSerialNumberSensor,
    SmartSolarCheckSumSensor,
    SmartSolarErrSensor,
    SmartSolarH19Sensor,
    SmartSolarH20Sensor,
    SmartSolarH21Sensor,
    SmartSolarH22Sensor,
    SmartSolarH23Sensor,
    SmartSolarISensor,
    SmartSolarILSensor,
    SmartSolarPPVSensor,
    SmartSolarVPVSensor,
    SmartSolarVSensor,
)

from .battery import (
    BatteryVoltageSensor,
    BatteryCurrentSensor,
    PowerFromBattSensor,
    PowerToBattSensor,
    BatteryPerCentSensor,
)

from .solar_panel import (
    SolarPanelVoltageSensor,
    SolarPanelCurrentSensor,
    SolarPanelPowerSensor,
    SolarPanelProductionTodaySensor,
    SolarPanelMaxPowerTodaySensor,
    SolarPanelProductionYesterdaySensor,
    SolarPanelMaxPowerYesterdaySensor,
    SolarPanelProductionTotalSensor,
)

from .power_distribution import (
    LoadPowerSensor,
    LoadCurrentSensor,
    RpiCurrentSensor,
    RpiPowerSensor,
)

from .fridge import FridgeCurrentSensor, FridgePowerSensor

from .adxl345 import (
    ADXL345AccelXSensor,
    ADXL345AccelYSensor,
    ADXL345AccelZSensor,
    ADXL345BandwidthSensor,
    ADXL345RangeSensor,
)

from .hmc5883L import (
    HCM5883LGainSensor,
    HCM5883LMagXSensor,
    HCM5883LMagYSensor,
    HCM5883LMagZSensor,
    HCM5883LMeasureConfigSensor,
    HCM5883LOperationModeSensor,
    HCM5883LOutputRateSensor,
    HCM5883LRangeSensor,
    HCM5883LResolutionSensor,
    HCM5883LSampleNoSensor,
)

from .ads1115 import ADS1115Sensor

from .acs714 import ACS712Sensor

from .power_lane import PowerLaneCurrentSensor


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    _sensors = []

    _sensors.append(SmartSolarCSSensor(coordinator, entry))
    _sensors.append(SmartSolarFirmwareSensor(coordinator, entry))
    _sensors.append(SmartSolarHSDSSensor(coordinator, entry))
    _sensors.append(SmartSolarORSensor(coordinator, entry))
    _sensors.append(SmartSolarMPPTSensor(coordinator, entry))
    _sensors.append(SmartSolarProductIDSensor(coordinator, entry))
    _sensors.append(SmartSolarSerialNumberSensor(coordinator, entry))
    _sensors.append(SmartSolarCheckSumSensor(coordinator, entry))
    _sensors.append(SmartSolarErrSensor(coordinator, entry))
    _sensors.append(SmartSolarH19Sensor(coordinator, entry))
    _sensors.append(SmartSolarH20Sensor(coordinator, entry))
    _sensors.append(SmartSolarH21Sensor(coordinator, entry))
    _sensors.append(SmartSolarH22Sensor(coordinator, entry))
    _sensors.append(SmartSolarH23Sensor(coordinator, entry))
    _sensors.append(SmartSolarISensor(coordinator, entry))
    _sensors.append(SmartSolarILSensor(coordinator, entry))
    _sensors.append(SmartSolarPPVSensor(coordinator, entry))
    _sensors.append(SmartSolarVPVSensor(coordinator, entry))
    _sensors.append(SmartSolarVSensor(coordinator, entry))

    _sensors.append(BatteryCurrentSensor(coordinator, entry))
    _sensors.append(BatteryVoltageSensor(coordinator, entry))
    _sensors.append(PowerFromBattSensor(coordinator, entry))
    _sensors.append(PowerToBattSensor(coordinator, entry))
    _sensors.append(BatteryPerCentSensor(coordinator, entry))

    _sensors.append(SolarPanelPowerSensor(coordinator, entry))
    _sensors.append(SolarPanelVoltageSensor(coordinator, entry))
    _sensors.append(SolarPanelCurrentSensor(coordinator, entry))
    _sensors.append(SolarPanelProductionTodaySensor(coordinator, entry))
    _sensors.append(SolarPanelMaxPowerTodaySensor(coordinator, entry))
    _sensors.append(SolarPanelProductionYesterdaySensor(coordinator, entry))
    _sensors.append(SolarPanelMaxPowerYesterdaySensor(coordinator, entry))
    _sensors.append(SolarPanelProductionTotalSensor(coordinator, entry))

    _sensors.append(LoadPowerSensor(coordinator, entry))
    _sensors.append(LoadCurrentSensor(coordinator, entry))
    _sensors.append(RpiCurrentSensor(coordinator, entry))
    _sensors.append(RpiPowerSensor(coordinator, entry))

    _sensors.append(FridgeCurrentSensor(coordinator, entry))
    _sensors.append(FridgePowerSensor(coordinator, entry))

    _sensors.append(ADS1115Sensor(coordinator, entry, 0))
    _sensors.append(ADS1115Sensor(coordinator, entry, 1))
    _sensors.append(ADS1115Sensor(coordinator, entry, 2))
    _sensors.append(ADS1115Sensor(coordinator, entry, 3))

    _sensors.append(ACS712Sensor(coordinator, entry, 0))
    _sensors.append(ACS712Sensor(coordinator, entry, 1))
    _sensors.append(ACS712Sensor(coordinator, entry, 2))
    _sensors.append(ACS712Sensor(coordinator, entry, 3))

    _sensors.append(PowerLaneCurrentSensor(coordinator, entry, "Power1", 12, 0))
    _sensors.append(PowerLaneCurrentSensor(coordinator, entry, "Power2", 16, 1))
    _sensors.append(PowerLaneCurrentSensor(coordinator, entry, "Power3", 18, 2))
    _sensors.append(PowerLaneCurrentSensor(coordinator, entry, "Power4", 13, 3))

    #    _sensors.append(ADXL345AccelXSensor(coordinator, entry))
    #    _sensors.append(ADXL345AccelYSensor(coordinator, entry))
    #    _sensors.append(ADXL345AccelZSensor(coordinator, entry))
    #    _sensors.append(ADXL345BandwidthSensor(coordinator, entry))
    #    _sensors.append(ADXL345RangeSensor(coordinator, entry))

    #    _sensors.append(HCM5883LGainSensor(coordinator, entry))
    #    _sensors.append(HCM5883LMagXSensor(coordinator, entry))
    #    _sensors.append(HCM5883LMagYSensor(coordinator, entry))
    #    _sensors.append(HCM5883LMagZSensor(coordinator, entry))
    #    _sensors.append(HCM5883LMeasureConfigSensor(coordinator, entry))
    #    _sensors.append(HCM5883LOperationModeSensor(coordinator, entry))
    #    _sensors.append(HCM5883LOutputRateSensor(coordinator, entry))
    #    _sensors.append(HCM5883LRangeSensor(coordinator, entry))
    #    _sensors.append(HCM5883LResolutionSensor(coordinator, entry))
    #    _sensors.append(HCM5883LSampleNoSensor(coordinator, entry))

    # _sensors.append(LoadPowerSensor(coordinator, entry))

    # _sensors.append(ClimaTemperatureSensor(coordinator, entry))
    # _sensors.append(ClimaHumiditySensor(coordinator, entry))

    async_add_devices(_sensors)


class IntegrationBlueprintSensor(VEDirectEntity, SensorEntity):
    """integration_blueprint Sensor class."""

    def __init__(self, coordinator, config_entry, key):
        super().__init__(coordinator, config_entry, key)
        _data = self.coordinator.data[self.key]
        if "device_class" in list(_data.keys()):
            self._attr_device_class = _data["device_class"]
        if "unit_meassurement" in list(_data.keys()):
            self._attr_native_unit_of_measurement = _data["unit_meassurement"]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.coordinator.data[self.key]["name"]

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        _data = self.coordinator.data[self.key]
        if isinstance(_data["value"], Decimal):
            _decimal = Decimal()
            _decimal = (_data["value"] * _data["unit_conversion"]).quantize(
                Decimal("1.000")
            )
            return _decimal

        if "value_list" in list(_data.keys()):
            return _data["value_list"][_data["value"]]

        return self.coordinator.data[self.key]["value"]

    @property
    def icon(self) -> str | None:
        _data = self.coordinator.data[self.key]
        if not isinstance(_data["value"], Decimal):
            if "icon" in list(_data.keys()):
                return _data["icon"]

        return super().icon


class ClimaTemperatureSensor(ClimaDHTEntity, SensorEntity):
    """Tempreature sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        self._attr_native_unit_of_measurement = TEMP_CELSIUS

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Temperatura"

    @property
    def native_value(self):
        return self.coordinator.clima_data["temp_c"]

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "temp"


class ClimaHumiditySensor(ClimaDHTEntity, SensorEntity):
    """Humidity sensor"""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_device_class = DEVICE_CLASS_HUMIDITY
        self._attr_native_unit_of_measurement = "%"

    @property
    def name(self):
        """Return the name of the sensor."""
        return "Humidity"

    @property
    def native_value(self):
        return self.coordinator.clima_data["humidity"]

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id + "hum"
