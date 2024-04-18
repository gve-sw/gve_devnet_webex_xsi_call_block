"""
Copyright (c) 2024 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Mark Orszycki <morszyck@cisco.com>"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import secrets
from config.config import c
from datetime import datetime, timezone
from logger.logrr import lm


def in_country(latitude: float, longitude: float):
    """
    Check if given latitude and longitude are within the bounds of the country.
    """
    LAT_MIN = c.LAT_MIN     # Latitude minimum and maximum values for the country
    LAT_MAX = c.LAT_MAX     # Latitude minimum and maximum values for the country
    LON_MIN = c.LON_MIN     # Longitude minimum and maximum values for the country
    LON_MAX = c.LON_MAX     # Longitude minimum and maximum values for the country
    return LAT_MIN <= latitude <= LAT_MAX and LON_MIN <= longitude <= LON_MAX   # Check if the coordinates are within the bounds


def is_geolocation_timeout(geolocation_data):
    """Check if the geolocation data is outdated."""
    geolocation_timeout = c.GEOLOCATION_TIMEOUT     # Timeout in seconds, set in .env
    last_update = geolocation_data.get('last_update')   # Last update time
    if last_update is None:    # Check if the last update time is missing
        lm.lnp("No last update time found; defaulting to timeout.", style="warning", level="warning")
        return True

    current_time = datetime.now(timezone.utc).timestamp()   # Current time in UTC
    if current_time - last_update > geolocation_timeout:    # Check if the geolocation data is outdated
        lm.lnp(f"Geolocation update for user {geolocation_data.get('user_id', 'Unknown')} has timed out.", style="warning", level="warning")
        return True
    lm.lnp(f"Geolocation update for user {geolocation_data.get('user_id', 'Unknown')} is within the allowed period.", style="success", level="info")
    return False


def is_token_expired(token):
    """Check if the token is expired."""
    try:
        return datetime.now().timestamp() > token.get('expires_at', 0)  # Check if the token has expired
    except Exception as e:
        lm.lnp(f"Error checking token expiration: {e}", style="error", level="error")
        return True  # Assume the token is expired if an error occurs


def is_refresh_token_expired(token):
    """Check if the refresh token is expired."""
    try:
        refresh_token_lifespan = token.get('refresh_token_expires_in', 0)  # lifespan in seconds
        token_acquired_time = token.get('acquired_at', datetime.now().timestamp())  # Time when the token was saved
        refresh_token_expiry_time = token_acquired_time + refresh_token_lifespan    # Time when the token will expire
        return datetime.now().timestamp() > refresh_token_expiry_time   # Check if the token has expired
    except Exception as e:
        lm.lnp(f"Error checking refresh token expiration: {e}", style="error", level="error")
        return True  # Assume the refresh token is expired if an error occurs


def generate_session_token(token_len: int = 24):
    """Generate a random session token."""
    token: str = secrets.token_urlsafe(token_len)
    return token
