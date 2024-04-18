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

import importlib
import pathlib
import secrets
from typing import Optional, ClassVar, Dict, Any
from dotenv import dotenv_values
from pathlib import Path


class Config:
    _instance: ClassVar[Optional['Config']] = None
    env_vars: Dict[str, Any] = {}  # Initializing as a class attribute

    # DIR PATHS
    DIR_PATH: ClassVar[pathlib.Path] = pathlib.Path(__file__).parents[2]
    ENV_FILE_PATH: ClassVar[pathlib.Path] = Path(pathlib.Path(__file__).parents[0] / '.env')
    SETTINGS_FILE_PATH: ClassVar[str] = str(pathlib.Path(__file__).parents[0] / 'settings.py')
    APP_SECRET_KEY: ClassVar[str] = secrets.token_hex(32)

    def __init__(self):
        # Load only the variables defined in the .env file
        self.env_vars = dotenv_values(self.ENV_FILE_PATH)
        for key, value in self.env_vars.items():
            setattr(self, key, value)

        # Load variables from user provided settings module
        # self.settings_module = importlib.import_module("settings")
        self.settings_module = importlib.import_module("config.settings")
        self._load_settings_vars()

        public_url = getattr(self, 'PUBLIC_URL', "http://localhost:8000")
        if public_url:
            self.USER_REDIRECT_URI = f"{public_url}/user/callback"
            self.ADMIN_REDIRECT_URI = f"{public_url}/admin/callback"
        else:
            self.USER_REDIRECT_URI = None
            self.ADMIN_REDIRECT_URI = None

    def _load_settings_vars(self):
        for attribute_name in dir(self.settings_module):
            if not attribute_name.startswith('__') and not attribute_name.endswith('__'):
                attribute_value = getattr(self.settings_module, attribute_name)
                # Filter out functions and classes, only load non-callable attributes
                if not callable(attribute_value):
                    setattr(self, attribute_name, attribute_value)

                    # Add to Environment Variable Dict for printing
                    self.env_vars[attribute_name] = attribute_value

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reload_config(cls):
        cls._instance = None  # Reset the singleton instance
        return cls.get_instance()


c = Config.get_instance()  # Singleton instance of Config
