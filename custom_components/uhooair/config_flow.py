"""Config flow to configure the Uhoo integration."""
import logging

from pyuhoo import Client
from pyuhoo.errors import UnauthorizedError

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from homeassistant.const import CONF_EMAIL, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class UhooFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a Uhoo config flow."""

    VERSION = 1

    def _show_setup_form(self, user_input=None, errors=None):
        """Show the setup form to the user."""
        if user_input is None:
            user_input = {}

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=user_input.get(
                            CONF_EMAIL, "dominik.traechslin@gmail.com"
                        ),
                    ): str,
                    vol.Required(
                        CONF_PASSWORD, default=user_input.get(CONF_PASSWORD, "")
                    ): str,
                }
            ),
            errors=errors or {},
        )

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle a flow initiated by the user."""
        errors = {}

        if user_input is None:
            return self._show_setup_form(user_input, errors)

        username = user_input[CONF_EMAIL]
        password = user_input[CONF_PASSWORD]

        websession = async_get_clientsession(self.hass)

        debug = False
        if _LOGGER.getEffectiveLevel() == logging.DEBUG:
            debug = True

        client = Client(username, password, websession, debug=debug)

        try:
            await client.login()
            await client.get_latest_data()
            # await self.hass.async_add_executor_job(client.get_latest_data)
        except UnauthorizedError as err:
            _LOGGER.error(f"Error: 401 Unauthorized error while logging in: {err}")
            return self.async_abort(reason="unknown")
        except Exception as exp:
            _LOGGER.error("Error when connection to pyuhoo: %s", exp)
            return self.async_abort(reason="unknown")

        devices = client.get_devices()
        for device in devices.values():

            _LOGGER.debug(
                f"Uhoo device found: {device.serial_number}\n \n  "
                + f"Temperatue: {device.temp}\n"
            )

            # Check if already configured
            await self.async_set_unique_id(
                device.serial_number, raise_on_progress=False
            )

            return self.async_create_entry(
                title=f"Uhoo device: {device.serial_number}\n{user_input[CONF_EMAIL]}",
                data=user_input,
            )
