"""uhooair component constants."""
from __future__ import annotations

from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription

from homeassistant.const import (
    PERCENTAGE,
    TEMP_CELSIUS,
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PRESSURE_PA,
    Platform,
)

DOMAIN = "uhooair"
PLATFORMS = [Platform.SENSOR]
ATTRIBUTION = "Data provided by ha_uhoo"


SCAN_INTERVAL = timedelta(minutes=5)


SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temp",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer",
    ),
    SensorEntityDescription(
        key="humidity",
        name="Humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        icon="mdi:water-percent",
    ),
    SensorEntityDescription(
        key="co2",
        name="Carbon Dioxide",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO2,
        icon="mdi:molecule-co2",
    ),
    SensorEntityDescription(
        key="co",
        name="Carbon Monoxide",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.CO,
        icon="mdi:molecule-co",
    ),
    SensorEntityDescription(
        key="voc",
        name="Volatile Organic Compounds",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        device_class=SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key="dust",
        name="Dust",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        device_class=SensorDeviceClass.PM25,
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key="ozone",
        name="Ozone",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_BILLION,
        device_class=SensorDeviceClass.OZONE,
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key="no2",
        name="Nitrogen Dioxide",
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        device_class=SensorDeviceClass.NITROGEN_DIOXIDE,
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key="pressure",
        name="Air pressure",
        native_unit_of_measurement=PRESSURE_PA,
        device_class=SensorDeviceClass.PRESSURE,
        icon="mdi:cloud",
    ),
)
