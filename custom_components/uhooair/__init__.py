"""
Support for the uHoo indoor air quality monitor.
For more details about this platform, please refer to the documentation at
Using api https://github.com/altr/pyuhoo.git@merge-patches based on https://gitlab.com/alelec/ha_uhoo
"""
import logging

from pyuhoo import Client
from pyuhoo.errors import UhooError, UnauthorizedError

import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.exceptions import ConfigEntryNotReady

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, PLATFORMS, SCAN_INTERVAL

from homeassistant.const import (
    CONF_EMAIL,
    CONF_PASSWORD,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a uhooair entry."""

    username = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    websession = async_get_clientsession(hass)

    debug = False
    if _LOGGER.getEffectiveLevel() == logging.DEBUG:
        debug = True

    try:
        client = Client(username, password, websession, debug=debug)
        await client.login()
        await client.get_latest_data()
    except UnauthorizedError as err:
        _LOGGER.error(f"Error: 401 Unauthorized error while logging in: {err}")
        return False
    except UhooError as err:
        raise ConfigEntryNotReady(err) from err

    async def async_update_data():
        """Fetch data from API endpoint.
        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            async with async_timeout.timeout(10):
                await client.login()
                await client.get_latest_data()
                return client.get_devices()
        except Exception as err:
            raise UpdateFailed(f"Error while retrieving data: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="uHoo",
        update_method=async_update_data,
        update_interval=SCAN_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    #hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    for platform in PLATFORMS:
        hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, platform))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
