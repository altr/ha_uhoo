"""
Support for the uHoo indoor air quality monitor.

For more details about this platform, please refer to the documentation at
https://github.com/mcclown/home-assistant-custom-components
"""

from datetime import timedelta
import logging
import async_timeout
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
    TEMP_CELSIUS,
)

from homeassistant.components.sensor import SensorDeviceClass

from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from homeassistant import config_entries, core

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

_LOGGER = logging.getLogger(__name__)

ATTR_SCORE = "score"
ATTR_TIMESTAMP = "timestamp"
ATTR_LAST_API_UPDATE = "last_api_update"
ATTR_COMPONENT = "component"
ATTR_VALUE = "value"
ATTR_SENSORS = "sensors"

DEVICE_CLASS_PM2_5 = "PM2.5"
DEVICE_CLASS_CARBON_DIOXIDE = "Carbon Dioxide"
DEVICE_CLASS_CARBON_MONOXIDE = "Carbon Monoxide"
DEVICE_CLASS_VOLATILE_ORGANIC_COMPOUNDS = "TVOC"
DEVICE_CLASS_OZONE = "Ozone"
DEVICE_CLASS_NITROGEN_DIOXIDE = "Nitrogen Dioxide"
DEVICE_CLASS_AIR_PRESSURE = "Air Pressure"

SENSOR_TYPES = {
    "temp": {
        "device_class": SensorDeviceClass.TEMPERATURE,
        "unit_of_measurement": TEMP_CELSIUS,
        "icon": "mdi:thermometer",
    },
    "humidity": {
        "device_class": SensorDeviceClass.HUMIDITY,
        "unit_of_measurement": "%",
        "icon": "mdi:water-percent",
    },
    "co2": {
        "device_class": DEVICE_CLASS_CARBON_DIOXIDE,
        "unit_of_measurement": "ppm",
        "icon": "mdi:periodic-table-co2",
    },
    "co": {
        "device_class": DEVICE_CLASS_CARBON_MONOXIDE,
        "unit_of_measurement": "ppm",
        "icon": "mdi:cloud",
    },
    "voc": {
        "device_class": DEVICE_CLASS_VOLATILE_ORGANIC_COMPOUNDS,
        "unit_of_measurement": "ppb",
        "icon": "mdi:cloud",
    },
    "dust": {
        "device_class": DEVICE_CLASS_PM2_5,
        "unit_of_measurement": "µg/m3",
        "icon": "mdi:cloud",
    },
    "ozone": {
        "device_class": DEVICE_CLASS_OZONE,
        "unit_of_measurement": "ppb",
        "icon": "mdi:cloud",
    },
    "no2": {
        "device_class": DEVICE_CLASS_NITROGEN_DIOXIDE,
        "unit_of_measurement": "ppb",
        "icon": "mdi:cloud",
    },
    "pressure": {
        "device_class": DEVICE_CLASS_AIR_PRESSURE,
        "unit_of_measurement": "nPa",
        "icon": "mdi:cloud",
    },
}

# This is the minimum time between throttled update calls.
# Don't bother asking us for state more often than that.
SCAN_INTERVAL = timedelta(minutes=5)

# UHOOAIR_DEVICE_SCHEMA = vol.Schema({
#    vol.Required(CONF_SERIAL_NUMBER): cv.string,
# })

PLATFORM_SCHEMA = cv.PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string
        # vol.Optional(CONF_DEVICES): vol.All(cv.ensure_list, [UHOOAIR_DEVICE_SCHEMA]),
    }
)


async def async_setup_platform(
    hass: core.HomeAssistant,
    config: config_entries.ConfigEntry,
    async_add_entities,
    discovery_info=None,
):
    """Connect to the uHoo API and find devices."""
    from pyuhoo import Client
    from aiohttp import ClientSession

    # from pyuhoo.data import get_all_devices
    # from pyuhoo.objects import UhooDev

    # session = async_get_clientsession(hass)
    # github = GitHubAPI(session, "requester", oauth_token=config[CONF_ACCESS_TOKEN])
    # sensors = [GitHubRepoSensor(github, repo) for repo in config[CONF_REPOS]]
    # async_add_entities(sensors, update_before_add=True)

    username = config[CONF_EMAIL]
    password = config[CONF_PASSWORD]
    async with ClientSession() as websession:

        debug = False
        if _LOGGER.level == logging.DEBUG:
            debug = True

        client = Client(username, password, websession, debug=debug)

        try:
            await client.login()
            await client.get_latest_data()

            async def async_update_data():
                """Fetch data from API endpoint.

                This is the place to pre-process the data to lookup tables
                so entities can quickly look up their data.
                """
                try:
                    # Note: asyncio.TimeoutError and aiohttp.ClientError are already
                    # handled by the data update coordinator.
                    async with async_timeout.timeout(10):
                        await client.login()
                        return await client.get_latest_data()
                except Exception as err:
                    raise UpdateFailed(f"Error communicating with API: {err}")

            coordinator = DataUpdateCoordinator(
                hass,
                _LOGGER,
                # Name of the data. For logging purposes.
                name="uHoo",
                update_method=async_update_data,
                # Polling interval. Will only be polled if there are subscribers.
                update_interval=timedelta(seconds=5 * 60),
            )

            # Fetch initial data so we have data when entities subscribe
            await coordinator.async_refresh()

            all_devices = []
            devices = client.get_devices()

            for device in devices.values():

                _LOGGER.debug(
                    f"Found: {device.serial_number}\n  {device.created_at}\n  "
                    + f"{device.temp} {client.user_settings_temp}\n"
                )

                for sensor in SENSOR_TYPES:
                    if hasattr(device, sensor):
                        uhoo_sensor = UhooAirSensor(coordinator, device, sensor)
                        all_devices.append(uhoo_sensor)

            async_add_entities(all_devices, update_before_add=True)
            return
        except Exception as e:
            _LOGGER.error("Error: {0}".format(e))

    raise PlatformNotReady


class UhooAirSensor(Entity):
    """Implementation of a uHooAir device."""

    def __init__(self, coordinator, device, sensor_type):
        """Initialize the sensor."""
        self._coordinator = coordinator
        self._device = device

        self._uuid = device.serial_number
        self._device_class = SENSOR_TYPES[sensor_type]["device_class"]
        self._name = "{0} {1}".format(device.name, self._device_class)
        self._unit_of_measurement = SENSOR_TYPES[sensor_type]["unit_of_measurement"]
        self._type = sensor_type
        self._available = True

    @property
    def device_class(self) -> str:
        """Return the device class."""
        return self._device_class

    @property
    def icon(self) -> str:
        """Icon to use in the frontend."""
        return SENSOR_TYPES[self._type]["icon"]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return self._unit_of_measurement

    @property
    def should_poll(self):
        """Should device be polled"""
        return True

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return the unique ID of the sensor."""
        return "{}_{}".format(self._uuid, self._type)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    @property
    def state(self) -> Optional[str]:
        return getattr(self._device, self._type)

    @property
    def device_state_attributes(self) -> Dict[str, Any]:
        return {}

    async def async_update(self):
        """Refresh data"""
        try:
            # Fetch data
            await self._coordinator.async_refresh()
        except Exception as e:
            _LOGGER.error("Error: {0}".format(e))
